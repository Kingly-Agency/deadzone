from __future__ import annotations

from app.domain.models import Point, Venue, Zone

ZONE_CAPACITY = {
    "near-scanner": 12,
    "mid-field": 20,
    "far-field": 24,
    "edge-unknown": 16,
}

ZONE_CENTROIDS = {
    "near-scanner": Point(x=24, y=38),
    "mid-field": Point(x=50, y=38),
    "far-field": Point(x=76, y=38),
    "edge-unknown": Point(x=50, y=74),
}


def demo_venue() -> Venue:
    return Venue(
        id="ble-capture-floor",
        name="Local BLE Capture Field",
        map_version="ble-rssi-zones-v1",
        bounds={"width": 100, "height": 100},
        zones=[
            Zone(
                id="near-scanner",
                name="Near Scanner",
                polygon=[
                    Point(x=8, y=18),
                    Point(x=40, y=18),
                    Point(x=40, y=58),
                    Point(x=8, y=58),
                ],
            ),
            Zone(
                id="mid-field",
                name="Mid Field",
                polygon=[
                    Point(x=40, y=18),
                    Point(x=62, y=18),
                    Point(x=62, y=58),
                    Point(x=40, y=58),
                ],
            ),
            Zone(
                id="far-field",
                name="Far Field",
                polygon=[
                    Point(x=62, y=18),
                    Point(x=94, y=18),
                    Point(x=94, y=58),
                    Point(x=62, y=58),
                ],
            ),
            Zone(
                id="edge-unknown",
                name="Weak / Edge Signal",
                polygon=[
                    Point(x=8, y=58),
                    Point(x=94, y=58),
                    Point(x=94, y=92),
                    Point(x=8, y=92),
                ],
            ),
        ],
    )


def zone_for_rssi(rssi: int) -> str:
    if rssi >= -60:
        return "near-scanner"
    if rssi >= -75:
        return "mid-field"
    if rssi >= -88:
        return "far-field"
    return "edge-unknown"
