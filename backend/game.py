from __future__ import annotations

import threading
import uuid

import chess

from .ai import choose_ai_move


def _normalize_name(name: str, fallback: str) -> str:
    clean = (name or "").strip()
    return clean or fallback


class ChessGame:
    def __init__(self, mode: str, difficulty: str, ai_model: str, white_name: str, black_name: str):
        self.mode = mode
        self.difficulty = difficulty
        self.ai_model = ai_model
        self.white_name = _normalize_name(white_name, "White")
        black_default = "Computer" if mode == "Single Player" else "Black"
        self.black_name = _normalize_name(black_name, black_default)
        self.board = chess.Board()
        self.move_history: list[str] = []
        self.last_move: str | None = None
        self.error: str | None = None
        self.ai_move: str | None = None
        self.move_explanation: str | None = None
        self.last_ai_move_fen: str | None = None

    def player_name(self, color: bool) -> str:
        return self.white_name if color == chess.WHITE else self.black_name

    @property
    def turn_name(self) -> str:
        return self.player_name(self.board.turn)

    def status(self) -> str:
        if self.board.is_checkmate():
            winner = chess.WHITE if self.board.turn == chess.BLACK else chess.BLACK
            return f"Checkmate! {self.player_name(winner)} wins."
        if self.board.is_stalemate():
            return "Stalemate! Draw."
        if self.board.is_insufficient_material():
            return "Draw by insufficient material."
        if self.board.can_claim_threefold_repetition():
            return "Draw by threefold repetition."
        if self.board.can_claim_fifty_moves():
            return "Draw by fifty-move rule."
        if self.board.is_check():
            return f"{self.turn_name} is in check."
        return f"{self.turn_name}'s turn."

    def legal_moves(self) -> list[str]:
        return [move.uci() for move in self.board.legal_moves]

    def to_payload(self, game_id: str) -> dict:
        return {
            "game_id": game_id,
            "mode": self.mode,
            "difficulty": self.difficulty,
            "ai_model": self.ai_model,
            "white_name": self.white_name,
            "black_name": self.black_name,
            "turn_name": self.turn_name,
            "status": self.status(),
            "error": self.error,
            "ai_move": self.ai_move,
            "last_move": self.last_move,
            "fen": self.board.fen(),
            "legal_moves": self.legal_moves(),
            "move_history": self.move_history,
            "is_game_over": self.board.is_game_over(),
            "move_explanation": self.move_explanation,
        }

    def reset(self) -> None:
        self.board.reset()
        self.move_history = []
        self.last_move = None
        self.error = None
        self.ai_move = None
        self.move_explanation = None
        self.last_ai_move_fen = None

    def push_move(self, move_uci: str) -> bool:
        try:
            move = chess.Move.from_uci(move_uci.lower())
        except Exception:
            self.error = "Move could not be parsed."
            return False

        if move not in self.board.legal_moves:
            self.error = "Illegal move."
            return False

        self.board.push(move)
        self.move_history.append(move.uci())
        self.last_move = move.uci()
        self.error = None
        return True

    def undo(self) -> None:
        if self.board.move_stack:
            self.board.pop()
            if self.move_history:
                self.move_history.pop()
            self.last_move = self.move_history[-1] if self.move_history else None
            self.error = None
            self.ai_move = None
            self.move_explanation = None
            self.last_ai_move_fen = None

    def undo_turn(self) -> None:
        self.undo()
        if self.mode == "Single Player" and self.board.move_stack and self.board.turn == chess.BLACK:
            self.undo()

    def maybe_play_ai(self) -> None:
        self.ai_move = None
        self.move_explanation = None
        # Only play AI if in single player mode, game is not over, and it's black's turn
        if self.mode != "Single Player" or self.board.is_game_over() or self.board.turn != chess.BLACK:
            return

        # Store FEN before AI makes its move (for later explanation)
        self.last_ai_move_fen = self.board.fen()
        
        move_uci, warning = choose_ai_move(self.board, self.difficulty, self.ai_model)
        if warning:
            self.error = warning
        if move_uci and self.push_move(move_uci):
            self.ai_move = move_uci


class GameStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._games: dict[str, ChessGame] = {}

    def create(
        self, mode: str, difficulty: str, ai_model: str, white_name: str, black_name: str
    ) -> tuple[str, ChessGame]:
        game_id = str(uuid.uuid4())
        game = ChessGame(
            mode=mode,
            difficulty=difficulty,
            ai_model=ai_model,
            white_name=white_name,
            black_name=black_name,
        )
        with self._lock:
            self._games[game_id] = game
        return game_id, game

    def get(self, game_id: str) -> ChessGame | None:
        with self._lock:
            return self._games.get(game_id)

    def remove(self, game_id: str) -> None:
        with self._lock:
            self._games.pop(game_id, None)
