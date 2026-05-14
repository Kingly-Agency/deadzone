from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from app.domain.models import CaptureStatus
from app.macos_bluetooth import disabled_reason as macos_bluetooth_disabled_reason
from app.privacy import capture_scoped_token
from app.settings import Settings
from app.spatial.venue import zone_for_rssi
from app.sources.base import BleObservation
from app.traces import TraceStore, safe_trace_id


def bleak_disabled_reason() -> str | None:
    macos_reason = macos_bluetooth_disabled_reason()
    if macos_reason:
        return macos_reason
    try:
        import bleak  # noqa: F401
    except ModuleNotFoundError:
        return "Install DeadZone backend dependencies with `uv sync` or run `uv run deadzone-backend`."
    except Exception as exc:  # pragma: no cover - platform-specific import failures
        return f"BLE stack unavailable: {exc}"
    return None


def normalize_ble_advertisement(
    *,
    raw_identifier: str,
    rssi: int,
    receiver_id: str,
    trace_id: str,
    salt: str,
    timestamp: datetime | None = None,
) -> BleObservation:
    return BleObservation(
        timestamp=timestamp or datetime.now(timezone.utc),
        receiver_id=receiver_id,
        beacon_hash=capture_scoped_token(raw_identifier, salt=salt, trace_id=trace_id),
        rssi=rssi,
        zone_id=zone_for_rssi(rssi),
    )


class BleCaptureManager:
    def __init__(self, settings: Settings, store: TraceStore) -> None:
        self.settings = settings
        self.store = store
        self.trace_id: str | None = None
        self.started_at: datetime | None = None
        self.latest_observation_at: datetime | None = None
        self.observations = 0
        self._scanner: Any | None = None
        self._stop_task: asyncio.Task[None] | None = None

    @property
    def disabled_reason(self) -> str | None:
        return bleak_disabled_reason()

    @property
    def active(self) -> bool:
        return self._scanner is not None

    async def start(self, trace_id: str | None = None, duration_s: float | None = None) -> CaptureStatus:
        disabled = self.disabled_reason
        if disabled:
            return self.status(disabled_reason=disabled)
        if self.active:
            return self.status()

        from bleak import BleakScanner  # type: ignore[import-not-found]

        self.trace_id = safe_trace_id(trace_id or self.store.new_trace_id())
        self.started_at = datetime.now(timezone.utc)
        self.latest_observation_at = None
        self.observations = 0

        def on_advertisement(device: Any, advertisement_data: Any) -> None:
            raw_identifier = getattr(device, "address", None) or getattr(device, "name", "unknown")
            rssi = getattr(advertisement_data, "rssi", None)
            if rssi is None:
                rssi = getattr(device, "rssi", -100)
            observation = normalize_ble_advertisement(
                raw_identifier=str(raw_identifier),
                rssi=int(rssi),
                receiver_id="local-ble-scanner",
                trace_id=self.trace_id or "capture",
                salt=self.settings.capture_salt,
            )
            if self.trace_id:
                self.store.append(self.trace_id, observation)
            self.observations += 1
            self.latest_observation_at = observation.timestamp

        self._scanner = BleakScanner(detection_callback=on_advertisement)
        try:
            await self._scanner.start()
        except Exception as exc:  # pragma: no cover - depends on local OS permissions
            self._scanner = None
            self.trace_id = None
            self.started_at = None
            self.latest_observation_at = None
            self.observations = 0
            return self.status(disabled_reason=f"BLE scanner failed to start: {exc}")
        if duration_s:
            self._stop_task = asyncio.create_task(self._stop_after(duration_s))
        return self.status()

    async def stop(self) -> CaptureStatus:
        current_task = asyncio.current_task()
        if self._stop_task and self._stop_task is not current_task:
            self._stop_task.cancel()
        if self._scanner:
            await self._scanner.stop()
            self._scanner = None
        self._stop_task = None
        return self.status()

    def status(self, disabled_reason: str | None = None) -> CaptureStatus:
        return CaptureStatus(
            active=self.active,
            trace_id=self.trace_id,
            observations=self.observations,
            backend="ble",
            disabled_reason=disabled_reason,
            started_at=self.started_at,
            latest_observation_at=self.latest_observation_at,
        )

    async def _stop_after(self, duration_s: float) -> None:
        await asyncio.sleep(duration_s)
        await self.stop()
