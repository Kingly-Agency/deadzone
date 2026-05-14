"""Per-laptop mesh node runner.

Owns a Scanner protocol, a tick loop, and an AggregateClient.
Posts zone-aggregate packets to the gateway every ``interval_s`` seconds.
Aggregate-only across the wire — no raw device identifiers ever leave the node.

Zero-coupling: this module does NOT import from ``app.sources``, ``app.runtime``,
``app.spatial``, ``app.api``, or ``app.main``.  The real BLE scanner is injected
externally via the :class:`Scanner` protocol.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from math import sin, pi
from typing import Protocol, runtime_checkable

from app.mesh.models import (
    AggregatePacket,
    Freshness,
    Position,
    ScannerKind,
    ScannerStatus,
    ZoneAggregate,
    utc_now,
)
from app.mesh.transport import AggregateClient

logger = logging.getLogger(__name__)


@runtime_checkable
class Scanner(Protocol):
    """Any object that knows how to produce zone-level aggregates for ONE tick.

    Implementations must NEVER expose raw device identifiers — only zone counts.
    """

    kind: ScannerKind
    status: ScannerStatus

    def aggregate(self) -> list[ZoneAggregate]:
        """Return the current per-zone aggregate snapshot."""
        ...


@dataclass
class MockNodeScanner:
    """Deterministic sinusoidal mock scanner for smoke tests.

    Produces zone counts that oscillate between 0 and ~max_devices_per_zone
    so two-node demos still show interesting movement without BLE hardware.
    """

    seed: int = 1337
    interval_s: float = 1.0
    max_devices_per_zone: int = 24
    zone_ids: list[str] = field(default_factory=lambda: ["near-scanner", "mid-field", "far-field"])
    kind: ScannerKind = "ble"
    status: ScannerStatus = "online"
    _t: float = field(default=0.0, init=False)
    _rng: random.Random = field(init=False, default=None)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def aggregate(self) -> list[ZoneAggregate]:
        self._t += self.interval_s
        out: list[ZoneAggregate] = []
        for i, zone_id in enumerate(self.zone_ids):
            # Each zone phases differently so the dashboard never goes flat.
            phase = (i / max(len(self.zone_ids), 1)) * 2 * pi
            base = (sin(self._t / 8.0 + phase) + 1.0) / 2.0  # 0..1
            jitter = self._rng.random() * 0.05
            density = min(1.0, max(0.0, base * 0.85 + jitter))
            estimated = int(density * self.max_devices_per_zone)
            trend: str
            # crude trend: derivative sign
            phase_next = (i / max(len(self.zone_ids), 1)) * 2 * pi
            slope = sin((self._t + self.interval_s) / 8.0 + phase_next) - sin(self._t / 8.0 + phase_next)
            if slope > 0.05:
                trend = "rising"
            elif slope < -0.05:
                trend = "falling"
            else:
                trend = "stable"
            out.append(
                ZoneAggregate(
                    zone_id=zone_id,
                    estimated_devices=estimated,
                    density=density,
                    trend=trend,  # type: ignore[arg-type]
                    confidence=0.35,
                )
            )
        return out


class MeshNode:
    """Runs the per-laptop POST loop.

    Owns: a Scanner, an AggregateClient, and a tick interval.
    Does NOT touch raw BLE data — that stays inside the scanner.
    """

    def __init__(
        self,
        *,
        node_id: str,
        client: AggregateClient,
        scanner: Scanner,
        interval_s: float = 1.0,
        position: Position | None = None,
    ) -> None:
        self.node_id = node_id
        self.client = client
        self.scanner = scanner
        self.interval_s = interval_s
        self.position = position
        self._task: asyncio.Task | None = None
        self._start_mono: float | None = None
        self._last_scanner_at: datetime | None = None

    @property
    def uptime_s(self) -> float:
        return 0.0 if self._start_mono is None else (time.monotonic() - self._start_mono)

    def _freshness(self) -> Freshness:
        if self.scanner is None:
            return "offline"
        if self._last_scanner_at is None:
            return "fresh"
        age = (utc_now() - self._last_scanner_at).total_seconds()
        if age <= 2.0:
            return "live"
        if age <= 5.0:
            return "stale"
        return "offline"

    def build_packet(self) -> AggregatePacket:
        zones = self.scanner.aggregate()
        self._last_scanner_at = utc_now()
        return AggregatePacket(
            node_id=self.node_id,
            position=self.position,
            timestamp=utc_now(),
            uptime_s=self.uptime_s,
            zones=zones,
            freshness=self._freshness(),
            scanner_kind=self.scanner.kind,
            scanner_status=self.scanner.status,
        )

    async def run(self) -> None:
        """Tick loop until cancelled."""
        if self._start_mono is None:
            self._start_mono = time.monotonic()
        logger.info("mesh node %s starting; interval=%.2fs", self.node_id, self.interval_s)
        try:
            while True:
                packet = self.build_packet()
                ok = await self.client.post(packet)
                if not ok:
                    logger.debug("post failed for node %s — see transport log", self.node_id)
                await asyncio.sleep(self.interval_s)
        except asyncio.CancelledError:
            logger.info("mesh node %s stopping", self.node_id)
            raise


__all__ = ["MeshNode", "MockNodeScanner", "Scanner"]
