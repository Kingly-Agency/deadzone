from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

Mode = Literal["mock", "replay", "ble", "wifi", "mesh", "hybrid"]
Freshness = Literal["live", "fresh", "stale", "offline"]
PlaybackState = Literal["idle", "playing", "paused", "ended"]
Trend = Literal["falling", "stable", "rising", "spiking"]
AlertKind = Literal["congestion", "queue_buildup", "hallway_stall", "sensor_offline"]
AlertSeverity = Literal["info", "warning", "critical"]
AlertStatus = Literal["active", "resolved"]
SensorKind = Literal["mock", "ble", "wifi", "mesh_gateway", "mesh_node"]
SensorStatus = Literal["online", "degraded", "offline", "adapter_disabled"]
EnvelopeType = Literal[
    "snapshot",
    "zone_update",
    "alert_upsert",
    "sensor_status",
    "flow_update",
    "replay_state",
    "error",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Point(BaseModel):
    x: float
    y: float


class Zone(BaseModel):
    id: str
    name: str
    polygon: list[Point]


class Venue(BaseModel):
    id: str
    name: str
    bounds: dict[str, float]
    zones: list[Zone]
    map_version: str


class StreamClock(BaseModel):
    timestamp: datetime
    replay_position_s: float = 0.0
    speed: float = 1.0


class StreamState(BaseModel):
    mode: Mode
    connected: bool
    sequence: int
    source_label: str
    freshness: Freshness
    clock: StreamClock
    playback_state: PlaybackState | None = None
    scenario_id: str | None = None
    duration_s: float | None = None


class ZoneAggregate(BaseModel):
    zone_id: str
    density: float = Field(ge=0.0, le=1.0)
    pressure_score: float = Field(ge=0.0, le=1.0)
    trend: Trend
    confidence: float = Field(ge=0.0, le=1.0)
    capacity: int = Field(default=0, ge=0)
    estimated_devices: int = Field(default=0, ge=0)
    updated_at: datetime


class FlowVector(BaseModel):
    id: str
    from_zone: str
    to_zone: str
    direction_deg: float
    magnitude: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


class Alert(BaseModel):
    id: str
    kind: AlertKind
    zone_id: str
    severity: AlertSeverity
    message: str
    status: AlertStatus
    started_at: datetime
    duration_s: float = 0.0
    supporting_sensor_ids: list[str] = Field(default_factory=list)


class SensorNode(BaseModel):
    id: str
    label: str
    kind: SensorKind
    status: SensorStatus
    zone_id: str
    position: Point
    battery: float | None = Field(default=None, ge=0.0, le=1.0)
    latency_ms: float | None = None
    last_seen: datetime


class MeshLink(BaseModel):
    from_node: str
    to_node: str
    quality: float = Field(ge=0.0, le=1.0)
    latency_ms: float
    last_packet_at: datetime | None = None


class SnapshotMetrics(BaseModel):
    estimated_devices: int
    hot_zones: int
    active_alerts: int
    offline_sensors: int


class IntelligenceSnapshot(BaseModel):
    stream: StreamState
    venue: Venue
    zones: list[ZoneAggregate]
    flow_vectors: list[FlowVector]
    alerts: list[Alert]
    sensors: list[SensorNode]
    mesh_links: list[MeshLink]
    metrics: SnapshotMetrics


class ErrorResponse(BaseModel):
    code: str
    message: str
    recoverable: bool
    detail: dict[str, object] = Field(default_factory=dict)


class StreamEnvelope(BaseModel):
    type: EnvelopeType
    sequence: int = Field(ge=0)
    timestamp: datetime
    mode: Mode
    payload: IntelligenceSnapshot | ZoneAggregate | Alert | SensorNode | FlowVector | StreamState | ErrorResponse


class ReplayScenario(BaseModel):
    id: str
    name: str
    description: str
    duration_s: float
    seed: str
    available_speeds: list[float]


class ReplayControlRequest(BaseModel):
    action: Literal["load", "play", "pause", "restart", "seek", "set_speed"]
    scenario_id: str | None = None
    position_s: float | None = None
    speed: float | None = None


class ModeControlRequest(BaseModel):
    mode: Mode


class CaptureStartRequest(BaseModel):
    trace_id: str | None = None
    duration_s: float | None = Field(default=None, gt=0)


class CaptureStatus(BaseModel):
    active: bool
    trace_id: str | None
    observations: int
    backend: Literal["ble"]
    disabled_reason: str | None = None
    started_at: datetime | None = None
    latest_observation_at: datetime | None = None


class SensorEventTailItem(BaseModel):
    timestamp: datetime
    sensor_id: str
    beacon_hash: str
    source: Literal["ble", "mock", "replay"]
    rssi: int | None = None
    zone_id: str
    event_count: int = 1


class ZoneDetail(BaseModel):
    zone: Zone
    aggregate: ZoneAggregate
    alerts: list[Alert]
    flow_vectors: list[FlowVector]
    last_seen: datetime | None


class AppConfig(BaseModel):
    active_mode: Mode
    available_modes: list[Mode]
    disabled_modes: dict[str, str]
    venue: Venue
    features: dict[str, bool]
    websocket_url: str


class HealthResponse(BaseModel):
    ok: bool
    service: Literal["deadzone-api"]
    version: str
    mode: Mode
