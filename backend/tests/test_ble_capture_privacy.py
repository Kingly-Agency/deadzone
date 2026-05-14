from __future__ import annotations

from datetime import datetime, timezone

from app.sources.ble import normalize_ble_advertisement
from app.traces import TraceStore


def test_ble_normalization_discards_raw_identifier_and_scopes_token_by_trace(tmp_path):
    raw = "AA:BB:CC:DD:EE:FF"
    first = normalize_ble_advertisement(
        raw_identifier=raw,
        rssi=-54,
        receiver_id="local-ble-scanner",
        trace_id="capture-a",
        salt="test-salt",
        timestamp=datetime(2026, 5, 14, tzinfo=timezone.utc),
    )
    second = normalize_ble_advertisement(
        raw_identifier=raw,
        rssi=-54,
        receiver_id="local-ble-scanner",
        trace_id="capture-b",
        salt="test-salt",
        timestamp=datetime(2026, 5, 14, tzinfo=timezone.utc),
    )

    assert first.beacon_hash != raw
    assert first.beacon_hash != second.beacon_hash
    assert first.zone_id == "near-scanner"
    assert raw not in first.model_dump_json()

    store = TraceStore(tmp_path, "public-id-salt")
    store.append("capture-a", first)
    persisted = store.path_for("capture-a").read_text(encoding="utf-8")

    assert raw not in persisted
    assert "beacon_hash" in persisted
    assert "AA:BB" not in persisted
