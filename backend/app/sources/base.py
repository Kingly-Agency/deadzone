from __future__ import annotations

from datetime import datetime
from typing import Literal, Protocol

from pydantic import BaseModel, Field


class BleObservation(BaseModel):
    """Privacy-safe BLE advertisement observation.

    The raw BLE address is intentionally absent. `beacon_hash` is capture-scoped
    and salted locally so replay/mock can count movement without stable identity.
    """

    timestamp: datetime
    source: Literal["ble"] = "ble"
    receiver_id: str
    beacon_hash: str
    rssi: int
    zone_id: str
    event_count: int = Field(default=1, ge=1)


class SensorSource(Protocol):
    @property
    def source_id(self) -> str:
        ...

    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...
