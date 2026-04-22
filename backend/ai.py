import os
import random

import chess

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    OPENAI_AVAILABLE = False


def _openai_client() -> OpenAI | None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not OPENAI_AVAILABLE:
        return None
    return OpenAI(api_key=api_key)


def choose_ai_move(board: chess.Board, difficulty: str) -> tuple[str | None, str | None]:
    client = _openai_client()
    if client:
        try:
            prompt = (
                "You are a chess AI. Given this FEN position:\n"
                f"{board.fen()}\n"
                "Return only one best legal move in UCI format, for example e2e4."
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1,
            )
            move_uci = (response.choices[0].message.content or "").strip().split()[0].lower()
            if move_uci in [m.uci() for m in board.legal_moves]:
                return move_uci, None
            return None, "AI suggested an illegal move. Falling back to heuristic."
        except Exception as exc:
            return None, f"AI error: {exc}. Falling back to heuristic."

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None, "No legal moves available."

    if difficulty == "Capture Priority":
        captures = [m for m in legal_moves if board.is_capture(m)]
        if captures:
            return random.choice(captures).uci(), None

    return random.choice(legal_moves).uci(), None

