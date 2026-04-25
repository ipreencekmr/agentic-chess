from backend.engine import StockfishService

def get_best_move_tool(fen: str, depth: int = 12):
    engine = StockfishService.getInstance()
    return engine.get_best_move(fen=fen, depth=depth)

def get_top_moves_tool(fen: str, depth: int = 12, k: int = 3):
    engine = StockfishService.getInstance()
    return engine.get_top_moves(fen=fen, depth=depth, k=k)