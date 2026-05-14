"""DeadZone Pydantic models — matches the OpenAPI contract exactly."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ───────────────────────────────────────────────────────────────────

class Mode(str, Enum):
    mock = "mock"
    replay = "replay"
    ble = "ble"
    wifi = "wifi"
    mesh = "mesh"
    hybrid = "hybrid"


class Freshness(str, Enum):
    live = "live"
    fresh = "fresh"
    stale = "stale"
    offline = "offline"


class Trend(str, Enum):
    falling = "falling"
    stable = "stable"
    rising = "rising"
    spiking = "spiking"


class AlertKind(str, Enum):
    congestion = "congestion"
    queue_buildup = "queue_buildup"
    hallway_stall = "hallway_stall"
    sensor_offline = "sensor_offline"


class Severity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class AlertStatus(str, Enum):
    active = "active"
    resolved = "resolved"


class SensorKind(str, Enum):
    mock = "mock"
    ble = "ble"
    wifi = "wifi"
    mesh_gateway = "mesh_gateway"
    mesh_node = "mesh_node"


class SensorStatus(str, Enum):
    online = "online"
    degraded = "degraded"
    offline = "offline"
    adapter_disabled = "adapter_disabled"


class EnvelopeType(str, Enum):
    snapshot = "snapshot"
    zone_update = "zone_update"
    alert_upsert = "alert_upsert"
    sensor_status = "sensor_status"
    flow_update = "flow_update"
    replay_state = "replay_state"
    error = "error"


class ReplayAction(str, Enum):
    load = "load"
    play = "play"
    pause = "pause"
    restart = "restart"
    seek = "seek"
    set_speed = "set_speed"


# ── Geometry ────────────────────────────────────────────────────────────────

class Point(BaseModel):
    x: float
    y: float


# ── Venue ───────────────────────────────────────────────────────────────────

class Zone(BaseModel):
    id: str
    name: str
    polygon: list[Point]


class VenueBounds(BaseModel):
    width: float
    height: float


class Venue(BaseModel):
    id: str
    name: str
    map_version: str
    bounds: VenueBounds
    zones: list[Zone]


# ── Zone Aggregate ──────────────────────────────────────────────────────────

class ZoneAggregate(BaseModel):
    zone_id: str
    density: float = Field(ge=0, le=1)
    pressure_score: float = Field(ge=0, le=1)
    trend: Trend
    confidence: float = Field(ge=0, le=1)
    estimated_devices: int = Field(default=0, ge=0)
    capacity: int = Field(default=0, ge=0)
    updated_at: datetime


# ── Flow Vector ─────────────────────────────────────────────────────────────

class FlowVector(BaseModel):
    id: str
    from_zone: str
    to_zone: str
    direction_deg: float
    magnitude: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)


# ── Alert ───────────────────────────────────────────────────────────────────

class Alert(BaseModel):
    id: str
    kind: AlertKind
    zone_id: str
    severity: Severity
    message: str
    status: AlertStatus
    started_at: datetime
    duration_s: Optional[float] = None
    supporting_sensor_ids: list[str] = Field(default_factory=list)


# ── Sensor ──────────────────────────────────────────────────────────────────

class SensorNode(BaseModel):
    id: str
    label: str
    kind: SensorKind
    status: SensorStatus
    zone_id: str
    position: Point
    battery: Optional[float] = Field(default=None, ge=0, le=1)
    latency_ms: Optional[float] = None
    last_seen: datetime


# ── Mesh ────────────────────────────────────────────────────────────────────

class MeshLink(BaseModel):
    from_node: str
    to_node: str
    quality: float = Field(ge=0, le=1)
    latency_ms: float
    last_packet_at: Optional[datetime] = None


# ── Metrics ─────────────────────────────────────────────────────────────────

class SnapshotMetrics(BaseModel):
    estimated_devices: int
    hot_zones: int
    active_alerts: int
    offline_sensors: int


# ── Stream State ────────────────────────────────────────────────────────────

class StreamClock(BaseModel):
    timestamp: datetime
    replay_position_s: float = 0.0
    speed: float = 1.0


class StreamState(BaseModel):
    mode: Mode
    connected: bool = True
    sequence: int = 0
    source_label: str = ""
    freshness: Freshness = Freshness.live
    clock: StreamClock


# ── Intelligence Snapshot ───────────────────────────────────────────────────

class IntelligenceSnapshot(BaseModel):
    stream: StreamState
    venue: Venue
    zones: list[ZoneAggregate]
    flow_vectors: list[FlowVector]
    alerts: list[Alert]
    sensors: list[SensorNode]
    mesh_links: list[MeshLink]
    metrics: SnapshotMetrics


# ── Stream Envelope ─────────────────────────────────────────────────────────

class StreamEnvelope(BaseModel):
    type: EnvelopeType
    sequence: int = Field(ge=0)
    timestamp: datetime
    mode: Mode
    payload: dict


# ── Config ──────────────────────────────────────────────────────────────────

class Features(BaseModel):
    replay: bool = True
    ble_adapter: bool = False
    wifi_adapter: bool = False
    mesh_adapter: bool = False


class AppConfig(BaseModel):
    active_mode: Mode
    available_modes: list[Mode]
    disabled_modes: dict[str, str] = Field(default_factory=dict)
    venue: Venue
    features: Features
    websocket_url: str = "ws://localhost:8000/ws/live"


# ── Replay ──────────────────────────────────────────────────────────────────

class ReplayScenario(BaseModel):
    id: str
    name: str
    description: str
    duration_s: float
    seed: str
    available_speeds: list[float] = Field(
        default_factory=lambda: [0.25, 0.5, 1.0, 2.0, 4.0]
    )


class ReplayControlRequest(BaseModel):
    action: ReplayAction
    scenario_id: Optional[str] = None
    position_s: Optional[float] = None
    speed: Optional[float] = None


# ── Health / Error ──────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "deadzone-api"
    version: str = "0.1.0"
    mode: Mode = Mode.mock


class ErrorResponse(BaseModel):
    code: str
    message: str
    recoverable: bool = True
    detail: Optional[dict] = None


# ── Raw Event (for sensor event tail) ───────────────────────────────────────

class RawSensorEvent(BaseModel):
    timestamp: datetime
    sensor_id: str
    rssi: Optional[float] = None
    zone_id: str
    device_count: int = 0
