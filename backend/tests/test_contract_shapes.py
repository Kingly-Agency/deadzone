from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_config_and_snapshot_contract_shapes():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["service"] == "deadzone-api"
    assert health.json()["mode"] == "ble"

    config = client.get("/api/v1/config").json()
    assert config["active_mode"] == "ble"
    assert config["available_modes"] == ["ble", "mock"]
    assert "mock" not in config["disabled_modes"]
    assert "replay" not in config["available_modes"]
    assert config["venue"]["id"] == "ble-capture-floor"

    snapshot = client.get("/api/v1/snapshot").json()
    assert set(snapshot) == {
        "stream",
        "venue",
        "zones",
        "flow_vectors",
        "alerts",
        "sensors",
        "mesh_links",
        "metrics",
    }
    assert snapshot["stream"]["mode"] == "ble"
    assert snapshot["sensors"][0]["id"] == "local-ble-scanner"
    assert "beacon_hash" not in str(snapshot)


def test_websocket_live_uses_stream_envelope():
    client = TestClient(app)
    with client.websocket_connect("/ws/live") as ws:
        envelope = ws.receive_json()
        update = ws.receive_json()
        error = None
        for _ in range(8):
            candidate = ws.receive_json()
            if candidate["type"] == "error":
                error = candidate
                break

    assert envelope["type"] == "snapshot"
    assert envelope["sequence"] >= 1
    assert envelope["mode"] == envelope["payload"]["stream"]["mode"]
    assert "payload" in envelope
    assert update["type"] == "zone_update"
    assert update["sequence"] > envelope["sequence"]
    assert error is not None
    assert error["payload"]["code"] == "mode_unavailable"
