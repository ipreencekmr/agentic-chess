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
  // Helper to update a specific field in the settings object
  const setField = (key, value) => {
    onSettingsChange((current) => ({ ...current, [key]: value }));
  };

  // Render select options for a given array
  const renderOptions = (options) =>
    options.map((option) => (
      <option key={option} value={option}>
        {option}
      </option>
    ));

  return (
    <div className="controls-grid">
      <label>
        Game Mode
        <select
          value={settings.mode}
          disabled={loading}
          onChange={(event) => setField("mode", event.target.value)}
        >
          {renderOptions(modes)}
        </select>
      </label>

      <label>
        AI Difficulty
        <select
          value={settings.difficulty}
          disabled={loading}
          onChange={(event) => setField("difficulty", event.target.value)}
        >
          {renderOptions(difficulties)}
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
            {renderOptions(aiModels)}
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
