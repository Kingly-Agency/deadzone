import { useStore } from "../store";
import { MODE_TOKENS } from "../types";
import type { Mode } from "../types";

const MODE_LIST: { mode: Mode; desc: string }[] = [
  { mode: "mock", desc: "Simulated data, seeded RNG" },
  { mode: "replay", desc: "Recorded scenario playback" },
  { mode: "ble", desc: "Real-time BLE sensors" },
  { mode: "wifi", desc: "Real-time Wi-Fi sensing" },
  { mode: "mesh", desc: "Meshtastic mesh network" },
  { mode: "hybrid", desc: "Combined live sensing" },
];

export function ConfigurationScreen() {
  const { config, snapshot, switchMode, connected } = useStore();
  const liveMode = snapshot?.stream.mode ?? config?.active_mode ?? "mock";
  const disabledModes = config?.disabled_modes ?? {};
  const features = config?.features;

  return (
    <div className="heatmap-page">
      <div className="heatmap-page-header">
        <div>
          <div className="heatmap-page-kicker">System</div>
          <div className="heatmap-page-title">Configuration</div>
        </div>
        <div className="heatmap-page-badge" style={{ background: MODE_TOKENS[liveMode].color }}>
          {MODE_TOKENS[liveMode].label} · Active
        </div>
        <div className="heatmap-page-conn">{connected ? "● connected" : "○ connecting…"}</div>
      </div>

      <div className="heatmap-page-zones">
        <div className="heatmap-page-kicker">Venue</div>
        <div className="config-kv-row">
          <span className="config-kv-label">Name</span>
          <span className="config-kv-value">{config?.venue?.name ?? "—"}</span>
        </div>
        <div className="config-kv-row">
          <span className="config-kv-label">Map version</span>
          <span className="config-kv-value">{config?.venue?.map_version ?? "—"}</span>
        </div>
      </div>

      <div className="heatmap-page-zones">
        <div className="heatmap-page-kicker">Stream</div>
        <div className="config-kv-row">
          <span className="config-kv-label">Live mode</span>
          <span className="config-kv-value">{liveMode}</span>
        </div>
        <div className="config-kv-row">
          <span className="config-kv-label">Source</span>
          <span className="config-kv-value">{snapshot?.stream.source_label ?? "—"}</span>
        </div>
        <div className="config-kv-row config-kv-row--mono">
          <span className="config-kv-label">WebSocket</span>
          <span className="config-kv-value">{config?.websocket_url ?? "—"}</span>
        </div>
      </div>

      <div className="heatmap-page-zones">
        <div className="heatmap-page-kicker">Operating mode</div>
        <div className="config-mode-options">
          {MODE_LIST.map(({ mode: m, desc }) => {
            const isActive = m === liveMode;
            const isDisabled = m in disabledModes;
            const t = MODE_TOKENS[m];
            return (
              <button
                type="button"
                key={m}
                className={`mode-option config-mode-option ${isActive ? "active" : ""} ${isDisabled ? "disabled" : ""}`}
                disabled={isDisabled || isActive}
                onClick={() => {
                  if (!isDisabled && !isActive) switchMode(m);
                }}
              >
                <span
                  className="mode-option-dot"
                  style={{ background: isDisabled ? "var(--text-dim)" : t.color }}
                />
                <div className="mode-option-info">
                  <div className="mode-option-name">{t.label}</div>
                  <div className="mode-option-desc">{isDisabled ? disabledModes[m] : desc}</div>
                </div>
                {isActive && <span className="mode-option-check">✓</span>}
              </button>
            );
          })}
        </div>
      </div>

      {features && (
        <div className="heatmap-page-metrics">
          <FeatureCard label="Replay" enabled={features.replay} />
          <FeatureCard label="BLE adapter" enabled={features.ble_adapter} />
          <FeatureCard label="Wi‑Fi adapter" enabled={features.wifi_adapter} />
          <FeatureCard label="Mesh adapter" enabled={features.mesh_adapter} />
        </div>
      )}
    </div>
  );
}

function FeatureCard({ label, enabled }: { label: string; enabled: boolean }) {
  return (
    <div className="heatmap-metric">
      <div className="heatmap-metric-label">{label}</div>
      <div className="heatmap-metric-value" style={{ fontSize: "16px" }}>
        {enabled ? "● Available" : "○ Off"}
      </div>
    </div>
  );
}
