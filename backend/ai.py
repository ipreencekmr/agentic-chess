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
    """Return an OpenAI client if API key and package are available, else None."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not OPENAI_AVAILABLE:
        return None
    return OpenAI(api_key=api_key)

def is_openai_ready() -> bool:
    """Check if OpenAI API key is set and package is available."""
    return bool(os.environ.get("OPENAI_API_KEY")) and OPENAI_AVAILABLE

def _capture_priority_move(board: chess.Board, legal_moves: list[chess.Move]) -> chess.Move:
    """Choose a capture move if available, otherwise pick a random legal move."""
    captures = [move for move in legal_moves if board.is_capture(move)]
    return random.choice(captures) if captures else random.choice(legal_moves)

def _get_stockfish_move(board: chess.Board, legal_moves: list[chess.Move], skill_level: int, depth: int) -> tuple[str | None, str | None]:
    """
    Get the best move from Stockfish engine.
    If engine fails or returns an illegal move, fallback to capture-priority heuristic.
    """
    try:
        engine = StockfishService.getInstance()
        engine.set_skill(skill_level)
        move_uci = engine.get_best_move(fen=board.fen(), depth=depth)
        print(f"Stockfish suggested move: {move_uci}")

        if move_uci and chess.Move.from_uci(move_uci) in legal_moves:
            return move_uci, None
        move = _capture_priority_move(board, legal_moves)
        return move.uci(), "Engine returned no legal move. Falling back to capture-priority heuristic."
    except Exception as exc:
        move = _capture_priority_move(board, legal_moves)
        return move.uci(), f"Engine error: {exc}. Falling back to capture-priority heuristic."

def _get_openai_move(board: chess.Board, legal_moves: list[chess.Move], ai_model: str) -> tuple[str | None, str | None]:
    """
    Get the move from OpenAI agent.
    If OpenAI is unavailable or returns an invalid move, fallback to random legal move.
    """
    client = _openai_client()
    if not client:
        return random.choice(legal_moves).uci(), "OpenAI unavailable"

    try:
        from .agents.move_agent import run_chess_agent
        
        move_uci, error = run_chess_agent(
            client,
            ai_model,
            board.fen(),
            legal_moves
        )

        legal_moves_uci = [m.uci() for m in legal_moves]
        if move_uci and move_uci in legal_moves_uci:
            return move_uci, None

        return random.choice(legal_moves).uci(), "Fallback: invalid move"

    except Exception as exc:
        return random.choice(legal_moves).uci(), f"AI error: {exc}"

def choose_ai_move(board: chess.Board, difficulty: str, ai_model: str) -> tuple[str | None, str | None]:
    """
    Choose an AI move based on difficulty and model.
    Returns a tuple of (move_uci, error_message).
    """
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None, "No legal moves available."

    stockfish_difficulties = {
        "Easy": {"skill_level": 1, "depth": 1},
        "Medium": {"skill_level": 8, "depth": 8},
        "Hard": {"skill_level": 20, "depth": 20},
    }

    if difficulty in stockfish_difficulties:
        params = stockfish_difficulties[difficulty]
        return _get_stockfish_move(board, legal_moves, params["skill_level"], params["depth"])

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

    # Default fallback: random legal move
    return random.choice(legal_moves).uci(), None

# Made with Bob
