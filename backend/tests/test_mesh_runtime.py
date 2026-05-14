"""Tests for 1-click mesh feature: runtime state machine, beacon discovery, and API endpoints.

Covers: MeshRuntime lifecycle (host/join/leave/unhost/shutdown),
BeaconPacket wire format, BeaconListener/BeaconBroadcaster behaviour,
DiscoveryService peer management, and the FastAPI endpoints from api_extra.
"""

from __future__ import annotations

import asyncio
import json
import random
import re
import time
from datetime import datetime, timedelta, timezone
import pytest

from app.mesh.discovery import (
    BEACON_SCHEMA,
    BeaconBroadcaster,
    BeaconListener,
    BeaconPacket,
    DiscoveredPeer,
    DiscoveryService,
    utc_now,
)
from app.mesh.runtime import MeshRuntime


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


async def wait_until(predicate, *, timeout: float = 3.0, interval: float = 0.05) -> None:
    """Poll *predicate* until it returns True, or raise after *timeout* seconds."""
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)
    raise AssertionError(f"wait_until timed out after {timeout}s")


def _pick_port() -> int:
    """Return a random port in the 28432-28999 range to avoid collisions."""
    return random.randint(28432, 28999)


# ---------------------------------------------------------------------------
# TestMeshRuntimeStateMachine
# ---------------------------------------------------------------------------


class TestMeshRuntimeStateMachine:
    """State-machine lifecycle transitions for MeshRuntime."""

    def test_initial_role_is_idle(self) -> None:
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        assert rt.role == "idle"
        assert rt.hosting is False
        assert rt.joined_url is None

    async def test_host_transitions_to_hosting_and_self_joins(self) -> None:
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        try:
            await rt.host()
            # Auto-self-join means role should reflect both hosting + joined-self
            # Per the state diagram, hosting with self-join shows as "hosting"
            # (self-join sets _is_self_join=True so role returns "hosting" not
            # "hosting_and_joined")
            assert rt.role == "hosting"
            assert rt.hosting is True
            assert rt.joined_url == "http://127.0.0.1:9999"
            assert rt.node_id is not None
            assert rt.node_id.endswith("-self")
        finally:
            await rt.shutdown()

    async def test_unhost_clears_self_join(self) -> None:
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        try:
            await rt.host()
            assert rt.hosting is True
            await rt.unhost()
            assert rt.role == "idle"
            assert rt.hosting is False
            assert rt.joined_url is None
        finally:
            await rt.shutdown()

    async def test_join_external_gateway(self) -> None:
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        try:
            await rt.join("http://127.0.0.1:1")
            assert rt.role == "joined"
            assert rt.node_id is not None
            assert re.match(r"^.+-node-[a-f0-9]+$", rt.node_id), (
                f"node_id '{rt.node_id}' does not match expected pattern"
            )
        finally:
            await rt.shutdown()

    async def test_join_when_already_joined_raises(self) -> None:
        """Joining when already joined raises RuntimeError (caller must leave first)."""
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        try:
            await rt.join("http://127.0.0.1:1")
            with pytest.raises(RuntimeError, match="already joined"):
                await rt.join("http://127.0.0.1:2")
        finally:
            await rt.shutdown()

    async def test_leave_then_join_replaces_gateway(self) -> None:
        """Leave first gateway, then join second; final joined_url is second."""
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        try:
            await rt.join("http://127.0.0.1:1")
            assert rt.joined_url == "http://127.0.0.1:1"
            await rt.leave()
            await rt.join("http://127.0.0.1:2")
            assert rt.joined_url == "http://127.0.0.1:2"
        finally:
            await rt.shutdown()

    async def test_leave_is_idempotent(self) -> None:
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        try:
            await rt.leave()  # no-op, should not raise
            assert rt.role == "idle"
        finally:
            await rt.shutdown()

    async def test_unhost_is_idempotent(self) -> None:
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        try:
            await rt.unhost()  # no-op, should not raise
            assert rt.role == "idle"
        finally:
            await rt.shutdown()

    async def test_shutdown_cleans_up_everything(self) -> None:
        rt = MeshRuntime(gateway_id="gw-test", gateway_port=9999)
        await rt.host()
        await rt.shutdown()
        assert rt.role == "idle"
        assert rt.hosting is False
        assert rt.joined_url is None


