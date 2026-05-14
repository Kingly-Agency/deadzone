from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.domain.models import (
    AppConfig,
    CaptureStatus,
    ErrorResponse,
    HealthResponse,
    IntelligenceSnapshot,
    Mode,
    ReplayControlRequest,
    StreamClock,
    StreamEnvelope,
    StreamState,
    ZoneDetail,
)
from app.settings import Settings
from app.sources.ble import BleCaptureManager
from app.sources.mesh import DISABLED_REASON as MESH_DISABLED_REASON
from app.sources.mock import MockFromTraceSource
from app.sources.replay import ReplayController
from app.sources.wifi import DISABLED_REASON as WIFI_DISABLED_REASON
from app.spatial.aggregate import aggregate_zones, flow_vectors, sensor_nodes, snapshot_metrics
from app.spatial.alerts import build_alerts
from app.spatial.venue import demo_venue
from app.traces import TraceStore

EXPOSED_MODES: list[Mode] = ["ble", "mock"]
HIDDEN_MODE_REASONS: dict[str, str] = {
    "replay": "Replay is not exposed in the live dashboard mode picker.",
    "wifi": WIFI_DISABLED_REASON,
    "mesh": MESH_DISABLED_REASON,
    "hybrid": "Hybrid is disabled until BLE capture plus Wi-Fi/Mesh adapters are validated.",
}


class DeadZoneEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = TraceStore(settings.capture_dir, settings.capture_salt)
        self.capture = BleCaptureManager(settings, self.store)
        self.replay = ReplayController(self.store)
        self.mock = MockFromTraceSource(self.store, settings.seed)
        self.active_mode: Mode = settings.mode if settings.mode in EXPOSED_MODES else "ble"
        self.sequence = 0
        self._live_start_lock = asyncio.Lock()

    def next_sequence(self) -> int:
        self.sequence += 1
        return self.sequence

    def disabled_modes(self) -> dict[str, str]:
        disabled: dict[str, str] = dict(HIDDEN_MODE_REASONS)
        ble_reason = self.capture.disabled_reason
        if ble_reason:
            disabled["ble"] = ble_reason
        return disabled

    def config(self) -> AppConfig:
        return AppConfig(
            active_mode=self.active_mode,
            available_modes=EXPOSED_MODES,
            disabled_modes=self.disabled_modes(),
            venue=demo_venue(),
            features={
                "replay": False,
                "ble_adapter": self.capture.disabled_reason is None,
                "wifi_adapter": False,
                "mesh_adapter": False,
            },
            websocket_url="ws://localhost:8000/ws/live",
        )

    def health(self) -> HealthResponse:
        return HealthResponse(ok=True, service="deadzone-api", version=self.settings.version, mode=self.active_mode)

    async def ensure_live_ble_capture(self) -> CaptureStatus | None:
        if self.active_mode != "ble":
            return None
        if self.capture.active:
            return self.capture.status()
        async with self._live_start_lock:
            if self.active_mode != "ble":
                return None
            if self.capture.active:
                return self.capture.status()
            return await self.start_capture(trace_id=None, duration_s=None)

    async def start_capture(self, trace_id: str | None, duration_s: float | None) -> CaptureStatus:
        status = await self.capture.start(trace_id=trace_id, duration_s=duration_s)
        if not status.disabled_reason:
            self.active_mode = "ble"
        return status

    async def stop_capture(self) -> CaptureStatus:
        return await self.capture.stop()

    def set_mode(self, mode: Mode) -> StreamState | ErrorResponse:
        disabled = self.disabled_modes()
        if mode in disabled:
            return ErrorResponse(
                code="mode_unavailable",
                message=disabled[mode],
                recoverable=True,
                detail={"mode": mode},
            )
        self.active_mode = mode
        return self.stream_state(mode, self.sequence)

    def control_replay(self, request: ReplayControlRequest) -> StreamState | ErrorResponse:
        response = self.replay.control(request, self.next_sequence())
        if isinstance(response, StreamState):
            self.active_mode = "replay"
        return response

    def reset_demo(self) -> IntelligenceSnapshot:
        self.sequence = 0
        self.active_mode = "ble"
        return self.snapshot()

    def snapshot(self) -> IntelligenceSnapshot:
        sequence = self.next_sequence()
        observations = self.current_observations()
        now = datetime.now(timezone.utc)
        zones = aggregate_zones(observations, now=now)
        sensors = sensor_nodes(observations, now=now)
        alerts = build_alerts(zones, sensors)
        vectors = flow_vectors(observations)
        return IntelligenceSnapshot(
            stream=self.stream_state(self.active_mode, sequence),
            venue=demo_venue(),
            zones=zones,
            flow_vectors=vectors,
            alerts=alerts,
            sensors=sensors,
            mesh_links=[],
            metrics=snapshot_metrics(zones, sensors, len(alerts)),
        )

    def envelope(self, envelope_type: str = "snapshot") -> StreamEnvelope:
        snapshot = self.snapshot()
        return StreamEnvelope(
            type=envelope_type,  # type: ignore[arg-type]
            sequence=snapshot.stream.sequence,
            timestamp=datetime.now(timezone.utc),
            mode=snapshot.stream.mode,
            payload=snapshot,
        )

    def envelopes(self) -> list[StreamEnvelope]:
        snapshot = self.snapshot()
        now = datetime.now(timezone.utc)
        envelopes: list[StreamEnvelope] = [
            StreamEnvelope(
                type="snapshot",
                sequence=snapshot.stream.sequence,
                timestamp=now,
                mode=snapshot.stream.mode,
                payload=snapshot,
            )
        ]
        for zone in snapshot.zones:
            envelopes.append(
                StreamEnvelope(
                    type="zone_update",
                    sequence=self.next_sequence(),
                    timestamp=now,
                    mode=snapshot.stream.mode,
                    payload=zone,
                )
            )
        for sensor in snapshot.sensors:
            envelopes.append(
                StreamEnvelope(
                    type="sensor_status",
                    sequence=self.next_sequence(),
                    timestamp=now,
                    mode=snapshot.stream.mode,
                    payload=sensor,
                )
            )
        for vector in snapshot.flow_vectors:
            envelopes.append(
                StreamEnvelope(
                    type="flow_update",
                    sequence=self.next_sequence(),
                    timestamp=now,
                    mode=snapshot.stream.mode,
                    payload=vector,
                )
            )
        for alert in snapshot.alerts:
            envelopes.append(
                StreamEnvelope(
                    type="alert_upsert",
                    sequence=self.next_sequence(),
                    timestamp=now,
                    mode=snapshot.stream.mode,
                    payload=alert,
                )
            )
        if snapshot.stream.mode == "replay":
            envelopes.append(
                StreamEnvelope(
                    type="replay_state",
                    sequence=self.next_sequence(),
                    timestamp=now,
                    mode=snapshot.stream.mode,
                    payload=self.replay.stream_state(self.sequence),
                )
            )
        error = self.active_mode_error()
        if error:
            envelopes.append(
                StreamEnvelope(
                    type="error",
                    sequence=self.next_sequence(),
                    timestamp=now,
                    mode=snapshot.stream.mode,
                    payload=error,
                )
            )
        return envelopes

    def active_mode_error(self) -> ErrorResponse | None:
        disabled = self.disabled_modes()
        reason = disabled.get(self.active_mode)
        if not reason:
            return None
        return ErrorResponse(
            code="mode_unavailable",
            message=reason,
            recoverable=True,
            detail={"mode": self.active_mode},
        )

    def zone_detail(self, zone_id: str) -> ZoneDetail | None:
        snapshot = self.snapshot()
        zone = next((item for item in snapshot.venue.zones if item.id == zone_id), None)
        aggregate = next((item for item in snapshot.zones if item.zone_id == zone_id), None)
        if not zone or not aggregate:
            return None
        return ZoneDetail(
            zone=zone,
            aggregate=aggregate,
            alerts=[alert for alert in snapshot.alerts if alert.zone_id == zone_id],
            flow_vectors=[
                vector
                for vector in snapshot.flow_vectors
                if vector.from_zone == zone_id or vector.to_zone == zone_id
            ],
            last_seen=aggregate.updated_at,
        )

    def sensor_event_tail(self, sensor_id: str, limit: int = 10) -> list[dict[str, Any]]:
        if sensor_id != "local-ble-scanner":
            return []
        trace_id = self.capture.trace_id or self.store.latest_trace_id()
        observations = self.store.read(trace_id) if trace_id else []
        return [
            {
                "timestamp": item.timestamp,
                "sensor_id": sensor_id,
                "beacon_hash": item.beacon_hash,
                "source": "ble" if self.active_mode == "ble" else self.active_mode,
                "rssi": item.rssi,
                "zone_id": item.zone_id,
                "event_count": item.event_count,
            }
            for item in observations[-limit:]
        ]

    def current_observations(self):
        if self.active_mode == "replay":
            return self.replay.observations_window()
        if self.active_mode == "mock":
            return self.mock.observations()
        trace_id = self.capture.trace_id or self.store.latest_trace_id()
        observations = self.store.read(trace_id) if trace_id else []
        return self._recent_observations(observations)

    def _recent_observations(self, observations, window_s: float = 30.0):
        if not observations:
            return []
        anchor = (
            datetime.now(timezone.utc)
            if self.capture.active
            else max(item.timestamp for item in observations)
        )
        return [
            item
            for item in observations
            if 0 <= (anchor - item.timestamp).total_seconds() <= window_s
        ]

    def stream_state(self, mode: Mode, sequence: int) -> StreamState:
        now = datetime.now(timezone.utc)
        if mode == "replay":
            return self.replay.stream_state(sequence)
        if mode == "mock":
            trace_id = self.store.latest_trace_id()
            return StreamState(
                mode="mock",
                connected=True,
                sequence=sequence,
                source_label=(
                    f"Mock derived from {self.store.public_label(trace_id)}"
                    if trace_id
                    else "Mock demo data"
                ),
                freshness="fresh",
                clock=StreamClock(timestamp=now, replay_position_s=0.0, speed=1.0),
            )
        if mode == "ble":
            latest = self.capture.latest_observation_at
            if latest is None:
                trace_id = self.capture.trace_id or self.store.latest_trace_id()
                observations = self.store.read(trace_id) if trace_id else []
                latest = max((item.timestamp for item in observations), default=None)
            if self.capture.active:
                freshness = "live"
            elif latest is None:
                freshness = "offline"
            else:
                age = (now - latest).total_seconds()
                freshness = "fresh" if age <= 30 else "stale" if age <= 60 else "offline"
            return StreamState(
                mode="ble",
                connected=self.capture.active,
                sequence=sequence,
                source_label="BLE capture: local scanner",
                freshness=freshness,
                clock=StreamClock(timestamp=now, replay_position_s=0.0, speed=1.0),
            )
        return StreamState(
            mode=mode,
            connected=False,
            sequence=sequence,
            source_label=f"{mode} unavailable",
            freshness="offline",
            clock=StreamClock(timestamp=now, replay_position_s=0.0, speed=1.0),
        )

    def legacy_frame(self) -> dict[str, Any]:
        snapshot = self.snapshot()
        zones_by_id = {zone.id: zone for zone in snapshot.venue.zones}
        zones = []
        for aggregate in snapshot.zones:
            zone = zones_by_id[aggregate.zone_id]
            zones.append(
                {
                    "id": aggregate.zone_id,
                    "name": zone.name,
                    "count": aggregate.estimated_devices,
                    "capacity": 100,
                    "trend_5m": aggregate.trend,
                }
            )
        peak = max(snapshot.zones, key=lambda item: item.pressure_score)
        return {
            "timestamp": snapshot.stream.clock.timestamp.timestamp(),
            "mode": "live" if snapshot.stream.mode == "ble" else snapshot.stream.mode,
            "venue_id": snapshot.venue.id,
            "zones": zones,
            "headline": {
                "total": snapshot.metrics.estimated_devices,
                "capacity_pct": max((zone.density for zone in snapshot.zones), default=0),
                "peak_zone": zones_by_id[peak.zone_id].name,
                "trend": peak.trend,
            },
        }
