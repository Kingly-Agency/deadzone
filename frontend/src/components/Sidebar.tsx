import { useState } from "react";
import { useStore } from "../store";

export function Sidebar({
  collapsed,
  onToggle,
  selectedZone,
  onZoneClick,
  activeSection,
  onSectionChange,
  isDrawerMode,
  onNavItemClick,
}: {
  collapsed: boolean;
  onToggle: () => void;
  selectedZone: string | null;
  onZoneClick: (zoneId: string) => void;
  activeSection: string;
  onSectionChange: (section: string) => void;
  isDrawerMode: boolean;
  onNavItemClick: () => void;
}) {
  const { snapshot, config } = useStore();
  const [areasOpen, setAreasOpen] = useState(true);

  const zones = snapshot?.venue.zones ?? [];
  const zoneAggs = snapshot?.zones ?? [];
  const alertCount = snapshot?.alerts.filter((a) => a.status === "active").length ?? 0;
  const sensorCount = snapshot?.sensors.length ?? 0;
  const isReplay = snapshot?.stream.mode === "replay";

  // When in drawer mode, clicking a nav item also closes the drawer
  const handleSectionChange = (section: string) => {
    onSectionChange(section);
    if (isDrawerMode) onNavItemClick();
  };

  const handleZoneClick = (zoneId: string) => {
    onZoneClick(zoneId);
    if (isDrawerMode) onNavItemClick();
  };

  return (
    <aside className={`sidebar ${collapsed ? "sidebar--collapsed" : ""}`}>
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
            <rect width="28" height="28" rx="8" fill="url(#logoGrad)" />
            <path d="M8 14L14 8L20 14L14 20Z" fill="white" fillOpacity="0.9" />
            <path d="M11 14L14 11L17 14L14 17Z" fill="url(#logoGrad)" />
            <defs>
              <linearGradient id="logoGrad" x1="0" y1="0" x2="28" y2="28">
                <stop stopColor="#6366F1" />
                <stop offset="1" stopColor="#8B5CF6" />
              </linearGradient>
            </defs>
          </svg>
          {!collapsed && <span className="sidebar-brand-text">DeadZone</span>}
        </div>
        <button
          className="sidebar-toggle"
          onClick={onToggle}
          aria-label={isDrawerMode ? "Close navigation" : collapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-expanded={isDrawerMode ? true : !collapsed}
        >
          {isDrawerMode ? "✕" : collapsed ? "›" : "‹"}
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <button
          className={`sidebar-item ${activeSection === "dashboard" ? "sidebar-item--active" : ""}`}
          onClick={() => handleSectionChange("dashboard")}
          title="Dashboard"
        >
          <span className="sidebar-icon">📊</span>
          {!collapsed && <span className="sidebar-label">Dashboard</span>}
        </button>

        {/* Areas section */}
        <button
          className={`sidebar-item ${activeSection === "areas" ? "sidebar-item--active" : ""}`}
          onClick={() => {
            onSectionChange("areas");
            if (!collapsed) setAreasOpen(!areasOpen);
          }}
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
                  onClick={() => handleZoneClick(z.id)}
                  title={`${z.name} — ${density}% density`}
                >
                  <span
                    className="sidebar-zone-dot"
                    style={{
                      background:
                        density > 75 ? "#EF4444" : density > 40 ? "#F59E0B" : "#22C55E",
                    }}
                  />
                  <span className="sidebar-zone-name">{z.name}</span>
                  <span className="sidebar-zone-pct">{density}%</span>
                </button>
              );
            })}
          </div>
        )}

        <button
          className={`sidebar-item ${activeSection === "heatmap" ? "sidebar-item--active" : ""}`}
          onClick={() => handleSectionChange("heatmap")}
          title="Heatmap"
        >
          <span className="sidebar-icon">🔥</span>
          {!collapsed && <span className="sidebar-label">Heatmap</span>}
        </button>

        <button
          className={`sidebar-item ${activeSection === "alerts" ? "sidebar-item--active" : ""}`}
          onClick={() => handleSectionChange("alerts")}
          title="Alerts"
        >
          <span className="sidebar-icon">🔔</span>
          {!collapsed && (
            <>
              <span className="sidebar-label">Alerts</span>
              {alertCount > 0 && (
                <span className="sidebar-alert-badge">{alertCount}</span>
              )}
            </>
          )}
          {collapsed && alertCount > 0 && <span className="sidebar-alert-pip" />}
        </button>

        <button
          className={`sidebar-item ${activeSection === "sensors" ? "sidebar-item--active" : ""}`}
          onClick={() => handleSectionChange("sensors")}
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
            onClick={() => handleSectionChange("replay")}
            title="Replay"
          >
            <span className="sidebar-icon">⏮</span>
            {!collapsed && <span className="sidebar-label">Replay</span>}
          </button>
        )}
      </nav>

      {/* Bottom status */}
      <div className="sidebar-footer">
        <div className="sidebar-status">
          <span className={`sidebar-conn-dot ${snapshot ? "online" : "offline"}`} />
          {!collapsed && (
            <span className="sidebar-conn-text">
              {snapshot
                ? (config?.active_mode?.toUpperCase() ?? "CONNECTED")
                : "Connecting…"}
            </span>
          )}
        </div>
      </div>
    </aside>
  );
}
