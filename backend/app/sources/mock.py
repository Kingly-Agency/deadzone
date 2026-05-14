"""Deterministic mock source — seeded synthetic crowd pressure loop."""

from __future__ import annotations

import math
import random
from datetime import datetime, timezone

from app.models import (
    Alert,
    AlertKind,
    AlertStatus,
    FlowVector,
    Freshness,
    IntelligenceSnapshot,
    MeshLink,
    Mode,
    Point,
    SensorKind,
    SensorNode,
    SensorStatus,
    Severity,
    SnapshotMetrics,
    StreamClock,
    StreamState,
    Trend,
    ZoneAggregate,
)
from app.sources import SensorSource
from app.venue import (
    MESH_LINK_DEFS,
    SENSOR_DEFS,
    VENUE,
    ZONE_ADJACENCY,
    ZONE_CAPACITIES,
)

_SEED = 42
_ALERT_FIRE_TIME = 90.0  # seconds into demo


class MockSource(SensorSource):
    """Deterministic mock generator with seeded RNG and timed alert."""

    def __init__(self) -> None:
        self._rng = random.Random(_SEED)
        self._elapsed = 0.0
        self._alert_fired = False
        self._alerts: list[Alert] = []
        self._sequence = 0

    async def reset(self) -> None:
        self._rng = random.Random(_SEED)
        self._elapsed = 0.0
        self._alert_fired = False
        self._alerts = []
        self._sequence = 0

    @property
    def source_label(self) -> str:
        return "Mock — simulated data"

    async def tick(self, elapsed_s: float) -> IntelligenceSnapshot:
        self._elapsed += elapsed_s
        self._sequence += 1
        t = self._elapsed
        now = datetime.now(timezone.utc)

        # ── Zone densities (deterministic sine curves + noise) ──────────
        zone_aggs: list[ZoneAggregate] = []
        for zone_def in VENUE.zones:
            zid = zone_def.id
            cap = ZONE_CAPACITIES[zid]
            base = self._zone_base(zid, t)
            noise = self._rng.gauss(0, 0.03)
            density = max(0.0, min(1.0, base + noise))
            count = int(density * cap)
            pressure = min(1.0, density * 1.15) if density > 0.6 else density * 0.5
            trend = self._compute_trend(zid, t)
            confidence = 0.85 + self._rng.uniform(0, 0.15)

            zone_aggs.append(
                ZoneAggregate(
                    zone_id=zid,
                    density=round(density, 3),
                    pressure_score=round(pressure, 3),
                    trend=trend,
                    confidence=round(confidence, 3),
                    estimated_devices=count,
                    capacity=cap,
                    updated_at=now,
                )
            )

        # ── Flow vectors ────────────────────────────────────────────────
        flow_vectors: list[FlowVector] = []
        zone_density = {z.zone_id: z.density for z in zone_aggs}
        for i, (fz, tz, direction) in enumerate(ZONE_ADJACENCY):
            diff = zone_density.get(fz, 0) - zone_density.get(tz, 0)
            mag = min(1.0, abs(diff) * 2 + self._rng.uniform(0, 0.1))
            actual_dir = direction if diff > 0 else (direction + 180) % 360
            flow_vectors.append(
                FlowVector(
                    id=f"flow-{i}",
                    from_zone=fz if diff > 0 else tz,
                    to_zone=tz if diff > 0 else fz,
                    direction_deg=actual_dir,
                    magnitude=round(mag, 3),
                    confidence=round(0.7 + self._rng.uniform(0, 0.3), 3),
                )
            )

        # ── Sensors ─────────────────────────────────────────────────────
        sensors: list[SensorNode] = []
        for sd in SENSOR_DEFS:
            # S4 and S7 are degraded in mock
            if sd["id"] == "s4":
                status = SensorStatus.degraded
            elif sd["id"] == "s7":
                status = SensorStatus.degraded if t > 30 else SensorStatus.online
            else:
                status = SensorStatus.online

            latency = self._rng.uniform(5, 50) if status == SensorStatus.online else self._rng.uniform(80, 200)
            battery = sd["battery"]
            if battery is not None:
                # Slowly drain battery
                battery = max(0.0, battery - (t / 36000))

            sensors.append(
                SensorNode(
                    id=sd["id"],
                    label=sd["label"],
                    kind=SensorKind(sd["kind"]),
                    status=status,
                    zone_id=sd["zone_id"],
                    position=Point(**sd["position"]),
                    battery=round(battery, 3) if battery is not None else None,
                    latency_ms=round(latency, 1),
                    last_seen=now,
                )
            )

        # ── Alerts ──────────────────────────────────────────────────────
        self._update_alerts(t, now, zone_aggs)

        # ── Mesh links ──────────────────────────────────────────────────
        mesh_links: list[MeshLink] = []
        for ml in MESH_LINK_DEFS:
            mesh_links.append(
                MeshLink(
                    from_node=ml["from_node"],
                    to_node=ml["to_node"],
                    quality=round(ml["quality"] + self._rng.uniform(-0.05, 0.05), 3),
                    latency_ms=round(ml["latency_ms"] + self._rng.uniform(-10, 10), 1),
                    last_packet_at=now,
                )
            )

        # ── Metrics ─────────────────────────────────────────────────────
        total_devices = sum(z.estimated_devices for z in zone_aggs)
        hot_zones = sum(1 for z in zone_aggs if z.density > 0.75)
        active_alerts = sum(1 for a in self._alerts if a.status == AlertStatus.active)
        offline_sensors = sum(1 for s in sensors if s.status == SensorStatus.offline)

        metrics = SnapshotMetrics(
            estimated_devices=total_devices,
            hot_zones=hot_zones,
            active_alerts=active_alerts,
            offline_sensors=offline_sensors,
        )

        stream = StreamState(
            mode=Mode.mock,
            connected=True,
            sequence=self._sequence,
            source_label=self.source_label,
            freshness=Freshness.live,
            clock=StreamClock(timestamp=now, replay_position_s=0, speed=1.0),
        )

        return IntelligenceSnapshot(
            stream=stream,
            venue=VENUE,
            zones=zone_aggs,
            flow_vectors=flow_vectors,
            alerts=list(self._alerts),
            sensors=sensors,
            mesh_links=mesh_links,
            metrics=metrics,
        )

    def _zone_base(self, zone_id: str, t: float) -> float:
        """Deterministic density curve per zone."""
        profiles = {
            "hall-a": lambda: 0.55 + 0.2 * math.sin(t / 30) + 0.1 * math.sin(t / 7),
            "hall-b": lambda: 0.65 + 0.2 * math.sin(t / 25 + 1) + 0.1 * math.cos(t / 11),
            "main-lobby": lambda: 0.4 + 0.15 * math.sin(t / 20 + 2) + 0.05 * math.sin(t / 5),
            "foodcourt": lambda: 0.3 + 0.25 * math.sin(t / 35 + 3),
            "registration": lambda: 0.5 + 0.15 * math.sin(t / 15 + 4) - 0.05 * math.cos(t / 8),
            "loading-dock": lambda: 0.15 + 0.1 * math.sin(t / 40 + 5),
        }
        fn = profiles.get(zone_id, lambda: 0.3)
        return max(0.0, min(1.0, fn()))

    def _compute_trend(self, zone_id: str, t: float) -> Trend:
        """Compute 5-minute trend by comparing current vs slightly earlier density."""
        now_density = self._zone_base(zone_id, t)
        prev_density = self._zone_base(zone_id, max(0, t - 5))
        diff = now_density - prev_density
        if diff > 0.1:
            return Trend.spiking
        elif diff > 0.02:
            return Trend.rising
        elif diff < -0.02:
            return Trend.falling
        return Trend.stable

    def _update_alerts(
        self, t: float, now: datetime, zones: list[ZoneAggregate]
    ) -> None:
        """Fire deterministic alert at 90s and threshold-based alerts."""
        # Timed critical alert at 90s
        if t >= _ALERT_FIRE_TIME and not self._alert_fired:
            self._alert_fired = True
            self._alerts.append(
                Alert(
                    id="alert-demo-critical",
                    kind=AlertKind.congestion,
                    zone_id="hall-b",
                    severity=Severity.critical,
                    message="Hall B congestion — 85% capacity threshold exceeded",
                    status=AlertStatus.active,
                    started_at=now,
                    supporting_sensor_ids=["s3", "s4"],
                )
            )

        # Dynamic threshold alerts
        for z in zones:
            alert_id = f"alert-threshold-{z.zone_id}"
            existing = next((a for a in self._alerts if a.id == alert_id), None)

            if z.density > 0.8 and existing is None:
                self._alerts.append(
                    Alert(
                        id=alert_id,
                        kind=AlertKind.queue_buildup,
                        zone_id=z.zone_id,
                        severity=Severity.warning,
                        message=f"{self._zone_name(z.zone_id)} at {int(z.density * 100)}% capacity",
                        status=AlertStatus.active,
                        started_at=now,
                    )
                )
            elif z.density <= 0.7 and existing is not None and existing.status == AlertStatus.active:
                existing.status = AlertStatus.resolved
                existing.duration_s = t

    @staticmethod
    def _zone_name(zone_id: str) -> str:
        for z in VENUE.zones:
            if z.id == zone_id:
                return z.name
        return zone_id
