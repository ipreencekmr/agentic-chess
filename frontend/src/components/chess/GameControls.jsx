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
  const updateSetting = (key, value) => {
    onSettingsChange((current) => ({ ...current, [key]: value }));
  };

  const renderSelect = (label, value, options, key) => (
    <label>
      {label}
      <select
        value={value}
        disabled={loading}
        onChange={(event) => updateSetting(key, event.target.value)}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <div className="controls-grid">
      {renderSelect("Game Mode", settings.mode, modes, "mode")}
      {renderSelect("AI Difficulty", settings.difficulty, difficulties, "difficulty")}

      {settings.mode === "Single Player" && settings.difficulty === "AI Agent" && (
        renderSelect("AI Agent Model", settings.aiModel, aiModels, "aiModel")
      )}

      {renderSelect("White Player Name", settings.whiteName, [], "whiteName")}
      {renderSelect(blackLabel, settings.blackName, [], "blackName")}

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