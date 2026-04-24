import os
import subprocess
from stockfish import Stockfish

def get_stockfish():
    path = os.getenv("STOCKFISH_PATH")

    if not path:
        raise RuntimeError("STOCKFISH_PATH environment variable is not set")

    if not os.path.exists(path):
        raise RuntimeError(f"Stockfish binary not found at: {path}")

    stockfish = Stockfish(path=path)
    stockfish.update_engine_parameters({"UCI_LimitStrength": "false"})
    return stockfish

def verify_stockfish(path: str):
    try:
        result = subprocess.run(
            [path],
            input="uci\nquit\n",
            text=True,
            capture_output=True,
            timeout=2
        )

        if "uciok" not in result.stdout:
            raise RuntimeError("Invalid Stockfish response")
    except Exception as e:
        raise RuntimeError(f"Stockfish verification failed: {e}")

def print_engine_settings(stockfish: Stockfish):
    # Move time (your env/config)
    move_time_ms = int(os.getenv("CHESS_ENGINE_MOVE_TIME", "1500"))

    # Depth (if you set it)
    depth = getattr(stockfish, "_depth", "Not explicitly set")

    # Skill level (Stockfish config)
    skill = stockfish.get_parameters().get("Skill Level", "Not set")

    print(f"Move Time (ms): {move_time_ms}")
    print(f"Depth: {depth}")
    print(f"Skill Level: {skill}")