import os
import random
import shutil

import chess
import chess.engine

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


def is_openai_ready() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY")) and OPENAI_AVAILABLE


def _capture_priority_move(board: chess.Board, legal_moves: list[chess.Move]) -> chess.Move:
    captures = [move for move in legal_moves if board.is_capture(move)]
    return random.choice(captures) if captures else random.choice(legal_moves)


def _stockfish_path() -> str | None:
    from_env = os.environ.get("STOCKFISH_PATH")
    if from_env:
        return from_env

    for candidate in ("stockfish", "stockfish.exe"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved

    return None


def choose_ai_move(board: chess.Board, difficulty: str, ai_model: str) -> tuple[str | None, str | None]:
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None, "No legal moves available."

    if difficulty == "Hard (Engine)":
        stockfish = _stockfish_path()
        if not stockfish:
            move = _capture_priority_move(board, legal_moves)
            return move.uci(), "Stockfish not found. Falling back to capture-priority heuristic."
        try:
            move_time = float(os.environ.get("CHESS_ENGINE_MOVE_TIME", "0.8"))
            move_time = max(0.1, min(move_time, 5.0))
            with chess.engine.SimpleEngine.popen_uci(stockfish) as engine:
                result = engine.play(board, chess.engine.Limit(time=move_time))
            if result.move and result.move in legal_moves:
                return result.move.uci(), None
            move = _capture_priority_move(board, legal_moves)
            return move.uci(), "Engine returned no legal move. Falling back to capture-priority heuristic."
        except Exception as exc:
            move = _capture_priority_move(board, legal_moves)
            return move.uci(), f"Engine error: {exc}. Falling back to capture-priority heuristic."

    if difficulty == "AI Agent":
        client = _openai_client()
        if not client:
            return random.choice(legal_moves).uci(), "OpenAI key unavailable. Falling back to random move."
        try:
            prompt = (
                "You are a chess AI. Given this FEN position:\n"
                f"{board.fen()}\n"
                "Return only one best legal move in UCI format, for example e2e4."
            )
            response = client.chat.completions.create(
                model=ai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1,
            )
            move_uci = (response.choices[0].message.content or "").strip().split()[0].lower()
            if move_uci in [m.uci() for m in legal_moves]:
                return move_uci, None
            return random.choice(legal_moves).uci(), "AI suggested an illegal move. Falling back to random move."
        except Exception as exc:
            return random.choice(legal_moves).uci(), f"AI error: {exc}. Falling back to random move."

    if difficulty == "Capture Priority":
        return _capture_priority_move(board, legal_moves).uci(), None

    return random.choice(legal_moves).uci(), None
