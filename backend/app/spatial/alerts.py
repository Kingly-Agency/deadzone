from __future__ import annotations

from datetime import datetime, timezone

from app.domain.models import Alert, SensorNode, ZoneAggregate


def build_alerts(zones: list[ZoneAggregate], sensors: list[SensorNode]) -> list[Alert]:
    now = datetime.now(timezone.utc)
    alerts: list[Alert] = []
    for zone in zones:
        if zone.pressure_score >= 0.85:
            alerts.append(
                Alert(
                    id=f"congestion-{zone.zone_id}",
                    kind="congestion",
                    zone_id=zone.zone_id,
                    severity="critical",
                    message=f"{zone.zone_id} pressure is critical from local BLE observations.",
                    status="active",
                    started_at=now,
                    supporting_sensor_ids=["local-ble-scanner"],
                )
            )
        elif zone.pressure_score >= 0.65:
            alerts.append(
                Alert(
                    id=f"queue-{zone.zone_id}",
                    kind="queue_buildup",
                    zone_id=zone.zone_id,
                    severity="warning",
                    message=f"{zone.zone_id} queue buildup detected from BLE signal density.",
                    status="active",
                    started_at=now,
                    supporting_sensor_ids=["local-ble-scanner"],
                )
            )
    for sensor in sensors:
        if sensor.status == "offline":
            alerts.append(
                Alert(
                    id=f"sensor-offline-{sensor.id}",
                    kind="sensor_offline",
                    zone_id=sensor.zone_id,
                    severity="warning",
                    message=f"{sensor.label} is not receiving BLE advertisements.",
                    status="active",
                    started_at=now,
                    supporting_sensor_ids=[sensor.id],
                )
            )
    return alerts
