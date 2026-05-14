"""Tests for the DeadZone WiFi-faked mesh feature.

Covers: wire protocol, gateway merge logic, stale/offline lifecycle,
privacy invariants, transport buffering, scanner determinism, and HTTP
integration via the satellite FastAPI app.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.mesh.gateway import MeshGateway
from app.mesh.models import (
    SCHEMA_AGGREGATE_V1,
    AggregatePacket,
    Position,
    ZoneAggregate,
)
from app.mesh.node import MockNodeScanner
from app.mesh.transport import AggregateClient


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def make_packet(
    node_id: str,
    *,
    zones: list[tuple[str, int, float, str]] | None = None,
    t: datetime | None = None,
    position: tuple[float, float] | None = None,
    confidence: float | None = None,
) -> AggregatePacket:
    """Build an AggregatePacket with sensible defaults for testing."""
    zs = zones or [("near-scanner", 5, 0.3, "rising")]
    return AggregatePacket(
        node_id=node_id,
        position=Position(x=position[0], y=position[1]) if position else None,
        timestamp=t or datetime.now(timezone.utc),
        uptime_s=1.0,
        zones=[
            ZoneAggregate(
                zone_id=zid,
                estimated_devices=ec,
                density=d,
                trend=tr,
                **({"confidence": confidence} if confidence is not None else {}),
            )
            for zid, ec, d, tr in zs
        ],
    )


class FakeClock:
    """Injectable clock for testing stale/offline timing."""

    def __init__(self, start: datetime | None = None) -> None:
        self._t = start or datetime(2026, 5, 14, 18, 0, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        return self._t

    def advance(self, seconds: float) -> None:
        self._t += timedelta(seconds=seconds)


# ---------------------------------------------------------------------------
# TestAggregatePacketWireProtocol
# ---------------------------------------------------------------------------


class TestAggregatePacketWireProtocol:
    """Wire-format assertions on AggregatePacket serialization and parsing."""

    def test_packet_serializes_schema_alias(self) -> None:
        pkt = make_packet("node-a")
        raw = json.loads(pkt.model_dump_json(by_alias=True))
        assert "schema" in raw
        assert raw["schema"] == SCHEMA_AGGREGATE_V1

    def test_packet_validates_schema_either_key(self) -> None:
        base = {
            "node_id": "x",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_s": 0.0,
            "zones": [],
        }
        # Accept via alias key "schema"
        p1 = AggregatePacket.model_validate({**base, "schema": SCHEMA_AGGREGATE_V1})
        assert p1.schema_id == SCHEMA_AGGREGATE_V1

        # Accept via field name "schema_id"
        p2 = AggregatePacket.model_validate({**base, "schema_id": SCHEMA_AGGREGATE_V1})
        assert p2.schema_id == SCHEMA_AGGREGATE_V1

    def test_packet_never_carries_raw_identifiers(self) -> None:
        forbidden = {"mac", "address", "beacon_hash", "rssi", "raw"}

        def walk_fields(model_cls: type, visited: set | None = None) -> set[str]:
            """Recursively collect all field names from a pydantic model."""
            if visited is None:
                visited = set()
            if id(model_cls) in visited:
                return set()
            visited.add(id(model_cls))
            names: set[str] = set()
            for name, field_info in model_cls.model_fields.items():
                names.add(name)
                annotation = field_info.annotation
                # Unwrap Optional / list generics
                origin = getattr(annotation, "__origin__", None)
                args = getattr(annotation, "__args__", ())
                candidates = list(args) if origin else [annotation]
                for candidate in candidates:
                    if isinstance(candidate, type) and hasattr(candidate, "model_fields"):
                        names |= walk_fields(candidate, visited)
            return names

        all_fields = walk_fields(AggregatePacket)
        overlap = all_fields & forbidden
        assert overlap == set(), f"AggregatePacket contains forbidden field(s): {overlap}"

    def test_zone_aggregate_density_bounds(self) -> None:
        with pytest.raises(ValidationError):
            ZoneAggregate(zone_id="z", estimated_devices=5, density=-0.1, trend="stable")
        with pytest.raises(ValidationError):
            ZoneAggregate(zone_id="z", estimated_devices=5, density=1.5, trend="stable")
        with pytest.raises(ValidationError):
            ZoneAggregate(zone_id="z", estimated_devices=-1, density=0.5, trend="stable")


# ---------------------------------------------------------------------------
# TestMeshGatewayMerge
# ---------------------------------------------------------------------------


class TestMeshGatewayMerge:
    """Zone-merge logic across multiple nodes."""

    def test_ingest_creates_node(self) -> None:
        gw = MeshGateway()
        gw.ingest(make_packet("node-a"))
        nodes = gw.nodes()
        assert len(nodes) == 1
        assert nodes[0].node_id == "node-a"
        assert nodes[0].status == "live"

    def test_sum_devices_across_two_nodes_same_zone(self) -> None:
        gw = MeshGateway()
        gw.ingest(make_packet("a", zones=[("zone-x", 5, 0.3, "stable")]))
        gw.ingest(make_packet("b", zones=[("zone-x", 7, 0.4, "stable")]))
        snap = gw.snapshot()
        zone_x = [z for z in snap.zones_merged if z.zone_id == "zone-x"]
        assert len(zone_x) == 1
        assert zone_x[0].estimated_devices == 12
        assert sorted(zone_x[0].contributing_nodes) == ["a", "b"]

    def test_max_density_across_nodes(self) -> None:
        gw = MeshGateway()
        gw.ingest(make_packet("a", zones=[("zone-x", 5, 0.3, "stable")]))
        gw.ingest(make_packet("b", zones=[("zone-x", 5, 0.8, "stable")]))
        snap = gw.snapshot()
        zone_x = [z for z in snap.zones_merged if z.zone_id == "zone-x"][0]
        assert zone_x.density == 0.8

    def test_min_confidence_across_nodes(self) -> None:
        """Merge rule: confidence = MIN (conservative).

        NOTE: The spec says MIN, not MEAN. The production code implements MIN.
        """
        gw = MeshGateway()
        gw.ingest(make_packet("a", zones=[("zone-x", 5, 0.3, "stable")], confidence=0.4))
        gw.ingest(make_packet("b", zones=[("zone-x", 5, 0.3, "stable")], confidence=0.6))
        snap = gw.snapshot()
        zone_x = [z for z in snap.zones_merged if z.zone_id == "zone-x"][0]
        assert zone_x.confidence == pytest.approx(0.4)

    def test_trend_majority_vote_with_tie_breaks_to_most_urgent(self) -> None:
        """Tie-breaking: 2 rising (urgency 2) + 2 falling (urgency 1) -> rising wins.

        NOTE: The spec merge_rules say ties broken by urgency (spiking > rising >
        falling > stable), so a 2-2 tie between rising and falling picks "rising",
        NOT "stable".
        """
        gw = MeshGateway()
        gw.ingest(make_packet("a", zones=[("z", 5, 0.3, "rising")]))
        gw.ingest(make_packet("b", zones=[("z", 5, 0.3, "falling")]))
        gw.ingest(make_packet("c", zones=[("z", 5, 0.3, "rising")]))
        gw.ingest(make_packet("d", zones=[("z", 5, 0.3, "falling")]))
        snap = gw.snapshot()
        zone = [z for z in snap.zones_merged if z.zone_id == "z"][0]
        assert zone.trend == "rising"

    def test_trend_clear_majority_wins(self) -> None:
        gw = MeshGateway()
        gw.ingest(make_packet("a", zones=[("z", 5, 0.3, "rising")]))
        gw.ingest(make_packet("b", zones=[("z", 5, 0.3, "rising")]))
        gw.ingest(make_packet("c", zones=[("z", 5, 0.3, "rising")]))
        gw.ingest(make_packet("d", zones=[("z", 5, 0.3, "falling")]))
        snap = gw.snapshot()
        zone = [z for z in snap.zones_merged if z.zone_id == "z"][0]
        assert zone.trend == "rising"

    def test_only_live_nodes_contribute_to_merge(self) -> None:
        clock = FakeClock()
        gw = MeshGateway(clock=clock)
        gw.ingest(make_packet("a", zones=[("z", 5, 0.3, "stable")]))
        gw.ingest(make_packet("b", zones=[("z", 7, 0.4, "stable")]))
        # Advance clock so node b becomes stale, then offline
        clock.advance(11.0)
        # Re-ingest only node a so it stays live
        gw.ingest(make_packet("a", zones=[("z", 5, 0.3, "stable")]))
        snap = gw.snapshot()
        zone = [z for z in snap.zones_merged if z.zone_id == "z"][0]
        assert zone.estimated_devices == 5
        assert zone.contributing_nodes == ["a"]

    def test_mesh_link_inferred_when_two_nodes_share_zone(self) -> None:
        clock = FakeClock()
        gw = MeshGateway(clock=clock)
        gw.ingest(make_packet("a", zones=[("zone-x", 5, 0.3, "stable")]))
        gw.ingest(make_packet("b", zones=[("zone-x", 7, 0.4, "stable")]))
        snap = gw.snapshot()
        assert len(snap.mesh_links) == 1
        link = snap.mesh_links[0]
        assert "zone-x" in link.shared_zones

    def test_mesh_link_not_inferred_for_disjoint_zones(self) -> None:
        clock = FakeClock()
        gw = MeshGateway(clock=clock)
        gw.ingest(make_packet("a", zones=[("zone-x", 5, 0.3, "stable")]))
        gw.ingest(make_packet("b", zones=[("zone-y", 7, 0.4, "stable")]))
        snap = gw.snapshot()
        assert len(snap.mesh_links) == 0

    def test_mesh_links_not_double_counted(self) -> None:
        clock = FakeClock()
        gw = MeshGateway(clock=clock)
        gw.ingest(make_packet("a", zones=[("zone-x", 5, 0.3, "stable")]))
        gw.ingest(make_packet("b", zones=[("zone-x", 7, 0.4, "stable")]))
        snap = gw.snapshot()
        # Should only have (a, b) once, never both (a, b) and (b, a)
        assert len(snap.mesh_links) == 1
        link = snap.mesh_links[0]
        # source < target lexicographically (implementation sorts node_ids)
        assert link.source_node < link.target_node


# ---------------------------------------------------------------------------
# TestStaleAndOfflineDetection
# ---------------------------------------------------------------------------


class TestStaleAndOfflineDetection:
    """Node lifecycle transitions: live -> stale -> offline -> live."""

    def test_node_marked_stale_after_3s(self) -> None:
        clock = FakeClock()
        gw = MeshGateway(clock=clock)
        gw.ingest(make_packet("a"))
        clock.advance(3.5)
        gw.sweep()
        nodes = gw.nodes()
        assert nodes[0].status == "stale"

    def test_node_marked_offline_after_10s(self) -> None:
        clock = FakeClock()
        gw = MeshGateway(clock=clock)
        gw.ingest(make_packet("a"))
        clock.advance(11.0)
        gw.sweep()
        nodes = gw.nodes()
        assert nodes[0].status == "offline"

    def test_node_returns_to_live_after_fresh_packet(self) -> None:
        clock = FakeClock()
        gw = MeshGateway(clock=clock)
        gw.ingest(make_packet("a"))
        clock.advance(11.0)
        gw.sweep()
        assert gw.nodes()[0].status == "offline"
        # New packet at t=12s brings node back to life
        clock.advance(1.0)
        gw.ingest(make_packet("a"))
        assert gw.nodes()[0].status == "live"


# ---------------------------------------------------------------------------
# TestPrivacyInvariants
# ---------------------------------------------------------------------------


class TestPrivacyInvariants:
    """No raw device identifiers ever appear in serialized output."""

    _FORBIDDEN_TOKENS = {"mac", "rssi", "beacon_hash", "address"}

    def test_aggregate_packet_json_has_no_raw_fields(self) -> None:
        pkt = make_packet("node-a", zones=[("zone-x", 5, 0.3, "rising")])
        raw_json = pkt.model_dump_json(by_alias=True).lower()
        for token in self._FORBIDDEN_TOKENS:
            assert token not in raw_json, f"Forbidden token '{token}' found in packet JSON"

    def test_mesh_snapshot_has_no_raw_fields(self) -> None:
        gw = MeshGateway()
        gw.ingest(make_packet("node-a", zones=[("zone-x", 5, 0.3, "rising")]))
        snap = gw.snapshot()
        raw_json = snap.model_dump_json(by_alias=True).lower()
        for token in self._FORBIDDEN_TOKENS:
            assert token not in raw_json, f"Forbidden token '{token}' found in snapshot JSON"


# ---------------------------------------------------------------------------
# TestAggregateClientTransport
# ---------------------------------------------------------------------------


class TestAggregateClientTransport:
    """AggregateClient buffering, sequencing, and error handling."""

    async def test_post_returns_false_when_gateway_unreachable_and_buffers(self) -> None:
        client = AggregateClient("http://127.0.0.1:1", timeout_s=0.1)
        results = []
        for _ in range(3):
            ok = await client.post(make_packet("n"))
            results.append(ok)
        assert results == [False, False, False]
        assert client.buffered == 3
        assert client.last_seq == 3

    async def test_buffer_does_not_double_count_on_replay(self) -> None:
        client = AggregateClient("http://127.0.0.1:1", timeout_s=0.1)
        for _ in range(3):
            await client.post(make_packet("n"))
        assert client.buffered == 3
        # Fourth post: drains buffer (all retry), adds 1 new = still 4 total
        await client.post(make_packet("n"))
        assert client.buffered == 4
        assert client.last_seq == 4

    async def test_buffer_bounded_by_maxlen(self) -> None:
        client = AggregateClient("http://127.0.0.1:1", timeout_s=0.1, buffer_size=2)
        for _ in range(5):
            await client.post(make_packet("n"))
        assert client.buffered == 2

    async def test_drop_on_4xx_does_not_buffer(self) -> None:
        client = AggregateClient("http://127.0.0.1:1", timeout_s=0.1)
        with patch.object(client, "_send", return_value="drop"):
            ok = await client.post(make_packet("n"))
        assert ok is False
        assert client.buffered == 0


# ---------------------------------------------------------------------------
# TestMockNodeScannerDeterminism
# ---------------------------------------------------------------------------


class TestMockNodeScannerDeterminism:
    """MockNodeScanner produces deterministic output from seed."""

    def test_two_scanners_same_seed_same_output(self) -> None:
        s1 = MockNodeScanner(seed=42)
        s2 = MockNodeScanner(seed=42)
        for _ in range(10):
            a1 = s1.aggregate()
            a2 = s2.aggregate()
            assert len(a1) == len(a2)
            for z1, z2 in zip(a1, a2):
                assert z1.zone_id == z2.zone_id
                assert z1.estimated_devices == z2.estimated_devices
                assert z1.density == pytest.approx(z2.density)
                assert z1.trend == z2.trend

    def test_different_seeds_differ(self) -> None:
        s1 = MockNodeScanner(seed=1)
        s2 = MockNodeScanner(seed=2)
        # Collect zone densities across 10 ticks
        densities_1 = [z.density for _ in range(10) for z in s1.aggregate()]
        densities_2 = [z.density for _ in range(10) for z in s2.aggregate()]
        assert densities_1 != densities_2


# ---------------------------------------------------------------------------
# TestSatelliteAppIntegration
# ---------------------------------------------------------------------------


class TestSatelliteAppIntegration:
    """HTTP integration tests against the satellite FastAPI app."""

    @pytest.fixture(autouse=True)
    def _setup_app(self) -> None:
        # Import at fixture time so the class is still collected if app.py
        # is missing; individual tests will skip via the guard below.
        try:
            from app.mesh.app import create_app
            from fastapi.testclient import TestClient

            self.app = create_app(gateway_id="test-gw")
            self.client = TestClient(self.app)
            self._available = True
        except ImportError:
            self._available = False

    def _skip_if_unavailable(self) -> None:
        if not self._available:
            pytest.skip("app.mesh.app not yet importable")

    def _post_packet(self, node_id: str, **kwargs: Any) -> Any:
        pkt = make_packet(node_id, **kwargs)
        return self.client.post(
            "/mesh/aggregate",
            content=pkt.model_dump_json(by_alias=True),
            headers={"Content-Type": "application/json"},
        )

    def test_healthz_returns_node_count(self) -> None:
        self._skip_if_unavailable()
        resp = self.client.get("/mesh/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["node_count"] == 0

    def test_aggregate_post_then_state_shows_node(self) -> None:
        self._skip_if_unavailable()
        resp = self._post_packet("node-a", zones=[("zone-x", 5, 0.3, "rising")])
        assert resp.status_code == 200
        state = self.client.get("/mesh/state").json()
        assert len(state["nodes"]) == 1
        assert len(state["zones_merged"]) == 1
        assert state["nodes"][0]["node_id"] == "node-a"

    def test_two_node_aggregation_via_http(self) -> None:
        self._skip_if_unavailable()
        self._post_packet("a", zones=[("zone-x", 5, 0.3, "stable")])
        self._post_packet("b", zones=[("zone-x", 7, 0.4, "stable")])
        state = self.client.get("/mesh/state").json()
        assert len(state["nodes"]) == 2
        zone_x = [z for z in state["zones_merged"] if z["zone_id"] == "zone-x"]
        assert len(zone_x) == 1
        assert zone_x[0]["estimated_devices"] == 12
        assert sorted(zone_x[0]["contributing_nodes"]) == ["a", "b"]

    def test_post_rejects_invalid_schema(self) -> None:
        self._skip_if_unavailable()
        resp = self.client.post(
            "/mesh/aggregate",
            json={"bad_field": "no_node_id"},
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422
