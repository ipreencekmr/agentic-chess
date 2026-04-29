import chess
from backend.engine import StockfishService
from langsmith import traceable

@traceable(name="stockfish-best-move")
def get_best_move_tool(fen: str, depth: int = 12):
    engine = StockfishService.getInstance()
    return engine.get_best_move(fen=fen, depth=depth)

def get_top_moves_tool(fen: str, depth: int = 12, k: int = 3):
    engine = StockfishService.getInstance()
    return engine.get_top_moves(fen=fen, depth=depth, k=k)

@traceable(name="explain-chess-move")
def explain_move_tool(fen: str, move_uci: str, depth: int = 12):
    """
    Analyze a chess move and provide context for LLM explanation.
    Returns: dict with move, evaluation, top alternatives, and move characteristics
    """
    engine = StockfishService.getInstance()
    
    # Get evaluation before move
    eval_before = engine.evaluate(fen, depth)
    
    # Get top moves for comparison
    top_moves = engine.get_top_moves(fen, depth, k=3)
    
    # Apply move and get evaluation after
    board = chess.Board(fen)
    move = chess.Move.from_uci(move_uci)
    
    # Get piece information before move
    piece_moved = board.piece_at(move.from_square)
    piece_symbol = piece_moved.symbol() if piece_moved else "?"
    
    # Check if it's a capture
    is_capture = board.is_capture(move)
    
    # Apply the move
    board.push(move)
    
    # Get evaluation after move
    eval_after = engine.evaluate(board.fen(), depth)
    
    # Check if move results in check
    is_check = board.is_check()
    
    return {
        "move": move_uci,
        "eval_before": eval_before,
        "eval_after": eval_after,
        "top_moves": top_moves,
        "is_capture": is_capture,
        "is_check": is_check,
        "piece_moved": piece_symbol
    }