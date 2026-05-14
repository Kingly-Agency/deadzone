"""REST API routes for the DeadZone backend."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import (
    AppConfig,
    ErrorResponse,
    HealthResponse,
    IntelligenceSnapshot,
    Mode,
    RawSensorEvent,
    ReplayControlRequest,
    ReplayScenario,
    SensorNode,
    StreamState,
    ZoneAggregate,
)
from app.runtime import engine
from app.sources.replay import SCENARIOS

router = APIRouter()


@router.get("/health")
async def health() -> HealthResponse:
    return HealthResponse(mode=engine.mode)


@router.get("/api/v1/config")
async def get_config() -> AppConfig:
    return engine.get_config()


@router.get("/api/v1/snapshot")
async def get_snapshot() -> IntelligenceSnapshot:
    snap = engine.latest_snapshot
    if snap is None:
        raise HTTPException(status_code=503, detail="No snapshot available yet")
    return snap


@router.get("/api/v1/zones")
async def list_zones() -> list[ZoneAggregate]:
    snap = engine.latest_snapshot
    if snap is None:
        return []
    return snap.zones


@router.get("/api/v1/zones/{zone_id}")
async def get_zone(zone_id: str) -> ZoneAggregate:
    snap = engine.latest_snapshot
    if snap is None:
        raise HTTPException(status_code=503, detail="No snapshot available yet")
    zone = next((z for z in snap.zones if z.zone_id == zone_id), None)
    if zone is None:
        raise HTTPException(status_code=404, detail=f"Zone {zone_id} not found")
    return zone


@router.get("/api/v1/sensors")
async def list_sensors() -> list[SensorNode]:
    snap = engine.latest_snapshot
    if snap is None:
        return []
    return snap.sensors


@router.get("/api/v1/sensors/{sensor_id}/events")
async def get_sensor_events(sensor_id: str) -> list[RawSensorEvent]:
    events = engine.get_raw_events(sensor_id, limit=10)
    return events


@router.get("/api/v1/replay/scenarios")
async def list_replay_scenarios() -> list[ReplayScenario]:
    return SCENARIOS


@router.post("/api/v1/replay/control")
async def control_replay(req: ReplayControlRequest) -> StreamState:
    rs = engine.replay_source
    try:
        if req.action.value == "load":
            if not req.scenario_id:
                raise HTTPException(status_code=400, detail="scenario_id required for load")
            rs.load(req.scenario_id)
        elif req.action.value == "play":
            rs.play()
        elif req.action.value == "pause":
            rs.pause()
        elif req.action.value == "restart":
            rs.restart()
        elif req.action.value == "seek":
            if req.position_s is None:
                raise HTTPException(status_code=400, detail="position_s required for seek")
            rs.seek(req.position_s)
        elif req.action.value == "set_speed":
            if req.speed is None:
                raise HTTPException(status_code=400, detail="speed required for set_speed")
            rs.set_speed(req.speed)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    snap = engine.latest_snapshot
    if snap:
        return snap.stream
    # Return a minimal stream state
    from datetime import datetime, timezone

    from app.models import Freshness, StreamClock

    return StreamState(
        mode=Mode.replay,
        connected=True,
        sequence=0,
        source_label=rs.source_label,
        freshness=Freshness.live,
        clock=StreamClock(
            timestamp=datetime.now(timezone.utc),
            replay_position_s=rs.position_s,
            speed=rs.speed,
        ),
    )


@router.post("/api/v1/mode")
async def switch_mode(body: dict) -> StreamState:
    mode_str = body.get("mode")
    if not mode_str:
        raise HTTPException(status_code=400, detail="mode field required")
    try:
        mode = Mode(mode_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown mode: {mode_str}")

    config = engine.get_config()
    if mode.value in config.disabled_modes:
        raise HTTPException(
            status_code=409,
            detail=config.disabled_modes[mode.value],
        )

    try:
        snapshot = await engine.switch_mode(mode)
        return snapshot.stream
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/api/v1/demo/reset")
async def demo_reset() -> IntelligenceSnapshot:
    return await engine.reset()
