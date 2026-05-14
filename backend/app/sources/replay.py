from __future__ import annotations

import time
from datetime import datetime, timezone

from app.domain.models import ErrorResponse, ReplayControlRequest, StreamClock, StreamState
from app.sources.base import BleObservation
from app.traces import TraceStore


class ReplayController:
    def __init__(self, store: TraceStore) -> None:
        self.store = store
        self.scenario_id: str | None = None
        self.public_scenario_id: str | None = None
        self.playing = False
        self.position_s = 0.0
        self.speed = 1.0
        self._started_monotonic: float | None = None
        self._started_position = 0.0

    def control(self, request: ReplayControlRequest, sequence: int) -> StreamState | ErrorResponse:
        if request.action == "load":
            scenario_id = self._resolve_requested_trace(request.scenario_id)
            if not scenario_id or not self.store.read(scenario_id):
                return ErrorResponse(
                    code="trace_not_found",
                    message="Replay requires a locally captured BLE trace.",
                    recoverable=True,
                    detail={"scenario_id": request.scenario_id},
                )
            self.scenario_id = scenario_id
            self.public_scenario_id = self.store.public_id(scenario_id)
            self.position_s = 0.0
            self.playing = False
        elif request.action == "play":
            if not self._ensure_loaded():
                return self._missing_trace_error()
            if self.playback_state() == "ended":
                self.position_s = 0.0
            self.playing = True
            self._started_monotonic = time.monotonic()
            self._started_position = self.position_s
        elif request.action == "pause":
            if not self._ensure_loaded():
                return self._missing_trace_error()
            self.position_s = self.current_position()
            self.playing = False
            self._started_monotonic = None
        elif request.action == "restart":
            if not self._ensure_loaded():
                return self._missing_trace_error()
            self.position_s = 0.0
            self.playing = True
            self._started_monotonic = time.monotonic()
            self._started_position = 0.0
        elif request.action == "seek":
            if not self._ensure_loaded():
                return self._missing_trace_error()
            self.position_s = min(self.duration_s(), max(0.0, request.position_s or 0.0))
            if self.playing:
                self._started_monotonic = time.monotonic()
                self._started_position = self.position_s
        elif request.action == "set_speed":
            if not self._ensure_loaded():
                return self._missing_trace_error()
            if request.speed not in ALLOWED_SPEEDS:
                return ErrorResponse(
                    code="invalid_replay_speed",
                    message="Replay speed must be one of 0.25, 0.5, 1, 2, or 4.",
                    recoverable=True,
                    detail={"speed": request.speed, "allowed": sorted(ALLOWED_SPEEDS)},
                )
            self.position_s = self.current_position()
            self.speed = request.speed or 1.0
            if self.playing:
                self._started_monotonic = time.monotonic()
                self._started_position = self.position_s
        return self.stream_state(sequence)

    def observations_window(self, window_s: float = 8.0) -> list[BleObservation]:
        if not self._ensure_loaded() or not self.scenario_id:
            return []
        observations = self.store.read(self.scenario_id)
        if not observations:
            return []
        start = min(item.timestamp for item in observations)
        position = self.current_position()
        lower = max(0.0, position - window_s)
        window = [
            item
            for item in observations
            if lower <= (item.timestamp - start).total_seconds() <= position
        ]
        return window or observations[:1]

    def stream_state(self, sequence: int) -> StreamState:
        playback_state = self.playback_state()
        return StreamState(
            mode="replay",
            connected=self.scenario_id is not None,
            sequence=sequence,
            source_label=(
                f"Replay: {self.store.public_label(self.scenario_id)}"
                if self.scenario_id
                else "Replay unavailable: capture BLE first"
            ),
            freshness="fresh" if self.scenario_id else "offline",
            clock=StreamClock(
                timestamp=datetime.now(timezone.utc),
                replay_position_s=self.current_position(),
                speed=self.speed,
            ),
            playback_state=playback_state,
            scenario_id=self.public_scenario_id,
            duration_s=self.duration_s() if self.scenario_id else None,
        )

    def current_position(self) -> float:
        if not self.playing or self._started_monotonic is None:
            return min(self.position_s, self.duration_s())
        position = self._started_position + (time.monotonic() - self._started_monotonic) * self.speed
        duration = self.duration_s()
        if position >= duration:
            self.position_s = duration
            self.playing = False
            self._started_monotonic = None
            return duration
        return position

    def duration_s(self) -> float:
        if not self.scenario_id:
            return 0.0
        observations = self.store.read(self.scenario_id)
        if not observations:
            return 0.0
        start = min(item.timestamp for item in observations)
        end = max(item.timestamp for item in observations)
        return max(1.0, (end - start).total_seconds())

    def playback_state(self) -> str:
        if not self.scenario_id:
            return "idle"
        if self.playing:
            if self.current_position() >= self.duration_s():
                return "ended"
            return "playing"
        if self.current_position() >= self.duration_s():
            return "ended"
        return "paused"

    def _ensure_loaded(self) -> bool:
        if self.scenario_id and self.store.read(self.scenario_id):
            return True
        latest = self.store.latest_trace_id()
        if latest and self.store.read(latest):
            self.scenario_id = latest
            self.public_scenario_id = self.store.public_id(latest)
            return True
        return False

    def _resolve_requested_trace(self, requested_id: str | None) -> str | None:
        if requested_id:
            return self.store.trace_id_for_public_id(requested_id)
        return self.store.latest_trace_id()

    def _missing_trace_error(self) -> ErrorResponse:
        return ErrorResponse(
            code="capture_required",
            message="Replay is unavailable until a BLE capture has been recorded locally.",
            recoverable=True,
        )
ALLOWED_SPEEDS = {0.25, 0.5, 1.0, 2.0, 4.0}
