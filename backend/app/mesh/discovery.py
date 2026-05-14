"""UDP beacon broadcast + listener for mesh gateway auto-discovery.

Stdlib only. Stop-friendly: both services use asyncio.Event for shutdown.

Beacon transport:
- UDP, default port 8002, configurable.
- Broadcast address: 255.255.255.255 (SO_BROADCAST).
- Interval: 3 seconds.
- TTL on listener side: 30 seconds (prune older).
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

BEACON_SCHEMA = "deadzone.mesh.beacon.v1"
DEFAULT_BEACON_PORT = 8002
DEFAULT_BROADCAST_INTERVAL_S = 3.0
DEFAULT_DISCOVERY_TTL_S = 30.0


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class DiscoveredPeer:
    """A gateway we've heard a beacon from on this LAN."""
    gateway_id: str
    gateway_url: str
    version: str
    first_seen: datetime
    last_seen: datetime
    beacon_count: int = 1


@dataclass
class BeaconPacket:
    gateway_id: str
    gateway_url: str
    version: str = "0.1.0"

    def to_json(self) -> bytes:
        return json.dumps({
            "schema": BEACON_SCHEMA,
            "gateway_id": self.gateway_id,
            "gateway_url": self.gateway_url,
            "version": self.version,
            "broadcast_at": utc_now().isoformat(),
        }).encode("utf-8")

    @classmethod
    def parse(cls, raw: bytes) -> "BeaconPacket | None":
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            return None
        if data.get("schema") != BEACON_SCHEMA:
            return None
        gid = data.get("gateway_id")
        gurl = data.get("gateway_url")
        if not gid or not gurl:
            return None
        return cls(gateway_id=gid, gateway_url=gurl, version=data.get("version", "?"))


class BeaconBroadcaster:
    """Periodically broadcasts a BeaconPacket on UDP. Run as a background task."""

    def __init__(self, *, gateway_id: str, gateway_url: str, version: str = "0.1.0",
                 port: int = DEFAULT_BEACON_PORT,
                 interval_s: float = DEFAULT_BROADCAST_INTERVAL_S) -> None:
        self.gateway_id = gateway_id
        self.gateway_url = gateway_url
        self.version = version
        self.port = port
        self.interval_s = interval_s
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._sock: socket.socket | None = None
        self.broadcasts_sent = 0

    @property
    def active(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self) -> None:
        if self.active:
            return
        self._stop.clear()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._task = asyncio.create_task(self._run())
        logger.info("beacon broadcaster started for %s (port %d)", self.gateway_id, self.port)

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            try:
                await asyncio.wait_for(self._task, timeout=self.interval_s + 1)
            except asyncio.TimeoutError:
                self._task.cancel()
            self._task = None
        if self._sock is not None:
            self._sock.close()
            self._sock = None
        logger.info("beacon broadcaster stopped for %s", self.gateway_id)

    async def _run(self) -> None:
        while not self._stop.is_set():
            packet = BeaconPacket(
                gateway_id=self.gateway_id,
                gateway_url=self.gateway_url,
                version=self.version,
            )
            body = packet.to_json()
            try:
                assert self._sock is not None
                # Blocking but fast; sending to broadcast is microseconds
                self._sock.sendto(body, ("255.255.255.255", self.port))
                self.broadcasts_sent += 1
            except OSError as exc:
                logger.debug("beacon send failed: %s", exc)
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval_s)
            except asyncio.TimeoutError:
                continue


