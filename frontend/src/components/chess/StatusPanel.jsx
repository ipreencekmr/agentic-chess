export function StatusPanel({ game, loading, requestError }) {
  if (!game) {
    return renderWaitingStatus();
  }

  return (
    <div className="status-stack">
      {renderGameStatus(game)}
      {renderPlayers(game)}
      {renderMoveHistory(game.move_history)}
      {renderErrorStatus(game.error, requestError)}
      {renderLoadingStatus(loading)}
    </div>
  );
}

function renderWaitingStatus() {
  return (
    <div className="status-card">
      <h3>Waiting to start</h3>
      <p>Set players and click Start Game.</p>
    </div>
  );
}

function renderGameStatus(game) {
  return (
    <div className="status-card">
      <h3>Status</h3>
      <p>{game.status}</p>
      <p>
        <strong>Turn:</strong> {game.turn_name}
      </p>
      {game.ai_move && (
        <p>
          <strong>AI Move:</strong> {game.ai_move}
        </p>
      )}
    </div>
  );
}

function renderPlayers(game) {
  return (
    <div className="status-card">
      <h3>Players</h3>
      <p>
        <strong>White:</strong> {game.white_name}
      </p>
      <p>
        <strong>Black:</strong> {game.black_name}
      </p>
    </div>
  );
}

function renderMoveHistory(moveHistory) {
  return (
    <div className="status-card">
      <h3>Move History</h3>
      {moveHistory.length === 0 ? (
        <p>No moves yet.</p>
      ) : (
        <ol className="history-list">
          {moveHistory.map((move, idx) => (
            <li key={`${move}-${idx}`}>{move}</li>
          ))}
        </ol>
      )}
    </div>
  );
}

function renderErrorStatus(gameError, requestError) {
  if (gameError || requestError) {
    return (
      <div className="status-card status-error">
        <h3>Issue</h3>
        <p>{requestError || gameError}</p>
      </div>
    );
  }
  return null;
}

function renderLoadingStatus(loading) {
  if (loading) {
    return (
      <div className="status-card">
        <p>Working...</p>
      </div>
    );
  }
  return null;
}