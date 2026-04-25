import subprocess
from openai import OpenAI

client = OpenAI()

def get_git_diff():
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "HEAD"],
        capture_output=True,
        text=True
    )
    return result.stdout[:12000]


def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""


def write_readme(content):
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


def update_readme(diff, readme):
    prompt = f"""
You are maintaining a GitHub README.

Update the README based on the latest code changes.

Rules:
- Keep it concise
- Do not remove useful sections
- Do not remove images or badges
- Add new features if detected
- Update setup instructions if needed
- Keep formatting clean markdown

--- CURRENT README ---
{readme}

--- CODE DIFF ---
{diff}

Return ONLY the updated README.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1500
    )

    return response.choices[0].message.content


def main():
    diff = get_git_diff()

    if not diff.strip():
        print("No changes detected")
        return

    readme = read_readme()
    updated = update_readme(diff, readme)

    if updated and updated != readme:
        write_readme(updated)
        print("README updated")
    else:
        print("No meaningful update")


if __name__ == "__main__":
    main()