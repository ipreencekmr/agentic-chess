import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .engine import StockfishService
from .ai import is_openai_ready
from .game import GameStore
from .schemas import GameStateResponse, MoveRequest, StartGameRequest
from .telemetry import setup_tracing  # ← new

load_dotenv()

app = FastAPI(title="Agentic Chess API", version="1.0.0")

setup_tracing(app)

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
    # Ensure Stockfish path is loaded from environment, but do not use the variable directly
    os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")
    StockfishService.getInstance()

@app.on_event("shutdown")
def shutdown_event():
    StockfishService.shutdown()

@app.get("/api/health")
def health() -> dict:
    # Check if AI Agent mode is explicitly disabled via environment variable
    disable_ai_mode = os.getenv("DISABLE_AI_MODE", "false").lower() == "true"
    # AI Agent is available only if OpenAI is ready AND not explicitly disabled
    ai_agent_available = is_openai_ready() and not disable_ai_mode
    return {"ok": True, "openai_available": ai_agent_available}

@app.post("/api/game/start", response_model=GameStateResponse)
def start_game(payload: StartGameRequest) -> dict:
    disable_ai_mode = os.getenv("DISABLE_AI_MODE", "false").lower() == "true"
    
    if payload.difficulty == "AI Agent":
        if disable_ai_mode:
            raise HTTPException(status_code=400, detail="AI Agent mode is disabled via DISABLE_AI_MODE environment variable.")
        if not is_openai_ready():
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

@app.post("/api/game/{game_id}/explain-move", response_model=GameStateResponse)
def explain_move(game_id: str) -> dict:
    """Explain the last AI move using LLM analysis."""
    game = _get_game_or_404(game_id)
    
    if not game.ai_move:
        raise HTTPException(status_code=400, detail="No AI move to explain.")
    
    if not game.last_ai_move_fen:
        raise HTTPException(status_code=400, detail="No position data available for explanation.")
    
    if not is_openai_ready():
        raise HTTPException(status_code=400, detail="OpenAI API not available for explanations.")
    
    try:
        from .agents.chess_agent import explain_chess_move
        from .ai import _openai_client
        
        client = _openai_client()
        if not client:
            raise HTTPException(status_code=500, detail="Failed to initialize OpenAI client.")
        
        explanation = explain_chess_move(
            client,
            game.ai_model,
            game.last_ai_move_fen,  # FEN before the move
            game.ai_move
        )
        
        game.move_explanation = explanation
        return game.to_payload(game_id)
        
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {exc}")



@app.delete("/api/game/{game_id}")
def close_game(game_id: str) -> dict:
    store.remove(game_id)
    return {"ok": True}
