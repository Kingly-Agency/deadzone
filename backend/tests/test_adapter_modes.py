from __future__ import annotations

import sys
import types

from fastapi.testclient import TestClient

from app import main as app_main
from app.macos_bluetooth import BLUETOOTH_CHILD_ENV
from app.runtime.engine import DeadZoneEngine
from app.main import app
from app.settings import Settings


def test_unavailable_modes_return_explicit_409_reasons():
    client = TestClient(app)

    wifi = client.post("/api/v1/mode", json={"mode": "wifi"})
    assert wifi.status_code == 409
    assert "Wi-Fi monitor capture is not enabled" in wifi.json()["message"]

    replay = client.post("/api/v1/mode", json={"mode": "replay"})
    assert replay.status_code == 409
    assert "not exposed" in replay.json()["message"]

    replay_control = client.post("/api/v1/replay/control", json={"action": "pause"})
    assert replay_control.status_code == 409
    assert replay_control.json()["code"] == "capture_required"


def test_capture_start_reports_ble_dependency_or_starts_capture():
    client = TestClient(app)

    response = client.post("/api/v1/capture/start", json={"trace_id": "api-capture"})
    assert response.status_code in {200, 409}
    body = response.json()
    if response.status_code == 409:
        assert body["backend"] == "ble"
        assert body["disabled_reason"]
    else:
        assert body["backend"] == "ble"
        assert body["trace_id"] == "api-capture"
        client.post("/api/v1/capture/stop")


def test_macos_direct_capture_reports_launcher_requirement(monkeypatch, tmp_path):
    monkeypatch.setattr("app.macos_bluetooth.sys.platform", "darwin")
    monkeypatch.delenv(BLUETOOTH_CHILD_ENV, raising=False)
    engine = DeadZoneEngine(
        Settings(mode="ble", seed=42, data_dir=tmp_path, capture_salt="test-salt")
    )

    assert "permission launcher" in (engine.capture.disabled_reason or "")


async def test_capture_start_failure_preserves_current_mode(monkeypatch, tmp_path):
    class FailingScanner:
        def __init__(self, detection_callback):
            self.detection_callback = detection_callback

        async def start(self):
            raise PermissionError("bluetooth denied")

        async def stop(self):
            return None

    monkeypatch.setitem(sys.modules, "bleak", types.SimpleNamespace(BleakScanner=FailingScanner))
    monkeypatch.setenv(BLUETOOTH_CHILD_ENV, "1")
    engine = DeadZoneEngine(
        Settings(mode="mock", seed=42, data_dir=tmp_path, capture_salt="test-salt")
    )

    status = await engine.start_capture("denied", None)

    assert status.disabled_reason == "BLE scanner failed to start: bluetooth denied"
    assert engine.active_mode == "mock"
    assert engine.capture.trace_id is None


def test_ble_mode_auto_starts_live_capture_for_streaming(monkeypatch, tmp_path):
    class FakeScanner:
        def __init__(self, detection_callback):
            self.detection_callback = detection_callback
            self.started = False

        async def start(self):
            self.started = True
            self.detection_callback(
                types.SimpleNamespace(address="AA:BB:CC:DD:EE:01"),
                types.SimpleNamespace(rssi=-54),
            )

        async def stop(self):
            self.started = False

    monkeypatch.setitem(sys.modules, "bleak", types.SimpleNamespace(BleakScanner=FakeScanner))
    monkeypatch.setenv(BLUETOOTH_CHILD_ENV, "1")
    engine = DeadZoneEngine(
        Settings(mode="ble", seed=42, data_dir=tmp_path, capture_salt="test-salt")
    )

    monkeypatch.setattr(app_main, "engine", engine)
    client = TestClient(app)
    response = client.get("/api/v1/snapshot")
    snapshot = response.json()
    status = engine.capture.status()

    assert response.status_code == 200
    assert status is not None
    assert status.active is True
    assert status.observations == 1
    assert snapshot["stream"]["mode"] == "ble"
    assert snapshot["stream"]["connected"] is True
    assert snapshot["stream"]["freshness"] == "live"
    assert snapshot["metrics"]["estimated_devices"] == 1

    client.post("/api/v1/capture/stop")
