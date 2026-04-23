export function GameControls({
  modes,
  difficulties,
  aiModels,
  settings,
  blackLabel,
  loading,
  onSettingsChange,
  onStart,
  onReset,
  onUndo
}) {
  const setField = (key, value) => {
    onSettingsChange((current) => ({ ...current, [key]: value }));
  };

  return (
    <div className="controls-grid">
      <label>
        Game Mode
        <select
          value={settings.mode}
          disabled={loading}
          onChange={(event) => setField("mode", event.target.value)}
        >
          {modes.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label>
        AI Difficulty
        <select
          value={settings.difficulty}
          disabled={loading}
          onChange={(event) => setField("difficulty", event.target.value)}
        >
          {difficulties.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      {settings.mode === "Single Player" && settings.difficulty === "AI Agent" ? (
        <label>
          AI Agent Model
          <select
            value={settings.aiModel}
            disabled={loading}
            onChange={(event) => setField("aiModel", event.target.value)}
          >
            {aiModels.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      ) : null}

      <label>
        White Player Name
        <input
          type="text"
          value={settings.whiteName}
          disabled={loading}
          onChange={(event) => setField("whiteName", event.target.value)}
        />
      </label>

      <label>
        {blackLabel}
        <input
          type="text"
          value={settings.blackName}
          disabled={loading}
          onChange={(event) => setField("blackName", event.target.value)}
        />
      </label>

      <div className="button-row">
        <button type="button" onClick={onStart} disabled={loading}>
          Start Game
        </button>
        <button type="button" onClick={onReset} disabled={loading}>
          Reset
        </button>
        <button type="button" onClick={onUndo} disabled={loading}>
          Undo
        </button>
      </div>
    </div>
  );
}
