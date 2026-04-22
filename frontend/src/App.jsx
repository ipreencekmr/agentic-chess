import { useEffect, useMemo, useState } from "react";

import { AppShell } from "./components/layout/AppShell";
import { ChessBoardPanel } from "./components/chess/ChessBoardPanel";
import { GameControls } from "./components/chess/GameControls";
import { StatusPanel } from "./components/chess/StatusPanel";
import { useChessGame } from "./hooks/useChessGame";

const MODES = ["Single Player", "Multiplayer"];
const DIFFICULTIES = ["Easy", "Capture Priority"];

export default function App() {
  const [settings, setSettings] = useState({
    mode: "Single Player",
    difficulty: "Easy",
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

  const blackLabel = useMemo(() => {
    if (settings.mode === "Single Player") return "Black Player Name (default: Computer)";
    return "Black Player Name";
  }, [settings.mode]);

  useEffect(() => {
    if (game?.is_game_over) {
      setShowResultDialog(true);
    } else {
      setShowResultDialog(false);
    }
  }, [game?.is_game_over, game?.status]);

  return (
    <>
      <AppShell
        header="AI Chess Arena"
        controls={
          <GameControls
            modes={MODES}
            difficulties={DIFFICULTIES}
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
