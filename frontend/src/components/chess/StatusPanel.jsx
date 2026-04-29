export function StatusPanel({ game, loading, requestError, onExplainMove }) {
  if (!game) {
    return (
      <div className="status-card">
        <h3>Waiting to start</h3>
        <p>Set players and click Start Game.</p>
      </div>
    );
  }

  return (
    <div className="status-stack">
      <div className="status-card">
        <h3>Status</h3>
        <p>{game.status}</p>
        <p>
          <strong>Turn:</strong> {game.turn_name}
        </p>
        {game.ai_move ? (
          <>
            <p>
              <strong>AI Move:</strong> {game.ai_move}
            </p>
            {!game.move_explanation && (
              <button
                type="button"
                onClick={onExplainMove}
                disabled={loading}
                className="explain-button"
              >
                {loading ? "Analyzing..." : "Explain Move"}
              </button>
            )}
          </>
        ) : null}
      </div>

      {game.move_explanation && (
        <div className="status-card explanation-card">
          <h3>Move Explanation</h3>
          <p>{game.move_explanation}</p>
        </div>
      )}

      <div className="status-card">
        <h3>Players</h3>
        <p>
          <strong>White:</strong> {game.white_name}
        </p>
        <p>
          <strong>Black:</strong> {game.black_name}
        </p>
      </div>

      <div className="status-card">
        <h3>Move History</h3>
        {game.move_history.length === 0 ? (
          <p>No moves yet.</p>
        ) : (
          <ol className="history-list">
            {game.move_history.map((move, idx) => (
              <li key={`${move}-${idx}`}>{move}</li>
            ))}
          </ol>
        )}
      </div>

      {(game.error || requestError) && (
        <div className="status-card status-error">
          <h3>Issue</h3>
          <p>{requestError || game.error}</p>
        </div>
      )}

      {loading && (
        <div className="status-card">
          <p>Working...</p>
        </div>
      )}
    </div>
  );
}

