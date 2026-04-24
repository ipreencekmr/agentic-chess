import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .stockfish_engine import verify_stockfish
from .ai import is_openai_ready
from .game import GameStore
from .schemas import GameStateResponse, MoveRequest, StartGameRequest

load_dotenv()

app = FastAPI(title="Agentic Chess API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = GameStore()

def _get_game_or_404(game_id: str):
    game = store.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found.")
    return game

@app.on_event("startup")
def startup_event():
    path = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")
    print(f"Verifying Stockfish at: {path}")
    verify_stockfish(path)
    print(f"[OK] Stockfish verified at {path}")

@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "openai_available": is_openai_ready()}

@app.post("/api/game/start", response_model=GameStateResponse)
def start_game(payload: StartGameRequest) -> dict:
    if payload.difficulty == "AI Agent" and not is_openai_ready():
        raise HTTPException(status_code=400, detail="AI Agent mode is unavailable because OPENAI_API_KEY is not set.")

    game_id, game = store.create(
        mode=payload.mode,
        difficulty=payload.difficulty,
        ai_model=payload.ai_model,
        white_name=payload.white_name,
        black_name=payload.black_name,
    )
    return game.to_payload(game_id)


@app.get("/api/game/{game_id}", response_model=GameStateResponse)
def get_game(game_id: str) -> dict:
    game = _get_game_or_404(game_id)
    return game.to_payload(game_id)


@app.post("/api/game/{game_id}/move", response_model=GameStateResponse)
def move(game_id: str, payload: MoveRequest) -> dict:
    game = _get_game_or_404(game_id)
    if game.board.is_game_over():
        game.error = "Game is already over."
        return game.to_payload(game_id)

    if not game.push_move(payload.move):
        return game.to_payload(game_id)

    return game.to_payload(game_id)


@app.post("/api/game/{game_id}/agent-move", response_model=GameStateResponse)
def agent_move(game_id: str) -> dict:
    game = _get_game_or_404(game_id)
    if game.board.is_game_over():
        game.error = "Game is already over."
        return game.to_payload(game_id)

    game.maybe_play_ai()
    return game.to_payload(game_id)


@app.post("/api/game/{game_id}/undo", response_model=GameStateResponse)
def undo(game_id: str) -> dict:
    game = _get_game_or_404(game_id)
    game.undo_turn()
    return game.to_payload(game_id)


@app.post("/api/game/{game_id}/reset", response_model=GameStateResponse)
def reset(game_id: str) -> dict:
    game = _get_game_or_404(game_id)
    game.reset()
    return game.to_payload(game_id)


@app.delete("/api/game/{game_id}")
def close_game(game_id: str) -> dict:
    store.remove(game_id)
    return {"ok": True}
