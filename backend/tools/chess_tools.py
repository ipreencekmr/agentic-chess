from backend.engine import StockfishService
from langsmith import traceable

@traceable(name="stockfish-best-move")
def get_best_move(fen: str, depth: int = 12) -> str:
    """Retrieve the best move for a given FEN string using the Stockfish engine."""
    engine = StockfishService.getInstance()
    return engine.get_best_move(fen=fen, depth=depth)

def get_top_moves(fen: str, depth: int = 12, num_moves: int = 3) -> list:
    """Retrieve the top moves for a given FEN string using the Stockfish engine."""
    engine = StockfishService.getInstance()
    return engine.get_top_moves(fen=fen, depth=depth, k=num_moves)