import { useEffect, useMemo, useRef, useState } from "react";

import { AppShell } from "./components/layout/AppShell";
import { ChessBoardPanel } from "./components/chess/ChessBoardPanel";
import { GameControls } from "./components/chess/GameControls";
import { StatusPanel } from "./components/chess/StatusPanel";
import { useChessGame } from "./hooks/useChessGame";
import { getHealth } from "./services/gameApi";

const MODES = ["Single Player", "Multiplayer"];
const DIFFICULTIES = ["Easy", "Medium", "Hard", "Capture Priority", "AI Agent"];
const AI_MODELS = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1", "gpt-4o"];

// Main application component
export default function App() {
  const prevDifficultyRef = useRef("Easy");
  const [isOpenAiAvailable, setIsOpenAiAvailable] = useState(false);
  const [settings, setSettings] = useState({
    mode: "Single Player",
    difficulty: "Easy",
    aiModel: "gpt-4o-mini",
    whiteName: "White",
    blackName: "Black"
  });
  const [isResultDialogVisible, setIsResultDialogVisible] = useState(false);

  const {
    game,
    loading,
    requestError,
    startGame,
    movePiece,
    resetGame,
    undoMove
  } = useChessGame();

  const blackLabel = useMemo(() => {
    return settings.mode === "Single Player" 
      ? "Black Player Name (default: Computer)" 
      : "Black Player Name";
  }, [settings.mode]);

  const availableDifficulties = useMemo(
    () => DIFFICULTIES.filter((difficulty) => isOpenAiAvailable || difficulty !== "AI Agent"),
    [isOpenAiAvailable]
  );

  useEffect(() => {
    let isActive = true;
    void (async () => {
      try {
        const health = await getHealth();
        if (isActive) setIsOpenAiAvailable(Boolean(health?.openai_available));
      } catch {
        if (isActive) setIsOpenAiAvailable(false);
      }
    })();
    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    if (isOpenAiAvailable || settings.difficulty !== "AI Agent") return;
    setSettings((current) => ({ ...current, difficulty: "Easy" }));
  }, [isOpenAiAvailable, settings.difficulty]);

  useEffect(() => {
    setIsResultDialogVisible(game?.is_game_over || false);
  }, [game?.is_game_over]);

  useEffect(() => {
    const previousDifficulty = prevDifficultyRef.current;
    prevDifficultyRef.current = settings.difficulty;

    if (previousDifficulty === settings.difficulty || !game?.game_id) return;

    setIsResultDialogVisible(false);
    void startGame(settings);
  }, [game?.game_id, settings, startGame]);

  return (
    <>
      <AppShell
        header="AI Chess Arena"
        controls={
          <GameControls
            modes={MODES}
            difficulties={availableDifficulties}
            aiModels={AI_MODELS}
            settings={settings}
            blackLabel={blackLabel}
            loading={loading}
            onSettingsChange={setSettings}
            onStart={() => startGame(settings)}
            onReset={resetGame}
            onUndo={undoMove}
          />
        }
        board={
          <ChessBoardPanel
            fen={game?.fen}
            lastMove={game?.last_move}
            turnName={game?.turn_name}
            mode={game?.mode}
            onMove={movePiece}
            disabled={!game || loading || game.is_game_over}
          />
        }
        sidePanel={<StatusPanel game={game} loading={loading} requestError={requestError} />}
      />

      {isResultDialogVisible && game?.is_game_over ? (
        <div className="result-dialog-backdrop" role="presentation">
          <div className="result-dialog" role="dialog" aria-modal="true" aria-label="Game result">
            <h2>Game Over</h2>
            <p>{game.status}</p>
            <button type="button" onClick={() => setIsResultDialogVisible(false)}>
              Close
            </button>
          </div>
        </div>
      ) : null}
    </>
  );
}