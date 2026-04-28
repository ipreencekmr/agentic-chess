import { useCallback, useState } from "react";
import * as gameApi from "../services/gameApi";

export function useChessGame() {
  const [gameId, setGameId] = useState("");
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(false);
  const [requestError, setRequestError] = useState("");

  // Helper to wrap API calls with loading and error handling
  const withLoading = useCallback(async (fn) => {
    setLoading(true);
    setRequestError("");
    try {
      return await fn();
    } catch (error) {
      const message =
        error?.response?.data?.detail ||
        error?.message ||
        "Request failed.";
      setRequestError(String(message));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Start a new chess game
  const startGame = useCallback(
    async ({ mode, difficulty, aiModel, whiteName, blackName }) => {
      const result = await withLoading(() =>
        gameApi.startGame({
          mode,
          difficulty,
          ai_model: aiModel,
          white_name: whiteName,
          black_name: blackName,
        })
      );
      if (!result) return false;
      setGameId(result.game_id);
      setGame(result);
      return true;
    },
    [withLoading]
  );

  // Make a move and trigger agent if needed
  const movePiece = useCallback(
    async (moveUci) => {
      if (!gameId) return false;
      const result = await withLoading(() => gameApi.move(gameId, moveUci));
      if (!result) return false;
      setGame(result);

      // If single player and it's black's turn, trigger agent move
      const shouldTriggerAgent =
        result.mode === "Single Player" &&
        !result.is_game_over &&
        result.turn_name === result.black_name;
      if (!shouldTriggerAgent) {
        return !result.error;
      }

      const agentResult = await withLoading(() => gameApi.agentMove(gameId));
      if (!agentResult) return false;
      setGame(agentResult);
      return !agentResult.error;
    },
    [gameId, withLoading]
  );

  // Reset the current game
  const resetGame = useCallback(
    async () => {
      if (!gameId) return false;
      const result = await withLoading(() => gameApi.reset(gameId));
      if (!result) return false;
      setGame(result);
      return true;
    },
    [gameId, withLoading]
  );

  // Undo the last move
  const undoMove = useCallback(
    async () => {
      if (!gameId) return false;
      const result = await withLoading(() => gameApi.undo(gameId));
      if (!result) return false;
      setGame(result);
      return true;
    },
    [gameId, withLoading]
  );

  return {
    game,
    loading,
    requestError,
    startGame,
    movePiece,
    resetGame,
    undoMove,
  };
}
