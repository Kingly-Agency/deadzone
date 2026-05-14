type Mode = "mock" | "replay" | "live" | "mesh";

interface Zone {
  id: string;
  name: string;
  count: number;
  capacity: number;
  trend_5m: string;
}

interface Headline {
  total: number;
  capacity_pct: number;
  peak_zone: string;
  trend: string;
}

interface AggregateFrame {
  timestamp: number;
  mode: Mode;
  venue_id: string;
  zones: Zone[];
  headline: Headline;
}

interface CaptureStatus {
  active: boolean;
  trace_id: string | null;
  observations: number;
  backend: "ble";
  disabled_reason: string | null;
  started_at: string | null;
  latest_observation_at: string | null;
}

const MODE_TOKENS: Record<Mode, { color: string; label: string }> = {
  mock: { color: "#3B82F6", label: "MOCK — simulated data" },
  replay: { color: "#F59E0B", label: "REPLAY — recorded data" },
  live: { color: "#10B981", label: "LIVE — real-time sensing" },
  mesh: { color: "#8B5CF6", label: "MESH — distributed sensors" },
};

export function HeatmapDashboard({
  frame,
  connected,
  capture,
  captureBusy,
  captureError,
  onStartCapture,
  onStopCapture,
}: {
  frame: AggregateFrame | null;
  connected: boolean;
  capture: CaptureStatus | null;
  captureBusy: boolean;
  captureError: string | null;
  onStartCapture: () => void;
  onStopCapture: () => void;
}) {
  const mode: Mode = frame?.mode ?? "mock";
  const token = MODE_TOKENS[mode];

  return (
    <div className="app">
      <header className="header">
        <div className="brand">DeadZone</div>
        <div className="provenance-badge" style={{ background: token.color }}>
          {token.label}
        </div>
        <div className="connection">{connected ? "● connected" : "○ connecting…"}</div>
      </header>

      <section className="metrics">
        {frame ? (
          <>
            <Metric label="Total" value={frame.headline.total.toLocaleString()} />
            <Metric label="Capacity" value={`${Math.round(frame.headline.capacity_pct * 100)}%`} />
            <Metric label="Peak Zone" value={frame.headline.peak_zone} />
            <Metric label="Trend" value={frame.headline.trend} />
          </>
        ) : (
          <SkeletonMetrics />
        )}
      </section>

      <section className="permission-strip">
        <div>
          <div className="permission-kicker">Bluetooth capture</div>
          <div className="permission-title">{captureTitle(capture, captureError)}</div>
          <div className="permission-detail">{captureDetail(capture, captureError)}</div>
        </div>
        <div className="permission-actions">
          {capture?.active ? (
            <button type="button" onClick={onStopCapture} disabled={captureBusy}>
              Stop scan
            </button>
          ) : (
            <button
              type="button"
              onClick={onStartCapture}
              disabled={captureBusy || Boolean(capture?.disabled_reason)}
            >
              {captureBusy ? "Starting…" : "Start BLE scan"}
            </button>
          )}
        </div>
      </section>

      <main className="canvas-and-rail">
        <div className="canvas">
          {frame ? (
            <ZonesList zones={frame.zones} />
          ) : (
            <div className="skeleton">Awaiting first frame…</div>
          )}
          <Legend />
        </div>
        <aside className="alerts">
          <h3>Alerts</h3>
          <p className="empty-state">No active alerts — system nominal.</p>
        </aside>
      </main>

      <footer className="footer">
        <span>{frame ? `Last frame: ${new Date(frame.timestamp * 1000).toLocaleTimeString()}` : "—"}</span>
        <span>v0.1.0</span>
      </footer>
    </div>
  );
}

function captureTitle(capture: CaptureStatus | null, error: string | null): string {
  if (error) return "Capture status needs attention";
  if (!capture) return "Checking Bluetooth";
  if (capture.disabled_reason) return "Permission launcher required";
  if (capture.active) return "Live scan running";
  return "Ready for live scan";
}

function captureDetail(capture: CaptureStatus | null, error: string | null): string {
  if (error) return error;
  if (!capture) return "Waiting for backend status.";
  if (capture.disabled_reason) return capture.disabled_reason;
  if (capture.active) {
    return `${capture.observations.toLocaleString()} observations captured in ${capture.trace_id ?? "current trace"}.`;
  }
  if (capture.trace_id) {
    return `${capture.observations.toLocaleString()} observations saved in ${capture.trace_id}.`;
  }
  return "The next scan may open the macOS Bluetooth prompt.";
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

function SkeletonMetrics() {
  return (
    <>
      {["Total", "Capacity", "Peak Zone", "Trend"].map((l) => (
        <div className="metric" key={l}>
          <div className="metric-label">{l}</div>
          <div className="metric-value skeleton-text">—</div>
        </div>
      ))}
    </>
  );
}

function ZonesList({ zones }: { zones: Zone[] }) {
  return (
    <ul className="zones">
      {zones.map((z) => {
        const pct = Math.min(1, z.count / z.capacity);
        return (
          <li key={z.id} className="zone">
            <div className="zone-name">{z.name}</div>
            <div className="zone-bar">
              <div className="zone-fill" style={{ width: `${pct * 100}%`, background: densityColor(pct) }} />
            </div>
            <div className="zone-count">
              {z.count.toLocaleString()} / {z.capacity.toLocaleString()} · {z.trend_5m}
            </div>
          </li>
        );
      })}
    </ul>
  );
}

function densityColor(pct: number): string {
  // Viridis-ish ramp (low → high)
  if (pct < 0.25) return "#440154";
  if (pct < 0.5) return "#3B528B";
  if (pct < 0.75) return "#21908C";
  if (pct < 0.9) return "#5DC863";
  return "#FDE725";
}

function Legend() {
  return (
    <div className="legend">
      <span>density (count / capacity)</span>
      <div className="legend-ramp">
        {[0.1, 0.3, 0.5, 0.7, 0.85, 0.95].map((p) => (
          <span key={p} style={{ background: densityColor(p) }} />
        ))}
      </div>
      <span>low → high</span>
    </div>
  );
}
