from backend.engine import StockfishService
from langsmith import traceable

@traceable(name="stockfish-best-move")
def get_best_move_tool(fen: str, depth: int = 12):
    """
    Get the best move for the given FEN position using Stockfish.

    Args:
        fen (str): Forsyth–Edwards Notation string representing the board state.
        depth (int): Search depth for Stockfish.

    Returns:
        str: The best move in UCI format.
    """
    engine = StockfishService.getInstance()
    return engine.get_best_move(fen=fen, depth=depth)

def get_top_moves_tool(fen: str, depth: int = 12, k: int = 3):
    """
    Get the top k moves for the given FEN position using Stockfish.

    Args:
        fen (str): Forsyth–Edwards Notation string representing the board state.
        depth (int): Search depth for Stockfish.
        k (int): Number of top moves to return.

    Returns:
        list[str]: List of top moves in UCI format.
    """
    engine = StockfishService.getInstance()
    return engine.get_top_moves(fen=fen, depth=depth, k=k)
