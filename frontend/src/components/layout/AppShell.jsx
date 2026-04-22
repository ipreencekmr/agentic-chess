export function AppShell({ header, controls, board, sidePanel }) {
  return (
    <div className="app-shell">
      <header className="top-bar">
        <h1>{header}</h1>
      </header>
      <section className="settings-panel">{controls}</section>
      <main className="content-grid">
        <section className="board-panel">{board}</section>
        <aside className="info-panel">{sidePanel}</aside>
      </main>
    </div>
  );
}