# ---------------------------------------------------------------------------
# TestBeaconPacket
# ---------------------------------------------------------------------------


class TestBeaconPacket:
    """Wire-format round-trip and rejection for BeaconPacket."""

    def test_packet_round_trip(self) -> None:
        original = BeaconPacket(
            gateway_id="gw-abc", gateway_url="http://10.0.0.1:8001", version="0.2.0",
        )
        raw = original.to_json()
        parsed = BeaconPacket.parse(raw)
        assert parsed is not None
        assert parsed.gateway_id == original.gateway_id
        assert parsed.gateway_url == original.gateway_url
        assert parsed.version == original.version

    def test_parse_rejects_wrong_schema(self) -> None:
        payload = json.dumps({
            "schema": "other.schema.v1",
            "gateway_id": "gw-x",
            "gateway_url": "http://10.0.0.1:8001",
        }).encode()
        assert BeaconPacket.parse(payload) is None

    def test_parse_rejects_missing_required_fields(self) -> None:
        # Missing gateway_url
        payload_no_url = json.dumps({
            "schema": BEACON_SCHEMA,
            "gateway_id": "gw-x",
        }).encode()
        assert BeaconPacket.parse(payload_no_url) is None

        # Missing gateway_id
        payload_no_id = json.dumps({
            "schema": BEACON_SCHEMA,
            "gateway_url": "http://10.0.0.1:8001",
        }).encode()
        assert BeaconPacket.parse(payload_no_id) is None

    def test_parse_rejects_invalid_json(self) -> None:
        assert BeaconPacket.parse(b"\x80\xff random garbage") is None
        assert BeaconPacket.parse(b"") is None


# ---------------------------------------------------------------------------
# TestDiscoveryService
# ---------------------------------------------------------------------------


class TestDiscoveryService:
    """BeaconListener, BeaconBroadcaster, and DiscoveryService behaviour."""

    async def test_listener_binds_and_starts(self) -> None:
        port = _pick_port()
        listener = BeaconListener(port=port, ttl_s=30.0)
        listener.start()
        try:
            assert listener.active is True
        finally:
            await listener.stop()
        assert listener.active is False

    async def test_broadcaster_starts_and_increments_counter(self) -> None:
        port = _pick_port()
        broadcaster = BeaconBroadcaster(
            gateway_id="gw-test",
            gateway_url="http://127.0.0.1:8001",
            port=port,
            interval_s=0.2,
        )
        broadcaster.start()
        try:
            await asyncio.sleep(0.7)
            assert broadcaster.broadcasts_sent >= 2
        finally:
            await broadcaster.stop()

    async def test_local_loopback_discovery(self) -> None:
        """Broadcaster + listener on same port; listener should discover the peer."""
        port = _pick_port()
        listener = BeaconListener(port=port, ttl_s=30.0, self_gateway_id=None)
        broadcaster = BeaconBroadcaster(
            gateway_id="loopback-gw",
            gateway_url="http://127.0.0.1:8001",
            port=port,
            interval_s=0.2,
        )
        listener.start()
        broadcaster.start()
        try:
            # Wait for at least one packet to arrive
            try:
                await wait_until(
                    lambda: listener.packets_received > 0, timeout=2.0,
                )
            except AssertionError:
                pytest.skip(
                    "UDP broadcast loopback not received — SO_REUSEPORT may not be "
                    "available on this platform"
                )
            peers = listener.peers(include_self=True)
            matching = [p for p in peers if p.gateway_id == "loopback-gw"]
            assert len(matching) >= 1
        finally:
            await broadcaster.stop()
            await listener.stop()

    async def test_peer_pruned_after_ttl(self) -> None:
        """Manually injected peer older than TTL is pruned from peers() result."""
        listener = BeaconListener(port=_pick_port(), ttl_s=0.5)
        # Manually inject a stale peer
        now = utc_now()
        listener._peers["stale-gw"] = DiscoveredPeer(
            gateway_id="stale-gw",
            gateway_url="http://10.0.0.99:8001",
            version="0.1.0",
            first_seen=now - timedelta(seconds=2.0),
            last_seen=now - timedelta(seconds=1.0),
            beacon_count=5,
        )
        peers = listener.peers()
        assert len(peers) == 0
        # Internal dict should also be cleaned
        assert "stale-gw" not in listener._peers

    async def test_self_filter(self) -> None:
        """Listener with self_gateway_id filters its own beacons from peers()."""
        listener = BeaconListener(port=_pick_port(), ttl_s=30.0, self_gateway_id="alpha")
        now = utc_now()
        # Inject two peers: self ("alpha") and another ("beta")
        for gid in ("alpha", "beta"):
            listener._peers[gid] = DiscoveredPeer(
                gateway_id=gid,
                gateway_url=f"http://10.0.0.1:8001",
                version="0.1.0",
                first_seen=now,
                last_seen=now,
                beacon_count=1,
            )
        peers = listener.peers(include_self=False)
        gids = [p.gateway_id for p in peers]
        assert "alpha" not in gids
        assert "beta" in gids


