from __future__ import annotations

import logging
import time
from collections import Counter, defaultdict
from collections.abc import Callable
from datetime import datetime, timedelta

from app.mesh.models import (
    AggregatePacket,
    GatewayHealth,
    MergedZone,
    MeshLink,
    MeshSnapshot,
    NodeState,
    ZoneAggregate,
    utc_now,
)

logger = logging.getLogger(__name__)

# Tunables (per spec merge_rules)
DEFAULT_STALE_AFTER_S = 3.0
DEFAULT_OFFLINE_AFTER_S = 10.0
DEFAULT_LINK_WINDOW_S = 2.0  # two nodes count as linked if both reported same zone within window

# Trend urgency ranking for tie-breaking (spec: spiking > rising > falling > stable)
_TREND_URGENCY: dict[str, int] = {
    "stable": 0,
    "falling": 1,
    "rising": 2,
    "spiking": 3,
}


class MeshGateway:
    """In-memory aggregator for a fleet of mesh nodes.

    Thread-safety: NOT thread-safe; use a single asyncio event loop or
    add external locking. FastAPI's default async route handlers are
    cooperative and serial per worker, which is sufficient for the MVP.
    """

    def __init__(
        self,
        *,
        gateway_id: str = "mesh-gateway",
        stale_after_s: float = DEFAULT_STALE_AFTER_S,
        offline_after_s: float = DEFAULT_OFFLINE_AFTER_S,
        link_window_s: float = DEFAULT_LINK_WINDOW_S,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self.gateway_id = gateway_id
        self.stale_after_s = stale_after_s
        self.offline_after_s = offline_after_s
        self.link_window_s = link_window_s
        self._clock = clock  # injectable for tests
        self._start_wall = self._clock()
        self._start_mono = time.monotonic()

        # Per-node state
        self._nodes: dict[str, NodeState] = {}
        # Per-node latest aggregate (zone-level only — no raw data)
        self._latest_aggregates: dict[str, list[ZoneAggregate]] = {}
        # Per-node last receive time (for link windowing)
        self._last_received_at: dict[str, datetime] = {}
        self._last_seq: dict[str, int] = {}

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def ingest(self, packet: AggregatePacket, *, received_at: datetime | None = None) -> int:
        """Apply a packet to gateway state. Returns the running sequence number for this node."""
        now = received_at or self._clock()
        latency_ms = max(0.0, (now - packet.timestamp).total_seconds() * 1000.0)
        self._last_seq[packet.node_id] = self._last_seq.get(packet.node_id, 0) + 1
        seq = self._last_seq[packet.node_id]
        prev = self._nodes.get(packet.node_id)
        packets_received = (prev.packets_received if prev else 0) + 1
        self._nodes[packet.node_id] = NodeState(
            node_id=packet.node_id,
            status="live",
            position=packet.position,
            last_seen=now,
            latency_ms=latency_ms,
            packets_received=packets_received,
            scanner_kind=packet.scanner_kind,
            scanner_status=packet.scanner_status,
            last_freshness=packet.freshness,
        )
        self._latest_aggregates[packet.node_id] = list(packet.zones)
        self._last_received_at[packet.node_id] = now
        return seq

    def sweep(self) -> None:
        """Mark stale/offline nodes based on last-seen times."""
        now = self._clock()
        for node_id, state in list(self._nodes.items()):
            age = (now - state.last_seen).total_seconds()
            if age >= self.offline_after_s:
                new_status = "offline"
            elif age >= self.stale_after_s:
                new_status = "stale"
            else:
                new_status = "live"
            if new_status != state.status:
                self._nodes[node_id] = state.model_copy(update={"status": new_status})

    def health(self) -> GatewayHealth:
        return GatewayHealth(
            ok=True,
            gateway_id=self.gateway_id,
            uptime_s=time.monotonic() - self._start_mono,
            node_count=len(self._nodes),
        )

    def snapshot(self) -> MeshSnapshot:
        self.sweep()
        now = self._clock()
        nodes = sorted(self._nodes.values(), key=lambda n: n.node_id)
        merged = self._merge_zones(only_live=True)
        links = self._infer_links(now)
        metrics: dict[str, int | float] = {
            "node_count": len(nodes),
            "live_count": sum(1 for n in nodes if n.status == "live"),
            "stale_count": sum(1 for n in nodes if n.status == "stale"),
            "offline_count": sum(1 for n in nodes if n.status == "offline"),
            "total_estimated_devices": sum(z.estimated_devices for z in merged),
            "merged_zone_count": len(merged),
            "mesh_link_count": len(links),
        }
        return MeshSnapshot(
            gateway_id=self.gateway_id,
            updated_at=now,
            uptime_s=time.monotonic() - self._start_mono,
            nodes=nodes,
            zones_merged=merged,
            mesh_links=links,
            metrics=metrics,
        )

    def nodes(self) -> list[NodeState]:
        self.sweep()
        return sorted(self._nodes.values(), key=lambda n: n.node_id)

    def last_seq(self, node_id: str) -> int:
        return self._last_seq.get(node_id, 0)

    # ------------------------------------------------------------------
    # merge helpers
    # ------------------------------------------------------------------

    def _merge_zones(self, *, only_live: bool = True) -> list[MergedZone]:
        """Combine zone aggregates from every contributing node.

        Per spec merge_rules:
          estimated_devices = SUM (assumes non-overlapping cohorts across nodes)
          density           = MAX
          trend             = majority vote; ties broken by urgency
                              (spiking > rising > falling > stable)
          confidence        = MIN (conservative)
        """
        contributions: dict[str, list[tuple[str, ZoneAggregate]]] = defaultdict(list)
        for node_id, zones in self._latest_aggregates.items():
            state = self._nodes.get(node_id)
            if state is None:
                continue
            if only_live and state.status != "live":
                continue
            for zone in zones:
                contributions[zone.zone_id].append((node_id, zone))

        merged: list[MergedZone] = []
        for zone_id, entries in sorted(contributions.items()):
            estimated = sum(z.estimated_devices for _, z in entries)
            density = max(z.density for _, z in entries)

            # Trend: majority vote with urgency tie-breaking
            trends = Counter(z.trend for _, z in entries)
            top_count = trends.most_common(1)[0][1]
            # All trends tied at top_count — pick the most urgent
            tied = [t for t, c in trends.items() if c == top_count]
            trend = max(tied, key=lambda t: _TREND_URGENCY.get(t, 0))

            confidence = min(z.confidence for _, z in entries)

            merged.append(
                MergedZone(
                    zone_id=zone_id,
                    estimated_devices=estimated,
                    density=density,
                    trend=trend,
                    confidence=confidence,
                    contributing_nodes=sorted({nid for nid, _ in entries}),
                )
            )
        return merged

    def _infer_links(self, now: datetime) -> list[MeshLink]:
        """A pair of nodes is linked if they both reported the same zone(s) recently."""
        window = timedelta(seconds=self.link_window_s)
        # Build per-node recent-zone sets
        recent: dict[str, set[str]] = {}
        for node_id, zones in self._latest_aggregates.items():
            last = self._last_received_at.get(node_id)
            if last is None or (now - last) > window:
                continue
            recent[node_id] = {z.zone_id for z in zones}

        links: list[MeshLink] = []
        node_ids = sorted(recent)
        for i, a in enumerate(node_ids):
            for b in node_ids[i + 1 :]:
                shared = sorted(recent[a] & recent[b])
                if shared:
                    inferred_at = min(self._last_received_at[a], self._last_received_at[b])
                    links.append(
                        MeshLink(
                            source_node=a,
                            target_node=b,
                            shared_zones=shared,
                            inferred_at=inferred_at,
                        )
                    )
        return links


__all__ = ["MeshGateway", "DEFAULT_STALE_AFTER_S", "DEFAULT_OFFLINE_AFTER_S", "DEFAULT_LINK_WINDOW_S"]
