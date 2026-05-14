import { useStore } from "../store";
import { SEVERITY_TOKENS } from "../types";
import type { Alert } from "../types";

export function AlertsPanel({ onViewZone }: { onViewZone: (zoneId: string) => void }) {
  const { snapshot, acknowledgedAlerts, acknowledgeAlert } = useStore();

  const alerts = snapshot?.alerts ?? [];
  const active = alerts.filter((a) => a.status === "active" && !acknowledgedAlerts.has(a.id));
  const acked = alerts.filter((a) => acknowledgedAlerts.has(a.id) || a.status === "resolved");
  const activeCount = active.length;

  return (
    <div className="alerts-panel">
      <div className="alerts-header">
        <span className="alerts-title">Alerts</span>
        <span
          className="alerts-count"
          style={{
            background: activeCount > 0 ? "#FEE2E2" : "var(--surface-2)",
            color: activeCount > 0 ? "var(--severity-critical)" : "var(--text-dim)",
          }}
        >
          {activeCount} active
        </span>
      </div>

      <div className="alerts-list">
        {active.length === 0 && acked.length === 0 && (
          <div className="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.5, marginBottom: 12, color: "var(--sensor-online)" }}>
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <div>No active alerts — system nominal.</div>
            {snapshot && (
              <div style={{ fontSize: 11, color: "var(--text-dim)" }}>
                Monitoring {snapshot.venue.zones.length} zones across {snapshot.sensors.length} sensors.
              </div>
            )}
          </div>
        )}

        {active.map((a) => (
          <AlertItem
            key={a.id}
            alert={a}
            acknowledged={false}
            onAck={() => acknowledgeAlert(a.id)}
            onView={() => onViewZone(a.zone_id)}
          />
        ))}

        {acked.length > 0 && active.length > 0 && (
          <div style={{ fontSize: 11, color: "var(--text-dim)", margin: "8px 0 4px", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: 600 }}>
            Acknowledged
          </div>
        )}

        {acked.map((a) => (
          <AlertItem
            key={a.id}
            alert={a}
            acknowledged={true}
            onAck={() => {}}
            onView={() => onViewZone(a.zone_id)}
          />
        ))}
      </div>
    </div>
  );
}

function AlertItem({
  alert,
  acknowledged,
  onAck,
  onView,
}: {
  alert: Alert;
  acknowledged: boolean;
  onAck: () => void;
  onView: () => void;
}) {
  const token = SEVERITY_TOKENS[alert.severity];
  const zoneName = alert.zone_id.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div className={`alert-item severity-${alert.severity} ${acknowledged ? "acknowledged" : ""}`}>
      <div className="alert-badge" style={{ color: token.color }}>
        {token.icon} {alert.severity.toUpperCase()}
      </div>
      <div className="alert-message">{alert.message}</div>
      <div className="alert-meta">
        <span>{zoneName}</span>
        <span>·</span>
        <span>{new Date(alert.started_at).toLocaleTimeString()}</span>
        {acknowledged && (
          <>
            <span>·</span>
            <span>✓ ack'd</span>
          </>
        )}
      </div>
      {!acknowledged && (
        <div className="alert-actions">
          <button className="alert-btn" onClick={onAck}>Acknowledge</button>
          <button className="alert-btn alert-btn-primary" onClick={onView}>View Zone</button>
        </div>
      )}
    </div>
  );
}
