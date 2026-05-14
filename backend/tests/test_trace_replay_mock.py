from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.domain.models import ErrorResponse, ReplayControlRequest, StreamState
from app.runtime.engine import DeadZoneEngine
from app.settings import Settings
from app.sources.ble import normalize_ble_advertisement


def make_engine(tmp_path) -> DeadZoneEngine:
    return DeadZoneEngine(
        Settings(
            mode="ble",
            seed=42,
            data_dir=tmp_path,
            capture_salt="test-salt",
        )
    )


def append_trace(engine: DeadZoneEngine, trace_id: str = "field-capture") -> None:
    base = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)
    samples = [
        ("AA:AA:AA:AA:AA:01", -52, 0),
        ("AA:AA:AA:AA:AA:02", -66, 1),
        ("AA:AA:AA:AA:AA:01", -72, 2),
        ("AA:AA:AA:AA:AA:03", -91, 3),
    ]
    for raw, rssi, offset_s in samples:
        engine.store.append(
            trace_id,
            normalize_ble_advertisement(
                raw_identifier=raw,
                rssi=rssi,
                receiver_id="local-ble-scanner",
                trace_id=trace_id,
                salt="test-salt",
                timestamp=base + timedelta(seconds=offset_s),
            ),
        )


def test_replay_and_mock_are_unavailable_until_ble_trace_exists(tmp_path):
    engine = make_engine(tmp_path)

    replay_responses = [
        engine.control_replay(ReplayControlRequest(action=action))
        for action in ["play", "pause", "restart", "seek", "set_speed"]
    ]
    load_response = engine.control_replay(ReplayControlRequest(action="load", scenario_id="missing"))
    mock_response = engine.set_mode("mock")

    assert all(isinstance(response, ErrorResponse) for response in replay_responses)
    assert {response.code for response in replay_responses if isinstance(response, ErrorResponse)} == {
        "capture_required"
    }
    assert isinstance(load_response, ErrorResponse)
    assert load_response.code == "trace_not_found"
    assert isinstance(mock_response, ErrorResponse)
    assert mock_response.code == "mode_unavailable"


def test_captured_ble_trace_becomes_replay_scenario(tmp_path):
    engine = make_engine(tmp_path)
    append_trace(engine)
    engine.store.path_for("empty-capture").write_text("", encoding="utf-8")

    scenarios = engine.store.scenarios()
    scenario_id = scenarios[0].id
    assert len(scenarios) == 1
    assert scenario_id.startswith("ble-")
    assert "field-capture" not in scenarios[0].name

    response = engine.control_replay(ReplayControlRequest(action="load", scenario_id=scenario_id))
    assert isinstance(response, StreamState)
    assert response.mode == "replay"
    assert scenario_id == response.scenario_id
    assert "field-capture" not in response.source_label

    engine.control_replay(ReplayControlRequest(action="play"))
    snapshot = engine.snapshot()
    assert snapshot.stream.mode == "replay"
    assert snapshot.metrics.estimated_devices == 1

    ended = engine.control_replay(ReplayControlRequest(action="seek", position_s=999))
    assert isinstance(ended, StreamState)
    assert ended.playback_state == "ended"
    assert ended.clock.replay_position_s == ended.duration_s

    bad_speed = engine.control_replay(ReplayControlRequest(action="set_speed", speed=-1))
    assert isinstance(bad_speed, ErrorResponse)
    assert bad_speed.code == "invalid_replay_speed"


def test_mock_is_derived_from_local_ble_trace(tmp_path):
    engine = make_engine(tmp_path)
    append_trace(engine)

    response = engine.set_mode("mock")
    assert isinstance(response, StreamState)

    snapshot = engine.snapshot()
    assert snapshot.stream.mode == "mock"
    assert "derived from local BLE trace" in snapshot.stream.source_label
    assert "field-capture" not in snapshot.stream.source_label
    assert snapshot.metrics.estimated_devices >= 1


def test_ble_aggregation_counts_latest_zone_per_device(tmp_path):
    engine = make_engine(tmp_path)
    append_trace(engine)

    snapshot = engine.snapshot()

    assert snapshot.metrics.estimated_devices == 3


def test_mock_preserves_captured_device_continuity(tmp_path):
    engine = make_engine(tmp_path)
    append_trace(engine)

    mock_observations = engine.mock.observations()

    assert len({item.beacon_hash for item in mock_observations}) == 3
    assert mock_observations[0].beacon_hash == mock_observations[2].beacon_hash
    assert mock_observations[0].beacon_hash != mock_observations[1].beacon_hash


def test_public_trace_ids_are_salt_scoped(tmp_path):
    first = make_engine(tmp_path / "first")
    second = DeadZoneEngine(
        Settings(mode="ble", seed=42, data_dir=tmp_path / "second", capture_salt="other-salt")
    )

    assert first.store.public_id("field-capture") != second.store.public_id("field-capture")
