from __future__ import annotations

import hashlib
import hmac
import re
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path

from app.domain.models import ReplayScenario
from app.sources.base import BleObservation

TRACE_ID_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


def safe_trace_id(trace_id: str) -> str:
    cleaned = TRACE_ID_RE.sub("-", trace_id.strip()).strip(".-")
    return cleaned or "capture"


class TraceStore:
    def __init__(self, capture_dir: Path, public_id_salt: str) -> None:
        self.capture_dir = capture_dir
        self.public_id_salt = public_id_salt
        self.capture_dir.mkdir(parents=True, exist_ok=True)

    def new_trace_id(self) -> str:
        return datetime.now(timezone.utc).strftime("ble-%Y%m%d-%H%M%S")

    def path_for(self, trace_id: str) -> Path:
        return self.capture_dir / f"{safe_trace_id(trace_id)}.jsonl"

    def public_label(self, trace_id: str) -> str:
        return f"local BLE trace {self.public_id(trace_id)}"

    def public_id(self, trace_id: str) -> str:
        return public_trace_id(trace_id, self.public_id_salt)

    def trace_id_for_public_id(self, public_id: str) -> str | None:
        return next((trace_id for trace_id in self.list_trace_ids() if self.public_id(trace_id) == public_id), None)

    def append(self, trace_id: str, observation: BleObservation) -> None:
        path = self.path_for(trace_id)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(observation.model_dump_json() + "\n")

    def read(self, trace_id: str) -> list[BleObservation]:
        path = self.path_for(trace_id)
        if not path.exists():
            return []
        observations: list[BleObservation] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    observations.append(BleObservation.model_validate_json(stripped))
        return observations

    def list_trace_ids(self) -> list[str]:
        return sorted(path.stem for path in self.capture_dir.glob("*.jsonl"))

    def latest_trace_id(self) -> str | None:
        trace_ids = self.list_trace_ids()
        return trace_ids[-1] if trace_ids else None

    def scenarios(self) -> list[ReplayScenario]:
        scenarios: list[ReplayScenario] = []
        for trace_id in self.list_trace_ids():
            observations = self.read(trace_id)
            if observations:
                scenarios.append(scenario_from_observations(trace_id, observations, self.public_id_salt))
        return scenarios


def scenario_from_observations(
    trace_id: str,
    observations: Iterable[BleObservation],
    public_id_salt: str,
) -> ReplayScenario:
    obs = list(observations)
    if obs:
        start = min(item.timestamp for item in obs)
        end = max(item.timestamp for item in obs)
        duration_s = max(1.0, (end - start).total_seconds())
        devices = len({item.beacon_hash for item in obs})
    else:
        duration_s = 1.0
        devices = 0
    public_id = public_trace_id(trace_id, public_id_salt)
    return ReplayScenario(
        id=public_id,
        name=f"BLE capture {public_trace_label(trace_id, public_id_salt)}",
        description=f"Locally captured BLE trace with {len(obs)} observations and {devices} devices.",
        duration_s=duration_s,
        seed=public_id,
        available_speeds=[0.25, 0.5, 1, 2, 4],
    )


def public_trace_id(trace_id: str, salt: str) -> str:
    digest = hmac.new(salt.encode("utf-8"), trace_id.encode("utf-8"), hashlib.sha256).hexdigest()[:12]
    return f"ble-{digest}"


def public_trace_label(trace_id: str, salt: str) -> str:
    digest = hmac.new(salt.encode("utf-8"), trace_id.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
    return f"local-{digest}"
