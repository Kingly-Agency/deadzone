"""Runtime engine — manages active source, snapshot cache, and WebSocket broadcaster."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import WebSocket

from app.models import (
    AppConfig,
    EnvelopeType,
    Features,
    IntelligenceSnapshot,
    Mode,
    RawSensorEvent,
    StreamEnvelope,
)
from app.sources import SensorSource
from app.sources.mock import MockSource
from app.sources.replay import SCENARIOS, ReplaySource
from app.venue import SENSOR_DEFS, VENUE

logger = logging.getLogger("deadzone.engine")


class Engine:
    """Central runtime engine. Drives tick loop, caches snapshot, broadcasts to WebSocket clients."""

    def __init__(self) -> None:
        self._mode: Mode = Mode.mock
        self._mock_source = MockSource()
        self._replay_source = ReplaySource()
        self._active_source: SensorSource = self._mock_source
        self._latest_snapshot: Optional[IntelligenceSnapshot] = None
        self._sequence: int = 0
        self._clients: set[WebSocket] = set()
        self._tick_task: Optional[asyncio.Task] = None
        self._raw_events: dict[str, list[RawSensorEvent]] = {
            sd["id"]: [] for sd in SENSOR_DEFS
        }

    @property
    def mode(self) -> Mode:
        return self._mode

    @property
    def latest_snapshot(self) -> Optional[IntelligenceSnapshot]:
        return self._latest_snapshot

    @property
    def replay_source(self) -> ReplaySource:
        return self._replay_source

    def get_config(self) -> AppConfig:
        return AppConfig(
            active_mode=self._mode,
            available_modes=[Mode.mock, Mode.replay],
            disabled_modes={
                "ble": "No Bluetooth adapter detected",
                "wifi": "Wi-Fi monitor mode not available",
                "mesh": "No Meshtastic gateway connected",
                "hybrid": "Requires at least one live adapter",
            },
            venue=VENUE,
            features=Features(replay=True),
            websocket_url="ws://localhost:8000/ws/live",
        )

    async def start(self) -> None:
        """Start the tick loop."""
        self._tick_task = asyncio.create_task(self._tick_loop())
        logger.info("Engine started in %s mode", self._mode.value)

    async def stop(self) -> None:
        """Stop the tick loop."""
        if self._tick_task:
            self._tick_task.cancel()
            try:
                await self._tick_task
            except asyncio.CancelledError:
                pass
        logger.info("Engine stopped")

    async def switch_mode(self, new_mode: Mode) -> IntelligenceSnapshot:
        """Switch the active data source."""
        if new_mode == Mode.mock:
            self._active_source = self._mock_source
        elif new_mode == Mode.replay:
            self._active_source = self._replay_source
        else:
            # Live modes are disabled in MVP
            raise ValueError(f"Mode {new_mode.value} is not available")

        self._mode = new_mode
        logger.info("Switched to %s mode", new_mode.value)

        # Generate first frame in new mode
        snapshot = await self._active_source.tick(0)
        self._latest_snapshot = snapshot
        await self._broadcast_snapshot(snapshot)
        return snapshot

    async def reset(self) -> IntelligenceSnapshot:
        """Reset current source and return fresh snapshot."""
        await self._active_source.reset()
        self._sequence = 0
        snapshot = await self._active_source.tick(0)
        self._latest_snapshot = snapshot
        await self._broadcast_snapshot(snapshot)
        logger.info("Demo reset in %s mode", self._mode.value)
        return snapshot

    def register_client(self, ws: WebSocket) -> None:
        self._clients.add(ws)
        logger.info("WebSocket client connected (%d total)", len(self._clients))

    def unregister_client(self, ws: WebSocket) -> None:
        self._clients.discard(ws)
        logger.info("WebSocket client disconnected (%d total)", len(self._clients))

    def get_raw_events(self, sensor_id: str, limit: int = 10) -> list[RawSensorEvent]:
        return list(reversed(self._raw_events.get(sensor_id, [])))[:limit]

    # ── Private ─────────────────────────────────────────────────────────

    async def _tick_loop(self) -> None:
        """Main tick loop — drives source at ~1 Hz."""
        while True:
            try:
                snapshot = await self._active_source.tick(1.0)
                self._latest_snapshot = snapshot
                self._generate_raw_events(snapshot)
                await self._broadcast_snapshot(snapshot)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Error in tick loop")
            await asyncio.sleep(1.0)

    async def _broadcast_snapshot(self, snapshot: IntelligenceSnapshot) -> None:
        """Send snapshot envelope to all connected clients."""
        self._sequence += 1
        envelope = StreamEnvelope(
            type=EnvelopeType.snapshot,
            sequence=self._sequence,
            timestamp=datetime.now(timezone.utc),
            mode=self._mode,
            payload=snapshot.model_dump(mode="json"),
        )
        msg = json.dumps(envelope.model_dump(mode="json"))

        dead: list[WebSocket] = []
        for ws in self._clients:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self._clients.discard(ws)

    def _generate_raw_events(self, snapshot: IntelligenceSnapshot) -> None:
        """Generate privacy-safe raw events for the event tail."""
        now = datetime.now(timezone.utc)
        for sensor in snapshot.sensors:
            zone_agg = next(
                (z for z in snapshot.zones if z.zone_id == sensor.zone_id), None
            )
            event = RawSensorEvent(
                timestamp=now,
                sensor_id=sensor.id,
                rssi=-60 - (sensor.latency_ms or 0) / 5 if sensor.latency_ms else None,
                zone_id=sensor.zone_id,
                device_count=zone_agg.estimated_devices // 4 if zone_agg else 0,
            )
            events = self._raw_events.setdefault(sensor.id, [])
            events.append(event)
            # Keep only last 50
            if len(events) > 50:
                self._raw_events[sensor.id] = events[-50:]


# Singleton
engine = Engine()
