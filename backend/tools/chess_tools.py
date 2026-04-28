from backend.engine import StockfishService
from langsmith import traceable

@traceable(name="stockfish-best-move")
def get_best_move_tool(fen: str, depth: int = 12):
    """
    Get the best move for a given FEN position using Stockfish.

    Args:
        fen (str): The FEN string representing the chess position.
        depth (int, optional): The search depth for Stockfish. Defaults to 12.

    Returns:
        str: The best move in UCI format.
    """
    engine = StockfishService.getInstance()
    return engine.get_best_move(fen=fen, depth=depth)

def get_top_moves_tool(fen: str, depth: int = 12, k: int = 3):
    """
    Get the top k moves for a given FEN position using Stockfish.

    Args:
        fen (str): The FEN string representing the chess position.
        depth (int, optional): The search depth for Stockfish. Defaults to 12.
        k (int, optional): The number of top moves to return. Defaults to 3.

    Returns:
        list[dict]: A list of the top k moves with their evaluations.
    """
    engine = StockfishService.getInstance()
    return engine.get_top_moves(fen=fen, depth=depth, k=k)
