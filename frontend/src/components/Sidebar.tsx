import { useEffect, useState } from "react";
import { useStore } from "../store";

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

export function Sidebar({
  collapsed,
  onToggle,
  selectedZone,
  onZoneClick,
  activeSection,
  onSectionChange,
}: {
  collapsed: boolean;
  onToggle: () => void;
  selectedZone: string | null;
  onZoneClick: (zoneId: string) => void;
  activeSection: string;
  onSectionChange: (section: string) => void;
}) {
  const { snapshot, reset } = useStore();
  const [areasOpen, setAreasOpen] = useState(true);
  const [theme, toggleTheme] = useTheme();

  const zones = snapshot?.venue.zones ?? [];
  const zoneAggs = snapshot?.zones ?? [];
  const alertCount = snapshot?.alerts.filter((a) => a.status === "active").length ?? 0;
  const sensorCount = snapshot?.sensors.length ?? 0;
  const isReplay = snapshot?.stream.mode === "replay";

  return (
    <aside className={`sidebar ${collapsed ? "sidebar--collapsed" : ""}`}>
      <div className="m-stripe-divider" aria-hidden="true" />

      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" aria-hidden="true">
            <rect width="28" height="28" rx="0" fill="#000" />
            <path d="M8 14L14 8L20 14L14 20Z" fill="#fff" />
            <path d="M11 14L14 11L17 14L14 17Z" fill="#e22718" />
          </svg>
          {!collapsed && <span className="sidebar-brand-text">DeadZone</span>}
        </div>
        <button className="sidebar-toggle" onClick={onToggle} aria-label="Toggle sidebar">
          {collapsed ? "›" : "‹"}
        </button>
      </div>

      <nav className="sidebar-nav">
        <button
          className={`sidebar-item ${activeSection === "dashboard" ? "sidebar-item--active" : ""}`}
          onClick={() => onSectionChange("dashboard")}
          title="Dashboard"
        >
          <span className="sidebar-icon">📊</span>
          {!collapsed && <span className="sidebar-label">Dashboard</span>}
        </button>

        <button
          className={`sidebar-item ${activeSection === "areas" ? "sidebar-item--active" : ""}`}
          onClick={() => { onSectionChange("areas"); if (!collapsed) setAreasOpen(!areasOpen); }}
          title="Areas"
        >
          <span className="sidebar-icon">📍</span>
          {!collapsed && (
            <>
              <span className="sidebar-label">Areas</span>
              <span className="sidebar-badge">{zones.length}</span>
              <span className={`sidebar-chevron ${areasOpen ? "sidebar-chevron--open" : ""}`}>‹</span>
            </>
          )}
        </button>

        {!collapsed && areasOpen && zones.length > 0 && (
          <div className="sidebar-sub-list">
            {zones.map((z) => {
              const agg = zoneAggs.find((za) => za.zone_id === z.id);
              const density = agg ? Math.round(agg.density * 100) : 0;
              const isSelected = selectedZone === z.id;
              return (
                <button
                  key={z.id}
                  className={`sidebar-zone ${isSelected ? "sidebar-zone--selected" : ""}`}
                  onClick={() => onZoneClick(z.id)}
                  title={`${z.name} — ${density}% density`}
                >
                  <span className="sidebar-zone-dot" style={{
                    background: density > 75 ? "var(--m-red)" : density > 40 ? "var(--warning)" : "var(--success)"
                  }} />
                  <span className="sidebar-zone-name">{z.name}</span>
                  <span className="sidebar-zone-pct">{density}%</span>
                </button>
              );
            })}
          </div>
        )}

        <button
          className={`sidebar-item ${activeSection === "heatmap" ? "sidebar-item--active" : ""}`}
          onClick={() => onSectionChange("heatmap")}
          title="Heatmap"
        >
          <span className="sidebar-icon">🔥</span>
          {!collapsed && <span className="sidebar-label">Heatmap</span>}
        </button>

        <button
          className={`sidebar-item ${activeSection === "alerts" ? "sidebar-item--active" : ""}`}
          onClick={() => onSectionChange("alerts")}
          title="Alerts"
        >
          <span className="sidebar-icon">🔔</span>
          {!collapsed && (
            <>
              <span className="sidebar-label">Alerts</span>
              {alertCount > 0 && <span className="sidebar-alert-badge">{alertCount}</span>}
            </>
          )}
          {collapsed && alertCount > 0 && <span className="sidebar-alert-pip" />}
        </button>

        <button
          className={`sidebar-item ${activeSection === "sensors" ? "sidebar-item--active" : ""}`}
          onClick={() => onSectionChange("sensors")}
          title="Sensors"
        >
          <span className="sidebar-icon">📡</span>
          {!collapsed && (
            <>
              <span className="sidebar-label">Sensors</span>
              <span className="sidebar-badge">{sensorCount}</span>
            </>
          )}
        </button>

        {isReplay && (
          <button
            className={`sidebar-item ${activeSection === "replay" ? "sidebar-item--active" : ""}`}
            onClick={() => onSectionChange("replay")}
            title="Replay"
          >
            <span className="sidebar-icon">⏮</span>
            {!collapsed && <span className="sidebar-label">Replay</span>}
          </button>
        )}

        <button
          className={`sidebar-item ${activeSection === "mesh" ? "sidebar-item--active" : ""}`}
          onClick={() => onSectionChange("mesh")}
          title="Mesh"
        >
          <span className="sidebar-icon">⌬</span>
          {!collapsed && <span className="sidebar-label">Mesh</span>}
        </button>

        <button
          className={`sidebar-item ${activeSection === "configuration" ? "sidebar-item--active" : ""}`}
          onClick={() => onSectionChange("configuration")}
          title="Configuration"
        >
          <span className="sidebar-icon">⚙︎</span>
          {!collapsed && <span className="sidebar-label">Configuration</span>}
        </button>
      </nav>

      <div className="sidebar-footer">
        <button
          type="button"
          className="sidebar-item"
          onClick={() => reset()}
          title="Reset demo (R)"
          aria-label="Reset demo"
        >
          <span className="sidebar-icon">↺</span>
          {!collapsed && <span className="sidebar-label">Reset</span>}
        </button>
        <button
          type="button"
          className="sidebar-theme-toggle"
          onClick={toggleTheme}
          title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          <span className="sidebar-theme-toggle-icon" aria-hidden="true">
            {theme === "dark" ? "☀" : "☾"}
          </span>
          {!collapsed && (
            <span className="sidebar-theme-toggle-label">
              {theme === "dark" ? "Light mode" : "Dark mode"}
            </span>
          )}
        </button>
      </div>
    </aside>
  );
}
