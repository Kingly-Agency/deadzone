"""Replay source — procedural scenario generation with playback controls."""

from __future__ import annotations

import math
import random
from datetime import datetime, timezone
from typing import Optional

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
    ReplayScenario,
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

# ── Bundled Scenarios ────────────────────────────────────────────────────────

SCENARIOS: list[ReplayScenario] = [
    ReplayScenario(
        id="convention-crowd",
        name="Convention Morning Rush",
        description="General traffic grows around food court and main hall as attendees arrive for the opening keynote.",
        duration_s=300,
        seed="convention-2026",
    ),
    ReplayScenario(
        id="concert-exit-rush",
        name="Concert Exit Rush",
        description="Large movement wave flows toward exits after a main-stage performance ends.",
        duration_s=210,
        seed="concert-exit-2026",
    ),
    ReplayScenario(
        id="hallway-stall",
        name="Hallway Congestion",
        description="Movement drops while pressure rises in the main lobby corridor during a session break.",
        duration_s=255,
        seed="hallway-stall-2026",
    ),
    ReplayScenario(
        id="stadium-ingress",
        name="Stadium Ingress",
        description="Rapid fan entry through registration and lobby to halls for a major event opening.",
        duration_s=360,
        seed="stadium-ingress-2026",
    ),
]


