from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from app.domain.models import FlowVector, SensorNode, SnapshotMetrics, ZoneAggregate
from app.sources.base import BleObservation
from app.spatial.venue import ZONE_CAPACITY, ZONE_CENTROIDS, demo_venue


def aggregate_zones(observations: list[BleObservation], now: datetime | None = None) -> list[ZoneAggregate]:
    current_time = now or datetime.now(timezone.utc)
    latest_by_device: dict[str, BleObservation] = {}
    for observation in observations:
        current = latest_by_device.get(observation.beacon_hash)
        if current is None or observation.timestamp > current.timestamp:
            latest_by_device[observation.beacon_hash] = observation

    devices_by_zone: dict[str, set[str]] = defaultdict(set)
    rssi_by_zone: dict[str, list[int]] = defaultdict(list)
    for observation in latest_by_device.values():
        devices_by_zone[observation.zone_id].add(observation.beacon_hash)
        rssi_by_zone[observation.zone_id].append(observation.rssi)

    aggregates: list[ZoneAggregate] = []
    for zone in demo_venue().zones:
        count = len(devices_by_zone[zone.id])
        capacity = ZONE_CAPACITY[zone.id]
        density = min(1.0, count / capacity)
        avg_rssi = sum(rssi_by_zone[zone.id]) / len(rssi_by_zone[zone.id]) if rssi_by_zone[zone.id] else -100
        signal_pressure = max(0.0, min(1.0, (avg_rssi + 95) / 45))
        pressure = min(1.0, density * 0.75 + signal_pressure * 0.25)
        if pressure >= 0.85:
            trend = "spiking"
        elif pressure >= 0.55:
            trend = "rising"
        elif count == 0:
            trend = "falling"
        else:
            trend = "stable"
        aggregates.append(
            ZoneAggregate(
                zone_id=zone.id,
                density=round(density, 3),
                pressure_score=round(pressure, 3),
                trend=trend,
                confidence=0.9 if count else 0.35,
                capacity=capacity,
                estimated_devices=count,
                updated_at=current_time,
            )
        )
    return aggregates


def flow_vectors(observations: list[BleObservation]) -> list[FlowVector]:
    by_device: dict[str, list[BleObservation]] = defaultdict(list)
    for observation in observations:
        by_device[observation.beacon_hash].append(observation)

    transitions: dict[tuple[str, str], int] = defaultdict(int)
    for items in by_device.values():
        ordered = sorted(items, key=lambda item: item.timestamp)
        for previous, current in zip(ordered, ordered[1:]):
            if previous.zone_id != current.zone_id:
                transitions[(previous.zone_id, current.zone_id)] += 1

    if not transitions:
        return []

    max_count = max(transitions.values())
    vectors: list[FlowVector] = []
    for (from_zone, to_zone), count in sorted(transitions.items()):
        start = ZONE_CENTROIDS[from_zone]
        end = ZONE_CENTROIDS[to_zone]
        direction = _direction_degrees(start.x, start.y, end.x, end.y)
        vectors.append(
            FlowVector(
                id=f"{from_zone}-to-{to_zone}",
                from_zone=from_zone,
                to_zone=to_zone,
                direction_deg=direction,
                magnitude=round(count / max_count, 3),
                confidence=0.8,
            )
        )
    return vectors


def sensor_nodes(observations: list[BleObservation], now: datetime | None = None) -> list[SensorNode]:
    current_time = now or datetime.now(timezone.utc)
    latest = max((item.timestamp for item in observations), default=None)
    if latest is None:
        status = "offline"
        last_seen = current_time
    else:
        age = (current_time - latest).total_seconds()
        status = "online" if age <= 30 else "degraded" if age <= 60 else "offline"
        last_seen = latest
    return [
        SensorNode(
            id="local-ble-scanner",
            label="Local BLE Scanner",
            kind="ble",
            status=status,
            zone_id="near-scanner",
            position=ZONE_CENTROIDS["near-scanner"],
            latency_ms=120 if status == "online" else None,
            last_seen=last_seen,
        )
    ]


def snapshot_metrics(zones: list[ZoneAggregate], sensors: list[SensorNode], active_alerts: int) -> SnapshotMetrics:
    return SnapshotMetrics(
        estimated_devices=sum(zone.estimated_devices for zone in zones),
        hot_zones=sum(1 for zone in zones if zone.pressure_score >= 0.65),
        active_alerts=active_alerts,
        offline_sensors=sum(1 for sensor in sensors if sensor.status == "offline"),
    )


def _direction_degrees(x1: float, y1: float, x2: float, y2: float) -> float:
    import math

    return round((math.degrees(math.atan2(y2 - y1, x2 - x1)) + 360) % 360, 1)
