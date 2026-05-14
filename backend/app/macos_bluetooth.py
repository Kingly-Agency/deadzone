from __future__ import annotations

import json
import os
import shutil
import shlex
import stat
import subprocess
import sys
import time
import uuid
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

BLUETOOTH_CHILD_ENV = "DEADZONE_MACOS_BLUETOOTH_CHILD"
USAGE_DESCRIPTION = (
    "DeadZone scans nearby Bluetooth Low Energy advertisements to build aggregate "
    "crowd-density demo data."
)


def requires_launcher() -> bool:
    return sys.platform == "darwin" and os.environ.get(BLUETOOTH_CHILD_ENV) != "1"


def disabled_reason() -> str | None:
    if not requires_launcher():
        return None
    return (
        "macOS Bluetooth requires the DeadZone permission launcher. Start with "
        "`uv run deadzone-backend` or run a one-shot scan with `uv run deadzone-scan`."
    )


def run_in_bluetooth_app(argv: list[str], *, cwd: Path | None = None) -> int:
    if sys.platform != "darwin":
        raise RuntimeError("The Bluetooth permission launcher is only used on macOS.")

    cwd = cwd or Path.cwd()
    state_dir = cwd / ".deadzone"
    run_dir = state_dir / "run"
    log_dir = state_dir / "logs"
    run_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    run_id = uuid.uuid4().hex[:12]
    config_path = run_dir / f"{run_id}.json"
    log_path = log_dir / f"{run_id}-{'-'.join(argv[:1]) or 'run'}.log"
    exit_path = run_dir / f"{run_id}.exit.json"

    config = {
        "argv": argv,
        "cwd": str(cwd),
        "env": {
            BLUETOOTH_CHILD_ENV: "1",
            "DEADZONE_MACOS_BLUETOOTH_LOG": str(log_path),
        },
        "log_path": str(log_path),
        "exit_path": str(exit_path),
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    bundle = ensure_bundle(cwd)
    process = subprocess.Popen(["open", "-W", "-n", str(bundle), "--args", str(config_path)])

    offset = 0
    try:
        while process.poll() is None:
            offset = _print_new_log(log_path, offset)
            time.sleep(0.25)
        offset = _print_new_log(log_path, offset)
    except KeyboardInterrupt:
        process.terminate()
        raise

    if exit_path.exists():
        try:
            return int(json.loads(exit_path.read_text(encoding="utf-8")).get("code", 1))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return 1
    return process.returncode or 0


def ensure_bundle(cwd: Path) -> Path:
    bundle = cwd / ".deadzone" / "DeadZone Bluetooth.app"
    contents = bundle / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    lib = contents / "lib"
    macos.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)
    lib.mkdir(parents=True, exist_ok=True)

    python_exe = Path(getattr(sys, "_base_executable", sys.executable)).resolve()
    python_home = Path(sys.base_prefix).resolve()
    python_name = f"python{sys.version_info.major}.{sys.version_info.minor}"
    bundled_python = macos / python_name
    bundled_lib = lib / f"libpython{sys.version_info.major}.{sys.version_info.minor}.dylib"
    source_lib = python_home / "lib" / bundled_lib.name

    if not bundled_python.exists() or bundled_python.stat().st_mtime < python_exe.stat().st_mtime:
        shutil.copy2(python_exe, bundled_python)
    if source_lib.exists() and (
        not bundled_lib.exists() or bundled_lib.stat().st_mtime < source_lib.stat().st_mtime
    ):
        shutil.copy2(source_lib, bundled_lib)
    bundled_python.chmod(bundled_python.stat().st_mode | stat.S_IXUSR)

    python_path = _python_path_for_child(cwd)
    launcher = macos / "deadzone-launch"
    launcher.write_text(
        "\n".join(
            [
                "#!/bin/sh",
                f"export PYTHONHOME={shlex.quote(str(python_home))}",
                f"export PYTHONPATH={shlex.quote(python_path)}",
                f"exec \"$(dirname \"$0\")/{python_name}\" -m app.macos_bluetooth --child \"$@\"",
                "",
            ]
        ),
        encoding="utf-8",
    )
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    (contents / "Info.plist").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleExecutable</key>
  <string>deadzone-launch</string>
  <key>CFBundleIdentifier</key>
  <string>com.kingly.deadzone.bluetooth</string>
  <key>CFBundleName</key>
  <string>DeadZone Bluetooth</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>NSBluetoothAlwaysUsageDescription</key>
  <string>{USAGE_DESCRIPTION}</string>
  <key>NSBluetoothPeripheralUsageDescription</key>
  <string>{USAGE_DESCRIPTION}</string>
</dict>
</plist>
""",
        encoding="utf-8",
    )
    return bundle


def child_main(config_path: str) -> int:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    log_path = Path(config["log_path"])
    exit_path = Path(config["exit_path"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    exit_path.parent.mkdir(parents=True, exist_ok=True)

    code = 1
    with log_path.open("a", encoding="utf-8") as log_file:
        with redirect_stdout(log_file), redirect_stderr(log_file):
            try:
                os.chdir(config["cwd"])
                os.environ.update(_string_dict(config.get("env", {})))
                from app.cli import main

                code = int(main(list(config["argv"])))
            except SystemExit as exc:
                code = int(exc.code) if isinstance(exc.code, int) else 1
            except Exception as exc:  # pragma: no cover - last-resort launcher diagnostics
                print(f"DeadZone Bluetooth launcher failed: {type(exc).__name__}: {exc}", flush=True)
                code = 1
    exit_path.write_text(json.dumps({"code": code}), encoding="utf-8")
    return code


def _python_path_for_child(cwd: Path) -> str:
    paths: list[str] = [str(cwd)]
    for item in sys.path:
        path = str(cwd) if item == "" else item
        if path not in paths:
            paths.append(path)
    return os.pathsep.join(paths)


def _print_new_log(path: Path, offset: int) -> int:
    if not path.exists():
        return offset
    with path.open("r", encoding="utf-8", errors="replace") as log_file:
        log_file.seek(offset)
        chunk = log_file.read()
        if chunk:
            print(chunk, end="", flush=True)
        return log_file.tell()


def _string_dict(value: dict[str, Any]) -> dict[str, str]:
    return {str(key): str(item) for key, item in value.items()}


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--child":
        return child_main(sys.argv[2])
    print("This module is launched internally by DeadZone.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
