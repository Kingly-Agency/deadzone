/* DeadZone TypeScript types — mirrors the backend OpenAPI contract exactly. */

export type Mode = "mock" | "replay" | "ble" | "wifi" | "mesh" | "hybrid";
export type Freshness = "live" | "fresh" | "stale" | "offline";
export type Trend = "falling" | "stable" | "rising" | "spiking";
export type AlertKind = "congestion" | "queue_buildup" | "hallway_stall" | "sensor_offline";
export type Severity = "info" | "warning" | "critical";
export type AlertStatus = "active" | "resolved";
export type SensorKind = "mock" | "ble" | "wifi" | "mesh_gateway" | "mesh_node";
export type SensorStatusType = "online" | "degraded" | "offline" | "adapter_disabled";
export type EnvelopeType = "snapshot" | "zone_update" | "alert_upsert" | "sensor_status" | "flow_update" | "replay_state" | "error";

export interface Point { x: number; y: number; }

export interface Zone {
  id: string;
  name: string;
  polygon: Point[];
}

export interface VenueBounds { width: number; height: number; }

export interface Venue {
  id: string;
  name: string;
  map_version: string;
  bounds: VenueBounds;
  zones: Zone[];
}

export interface ZoneAggregate {
  zone_id: string;
  density: number;
  pressure_score: number;
  trend: Trend;
  confidence: number;
  estimated_devices: number;
  capacity: number;
  updated_at: string;
}

export interface FlowVector {
  id: string;
  from_zone: string;
  to_zone: string;
  direction_deg: number;
  magnitude: number;
  confidence: number;
}

export interface Alert {
  id: string;
  kind: AlertKind;
  zone_id: string;
  severity: Severity;
  message: string;
  status: AlertStatus;
  started_at: string;
  duration_s?: number;
  supporting_sensor_ids: string[];
}

export interface SensorNode {
  id: string;
  label: string;
  kind: SensorKind;
  status: SensorStatusType;
  zone_id: string;
  position: Point;
  battery: number | null;
  latency_ms: number | null;
  last_seen: string;
}

export interface MeshLink {
  from_node: string;
  to_node: string;
  quality: number;
  latency_ms: number;
  last_packet_at: string | null;
}

export interface SnapshotMetrics {
  estimated_devices: number;
  hot_zones: number;
  active_alerts: number;
  offline_sensors: number;
}

export interface StreamClock {
  timestamp: string;
  replay_position_s: number;
  speed: number;
}

export interface StreamState {
  mode: Mode;
  connected: boolean;
  sequence: number;
  source_label: string;
  freshness: Freshness;
  clock: StreamClock;
  playback_state?: "idle" | "playing" | "paused" | "ended" | null;
  scenario_id?: string | null;
  duration_s?: number | null;
}

export interface IntelligenceSnapshot {
  stream: StreamState;
  venue: Venue;
  zones: ZoneAggregate[];
  flow_vectors: FlowVector[];
  alerts: Alert[];
  sensors: SensorNode[];
  mesh_links: MeshLink[];
  metrics: SnapshotMetrics;
}

export interface StreamEnvelope {
  type: EnvelopeType;
  sequence: number;
  timestamp: string;
  mode: Mode;
  payload: IntelligenceSnapshot | ZoneAggregate | Alert | SensorNode | FlowVector | StreamState | ErrorResponse;
}

export interface ErrorResponse {
  code: string;
  message: string;
  recoverable: boolean;
  detail: Record<string, unknown>;
}

export interface Features {
  replay: boolean;
  ble_adapter: boolean;
  wifi_adapter: boolean;
  mesh_adapter: boolean;
}

export interface AppConfig {
  active_mode: Mode;
  available_modes: Mode[];
  disabled_modes: Record<string, string>;
  venue: Venue;
  features: Features;
  websocket_url: string;
}

export interface ReplayScenario {
  id: string;
  name: string;
  description: string;
  duration_s: number;
  seed: string;
  available_speeds: number[];
}

export interface RawSensorEvent {
  timestamp: string;
  sensor_id: string;
  rssi: number | null;
  zone_id: string;
  device_count: number;
}

export interface CaptureStatus {
  active: boolean;
  trace_id: string | null;
  observations: number;
  backend: "ble";
  disabled_reason: string | null;
  started_at: string | null;
  latest_observation_at: string | null;
}

// ── Mode display tokens ─────────────────────────────────────────────────
export const MODE_TOKENS: Record<Mode, { color: string; label: string; badge: string }> = {
  mock:   { color: "#3B82F6", label: "MOCK",   badge: "Simulated data" },
  replay: { color: "#F59E0B", label: "REPLAY", badge: "Recorded data" },
  ble:    { color: "#10B981", label: "BLE",    badge: "Real-time BLE sensing" },
  wifi:   { color: "#14B8A6", label: "WI-FI",  badge: "Real-time Wi-Fi sensing" },
  mesh:   { color: "#8B5CF6", label: "MESH",   badge: "Distributed sensors" },
  hybrid: { color: "#22C55E", label: "HYBRID", badge: "Combined live sensing" },
};

export const SEVERITY_TOKENS: Record<Severity, { color: string; icon: string }> = {
  info:     { color: "#3B82F6", icon: "●" },
  warning:  { color: "#F59E0B", icon: "▲" },
  critical: { color: "#EF4444", icon: "▲▲" },
};

export const TREND_ICONS: Record<Trend, string> = {
  falling: "↘",
  stable: "→",
  rising: "↗",
  spiking: "⬆",
};
