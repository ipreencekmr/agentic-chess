import os
import chess
import threading

class StockfishService:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, path: str):
        import chess.engine
        self.engine = chess.engine.SimpleEngine.popen_uci(path)

    def set_skill(self, level: int):
        self.engine.configure({"Skill Level": level})

    def get_best_move(self, fen: str, depth: int = 12):
        board = chess.Board(fen)
        result = self.engine.play(board, chess.engine.Limit(depth=depth))
        return result.move.uci()

    def get_top_moves(self, fen: str, depth: int = 12, k: int = 3):
        board = chess.Board(fen)
        info = self.engine.analyse(
            board,
            chess.engine.Limit(depth=depth),
            multipv=k
        )

        moves = []
        for entry in info:
            move = entry["pv"][0].uci()
            score = entry["score"].relative.score(mate_score=10000)
            moves.append({"move": move, "score": score})

        return moves

    def evaluate(self, fen: str, depth: int = 12):
        board = chess.Board(fen)
        info = self.engine.analyse(board, chess.engine.Limit(depth=depth))
        score = info["score"].relative

        return {
            "centipawns": score.score(),
            "mate": score.mate()
        }

    def close(self):
        if hasattr(self, "engine") and self.engine:
            try:
                self.engine.quit()
            except Exception:
                pass
            finally:
                self.engine = None
    
    @classmethod
    def shutdown(cls):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    path = os.getenv("STOCKFISH_PATH")

                    print(f"StockfishService->Initialized: {path}")

                    if not path:
                        raise RuntimeError("STOCKFISH_PATH not set")

                    if not os.path.exists(path):
                        raise RuntimeError(f"Stockfish not found at: {path}")

                    cls._instance = cls(path)

        return cls._instance