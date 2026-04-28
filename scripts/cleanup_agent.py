"""
scripts/cleanup_agent.py

Weekly code cleanup agent — reads ESLint + Ruff lint reports generated
by the CI workflow, calls OpenAI to refactor each source file, writes
changes back to disk, and produces a PR body summary.

Triggered by: .github/workflows/code-cleanup.yml
Writes to:    backend/**  and  frontend/src/**
Produces:     pr_body.md  (consumed by peter-evans/create-pull-request)
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path

from openai import OpenAI

# ─── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent

# Source trees the agent is allowed to touch (mirrors workflow add-paths)
ALLOWED_TREES = [
    REPO_ROOT / "backend",
    REPO_ROOT / "frontend" / "src",
]

# File extensions to process
PYTHON_EXTS = {".py"}
JS_EXTS = {".js", ".jsx", ".ts", ".tsx"}

# Lint report paths written by the workflow before this script runs
ESLINT_REPORT = REPO_ROOT / "eslint-report.json"
RUFF_REPORT = REPO_ROOT / "ruff-report.json"

# Output: PR body consumed by create-pull-request action
PR_BODY_PATH = REPO_ROOT / "pr_body.md"

# OpenAI settings
MODEL = os.environ.get("CLEANUP_MODEL", "gpt-4o-mini")
MAX_TOKENS = 4096


# ─── Helpers ──────────────────────────────────────────────────────────────────


def load_json_report(path: Path) -> list[dict]:
    """Load a lint JSON report, returning [] if missing or invalid."""
    if not path.exists():
        print(f"[info] Report not found, skipping: {path.name}")
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError as exc:
        print(f"[warn] Could not parse {path.name}: {exc}")
        return []


def collect_lint_issues(eslint: list[dict], ruff: list[dict]) -> dict[Path, list[str]]:
    """
    Merge ESLint and Ruff reports into a dict keyed by absolute file path,
    with a list of human-readable issue strings per file.
    """
    issues: dict[Path, list[str]] = {}

    # ESLint report: list of {filePath, messages: [{ruleId, message, line, column}]}
    for file_result in eslint:
        path = Path(file_result.get("filePath", ""))
        if not path.exists():
            continue
        msgs = file_result.get("messages", [])
        if not msgs:
            continue
        issues.setdefault(path, [])
        for m in msgs:
            rule = m.get("ruleId") or "no-rule"
            line = m.get("line", "?")
            col = m.get("column", "?")
            text = m.get("message", "")
            issues[path].append(f"  [{rule}] line {line}:{col} — {text}")

    # Ruff report: list of {filename, message, code, location: {row, column}}
    for entry in ruff:
        path = Path(entry.get("filename", ""))
        if not path.exists():
            continue
        issues.setdefault(path, [])
        code = entry.get("code", "?")
        loc = entry.get("location", {})
        row = loc.get("row", "?")
        col = loc.get("column", "?")
        msg = entry.get("message", "")
        issues[path].append(f"  [{code}] line {row}:{col} — {msg}")

    return issues


def collect_source_files() -> list[Path]:
    """Walk ALLOWED_TREES and return all processable source files."""
    files: list[Path] = []
    for tree in ALLOWED_TREES:
        if not tree.exists():
            continue
        for ext in PYTHON_EXTS | JS_EXTS:
            files.extend(tree.rglob(f"*{ext}"))
    # Exclude common non-source paths
    excluded = {"node_modules", "__pycache__", ".git", "dist", "build", ".venv"}
    return [f for f in files if not any(part in excluded for part in f.parts)]


def language_label(path: Path) -> str:
    return "Python" if path.suffix in PYTHON_EXTS else "JavaScript/JSX"


def build_system_prompt() -> str:
    return textwrap.dedent("""\
        You are a senior software engineer performing a code cleanup and refactor pass.

        Your job:
        1. Fix all lint issues listed (if any) for the given file.
        2. Apply these best practices regardless of lint findings:
           - Remove unused imports and dead code
           - Improve naming (PEP8 for Python; camelCase/PascalCase for JS/JSX)
           - Extract repeated logic into well-named helper functions
           - Add or improve inline comments for non-obvious logic
           - Prefer explicit over implicit; avoid magic numbers
           - Keep functions short and single-purpose
           - Preserve all existing behaviour exactly — do NOT change logic

        Rules:
        - Return ONLY the fully refactored file content, no markdown fences, no explanation.
        - If the file needs no changes, return it exactly as provided.
        - Never change public API signatures, exported names, or class/function contracts.
    """)


def refactor_file(
    client: OpenAI,
    path: Path,
    source: str,
    lint_issues: list[str],
) -> tuple[str, bool]:
    """
    Ask OpenAI to refactor a single file.
    Returns (refactored_source, was_changed).
    """
    lang = language_label(path)
    issues_block = (
        "\n".join(lint_issues)
        if lint_issues
        else "  (no lint issues reported — apply general best practices)"
    )

    user_prompt = textwrap.dedent(f"""\
        Language: {lang}
        File: {path.relative_to(REPO_ROOT)}

        Lint issues to fix:
        {issues_block}

        Source code:
        ```
        {source}
        ```
    """)

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,  # Low temperature for deterministic refactoring
    )

    refactored = response.choices[0].message.content or source

    # Strip accidental markdown fences the model may add despite instructions
    if refactored.startswith("```"):
        lines = refactored.splitlines()
        # Drop first and last fence lines
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        refactored = "\n".join(inner)

    was_changed = refactored.strip() != source.strip()
    return refactored, was_changed


# ─── PR Body Builder ──────────────────────────────────────────────────────────


def build_pr_body(changed: list[Path], skipped: list[Path], errors: list[tuple[Path, str]]) -> str:
    lines = [
        "## Automated Weekly Code Cleanup",
        "",
        "This PR was generated by `scripts/cleanup_agent.py` using OpenAI.",
        "",
        "### What was reviewed",
        "- Dead code and unused imports",
        "- Naming conventions (PEP8 / camelCase / PascalCase)",
        "- Code duplication and extract-function opportunities",
        "- ESLint warnings (frontend) and Ruff lint warnings (backend)",
        "- Inline comments and general readability",
        "",
    ]

    if changed:
        lines.append(f"### Files refactored ({len(changed)})")
        for p in sorted(changed):
            lines.append(f"- `{p.relative_to(REPO_ROOT)}`")
        lines.append("")

    if skipped:
        lines.append(f"### Files with no changes needed ({len(skipped)})")
        for p in sorted(skipped):
            lines.append(f"- `{p.relative_to(REPO_ROOT)}`")
        lines.append("")

    if errors:
        lines.append(f"### Files that could not be processed ({len(errors)})")
        for p, reason in sorted(errors, key=lambda x: x[0]):
            lines.append(f"- `{p.relative_to(REPO_ROOT)}` — {reason}")
        lines.append("")

    lines += [
        "> **Review before merging.** This PR is opened as a draft.",
        "> Verify each change preserves existing behaviour.",
    ]

    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[error] OPENAI_API_KEY is not set. Aborting.")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Load lint reports produced by the workflow's ESLint + Ruff steps
    print("[step] Loading lint reports...")
    eslint_data = load_json_report(ESLINT_REPORT)
    ruff_data = load_json_report(RUFF_REPORT)
    lint_issues = collect_lint_issues(eslint_data, ruff_data)

    files_with_issues = len(lint_issues)
    total_issues = sum(len(v) for v in lint_issues.values())
    print(f"[info] {files_with_issues} files with lint issues, {total_issues} total findings")

    # Collect all source files in scope
    source_files = collect_source_files()
    print(f"[step] Found {len(source_files)} source files to process")

    changed: list[Path] = []
    skipped: list[Path] = []
    errors: list[tuple[Path, str]] = []

    for path in source_files:
        rel = path.relative_to(REPO_ROOT)
        issues = lint_issues.get(path, [])

        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"  [skip] Cannot read {rel}: {exc}")
            errors.append((path, str(exc)))
            continue

        # Skip empty files
        if not source.strip():
            skipped.append(path)
            continue

        print(f"  [refactor] {rel} ({len(issues)} lint issues)...")

        try:
            refactored, was_changed = refactor_file(client, path, source, issues)
        except Exception as exc:
            print(f"  [error] {rel}: {exc}")
            errors.append((path, str(exc)))
            continue

        if was_changed:
            path.write_text(refactored, encoding="utf-8")
            print(f"  [updated] {rel}")
            changed.append(path)
        else:
            print(f"  [no change] {rel}")
            skipped.append(path)

    # Write PR body for the create-pull-request action to consume
    pr_body = build_pr_body(changed, skipped, errors)
    PR_BODY_PATH.write_text(pr_body, encoding="utf-8")
    print(f"\n[done] PR body written to {PR_BODY_PATH.name}")
    print(f"[done] {len(changed)} files updated, {len(skipped)} unchanged, {len(errors)} errors")

    # Exit non-zero only on hard errors so the workflow can decide
    if errors and not changed:
        sys.exit(1)


if __name__ == "__main__":
    main()