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

export default function App() {
  const prevDifficultyRef = useRef("Easy");
  const [openAiAvailable, setOpenAiAvailable] = useState(false);
  const [settings, setSettings] = useState({
    mode: "Single Player",
    difficulty: "Easy",
    aiModel: "gpt-4o-mini",
    whiteName: "White",
    blackName: "Black"
  });
  const [showResultDialog, setShowResultDialog] = useState(false);

  const {
    game,
    loading,
    requestError,
    startGame,
    movePiece,
    resetGame,
    undoMove
  } = useChessGame();

  // Memoize black player label based on mode
  const blackLabel = useMemo(() => {
    if (settings.mode === "Single Player") return "Black Player Name (default: Computer)";
    return "Black Player Name";
  }, [settings.mode]);

  // Only show "AI Agent" difficulty if OpenAI is available
  const availableDifficulties = useMemo(
    () => DIFFICULTIES.filter((difficulty) => openAiAvailable || difficulty !== "AI Agent"),
    [openAiAvailable]
  );

  // Check OpenAI health on mount
  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const health = await getHealth();
        if (active) setOpenAiAvailable(Boolean(health?.openai_available));
      } catch {
        if (active) setOpenAiAvailable(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  // If OpenAI becomes unavailable, revert from "AI Agent" difficulty
  useEffect(() => {
    if (openAiAvailable || settings.difficulty !== "AI Agent") return;
    setSettings((current) => ({ ...current, difficulty: "Easy" }));
  }, [openAiAvailable, settings.difficulty]);

  // Show result dialog when game is over
  useEffect(() => {
    if (game?.is_game_over) {
      setShowResultDialog(true);
    } else {
      setShowResultDialog(false);
    }
  }, [game?.is_game_over, game?.status]);

  // Restart game if difficulty changes
  useEffect(() => {
    const previousDifficulty = prevDifficultyRef.current;
    prevDifficultyRef.current = settings.difficulty;

    if (previousDifficulty === settings.difficulty) return;
    if (!game?.game_id) return;

    setShowResultDialog(false);
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

      {showResultDialog && game?.is_game_over ? (
        <div className="result-dialog-backdrop" role="presentation">
          <div className="result-dialog" role="dialog" aria-modal="true" aria-label="Game result">
            <h2>Game Over</h2>
            <p>{game.status}</p>
            <button type="button" onClick={() => setShowResultDialog(false)}>
              Close
            </button>
          </div>
        </div>
      ) : null}
    </>
  );
}
