from __future__ import annotations

import random
from datetime import timedelta

from app.sources.base import BleObservation
from app.traces import TraceStore


class MockFromTraceSource:
    def __init__(self, store: TraceStore, seed: int) -> None:
        self.store = store
        self.seed = seed

    def observations(self) -> list[BleObservation]:
        trace_id = self.store.latest_trace_id()
        if not trace_id:
            return []
        source = self.store.read(trace_id)
        if not source:
            return []
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