class BeaconListener:
    """Listens for peer beacons on UDP. Maintains an in-memory peer table."""

    def __init__(self, *, port: int = DEFAULT_BEACON_PORT,
                 ttl_s: float = DEFAULT_DISCOVERY_TTL_S,
                 self_gateway_id: str | None = None) -> None:
        self.port = port
        self.ttl_s = ttl_s
        self.self_gateway_id = self_gateway_id  # filter self-beacons in `peers()`
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._sock: socket.socket | None = None
        self._peers: dict[str, DiscoveredPeer] = {}
        self.packets_received = 0

    @property
    def active(self) -> bool:
        return self._task is not None and not self._task.done()

    def start(self) -> None:
        if self.active:
            return
        self._stop.clear()
        # Bind UDP for receive on broadcast port. SO_REUSEADDR so we can co-exist
        # with other listeners on the same host (multiple satellites for testing).
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass  # not available on all platforms
        self._sock.setblocking(False)
        try:
            self._sock.bind(("", self.port))
        except OSError as exc:
            logger.warning("beacon listener bind failed on port %d: %s", self.port, exc)
            self._sock.close()
            self._sock = None
            return
        self._task = asyncio.create_task(self._run())
        logger.info("beacon listener started on port %d", self.port)

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._sock is not None:
            self._sock.close()
            self._sock = None
        logger.info("beacon listener stopped")

    async def _run(self) -> None:
        loop = asyncio.get_running_loop()
        while not self._stop.is_set():
            try:
                data = await loop.sock_recv(self._sock, 4096)  # type: ignore[arg-type]
            except (asyncio.CancelledError, OSError):
                return
            if not data:
                continue
            self.packets_received += 1
            packet = BeaconPacket.parse(data)
            if packet is None:
                continue
            now = utc_now()
            existing = self._peers.get(packet.gateway_id)
            if existing is None:
                self._peers[packet.gateway_id] = DiscoveredPeer(
                    gateway_id=packet.gateway_id,
                    gateway_url=packet.gateway_url,
                    version=packet.version,
                    first_seen=now,
                    last_seen=now,
                    beacon_count=1,
                )
            else:
                existing.last_seen = now
                existing.gateway_url = packet.gateway_url  # url may change with new IP
                existing.version = packet.version
                existing.beacon_count += 1

    def peers(self, *, include_self: bool = False) -> list[DiscoveredPeer]:
        """Return non-stale peers. Prunes the peer table as a side effect."""
        now = utc_now()
        result: list[DiscoveredPeer] = []
        stale: list[str] = []
        for gid, peer in self._peers.items():
            if (now - peer.last_seen).total_seconds() > self.ttl_s:
                stale.append(gid)
                continue
            if not include_self and self.self_gateway_id and gid == self.self_gateway_id:
                continue
            result.append(peer)
        for gid in stale:
            del self._peers[gid]
        result.sort(key=lambda p: p.gateway_id)
        return result


class DiscoveryService:
    """Convenience wrapper around BeaconBroadcaster + BeaconListener."""

    def __init__(self, *, gateway_id: str, gateway_url: str,
                 port: int = DEFAULT_BEACON_PORT,
                 interval_s: float = DEFAULT_BROADCAST_INTERVAL_S,
                 ttl_s: float = DEFAULT_DISCOVERY_TTL_S) -> None:
        self.broadcaster = BeaconBroadcaster(
            gateway_id=gateway_id, gateway_url=gateway_url,
            port=port, interval_s=interval_s,
        )
        self.listener = BeaconListener(
            port=port, ttl_s=ttl_s, self_gateway_id=gateway_id,
        )

    def start_listening(self) -> None:
        self.listener.start()

    def start_broadcasting(self) -> None:
        self.broadcaster.start()

    async def stop_broadcasting(self) -> None:
        await self.broadcaster.stop()

    async def shutdown(self) -> None:
        await self.broadcaster.stop()
        await self.listener.stop()

    def peers(self) -> list[DiscoveredPeer]:
        return self.listener.peers(include_self=False)

    @property
    def is_broadcasting(self) -> bool:
        return self.broadcaster.active


__all__ = [
    "BEACON_SCHEMA",
    "DEFAULT_BEACON_PORT",
    "BeaconBroadcaster",
    "BeaconListener",
    "BeaconPacket",
    "DiscoveryService",
    "DiscoveredPeer",
]
