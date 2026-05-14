"""Pydantic v2 models for the DeadZone mesh wire protocol and internal state.

These types define the aggregate-only packets exchanged between mesh nodes
and the gateway, plus the gateway's internal bookkeeping structures.
No raw device identifiers ever appear on the wire.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

Trend = Literal["falling", "stable", "rising", "spiking"]
Freshness = Literal["live", "fresh", "stale", "offline"]
ScannerKind = Literal["ble", "wifi"]
ScannerStatus = Literal["online", "degraded", "offline", "adapter_disabled"]
NodeStatus = Literal["live", "stale", "offline"]

SCHEMA_AGGREGATE_V1 = "deadzone.mesh.aggregate.v1"


def utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


class Position(BaseModel):
    """2-D position of a node within the venue coordinate system."""

    x: float
    y: float


class ZoneAggregate(BaseModel):
    """Zone-level aggregate from ONE node.

    Never carries device identifiers — only counts and derived metrics.
    """

    zone_id: str
    estimated_devices: int = Field(ge=0)
    density: float = Field(ge=0.0, le=1.0)
    trend: Trend = "stable"
    confidence: float = Field(ge=0.0, le=1.0, default=0.35)


class AggregatePacket(BaseModel):
    """Wire packet: one node's view at one tick.

    POSTed to ``/mesh/aggregate`` by every node at ~1 Hz.
    The ``schema`` alias keeps the JSON key short while ``schema_id``
    avoids shadowing Python builtins in application code.
    """

    schema_id: str = Field(default=SCHEMA_AGGREGATE_V1, alias="schema")
    node_id: str
    position: Position | None = None
    timestamp: datetime
    uptime_s: float = Field(ge=0.0)
    zones: list[ZoneAggregate]
    freshness: Freshness = "live"
    scanner_kind: ScannerKind = "ble"
    scanner_status: ScannerStatus = "online"

    model_config = {"populate_by_name": True}


class NodeState(BaseModel):
    """Gateway's internal view of a single mesh node."""

    node_id: str
    status: NodeStatus
    position: Position | None = None
    last_seen: datetime
    latency_ms: float | None = None
    packets_received: int = 0
    scanner_kind: ScannerKind = "ble"
    scanner_status: ScannerStatus = "online"
    last_freshness: Freshness = "live"


class MergedZone(BaseModel):
    """Zone aggregated across multiple nodes.

    ``contributing_nodes`` lists every node whose most recent packet
    contained data for this zone.
    """

    zone_id: str
    estimated_devices: int
    density: float
    trend: Trend
    confidence: float
    contributing_nodes: list[str]


class MeshLink(BaseModel):
    """An inferred connection between two nodes.

    Created when both nodes report the same zone(s) within a recent time window.
    ``shared_zones`` is the list of zone_ids both nodes contributed to.
    """

    source_node: str
    target_node: str
    shared_zones: list[str]
    inferred_at: datetime


class MeshSnapshot(BaseModel):
    """Full gateway state returned by ``GET /mesh/state``.

    ``metrics`` carries key counters such as *node_count*, *live_count*,
    and *total_estimated_devices*.
    """

    gateway_id: str
    updated_at: datetime
    uptime_s: float
    nodes: list[NodeState]
    zones_merged: list[MergedZone]
    mesh_links: list[MeshLink]
    metrics: dict[str, int | float]


class GatewayHealth(BaseModel):
    """Lightweight health-check response for ``GET /mesh/healthz``."""

    ok: bool = True
    gateway_id: str
    uptime_s: float
    node_count: int


class AggregateAccepted(BaseModel):
    """Acknowledgement returned after a successful aggregate POST."""

    accepted: bool = True
    last_seq: int
    node_id: str
    received_at: datetime


# ---------------------------------------------------------------------------
# UI-driven mesh lifecycle (Batch B addition)
# ---------------------------------------------------------------------------

MeshRole = Literal["idle", "hosting", "joined", "hosting_and_joined"]


class HostRequest(BaseModel):
    """Request body for POST /mesh/host."""

    gateway_id: str | None = None
    beacon: bool = True


class JoinRequest(BaseModel):
    """Request body for POST /mesh/join."""

    gateway_url: str
    node_id: str | None = None
    position: tuple[float, float] | None = None
    scanner: Literal["mock"] = "mock"
    seed: int = 1337


class MeRoleResponse(BaseModel):
    """Response from GET /mesh/me — current role of this satellite."""

    role: MeshRole
    hosting: bool
    beacon_active: bool
    joined: bool
    joined_url: str | None = None
    joined_gateway_id: str | None = None
    node_id: str | None = None
    packets_sent: int = 0
    buffered: int = 0
    gateway_id: str
    listening: bool
    discovered_peer_count: int = 0


class DiscoveredGatewayResponse(BaseModel):
    """Response item in GET /mesh/discover."""

    gateway_id: str
    gateway_url: str
    version: str
    last_seen_s_ago: float
    first_seen: datetime
    beacon_count: int
    is_self: bool = False


__all__ = [
    "AggregateAccepted",
    "AggregatePacket",
    "DiscoveredGatewayResponse",
    "Freshness",
    "GatewayHealth",
    "HostRequest",
    "JoinRequest",
    "MeRoleResponse",
    "MergedZone",
    "MeshLink",
    "MeshRole",
    "MeshSnapshot",
    "NodeState",
    "NodeStatus",
    "Position",
    "SCHEMA_AGGREGATE_V1",
    "ScannerKind",
    "ScannerStatus",
    "Trend",
    "ZoneAggregate",
    "utc_now",
]
