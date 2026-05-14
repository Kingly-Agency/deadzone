import { useState } from "react";
import { useStore } from "../store";
import { MODE_TOKENS } from "../types";
import type { Mode } from "../types";

const MODE_LIST: { mode: Mode; desc: string }[] = [
  { mode: "mock",   desc: "Simulated data, seeded RNG" },
  { mode: "replay", desc: "Recorded scenario playback" },
  { mode: "ble",    desc: "Real-time BLE sensors" },
  { mode: "wifi",   desc: "Real-time Wi-Fi sensing" },
  { mode: "mesh",   desc: "Meshtastic mesh network" },
  { mode: "hybrid", desc: "Combined live sensing" },
];

export function Header() {
  const { snapshot, config, switchMode, reset } = useStore();
  const [showModes, setShowModes] = useState(false);

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

      <div className="header-center">
        <div className="header-search">
          <span className="search-icon">⌕</span>
          <input type="text" placeholder="Search zones, sensors…" className="search-input" readOnly />
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

        <button className="header-btn" onClick={() => reset()} title="Reset demo (R)">
          ↺ Reset
        </button>

        {/* Notification bell */}
        <button className="header-btn header-bell" title="Notifications">
          🔔
          {(snapshot?.metrics.active_alerts ?? 0) > 0 && (
            <span className="bell-badge">{snapshot?.metrics.active_alerts}</span>
          )}
        </button>

        {/* Avatar */}
        <div className="header-avatar" title="Operator">
          <span>OP</span>
        </div>
      </div>
    </header>
  );
}