class ReplaySource(SensorSource):
    """Procedural replay source with playback controls."""

    def __init__(self) -> None:
        self._scenario: Optional[ReplayScenario] = None
        self._position_s: float = 0.0
        self._speed: float = 1.0
        self._playing: bool = False
        self._rng = random.Random(0)
        self._sequence = 0
        self._alerts: list[Alert] = []

    async def reset(self) -> None:
        self._position_s = 0.0
        self._playing = False
        self._alerts = []
        self._sequence = 0
        if self._scenario:
            self._rng = random.Random(self._scenario.seed)

    @property
    def source_label(self) -> str:
        if self._scenario:
            return f"Replay: {self._scenario.name}"
        return "Replay — no scenario loaded"

    @property
    def scenario(self) -> Optional[ReplayScenario]:
        return self._scenario

    @property
    def position_s(self) -> float:
        return self._position_s

    @property
    def speed(self) -> float:
        return self._speed

    @property
    def playing(self) -> bool:
        return self._playing

    def load(self, scenario_id: str) -> ReplayScenario:
        sc = next((s for s in SCENARIOS if s.id == scenario_id), None)
        if sc is None:
            raise ValueError(f"Unknown scenario: {scenario_id}")
        self._scenario = sc
        self._rng = random.Random(sc.seed)
        self._position_s = 0.0
        self._playing = False
        self._alerts = []
        return sc

    def play(self) -> None:
        self._playing = True

    def pause(self) -> None:
        self._playing = False

    def restart(self) -> None:
        self._position_s = 0.0
        self._playing = True
        self._alerts = []
        if self._scenario:
            self._rng = random.Random(self._scenario.seed)

    def seek(self, position_s: float) -> None:
        if self._scenario:
            self._position_s = max(0, min(position_s, self._scenario.duration_s))

    def set_speed(self, speed: float) -> None:
        self._speed = max(0.25, min(4.0, speed))

    async def tick(self, elapsed_s: float) -> IntelligenceSnapshot:
        self._sequence += 1
        now = datetime.now(timezone.utc)

        if self._scenario is None:
            # Return empty snapshot
            return self._empty_snapshot(now)

        # Advance position if playing
        if self._playing:
            self._position_s += elapsed_s * self._speed
            if self._position_s >= self._scenario.duration_s:
                self._position_s = self._scenario.duration_s
                self._playing = False

        t = self._position_s
        sc = self._scenario
        progress = t / sc.duration_s if sc.duration_s > 0 else 0

        # Generate zone data based on scenario profile
        zone_aggs = self._gen_zones(t, progress, now)
        flow_vectors = self._gen_flows(zone_aggs)
        sensors = self._gen_sensors(now)
        self._gen_alerts(t, progress, now, zone_aggs)

        mesh_links = [
            MeshLink(
                from_node=ml["from_node"],
                to_node=ml["to_node"],
                quality=round(ml["quality"] + self._rng.uniform(-0.05, 0.05), 3),
                latency_ms=round(ml["latency_ms"] + self._rng.uniform(-10, 10), 1),
                last_packet_at=now,
            )
            for ml in MESH_LINK_DEFS
        ]

        total_devices = sum(z.estimated_devices for z in zone_aggs)
        metrics = SnapshotMetrics(
            estimated_devices=total_devices,
            hot_zones=sum(1 for z in zone_aggs if z.density > 0.75),
            active_alerts=sum(1 for a in self._alerts if a.status == AlertStatus.active),
            offline_sensors=sum(1 for s in sensors if s.status == SensorStatus.offline),
        )

        stream = StreamState(
            mode=Mode.replay,
            connected=True,
            sequence=self._sequence,
            source_label=self.source_label,
            freshness=Freshness.live,
            clock=StreamClock(timestamp=now, replay_position_s=t, speed=self._speed),
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

    def _gen_zones(
        self, t: float, progress: float, now: datetime
    ) -> list[ZoneAggregate]:
        """Generate zone data based on scenario-specific profiles."""
        sc_id = self._scenario.id if self._scenario else "convention-crowd"
        zones: list[ZoneAggregate] = []

        for zone_def in VENUE.zones:
            zid = zone_def.id
            cap = ZONE_CAPACITIES[zid]
            density = self._scenario_density(sc_id, zid, t, progress)
            noise = self._rng.gauss(0, 0.02)
            density = max(0.0, min(1.0, density + noise))
            count = int(density * cap)
            pressure = min(1.0, density * 1.2) if density > 0.6 else density * 0.4

            # Trend
            prev = self._scenario_density(sc_id, zid, max(0, t - 5), max(0, progress - 0.02))
            diff = density - prev
            if diff > 0.08:
                trend = Trend.spiking
            elif diff > 0.02:
                trend = Trend.rising
            elif diff < -0.02:
                trend = Trend.falling
            else:
                trend = Trend.stable

            zones.append(
                ZoneAggregate(
                    zone_id=zid,
                    density=round(density, 3),
                    pressure_score=round(pressure, 3),
                    trend=trend,
                    confidence=round(0.8 + self._rng.uniform(0, 0.2), 3),
                    estimated_devices=count,
                    capacity=cap,
                    updated_at=now,
                )
            )
        return zones

    def _scenario_density(
        self, sc_id: str, zone_id: str, t: float, progress: float
    ) -> float:
        """Per-scenario, per-zone density curves."""
        if sc_id == "convention-crowd":
            # Gradual fill-up, food court peaks mid-way
            profiles = {
                "hall-a": 0.3 + 0.5 * progress + 0.1 * math.sin(t / 20),
                "hall-b": 0.2 + 0.6 * progress + 0.1 * math.sin(t / 15),
                "main-lobby": 0.5 + 0.2 * math.sin(t / 10) - 0.2 * progress,
                "foodcourt": 0.2 + 0.6 * math.sin(math.pi * progress),
                "registration": 0.7 - 0.5 * progress,
                "loading-dock": 0.1 + 0.05 * math.sin(t / 30),
            }
        elif sc_id == "concert-exit-rush":
            # Halls drain, lobby floods, then exits
            profiles = {
                "hall-a": 0.9 - 0.7 * progress,
                "hall-b": 0.95 - 0.8 * progress,
                "main-lobby": 0.3 + 0.6 * math.sin(math.pi * progress),
                "foodcourt": 0.2 + 0.3 * math.sin(math.pi * progress * 0.5),
                "registration": 0.1 + 0.7 * progress,
                "loading-dock": 0.1 + 0.5 * max(0, progress - 0.5),
            }
        elif sc_id == "hallway-stall":
            # Lobby stalls, pressure builds
            profiles = {
                "hall-a": 0.5 + 0.1 * math.sin(t / 20),
                "hall-b": 0.5 + 0.1 * math.cos(t / 20),
                "main-lobby": 0.4 + 0.5 * progress + 0.05 * math.sin(t / 5),
                "foodcourt": 0.3 + 0.1 * math.sin(t / 15),
                "registration": 0.6 - 0.2 * progress,
                "loading-dock": 0.1 + 0.05 * progress,
            }
        elif sc_id == "stadium-ingress":
            # Massive inflow from registration through lobby to halls
            wave = min(1.0, progress * 2)
            profiles = {
                "hall-a": 0.1 + 0.7 * max(0, wave - 0.3),
                "hall-b": 0.1 + 0.8 * max(0, wave - 0.4),
                "main-lobby": 0.2 + 0.7 * math.sin(math.pi * wave),
                "foodcourt": 0.1 + 0.3 * max(0, wave - 0.6),
                "registration": 0.8 * max(0, 1 - wave * 1.5),
                "loading-dock": 0.05 + 0.1 * wave,
            }
        else:
            profiles = {zid: 0.3 for zid in ZONE_CAPACITIES}

        return max(0.0, min(1.0, profiles.get(zone_id, 0.3)))

    def _gen_flows(self, zones: list[ZoneAggregate]) -> list[FlowVector]:
        density_map = {z.zone_id: z.density for z in zones}
        flows = []
        for i, (fz, tz, direction) in enumerate(ZONE_ADJACENCY):
            diff = density_map.get(fz, 0) - density_map.get(tz, 0)
            mag = min(1.0, abs(diff) * 2.5 + self._rng.uniform(0, 0.05))
            actual_dir = direction if diff > 0 else (direction + 180) % 360
            flows.append(
                FlowVector(
                    id=f"flow-{i}",
                    from_zone=fz if diff > 0 else tz,
                    to_zone=tz if diff > 0 else fz,
                    direction_deg=actual_dir,
                    magnitude=round(mag, 3),
                    confidence=round(0.7 + self._rng.uniform(0, 0.3), 3),
                )
            )
        return flows

    def _gen_sensors(self, now: datetime) -> list[SensorNode]:
        sensors = []
        for sd in SENSOR_DEFS:
            sensors.append(
                SensorNode(
                    id=sd["id"],
                    label=sd["label"],
                    kind=SensorKind(sd["kind"]),
                    status=SensorStatus.online,
                    zone_id=sd["zone_id"],
                    position=Point(**sd["position"]),
                    battery=sd["battery"],
                    latency_ms=round(self._rng.uniform(5, 40), 1),
                    last_seen=now,
                )
            )
        return sensors

    def _gen_alerts(
        self,
        t: float,
        progress: float,
        now: datetime,
        zones: list[ZoneAggregate],
    ) -> None:
        """Generate scenario-specific alerts."""
        sc_id = self._scenario.id if self._scenario else ""

        # Threshold-based alerts
        for z in zones:
            aid = f"replay-alert-{z.zone_id}"
            existing = next((a for a in self._alerts if a.id == aid), None)
            if z.density > 0.85 and existing is None:
                kind = AlertKind.congestion
                if sc_id == "convention-crowd":
                    kind = AlertKind.queue_buildup
                elif sc_id == "hallway-stall" and z.zone_id == "main-lobby":
                    kind = AlertKind.hallway_stall
                zone_name = next(
                    (zd.name for zd in VENUE.zones if zd.id == z.zone_id), z.zone_id
                )
                self._alerts.append(
                    Alert(
                        id=aid,
                        kind=kind,
                        zone_id=z.zone_id,
                        severity=Severity.warning if z.density < 0.92 else Severity.critical,
                        message=f"{zone_name} at {int(z.density * 100)}% capacity",
                        status=AlertStatus.active,
                        started_at=now,
                    )
                )
            elif z.density <= 0.7 and existing and existing.status == AlertStatus.active:
                existing.status = AlertStatus.resolved

    def _empty_snapshot(self, now: datetime) -> IntelligenceSnapshot:
        stream = StreamState(
            mode=Mode.replay,
            connected=True,
            sequence=self._sequence,
            source_label=self.source_label,
            freshness=Freshness.live,
            clock=StreamClock(timestamp=now, replay_position_s=0, speed=1.0),
        )
        return IntelligenceSnapshot(
            stream=stream,
            venue=VENUE,
            zones=[],
            flow_vectors=[],
            alerts=[],
            sensors=[],
            mesh_links=[],
            metrics=SnapshotMetrics(
                estimated_devices=0, hot_zones=0, active_alerts=0, offline_sensors=0
            ),
        )

