import os
import random
import chess
from .engine import StockfishService

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
        "Easy": {"skill_level": 1, "depth": 1},
        "Medium": {"skill_level": 8, "depth": 8},
        "Hard": {"skill_level": 20, "depth": 20},
    }
    if difficulty in stockfish_difficulties:
        try:
            params = stockfish_difficulties[difficulty]
            engine = StockfishService.getInstance()
            engine.set_skill(params["skill_level"])
            move_uci = engine.get_best_move(fen=board.fen(), depth=params["depth"])
            print(f"Stockfish suggested move: {move_uci}")

            if move_uci and chess.Move.from_uci(move_uci) in legal_moves:
                return move_uci, None
            move = _capture_priority_move(board, legal_moves)
            return move.uci(), "Engine returned no legal move. Falling back to capture-priority heuristic."
        except Exception as exc:
            move = _capture_priority_move(board, legal_moves)
            return move.uci(), f"Engine error: {exc}. Falling back to capture-priority heuristic."

    # AI Agent uses LLM with tool calling (LLM must use tool, not its own reasoning)
    if difficulty == "AI Agent":
        client = _openai_client()
        if not client:
            return random.choice(legal_moves).uci(), "OpenAI unavailable"

        try:
            from .agents.chess_agent import get_agent_move
            
            move_uci, error = get_agent_move(
                client,
                ai_model,
                board.fen(),
                legal_moves
            )

            if move_uci and move_uci in [m.uci() for m in legal_moves]:
                return move_uci, None

            return random.choice(legal_moves).uci(), "Fallback: invalid move"

        except Exception as exc:
            return random.choice(legal_moves).uci(), f"AI error: {exc}"

    if difficulty == "Capture Priority":
        return _capture_priority_move(board, legal_moves).uci(), None

    return random.choice(legal_moves).uci(), None
