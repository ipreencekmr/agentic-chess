from typing import Literal

from pydantic import BaseModel, Field


GameMode = Literal["Single Player", "Multiplayer"]
Difficulty = Literal["Easy", "Capture Priority"]


class StartGameRequest(BaseModel):
    mode: GameMode = "Single Player"
    difficulty: Difficulty = "Easy"
    white_name: str = Field(default="White", max_length=40)
    black_name: str = Field(default="Black", max_length=40)


class MoveRequest(BaseModel):
    move: str = Field(min_length=4, max_length=5)


class GameStateResponse(BaseModel):
    game_id: str
    mode: GameMode
    difficulty: Difficulty
    white_name: str
    black_name: str
    turn_name: str
    status: str
    error: str | None = None
    ai_move: str | None = None
    last_move: str | None = None
    fen: str
    legal_moves: list[str]
    move_history: list[str]
    is_game_over: bool

