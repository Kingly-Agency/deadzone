from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

import uvicorn

from app.macos_bluetooth import disabled_reason as macos_disabled_reason
from app.macos_bluetooth import requires_launcher, run_in_bluetooth_app
from app.runtime.engine import DeadZoneEngine
from app.settings import load_settings


def serve() -> int:
    return main(["serve", *sys.argv[1:]])


def scan() -> int:
    return main(["scan", *sys.argv[1:]])


def permissions() -> int:
    return main(["permissions", *sys.argv[1:]])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="deadzone")
    subcommands = parser.add_subparsers(dest="command", required=True)

    serve_parser = subcommands.add_parser("serve", help="Run the DeadZone backend API")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.add_argument(
        "--no-macos-bluetooth-app",
        action="store_true",
        help="Run directly instead of using the macOS Bluetooth permission launcher.",
    )

    scan_parser = subcommands.add_parser("scan", help="Run a local BLE scan and persist a trace")
    scan_parser.add_argument("--duration", type=float, default=8.0)
    scan_parser.add_argument("--trace-id", default=None)
    scan_parser.add_argument(
        "--no-macos-bluetooth-app",
        action="store_true",
        help="Run directly instead of using the macOS Bluetooth permission launcher.",
    )

    permission_parser = subcommands.add_parser(
        "permissions",
        help="Trigger the macOS Bluetooth permission prompt with a short scan",
    )
    permission_parser.add_argument("--duration", type=float, default=3.0)

    args = parser.parse_args(argv)
    if args.command == "serve":
        if requires_launcher() and not args.no_macos_bluetooth_app:
            return run_in_bluetooth_app(
                ["serve", "--host", args.host, "--port", str(args.port), "--no-macos-bluetooth-app"],
                cwd=Path.cwd(),
            )
        return run_server(host=args.host, port=args.port)
    if args.command == "scan":
        if requires_launcher() and not args.no_macos_bluetooth_app:
            command = ["scan", "--duration", str(args.duration), "--no-macos-bluetooth-app"]
            if args.trace_id:
                command.extend(["--trace-id", args.trace_id])
            return run_in_bluetooth_app(command, cwd=Path.cwd())
        return asyncio.run(run_scan(duration_s=args.duration, trace_id=args.trace_id))
    if args.command == "permissions":
        return main(["scan", "--duration", str(args.duration)])
    parser.error(f"Unknown command: {args.command}")
    return 2


def run_server(*, host: str, port: int) -> int:
    print(f"DeadZone backend listening on http://{host}:{port}", flush=True)
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
    return 0


async def run_scan(*, duration_s: float, trace_id: str | None) -> int:
    reason = macos_disabled_reason()
    if reason:
        print(reason, file=sys.stderr)
        return 2

    engine = DeadZoneEngine(load_settings())
    status = await engine.start_capture(trace_id=trace_id, duration_s=None)
    if status.disabled_reason:
        print(status.disabled_reason, file=sys.stderr)
        return 2

    print(
        f"BLE scan started: trace_id={status.trace_id} duration={duration_s:.1f}s",
        flush=True,
    )
    await asyncio.sleep(duration_s)
    status = await engine.stop_capture()
    print(
        f"BLE scan complete: trace_id={status.trace_id} observations={status.observations}",
        flush=True,
    )
    if status.observations == 0:
        print("No BLE advertisements were observed. Bluetooth was available, but the room was quiet.")
    return 0
