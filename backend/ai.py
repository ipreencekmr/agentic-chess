import os
import random
import chess
from stockfish import Stockfish

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

def choose_ai_move(board: chess.Board, difficulty: str, ai_model: str) -> tuple[str | None, str | None]:
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None, "No legal moves available."

    # Stockfish for Easy, Medium, Hard
    stockfish_difficulties = {
        "Easy": {"skill_level": 1},
        "Medium": {"skill_level": 8},
        "Hard": {"skill_level": 20},
    }
    if difficulty in stockfish_difficulties:
        try:
            params = stockfish_difficulties[difficulty]
            stockfish = Stockfish()
            stockfish.set_fen_position(board.fen())
            stockfish.set_skill_level(params["skill_level"])
            move_uci = stockfish.get_best_move()
            if move_uci and chess.Move.from_uci(move_uci) in legal_moves:
                return move_uci, None
            move = _capture_priority_move(board, legal_moves)
            return move.uci(), "Engine returned no legal move. Falling back to capture-priority heuristic."
        except Exception as exc:
            move = _capture_priority_move(board, legal_moves)
            return move.uci(), f"Engine error: {exc}. Falling back to capture-priority heuristic."

    # OpenAI agent for AI Agent
    if difficulty == "AI Agent":
        client = _openai_client()
        if not client:
            return random.choice(legal_moves).uci(), "OpenAI key unavailable. Falling back to random move."
        try:
            prompt = (
                "You are a chess AI. Given this FEN position:\n"
                f"{board.fen()}\n"
                f"Legal moves: {', '.join(m.uci() for m in legal_moves)}\n"
                "Diligently analyze the current position, considering tactics, strategy, and positional advantages. "
                "Select the best legal move in UCI format. Provide a brief reasoning for your choice. "
                "Format your response as: Move: <uci> Reasoning: <brief reason>"
            )
            response = client.chat.completions.create(
                model=ai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1,
            )
            content = (response.choices[0].message.content or "").strip()
            if "Move:" in content:
                move_uci = content.split("Move:")[1].split()[0].strip().lower()
            else:
                move_uci = content.split()[0].lower()
            if move_uci in [m.uci() for m in legal_moves]:
                return move_uci, None
            return random.choice(legal_moves).uci(), "AI suggested an illegal move. Falling back to random move."
        except Exception as exc:
            return random.choice(legal_moves).uci(), f"AI error: {exc}. Falling back to random move."

    if difficulty == "Capture Priority":
        return _capture_priority_move(board, legal_moves).uci(), None

    return random.choice(legal_moves).uci(), None
