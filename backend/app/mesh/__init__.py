"""DeadZone WiFi-faked mesh: standalone satellite service on port 8001.

Two or more laptops each run ``python -m app.mesh node``; one runs
``python -m app.mesh gateway``. Nodes POST zone-aggregate packets at 1Hz.
Aggregate-only across the wire — raw hashes and trace files stay local.
"""

from app.mesh.models import (
    AggregateAccepted,
    AggregatePacket,
    GatewayHealth,
    MergedZone,
    MeshLink,
    MeshSnapshot,
    NodeState,
    Position,
    ZoneAggregate,
)
from app.mesh.transport import AggregateClient, TransportError, build_gateway_url

__version__ = "0.1.0"

__all__ = [
    "AggregateAccepted",
    "AggregateClient",
    "AggregatePacket",
    "GatewayHealth",
    "MergedZone",
    "MeshLink",
    "MeshSnapshot",
    "NodeState",
    "Position",
    "TransportError",
    "ZoneAggregate",
    "build_gateway_url",
]
