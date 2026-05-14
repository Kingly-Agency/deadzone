"""Stdlib HTTP transport for node-to-gateway aggregate POSTs.

Uses only ``urllib.request`` so the mesh package stays dependency-free.
The blocking ``urlopen`` call is wrapped in ``run_in_executor`` to keep
the caller's async loop responsive.

Concurrency contract
--------------------
``AggregateClient.post`` is **not** safe for concurrent callers. The node
runner ticks at 1 Hz from a single coroutine, which is the only intended
caller pattern. If you need concurrent producers, wrap ``post`` calls in
an external ``asyncio.Lock``.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.mesh.models import AggregatePacket

logger = logging.getLogger(__name__)

USER_AGENT = "deadzone-mesh/0.1.0"

# Tri-state result for a single HTTP attempt — keeps buffer management
# entirely in the caller and out of the wire-level send.
SendResult = Literal["ok", "drop", "retry"]


class TransportError(Exception):
    """Raised for explicit transport-layer failures."""


def build_gateway_url(host: str, port: int = 8001) -> str:
    """Compose ``http://host:port`` for use as *gateway_url*."""
    return f"http://{host}:{port}"


class AggregateClient:
    """Post :class:`AggregatePacket` payloads to the mesh gateway.

    Parameters
    ----------
    gateway_url:
        Base URL of the gateway (e.g. ``http://192.168.1.42:8001``).
    timeout_s:
        Per-request socket timeout in seconds.
    buffer_size:
        Maximum number of packets to hold when the gateway is unreachable.
        Oldest packets are evicted first when the buffer is full.
    """

    def __init__(
        self,
        gateway_url: str,
        *,
        timeout_s: float = 2.0,
        buffer_size: int = 60,
    ) -> None:
        self._url = f"{gateway_url.rstrip('/')}/mesh/aggregate"
        self._timeout = timeout_s
        # Buffered bytes carry the seq header value they should be sent with.
        self._buffer: deque[tuple[int, bytes]] = deque(maxlen=buffer_size)
        self._seq: int = 0

    # ------------------------------------------------------------------
    # public async API
    # ------------------------------------------------------------------

    async def post(self, packet: AggregatePacket) -> bool:
        """Serialize *packet* and POST it to the gateway.

        Returns ``True`` if the freshly-built packet reached the gateway
        with a 2xx response. Buffered packets are replayed first; their
        results don't affect the return value.

        On network errors or 5xx the fresh packet is buffered for later
        replay. On 4xx the packet is logged and silently dropped.
        """
        body = packet.model_dump_json(by_alias=True).encode()
        loop = asyncio.get_running_loop()
        # Each packet has its own send-attempt sequence stamped at creation.
        self._seq += 1
        seq = self._seq
        # Replay any buffered packets first (oldest -> newest). Replay
        # results don't affect the caller's view of THIS packet's outcome.
        await self._drain_buffer(loop)
        result = await loop.run_in_executor(None, self._send, seq, body)
        if result == "ok":
            return True
        if result == "retry":
            self._buffer.append((seq, body))
        # "drop" -> nothing buffered, return False
        return False

    @property
    def buffered(self) -> int:
        """Current number of packets pending replay (for diagnostics)."""
        return len(self._buffer)

    @property
    def last_seq(self) -> int:
        """Most recently assigned send-attempt sequence number."""
        return self._seq

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    async def _drain_buffer(self, loop: asyncio.AbstractEventLoop) -> None:
        """Flush buffered packets oldest-first.

        Each packet is popped, attempted, and either discarded (ok / drop)
        or re-inserted at the front (retry). A retry result stops further
        draining — the gateway is still unreachable.
        """
        while self._buffer:
            seq, body = self._buffer.popleft()
            result = await loop.run_in_executor(None, self._send, seq, body)
            if result == "retry":
                # Gateway still unreachable; preserve order and stop.
                self._buffer.appendleft((seq, body))
                return
            # "ok" or "drop" -> packet is gone from the buffer.

    def _send(self, seq: int, body: bytes) -> SendResult:
        """Perform a blocking POST and classify the outcome.

        Returns:
            "ok"    - 2xx response, packet delivered.
            "drop"  - 4xx response, retry won't help.
            "retry" - 5xx or network failure, caller should buffer.
        """
        req = Request(
            self._url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
                "X-Mesh-Seq": str(seq),
            },
        )
        try:
            with urlopen(req, timeout=self._timeout) as resp:
                resp.read()  # drain socket; urlopen raises on non-2xx
                return "ok"
        except HTTPError as exc:
            if 400 <= exc.code < 500:
                logger.warning(
                    "gateway rejected packet seq=%d (HTTP %d) — dropping: %s",
                    seq,
                    exc.code,
                    exc.reason,
                )
                return "drop"
            logger.debug("gateway returned %d for seq=%d — will retry", exc.code, seq)
            return "retry"
        except (URLError, OSError) as exc:
            logger.debug("gateway unreachable for seq=%d (%s) — will retry", seq, exc)
            return "retry"


__all__ = [
    "AggregateClient",
    "SendResult",
    "TransportError",
    "USER_AGENT",
    "build_gateway_url",
]
