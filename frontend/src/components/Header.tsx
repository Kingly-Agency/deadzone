import { useEffect, useRef, useState } from "react";
import { useStore } from "../store";
import { MODE_TOKENS } from "../types";
import type { Mode } from "../types";

function getInitialTheme(): "dark" | "light" {
  if (typeof window === "undefined") return "dark";
  const saved = window.localStorage.getItem("deadzone-theme");
  return saved === "light" ? "light" : "dark";
}

const MODE_LIST: { mode: Mode; desc: string }[] = [
  { mode: "mock",   desc: "Simulated data, seeded RNG" },
  { mode: "replay", desc: "Recorded scenario playback" },
  { mode: "ble",    desc: "Real-time BLE sensors" },
  { mode: "wifi",   desc: "Real-time Wi-Fi sensing" },
  { mode: "mesh",   desc: "Meshtastic mesh network" },
  { mode: "hybrid", desc: "Combined live sensing" },
];

export function Header({
  onMenuToggle,
  onBellClick,
  isMobileNavOpen,
  isAlertsOpen,
  isNarrow,
  bellRef,
  menuBtnRef,
}: {
  onMenuToggle: () => void;
  onBellClick: () => void;
  isMobileNavOpen: boolean;
  isAlertsOpen: boolean;
  isNarrow: boolean;
  bellRef: React.RefObject<HTMLButtonElement>;
  menuBtnRef: React.RefObject<HTMLButtonElement>;
}) {
  const { snapshot, config, switchMode, reset } = useStore();
  const [showModes, setShowModes] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">(() => getInitialTheme());
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("deadzone-theme", theme);
  }, [theme]);
  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  const mode: Mode = snapshot?.stream.mode ?? config?.active_mode ?? "mock";
  const token = MODE_TOKENS[mode];
  const disabledModes = config?.disabled_modes ?? {};

  return (
    <header className="header">
      <div className="header-left">
        {/* Mobile/tablet hamburger — visible via CSS at ≤1024px */}
        <button
          ref={menuBtnRef}
          className="header-menu-btn"
          onClick={onMenuToggle}
          aria-label="Open navigation menu"
          aria-expanded={isNarrow ? isMobileNavOpen : undefined}
          aria-haspopup="dialog"
        >
          ☰
        </button>

        <nav className="breadcrumb">
          <span className="breadcrumb-item">Dashboard</span>
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">Overview</span>
        </nav>
      </div>

      {/* Search — collapses to icon on mobile */}
      <div className="header-center">
        <div
          className="header-search"
          onClick={() => searchInputRef.current?.focus()}
        >
          <span className="search-icon">⌕</span>
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search zones, sensors…"
            className="search-input"
            readOnly
            aria-label="Search zones and sensors"
          />
          <kbd className="search-kbd">⌘K</kbd>
        </div>
      </div>

      <div className="header-right">
        {/* Mode Chip */}
        <div style={{ position: "relative" }}>
          <div
            className="mode-chip"
            style={{ background: token.color }}
            onClick={() => setShowModes(!showModes)}
            role="button"
            tabIndex={0}
            aria-label={`Current mode: ${token.label}. Click to change.`}
            aria-haspopup="listbox"
            aria-expanded={showModes}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") setShowModes(!showModes); }}
          >
            <span className="dot" />
            <span className="mode-chip-label">{token.label}</span>
          </div>

          {showModes && (
            <>
              <div
                className="mode-dropdown-backdrop"
                onClick={() => setShowModes(false)}
              />
              <div className="mode-dropdown" role="listbox" aria-label="Select mode">
                {MODE_LIST.map(({ mode: m, desc }) => {
                  const isActive = m === mode;
                  const isDisabled = m in disabledModes;
                  const t = MODE_TOKENS[m];
                  return (
                    <div
                      key={m}
                      role="option"
                      aria-selected={isActive}
                      className={`mode-option ${isActive ? "active" : ""} ${isDisabled ? "disabled" : ""}`}
                      onClick={() => {
                        if (!isDisabled && !isActive) {
                          switchMode(m);
                          setShowModes(false);
                        }
                      }}
                    >
                      <span
                        className="mode-option-dot"
                        style={{ background: isDisabled ? "var(--text-dim)" : t.color }}
                      />
                      <div className="mode-option-info">
                        <div className="mode-option-name">{t.label}</div>
                        <div className="mode-option-desc">
                          {isDisabled ? disabledModes[m] : desc}
                        </div>
                      </div>
                      {isActive && <span className="mode-option-check">✓</span>}
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        <button
          className="header-btn header-btn--reset"
          onClick={() => reset()}
          title="Reset demo (R)"
        >
          ↺ Reset
        </button>

        {/* Notification bell — acts as alerts drawer trigger on mobile/tablet */}
        <button
          ref={bellRef}
          className="header-btn header-bell"
          title={isNarrow ? (isAlertsOpen ? "Close alerts" : "Open alerts") : "Notifications"}
          onClick={onBellClick}
          aria-label="Notifications"
          aria-expanded={isNarrow ? isAlertsOpen : undefined}
          aria-haspopup={isNarrow ? "dialog" : undefined}
        >
          🔔
          {(snapshot?.metrics.active_alerts ?? 0) > 0 && (
            <span className="bell-badge">{snapshot?.metrics.active_alerts}</span>
          )}
        </button>

        {/* Theme toggle */}
        <button
          type="button"
          className="header-btn header-theme-toggle"
          onClick={toggleTheme}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          <span aria-hidden="true">{theme === "dark" ? "☀" : "☾"}</span>
        </button>

        {/* Avatar */}
        <div className="header-avatar" title="Operator" aria-label="Operator account">
          <span>OP</span>
        </div>
      </div>
    </header>
  );
}
