export function StatusPanel({ game, loading, requestError }) {
  if (!game) {
    return (
      <div className="status-card">
        <h3>Waiting to start</h3>
        <p>Set players and click Start Game.</p>
      </div>
    );
  }

  // Helper to render a player's name
  function renderPlayer(label, name) {
    return (
      <p>
        <strong>{label}:</strong> {name}
      </p>
    );
  }

  // Helper to render a status card
  function StatusCard({ title, children, extraClass = '' }) {
    return (
      <div className={`status-card${extraClass ? ' ' + extraClass : ''}`}>
        <h3>{title}</h3>
        {children}
      </div>
    );
  }

  // Helper to render move history
  function renderMoveHistory(moves) {
    if (moves.length === 0) {
      return <p>No moves yet.</p>;
    }
    return (
      <ol className="history-list">
        {moves.map((move, idx) => (
          <li key={`${move}-${idx}`}>{move}</li>
        ))}
      </ol>
    );
  }

  return (
    <div className="status-stack">
      <StatusCard title="Status">
        <p>{game.status}</p>
        <p>
          <strong>Turn:</strong> {game.turn_name}
        </p>
        {game.ai_move && (
          <p>
            <strong>AI Move:</strong> {game.ai_move}
          </p>
        )}
      </StatusCard>

      <StatusCard title="Players">
        {renderPlayer('White', game.white_name)}
        {renderPlayer('Black', game.black_name)}
      </StatusCard>

      <StatusCard title="Move History">
        {renderMoveHistory(game.move_history)}
      </StatusCard>

      {(game.error || requestError) && (
        <StatusCard title="Issue" extraClass="status-error">
          <p>{requestError || game.error}</p>
        </StatusCard>
      )}

      {loading && (
        <StatusCard title="">
          <p>Working...</p>
        </StatusCard>
      )}
    </div>
  );
}
