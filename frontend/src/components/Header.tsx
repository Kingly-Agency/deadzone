import { useState, useEffect } from "react";
import { useStore } from "../store";
import { MODE_TOKENS } from "../types";
import type { Mode } from "../types";

function getInitialTheme(): "dark" | "light" {
  if (typeof window === "undefined") return "dark";
  const saved = window.localStorage.getItem("deadzone-theme");
  if (saved === "light" || saved === "dark") return saved;
  return "dark";
}

function useTheme(): ["dark" | "light", () => void] {
  const [theme, setTheme] = useState<"dark" | "light">(() => getInitialTheme());
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    window.localStorage.setItem("deadzone-theme", theme);
  }, [theme]);
  return [theme, () => setTheme((t) => (t === "dark" ? "light" : "dark"))];
}

const MODE_LIST: { mode: Mode; desc: string }[] = [
  { mode: "mock",   desc: "Simulated data, seeded RNG" },
  { mode: "replay", desc: "Recorded scenario playback" },
  { mode: "ble",    desc: "Real-time BLE sensors" },
  { mode: "wifi",   desc: "Real-time Wi-Fi sensing" },
  { mode: "mesh",   desc: "Meshtastic mesh network" },
  { mode: "hybrid", desc: "Combined live sensing" },
];

export function Header() {
  const { snapshot, config, switchMode } = useStore();
  const [showModes, setShowModes] = useState(false);
  const [theme, toggleTheme] = useTheme();

  const mode: Mode = snapshot?.stream.mode ?? config?.active_mode ?? "mock";
  const token = MODE_TOKENS[mode];
  const disabledModes = config?.disabled_modes ?? {};

  return (
    <header className="header">
      <div className="header-left">
        <nav className="breadcrumb">
          <span className="breadcrumb-item">Dashboard</span>
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">Overview</span>
        </nav>
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
            aria-label={`Current mode: ${token.label}`}
          >
            <span className="dot" />
            {token.label}
          </div>

          {showModes && (
            <>
              <div className="mode-dropdown-backdrop" onClick={() => setShowModes(false)} />
              <div className="mode-dropdown">
                {MODE_LIST.map(({ mode: m, desc }) => {
                  const isActive = m === mode;
                  const isDisabled = m in disabledModes;
                  const t = MODE_TOKENS[m];
                  return (
                    <div
                      key={m}
                      className={`mode-option ${isActive ? "active" : ""} ${isDisabled ? "disabled" : ""}`}
                      onClick={() => {
                        if (!isDisabled && !isActive) {
                          switchMode(m);
                          setShowModes(false);
                        }
                      }}
                    >
                      <span className="mode-option-dot" style={{ background: isDisabled ? "var(--text-dim)" : t.color }} />
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
          className="header-btn"
          onClick={toggleTheme}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          {theme === "dark" ? "☀" : "☾"}
        </button>

      </div>
    </header>
  );
}
