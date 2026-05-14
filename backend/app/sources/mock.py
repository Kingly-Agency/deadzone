from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.sources.base import BleObservation
from app.spatial.venue import zone_for_rssi
from app.traces import TraceStore


class MockFromTraceSource:
    def __init__(self, store: TraceStore, seed: int) -> None:
        self.store = store
        self.seed = seed

    def observations(self) -> list[BleObservation]:
        trace_id = self.store.latest_trace_id()
        if not trace_id:
            return self._demo_observations()
        source = self.store.read(trace_id)
        if not source:
            return self._demo_observations()
        rng = random.Random(f"{self.seed}:{trace_id}")
        shifted: list[BleObservation] = []
        device_aliases = {
            beacon_hash: f"mock-{index}"
            for index, beacon_hash in enumerate(sorted({obs.beacon_hash for obs in source}))
        }
        for index, item in enumerate(source[:120]):
            rssi_shift = rng.randint(-4, 4)
            shifted.append(
                item.model_copy(
                    update={
                        "beacon_hash": device_aliases[item.beacon_hash],
                        "rssi": max(-100, min(-35, item.rssi + rssi_shift)),
                        "timestamp": item.timestamp + timedelta(milliseconds=index * 25),
                    }
                )
            )
        return shifted

    def _demo_observations(self) -> list[BleObservation]:
        rng = random.Random(f"{self.seed}:demo")
        now = datetime.now(timezone.utc)
        devices = [
            ("mock-near-01", -52),
            ("mock-near-02", -58),
            ("mock-mid-01", -66),
            ("mock-mid-02", -69),
            ("mock-far-01", -75),
            ("mock-edge-01", -91),
        ]
        observations: list[BleObservation] = []
        for index, (device_id, base_rssi) in enumerate(devices):
            rssi = max(-100, min(-35, base_rssi + rng.randint(-3, 3)))
            observations.append(
                BleObservation(
                    timestamp=now - timedelta(seconds=len(devices) - index),
                    receiver_id="local-ble-scanner",
                    beacon_hash=device_id,
                    rssi=rssi,
                    zone_id=zone_for_rssi(rssi),
                )
            )
        return observations
