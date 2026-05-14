import { useStore } from "../store";
import { MODE_TOKENS, TREND_ICONS } from "../types";
import type { ZoneAggregate } from "../types";

export function HeatmapDashboard() {
  const { snapshot, connected } = useStore();
  const mode = snapshot?.stream.mode ?? "mock";
  const token = MODE_TOKENS[mode];
  const zones = snapshot?.zones ?? [];
  const venueZones = snapshot?.venue.zones ?? [];
  const metrics = snapshot?.metrics;

  return (
    <div className="heatmap-page">
      <div className="heatmap-page-header">
        <div>
          <div className="heatmap-page-kicker">Density heatmap</div>
          <div className="heatmap-page-title">Zone pressure by viridis ramp</div>
        </div>
        <div className="heatmap-page-badge" style={{ background: token.color }}>
          {token.label} · {token.badge}
        </div>
        <div className="heatmap-page-conn">
          {connected ? "● connected" : "○ connecting…"}
        </div>
      </div>

      <div className="heatmap-page-metrics">
        <HeatmapMetric label="Devices" value={metrics?.estimated_devices?.toLocaleString() ?? "—"} />
        <HeatmapMetric label="Hot zones" value={metrics?.hot_zones?.toString() ?? "—"} />
        <HeatmapMetric label="Active alerts" value={metrics?.active_alerts?.toString() ?? "—"} />
        <HeatmapMetric label="Offline sensors" value={metrics?.offline_sensors?.toString() ?? "—"} />
      </div>

      <div className="heatmap-page-zones">
        {zones.length === 0 ? (
          <div className="heatmap-page-empty">Awaiting first snapshot…</div>
        ) : (
          <ul className="heatmap-zone-list">
            {zones.map((agg) => {
              const venueZone = venueZones.find((z) => z.id === agg.zone_id);
              return <HeatmapZoneRow key={agg.zone_id} agg={agg} name={venueZone?.name ?? agg.zone_id} />;
            })}
          </ul>
        )}
        <HeatmapLegend />
      </div>
    </div>
  );
}

function HeatmapMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="heatmap-metric">
      <div className="heatmap-metric-label">{label}</div>
      <div className="heatmap-metric-value">{value}</div>
    </div>
  );
}

function HeatmapZoneRow({ agg, name }: { agg: ZoneAggregate; name: string }) {
  const pct = Math.max(0, Math.min(1, agg.density));
  return (
    <li className="heatmap-zone">
      <div className="heatmap-zone-name">{name}</div>
      <div className="heatmap-zone-bar">
        <div
          className="heatmap-zone-fill"
          style={{ width: `${pct * 100}%`, background: densityColor(pct) }}
        />
      </div>
      <div className="heatmap-zone-stats">
        <span>{agg.estimated_devices.toLocaleString()} / {agg.capacity.toLocaleString()}</span>
        <span className="heatmap-zone-trend">{TREND_ICONS[agg.trend]} {agg.trend}</span>
      </div>
    </li>
  );
}

function HeatmapLegend() {
  return (
    <div className="heatmap-legend">
      <span>density</span>
      <div className="heatmap-legend-ramp">
        {[0.1, 0.3, 0.5, 0.7, 0.85, 0.95].map((p) => (
          <span key={p} style={{ background: densityColor(p) }} />
        ))}
      </div>
      <span>low → high</span>
    </div>
  );
}

function densityColor(pct: number): string {
  if (pct < 0.25) return "#440154";
  if (pct < 0.5) return "#3B528B";
  if (pct < 0.75) return "#21908C";
  if (pct < 0.9) return "#5DC863";
  return "#FDE725";
}
