import { useStore } from "../store";
import { TREND_ICONS } from "../types";
import { useAnimatedNumber } from "../hooks/useAnimatedNumber";

export function MetricsBar() {
  const { snapshot } = useStore();

  const animatedTotalDevices = useAnimatedNumber(snapshot?.metrics.estimated_devices ?? 0);
  const animatedActiveAlerts = useAnimatedNumber(snapshot?.metrics.active_alerts ?? 0);

  if (!snapshot) {
    return (
      <div className="metrics-bar">
        {["Total Devices", "Capacity", "Peak Zone", "Trend", "Active Alerts", "Offline Sensors"].map((l) => (
          <div className="metric-card" key={l}>
            <div className="metric-label">{l}</div>
            <div className="skeleton-block skeleton-metric" />
          </div>
        ))}
      </div>
    );
  }

  const { metrics, zones } = snapshot;
  const totalCapacity = zones.reduce((s, z) => s + z.capacity, 0);
  const capacityPct = totalCapacity > 0 ? Math.round((metrics.estimated_devices / totalCapacity) * 100) : 0;
  const peakZone = zones.reduce((a, b) => (a.density > b.density ? a : b), zones[0]);
  const peakZoneName = snapshot.venue.zones.find((z) => z.id === peakZone?.zone_id)?.name ?? "—";

  // Overall trend from peak zone
  const trend = peakZone?.trend ?? "stable";
  const trendIcon = TREND_ICONS[trend];

  return (
    <div className="metrics-bar">
      <div className="metric-card">
        <span className="metric-icon">👥</span>
        <div className="metric-label">Total Devices</div>
        <div className="metric-value">{animatedTotalDevices.toLocaleString()}</div>
        <div className="metric-sub">Estimated from RF signals</div>
      </div>
      <div className={`metric-card${capacityPct > 85 ? " metric-card--critical" : capacityPct > 70 ? " metric-card--warning" : ""}`}>
        <span className="metric-icon">📈</span>
        <div className="metric-label">Capacity</div>
        <div className={`metric-value ${capacityPct > 85 ? "trend-spiking" : capacityPct > 70 ? "trend-rising" : ""}`}>
          {capacityPct}%
        </div>
        <div className="metric-sub">{metrics.estimated_devices.toLocaleString()} / {totalCapacity.toLocaleString()}</div>
      </div>
      <div className="metric-card">
        <span className="metric-icon">🔥</span>
        <div className="metric-label">Peak Zone</div>
        <div className="metric-value">{peakZoneName}</div>
        <div className="metric-sub">{peakZone ? `${Math.round(peakZone.density * 100)}% density` : "—"}</div>
      </div>
      <div className="metric-card">
        <span className="metric-icon">📊</span>
        <div className="metric-label">Trend (5m)</div>
        <div className={`metric-value trend-${trend}`}>
          {trendIcon} {trend}
        </div>
      </div>
      <div className={`metric-card${animatedActiveAlerts > 0 ? " metric-card--critical" : ""}`}>
        <span className="metric-icon">🔔</span>
        <div className="metric-label">Active Alerts</div>
        <div className={`metric-value ${animatedActiveAlerts > 0 ? "trend-spiking" : ""}`}>
          {animatedActiveAlerts}
        </div>
      </div>
      <div className={`metric-card${metrics.offline_sensors > 0 ? " metric-card--warning" : ""}`}>
        <span className="metric-icon">📡</span>
        <div className="metric-label">Offline Sensors</div>
        <div className={`metric-value ${metrics.offline_sensors > 0 ? "trend-rising" : ""}`}>
          {metrics.offline_sensors}
        </div>
        <div className="metric-sub">{snapshot.sensors.length} total</div>
      </div>
    </div>
  );
}
