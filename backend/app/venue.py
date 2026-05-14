"""Static venue definition — convention center with 6 zones and 8 sensors."""

from __future__ import annotations

from .models import Point, Venue, VenueBounds, Zone

# Coordinate space: 1000 x 700 (arbitrary units, mapped to Leaflet CRS.Simple)

VENUE = Venue(
    id="demo-venue",
    name="Metro Convention Center",
    map_version="1.0.0",
    bounds=VenueBounds(width=1000, height=700),
    zones=[
        Zone(
            id="hall-a",
            name="Hall A",
            polygon=[
                Point(x=50, y=50),
                Point(x=350, y=50),
                Point(x=350, y=300),
                Point(x=50, y=300),
            ],
        ),
        Zone(
            id="hall-b",
            name="Hall B",
            polygon=[
                Point(x=400, y=50),
                Point(x=700, y=50),
                Point(x=700, y=300),
                Point(x=400, y=300),
            ],
        ),
        Zone(
            id="main-lobby",
            name="Main Lobby",
            polygon=[
                Point(x=50, y=320),
                Point(x=450, y=320),
                Point(x=450, y=480),
                Point(x=50, y=480),
            ],
        ),
        Zone(
            id="foodcourt",
            name="Food Court",
            polygon=[
                Point(x=500, y=320),
                Point(x=750, y=320),
                Point(x=750, y=480),
                Point(x=500, y=480),
            ],
        ),
        Zone(
            id="registration",
            name="Registration",
            polygon=[
                Point(x=50, y=500),
                Point(x=350, y=500),
                Point(x=350, y=650),
                Point(x=50, y=650),
            ],
        ),
        Zone(
            id="loading-dock",
            name="Loading Dock",
            polygon=[
                Point(x=400, y=500),
                Point(x=700, y=500),
                Point(x=700, y=650),
                Point(x=400, y=650),
            ],
        ),
    ],
)

# Zone capacities (max devices)
ZONE_CAPACITIES: dict[str, int] = {
    "hall-a": 600,
    "hall-b": 800,
    "main-lobby": 500,
    "foodcourt": 400,
    "registration": 300,
    "loading-dock": 150,
}

# Sensor positions and metadata
SENSOR_DEFS: list[dict] = [
    {"id": "s1", "label": "S1 — Hall A NW", "kind": "ble", "zone_id": "hall-a",
     "position": {"x": 100, "y": 100}, "battery": 0.82},
    {"id": "s2", "label": "S2 — Hall A SE", "kind": "wifi", "zone_id": "hall-a",
     "position": {"x": 300, "y": 250}, "battery": None},
    {"id": "s3", "label": "S3 — Hall B NW", "kind": "ble", "zone_id": "hall-b",
     "position": {"x": 450, "y": 100}, "battery": 0.67},
    {"id": "s4", "label": "S4 — Hall B SE", "kind": "ble", "zone_id": "hall-b",
     "position": {"x": 650, "y": 250}, "battery": 0.23},
    {"id": "s5", "label": "S5 — Lobby Center", "kind": "mesh_node", "zone_id": "main-lobby",
     "position": {"x": 250, "y": 400}, "battery": 0.91},
    {"id": "s6", "label": "S6 — Food Court", "kind": "wifi", "zone_id": "foodcourt",
     "position": {"x": 625, "y": 400}, "battery": None},
    {"id": "s7", "label": "S7 — Registration", "kind": "ble", "zone_id": "registration",
     "position": {"x": 200, "y": 575}, "battery": 0.11},
    {"id": "s8", "label": "S8 — Loading Dock", "kind": "ble", "zone_id": "loading-dock",
     "position": {"x": 550, "y": 575}, "battery": 0.55},
]

# Adjacency graph for flow vectors (bidirectional pairs)
ZONE_ADJACENCY: list[tuple[str, str, float]] = [
    # (from_zone, to_zone, direction_deg)
    ("hall-a", "hall-b", 90),       # Hall A → Hall B (east)
    ("hall-a", "main-lobby", 180),  # Hall A → Lobby (south)
    ("hall-b", "foodcourt", 180),   # Hall B → Food Court (south)
    ("main-lobby", "foodcourt", 90),  # Lobby → Food Court (east)
    ("main-lobby", "registration", 180),  # Lobby → Registration (south)
    ("foodcourt", "loading-dock", 180),   # Food Court → Loading Dock (south)
    ("registration", "loading-dock", 90),  # Registration → Loading Dock (east)
]

# Mesh links (simulated)
MESH_LINK_DEFS: list[dict] = [
    {"from_node": "s5", "to_node": "s1", "quality": 0.85, "latency_ms": 45},
    {"from_node": "s5", "to_node": "s3", "quality": 0.72, "latency_ms": 62},
    {"from_node": "s5", "to_node": "s7", "quality": 0.91, "latency_ms": 38},
    {"from_node": "s5", "to_node": "s8", "quality": 0.68, "latency_ms": 78},
]
