import { useEffect, useState } from "react";
import { useStore } from "../store";
import { TREND_ICONS, SEVERITY_TOKENS } from "../types";

export function ZoneDetail({
  zoneId,
  onClose,
}: {
  zoneId: string;
  onClose: () => void;
}) {
  const { snapshot } = useStore();
  const zone = snapshot?.zones.find((z) => z.zone_id === zoneId);
  const venueDef = snapshot?.venue.zones.find((z) => z.id === zoneId);
  const zoneAlerts = snapshot?.alerts.filter((a) => a.zone_id === zoneId && a.status === "active") ?? [];
  const zoneSensors = snapshot?.sensors.filter((s) => s.zone_id === zoneId) ?? [];
  const [history, setHistory] = useState<number[]>([]);

  // Build a mini sparkline from density over time
  useEffect(() => {
    if (!zone) return;
    setHistory((prev) => {
      const next = [...prev, zone.density];
      return next.slice(-30); // Last 30 ticks ≈ 30 seconds
    });
  }, [zone?.density]);

  if (!zone || !venueDef) return null;

  const pct = zone.density;

  return (
    <div className="zone-drawer">
      <div className="zone-drawer-header">
        <div className="zone-drawer-title-wrap">
          <button className="zone-drawer-back" onClick={onClose} aria-label="Back">‹</button>
          <h3 className="zone-drawer-title">{venueDef.name}</h3>
        </div>
      </div>

      <div className="zone-drawer-body">
        {/* Primary metrics */}
        <div className="zone-drawer-metrics">
          <div className="zone-drawer-metric">
            <span className="metric-label">Occupancy</span>
            <span className="metric-value">{zone.estimated_devices.toLocaleString()}</span>
            <span className="metric-sub">of {zone.capacity.toLocaleString()} capacity</span>
          </div>
          <div className="zone-drawer-metric">
            <span className="metric-label">Density</span>
            <span className={`metric-value ${pct > 0.85 ? "trend-spiking" : pct > 0.7 ? "trend-rising" : ""}`}>
              {Math.round(pct * 100)}%
            </span>
          </div>
          <div className="zone-drawer-metric">
            <span className="metric-label">Trend</span>
            <span className={`metric-value trend-${zone.trend}`}>
              {TREND_ICONS[zone.trend]} {zone.trend}
            </span>
          </div>
        </div>

        {/* Capacity bar */}
        <div className="zone-drawer-section">
          <div className="metric-label section-label">Capacity utilization</div>
          <div className="zone-bar-track" style={{ height: 10 }}>
            <div
              className="zone-bar-fill"
              style={{
                width: `${Math.min(pct * 100, 100)}%`,
                background: pct > 0.85 ? "var(--severity-critical)" : pct > 0.6 ? "var(--severity-warn)" : "var(--sensor-online)",
              }}
            />
          </div>
        </div>

        {/* Sparkline */}
        {history.length > 2 && (
          <div className="zone-drawer-section">
            <div className="metric-label section-label">Density trend (30s)</div>
            <svg viewBox={`0 0 ${history.length - 1} 100`} className="sparkline">
              <polyline
                fill="none"
                stroke="#6366F1"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                points={history.map((v, i) => `${i},${100 - v * 100}`).join(" ")}
              />
            </svg>
          </div>
        )}

        {/* Pressure */}
        <div className="zone-drawer-metric zone-drawer-section">
          <span className="metric-label section-label">Pressure score</span>
          <span className={`metric-value ${zone.pressure_score > 0.7 ? "trend-spiking" : ""}`}>
            {Math.round(zone.pressure_score * 100)}%
          </span>
          <span className="metric-sub">Confidence: {Math.round(zone.confidence * 100)}%</span>
        </div>

        {/* Zone alerts */}
        {zoneAlerts.length > 0 && (
          <div className="zone-drawer-section">
            <div className="metric-label section-label">Zone Alerts</div>
            {zoneAlerts.map((a) => {
              const tok = SEVERITY_TOKENS[a.severity];
              return (
                <div key={a.id} className={`alert-item severity-${a.severity}`} style={{ marginBottom: 8, padding: 12 }}>
                  <div className="alert-badge" style={{ color: tok.color }}>
                    {tok.icon} {a.severity.toUpperCase()}
                  </div>
                  <div className="alert-message" style={{ marginBottom: 0 }}>{a.message}</div>
                </div>
              );
            })}
          </div>
        )}

        {/* Zone sensors */}
        <div className="zone-drawer-section">
          <div className="metric-label section-label">Sensors in zone</div>
          {zoneSensors.length > 0 ? (
            <div className="sensor-list">
              {zoneSensors.map((s) => (
                <div key={s.id} className="sensor-item">
                  <span className={`connection-dot ${s.status === "online" ? "online" : s.status === "degraded" ? "stale" : "offline"}`} />
                  <span className="sensor-name">{s.label}</span>
                  <span className="sensor-latency">{s.latency_ms?.toFixed(0)}ms</span>
                  {s.battery !== null && (
                    <span className="sensor-battery" style={{ color: s.battery < 0.2 ? "var(--severity-critical)" : "inherit" }}>
                      🔋 {Math.round(s.battery * 100)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: "16px 0" }}>
              <div className="empty-icon" style={{ fontSize: 24 }}>📡</div>
              <div>No sensors mapped to this zone.</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
