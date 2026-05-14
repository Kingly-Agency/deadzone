"""DeadZone mesh CLI entry: `python -m app.mesh {gateway|node}`.

Standalone satellite — does NOT import from app.main, app.runtime, app.api,
app.sources, or app.spatial.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
from typing import Sequence

from app.mesh.app import create_app
from app.mesh.node import MeshNode, MockNodeScanner
from app.mesh.transport import AggregateClient


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m app.mesh",
        description="DeadZone WiFi-faked mesh CLI",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    gw = sub.add_parser("gateway", help="Run the mesh gateway HTTP server")
    gw.add_argument("--host", default="0.0.0.0")
    gw.add_argument("--port", type=int, default=8001)
    gw.add_argument("--gateway-id", default="mesh-gateway-local")
    gw.add_argument("--log-level", default="info")

    nd = sub.add_parser("node", help="Run a mesh node that POSTs aggregates to a gateway")
    nd.add_argument("--gateway", required=True, help="Gateway base URL, e.g. http://192.168.1.42:8001")
    nd.add_argument("--node-id", required=True)
    nd.add_argument("--interval", type=float, default=1.0)
    nd.add_argument("--scanner", choices=["mock"], default="mock",
                    help="Which scanner to use. Only 'mock' is wired today; 'ble' is reserved for the BE-agent scanner.")
    nd.add_argument("--position", type=float, nargs=2, metavar=("X", "Y"))
    nd.add_argument("--seed", type=int, default=1337)
    nd.add_argument("--log-level", default="info")
    return p


def run_gateway(args: argparse.Namespace) -> int:
    import uvicorn  # local import: only the gateway path needs it
    _configure_logging(args.log_level)
    app = create_app(gateway_id=args.gateway_id)
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())
    return 0


async def _run_node_async(args: argparse.Namespace) -> int:
    from app.mesh.models import Position  # local import to keep module-load light

    scanner = MockNodeScanner(seed=args.seed, interval_s=args.interval)
    client = AggregateClient(args.gateway)
    position = Position(x=args.position[0], y=args.position[1]) if args.position else None
    node = MeshNode(
        node_id=args.node_id,
        client=client,
        scanner=scanner,
        interval_s=args.interval,
        position=position,
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _stop(*_a) -> None:
        stop_event.set()

    # SIGTERM / SIGINT graceful shutdown
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, _stop)
        except (NotImplementedError, RuntimeError):
            # Windows / non-main thread fallback
            signal.signal(sig, lambda *_a: _stop())

    task = asyncio.create_task(node.run())
    await stop_event.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    return 0


def run_node(args: argparse.Namespace) -> int:
    _configure_logging(args.log_level)
    return asyncio.run(_run_node_async(args))


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.cmd == "gateway":
        return run_gateway(args)
    if args.cmd == "node":
        return run_node(args)
    return 2  # unreachable due to required=True


if __name__ == "__main__":
    sys.exit(main())
