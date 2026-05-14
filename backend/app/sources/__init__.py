"""SensorSource protocol — abstract interface for all data sources."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models import IntelligenceSnapshot


class SensorSource(ABC):
    """Base class for all DeadZone data sources (mock, replay, live adapters)."""

    @abstractmethod
    async def tick(self, elapsed_s: float) -> IntelligenceSnapshot:
        """Produce one snapshot tick. Called by the runtime engine at ~1 Hz."""
        ...

    @abstractmethod
    async def reset(self) -> None:
        """Reset the source to initial state (demo reset)."""
        ...

    @property
    @abstractmethod
    def source_label(self) -> str:
        """Human-readable label for provenance display."""
        ...
