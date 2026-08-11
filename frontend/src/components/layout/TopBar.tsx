import "../../styles/topbar.css";

function TopBar() {
  return (
    <header className="topbar">
      <div className="search-box">
        <span className="search-icon">⌕</span>

        <input
          type="text"
          placeholder="Search Command Center..."
        />

        <span className="search-shortcut">⌘K</span>
      </div>

      <div className="topbar-actions">
        <button
          className="icon-button"
          aria-label="Notifications"
        >
          ♧
        </button>

        <button
          className="icon-button"
          aria-label="Refresh"
        >
          🔍︎
        </button>

        <div className="topbar-divider" />

        <button className="avatar-button">
          R
        </button>
      </div>
    </header>
  );
}

export default TopBar;