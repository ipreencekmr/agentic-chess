from typing import Literal, Optional, List

from pydantic import BaseModel, Field

GameMode = Literal["Single Player", "Multiplayer"]
Difficulty = Literal["Easy", "Medium", "Hard", "Capture Priority", "AI Agent"]

class StartGameRequest(BaseModel):
    mode: GameMode = "Single Player"
    difficulty: Difficulty = "Easy"
    ai_model: str = Field(default="gpt-4o-mini", max_length=60)
    white_name: str = Field(default="White", max_length=40)
    black_name: str = Field(default="Black", max_length=40)


class MoveRequest(BaseModel):
    move: str = Field(min_length=4, max_length=5)


class GameStateResponse(BaseModel):
    game_id: str
    mode: GameMode
    difficulty: Difficulty
    ai_model: str
    white_name: str
    black_name: str
    turn_name: str
    status: str
    error: Optional[str] = None
    ai_move: Optional[str] = None
    last_move: Optional[str] = None
    fen: str
    legal_moves: List[str]
    move_history: List[str]
    is_game_over: bool