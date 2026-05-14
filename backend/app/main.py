from __future__ import annotations

import asyncio
import json
import os
import time
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

Mode = Literal["mock", "replay", "live", "mesh"]

ACTIVE_MODE: Mode = os.environ.get("DEADZONE_MODE", "mock")  # type: ignore[assignment]


class AggregateFrame(BaseModel):
    """A single tick of zone-level aggregate telemetry (no device identifiers)."""

    timestamp: float
    mode: Mode
    venue_id: str
    zones: list[dict]
    headline: dict


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="DeadZone", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "mode": ACTIVE_MODE, "version": app.version}


@app.get("/modes")
async def modes() -> dict:
    return {
        "active": ACTIVE_MODE,
        "available": ["mock", "replay", "live", "mesh"],
    }


def _mock_frame() -> AggregateFrame:
    """Placeholder mock frame. Real generator lives in tasks/deadzone-be-mock-replay."""
    now = time.time()
    return AggregateFrame(
        timestamp=now,
        mode=ACTIVE_MODE,
        venue_id="demo-venue",
        zones=[
            {"id": "hall-a", "name": "Hall A", "count": 412, "capacity": 600, "trend_5m": "up"},
            {"id": "hall-b", "name": "Hall B", "count": 678, "capacity": 800, "trend_5m": "up"},
            {"id": "foodcourt", "name": "Food Court", "count": 157, "capacity": 400, "trend_5m": "flat"},
        ],
        headline={"total": 1247, "capacity_pct": 0.72, "peak_zone": "Hall B", "trend": "rising"},
    )


@app.websocket("/ws/events")
async def ws_events(ws: WebSocket) -> None:
    """Aggregate frame stream. Replace with real source when task-be-contract-spine lands."""
    await ws.accept()
    try:
        while True:
            frame = _mock_frame()
            await ws.send_text(json.dumps(frame.model_dump()))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
