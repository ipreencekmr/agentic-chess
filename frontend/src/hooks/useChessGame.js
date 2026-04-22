import { useCallback, useState } from "react";

import * as gameApi from "../services/gameApi";

export function useChessGame() {
  const [gameId, setGameId] = useState("");
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(false);
  const [requestError, setRequestError] = useState("");

  const withLoading = useCallback(async (fn) => {
    setLoading(true);
    setRequestError("");
    try {
      return await fn();
    } catch (error) {
      const message = error?.response?.data?.detail || error?.message || "Request failed.";
      setRequestError(String(message));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const startGame = useCallback(
    async ({ mode, difficulty, whiteName, blackName }) => {
      const result = await withLoading(() =>
        gameApi.startGame({
          mode,
          difficulty,
          white_name: whiteName,
          black_name: blackName
        })
      );
      if (!result) return false;
      setGameId(result.game_id);
      setGame(result);
      return true;
    },
    [withLoading]
  );

  const movePiece = useCallback(
    async (moveUci) => {
      if (!gameId) return false;
      const result = await withLoading(() => gameApi.move(gameId, moveUci));
      if (!result) return false;
      setGame(result);
      return !result.error;
    },
    [gameId, withLoading]
  );

  const resetGame = useCallback(async () => {
    if (!gameId) return false;
    const result = await withLoading(() => gameApi.reset(gameId));
    if (!result) return false;
    setGame(result);
    return true;
  }, [gameId, withLoading]);

  const undoMove = useCallback(async () => {
    if (!gameId) return false;
    const result = await withLoading(() => gameApi.undo(gameId));
    if (!result) return false;
    setGame(result);
    return true;
  }, [gameId, withLoading]);

  return {
    game,
    loading,
    requestError,
    startGame,
    movePiece,
    resetGame,
    undoMove
  };
}