# ---------------------------------------------------------------------------
# TestApiExtraEndpoints
# ---------------------------------------------------------------------------


class TestApiExtraEndpoints:
    """HTTP integration tests for the mesh lifecycle API endpoints."""

    @pytest.fixture()
    def mesh_app(self):
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        from app.mesh.api_extra import router as extra_router
        from app.mesh.runtime import MeshRuntime
        from app.mesh.discovery import DiscoveryService

        runtime = MeshRuntime(gateway_id="test-gw", gateway_port=8001)
        discovery = DiscoveryService(
            gateway_id="test-gw",
            gateway_url="http://127.0.0.1:8001",
            port=_pick_port(),
            interval_s=10.0,
        )

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            app.state.runtime = runtime
            app.state.discovery = discovery
            yield
            await runtime.shutdown()
            await discovery.shutdown()

        app = FastAPI(lifespan=lifespan)
        app.include_router(extra_router)
        yield app

    def _client(self, mesh_app):
        from fastapi.testclient import TestClient
        return TestClient(mesh_app)

    def test_get_me_idle(self, mesh_app) -> None:
        with self._client(mesh_app) as client:
            resp = client.get("/mesh/me")
            assert resp.status_code == 200
            body = resp.json()
            assert body["role"] == "idle"

    def test_post_host_then_me_shows_hosting(self, mesh_app) -> None:
        with self._client(mesh_app) as client:
            resp = client.post("/mesh/host", json={})
            assert resp.status_code == 200
            body = resp.json()
            # After hosting with auto-self-join, role is "hosting" (self-join
            # is recognized as self so role property returns "hosting")
            assert body["role"] == "hosting"
            assert body["beacon_active"] is True

    def test_post_unhost_resets(self, mesh_app) -> None:
        with self._client(mesh_app) as client:
            client.post("/mesh/host", json={})
            resp = client.post("/mesh/unhost")
            assert resp.status_code == 200
            body = resp.json()
            assert body["role"] == "idle"

    def test_post_join_with_url(self, mesh_app) -> None:
        with self._client(mesh_app) as client:
            resp = client.post("/mesh/join", json={"gateway_url": "http://127.0.0.1:1"})
            assert resp.status_code == 200
            body = resp.json()
            assert "joined" in body["role"]

    def test_get_discover_empty(self, mesh_app) -> None:
        with self._client(mesh_app) as client:
            resp = client.get("/mesh/discover")
            assert resp.status_code == 200
            assert resp.json() == []

    def test_post_join_with_missing_url_validation(self, mesh_app) -> None:
        with self._client(mesh_app) as client:
            resp = client.post("/mesh/join", json={})
            assert resp.status_code == 422
