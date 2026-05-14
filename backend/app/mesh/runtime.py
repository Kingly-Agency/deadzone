"""In-process state machine for hosting + joining mesh roles.

Manages a single optional :class:`MeshNode` coroutine alongside the
always-running :class:`MeshGateway`.  The runtime is the single source
of truth for "what role is this satellite playing right now?"

State diagram::

    idle ──host()──▶ hosting (auto-self-join)
    idle ──join()──▶ joined
    hosting ──join(remote)──▶ hosting_and_joined
    hosting ──unhost()──▶ idle
    joined  ──leave()──▶ idle
    hosting_and_joined ──unhost()──▶ joined
    hosting_and_joined ──leave()──▶ hosting (re-self-join)

NOT thread-safe — assumes a single asyncio event loop.
"""

from __future__ import annotations

import asyncio
import json
import logging
import secrets
from datetime import datetime, timezone
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.mesh.models import Position
from app.mesh.node import MeshNode, MockNodeScanner
from app.mesh.transport import AggregateClient

logger = logging.getLogger(__name__)

__all__ = ["MeshRuntime"]


class MeshRuntime:
    """In-process state machine for hosting + joining mesh roles.

    Single asyncio loop.  NOT thread-safe.
    Allows at most ONE active node coroutine at a time.
    """

    def __init__(self, *, gateway_id: str, gateway_port: int = 8001) -> None:
        self._gateway_id = gateway_id
        self._gateway_port = gateway_port
        self._self_url = f"http://127.0.0.1:{gateway_port}"

        # Hosting state
        self._hosting = False

        # Node state
        self._node: MeshNode | None = None
        self._node_task: asyncio.Task[None] | None = None
        self._client: AggregateClient | None = None
        self._joined_url: str | None = None
        self._joined_gateway_id: str | None = None
        self._is_self_join: bool = False

        # Timestamps
        self._started_at: datetime = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def gateway_id(self) -> str:
        """Public accessor for the gateway identifier."""
        return self._gateway_id

    @property
    def role(self) -> Literal["idle", "hosting", "joined", "hosting_and_joined"]:
        has_node = self._node_task is not None and not self._node_task.done()
        if self._hosting and has_node and not self._is_self_join:
            return "hosting_and_joined"
        if self._hosting:
            return "hosting"
        if has_node:
            return "joined"
        return "idle"

    @property
    def hosting(self) -> bool:
        return self._hosting

    @property
    def joined_url(self) -> str | None:
        if self._node_task is not None and not self._node_task.done():
            return self._joined_url
        return None

    @property
    def joined_gateway_id(self) -> str | None:
        return self._joined_gateway_id

    @property
    def node_id(self) -> str | None:
        if self._node is not None and self._node_task is not None and not self._node_task.done():
            return self._node.node_id
        return None

    @property
    def node_packets_sent(self) -> int:
        """Number of send-attempt sequences via ``client.last_seq``."""
        if self._client is not None:
            return self._client.last_seq
        return 0

    @property
    def node_buffered(self) -> int:
        """Packets currently buffered for replay."""
        if self._client is not None:
            return self._client.buffered
        return 0

    # ------------------------------------------------------------------
    # Host / Unhost
    # ------------------------------------------------------------------

    async def host(self, *, beacon: bool = True) -> None:
        """Enter hosting mode.  Idempotent.

        Auto-joins self at ``127.0.0.1:<port>`` unless already joined
        to an external gateway.
        """
        if self._hosting:
            return
        self._hosting = True
        logger.info("mesh runtime entering hosting mode (gateway_id=%s)", self._gateway_id)

        # Auto-self-join if not already joined elsewhere
        if self._node_task is None or self._node_task.done():
            try:
                await self._self_join()
            except Exception:
                self._hosting = False
                raise

    async def unhost(self) -> None:
        """Exit hosting mode.  Stops the self-join node coroutine if active."""
        if not self._hosting:
            return
        self._hosting = False
        logger.info("mesh runtime leaving hosting mode")

        # If currently self-joined, tear down the node
        if self._is_self_join:
            await self.leave()

    # ------------------------------------------------------------------
    # Join / Leave
    # ------------------------------------------------------------------

    async def join(
        self,
        gateway_url: str,
        *,
        node_id: str | None = None,
        position: tuple[float, float] | None = None,
        scanner: str = "mock",
        seed: int = 1337,
    ) -> None:
        """Start a node coroutine POSTing to *gateway_url*.

        Raises :class:`RuntimeError` if already joined (call
        :meth:`leave` first).  Pings ``gateway_url/mesh/healthz`` to
        learn the remote gateway_id (best-effort).
        """
        # Guard: at most one node at a time
        if self._node_task is not None and not self._node_task.done():
            raise RuntimeError(
                "already joined — call leave() before joining a different gateway"
            )

        if node_id is None:
            short_id = secrets.token_hex(3)
            node_id = f"{self._gateway_id}-node-{short_id}"

        self._joined_url = gateway_url
        self._joined_gateway_id = await self._probe_gateway_id(gateway_url)

        # Build transport + scanner + node
        self._client = AggregateClient(gateway_url)
        scanner_obj = MockNodeScanner(seed=seed)
        pos = Position(x=position[0], y=position[1]) if position else None

        self._node = MeshNode(
            node_id=node_id,
            client=self._client,
            scanner=scanner_obj,
            position=pos,
        )
        self._node_task = asyncio.create_task(
            self._node.run(), name=f"mesh-node-{node_id}"
        )
        logger.info(
            "mesh node %s started → %s (gateway_id=%s)",
            node_id,
            gateway_url,
            self._joined_gateway_id or "unknown",
        )

    async def leave(self) -> None:
        """Cancel the node coroutine.  Idempotent."""
        if self._node_task is None or self._node_task.done():
            self._cleanup_node_state()
            return

        self._node_task.cancel()
        try:
            await self._node_task
        except asyncio.CancelledError:
            pass
        logger.info("mesh node stopped")
        was_self_join = self._is_self_join
        self._cleanup_node_state()

        # If we were hosting and just tore down a non-self-join, re-self-join
        if self._hosting and not was_self_join:
            await self._self_join()

    async def shutdown(self) -> None:
        """Called from lifespan teardown.  Cancels everything cleanly."""
        logger.info("mesh runtime shutting down")
        # Leave first (cancels node task)
        if self._node_task is not None and not self._node_task.done():
            self._node_task.cancel()
            try:
                await self._node_task
            except asyncio.CancelledError:
                pass
        self._cleanup_node_state()
        self._hosting = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _self_join(self) -> None:
        """Auto-join self at the local gateway URL."""
        await self.join(
            self._self_url,
            node_id=f"{self._gateway_id}-self",
        )
        self._is_self_join = True  # set AFTER join() succeeds

    def _cleanup_node_state(self) -> None:
        """Reset all node-related state."""
        self._node = None
        self._node_task = None
        self._client = None
        self._joined_url = None
        self._joined_gateway_id = None
        self._is_self_join = False

    async def _probe_gateway_id(self, gateway_url: str) -> str | None:
        """Best-effort GET on ``/mesh/healthz`` to learn the gateway_id.

        Uses stdlib urllib in ``run_in_executor`` with a 1 s timeout.
        Returns ``None`` on any failure.
        """
        url = f"{gateway_url.rstrip('/')}/mesh/healthz"
        loop = asyncio.get_running_loop()
        try:
            data: bytes = await loop.run_in_executor(None, self._blocking_get, url)
            parsed = json.loads(data)
            return parsed.get("gateway_id")
        except Exception:
            logger.debug("could not probe gateway_id at %s", url, exc_info=True)
            return None

    @staticmethod
    def _blocking_get(url: str) -> bytes:
        """Blocking HTTP GET with 1 s timeout."""
        req = Request(url, method="GET", headers={"User-Agent": "deadzone-mesh-runtime/0.1"})
        with urlopen(req, timeout=1.0) as resp:
            return resp.read()
