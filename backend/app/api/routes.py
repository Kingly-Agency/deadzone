from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.domain.models import (
    AppConfig,
    CaptureStartRequest,
    CaptureStatus,
    ErrorResponse,
    HealthResponse,
    IntelligenceSnapshot,
    ModeControlRequest,
    ReplayControlRequest,
    ReplayScenario,
    SensorEventTailItem,
    SensorNode,
    StreamState,
    ZoneAggregate,
    ZoneDetail,
)
from app.runtime.engine import DeadZoneEngine

router = APIRouter()


def conflict(error: ErrorResponse | CaptureStatus) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=error.model_dump(mode="json"))


def get_engine() -> DeadZoneEngine:
    from app.main import engine

    return engine


@router.get("/health", response_model=HealthResponse)
async def health(engine: DeadZoneEngine = Depends(get_engine)) -> HealthResponse:
    return engine.health()


@router.get("/healthz")
async def healthz(engine: DeadZoneEngine = Depends(get_engine)) -> dict[str, object]:
    response = engine.health()
    return {"status": "ok", "mode": response.mode, "version": response.version}


@router.get("/modes")
async def modes(engine: DeadZoneEngine = Depends(get_engine)) -> dict[str, object]:
    config = engine.config()
    return {
        "active": config.active_mode,
        "available": config.available_modes,
        "disabled": config.disabled_modes,
    }


@router.get("/api/v1/config", response_model=AppConfig)
async def app_config(engine: DeadZoneEngine = Depends(get_engine)) -> AppConfig:
    return engine.config()


@router.get("/api/v1/snapshot", response_model=IntelligenceSnapshot)
async def snapshot(engine: DeadZoneEngine = Depends(get_engine)) -> IntelligenceSnapshot:
    return engine.snapshot()


@router.get("/api/v1/zones", response_model=list[ZoneAggregate])
async def zones(engine: DeadZoneEngine = Depends(get_engine)) -> list[ZoneAggregate]:
    return engine.snapshot().zones


@router.get("/api/v1/zones/{zone_id}", response_model=ZoneDetail)
async def zone_detail(zone_id: str, engine: DeadZoneEngine = Depends(get_engine)) -> ZoneDetail:
    detail = engine.zone_detail(zone_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown zone")
    return detail


@router.get("/api/v1/sensors", response_model=list[SensorNode])
async def sensors(engine: DeadZoneEngine = Depends(get_engine)) -> list[SensorNode]:
    return engine.snapshot().sensors


@router.get("/api/v1/sensors/{sensor_id}/events", response_model=list[SensorEventTailItem])
async def sensor_events(
    sensor_id: str,
    engine: DeadZoneEngine = Depends(get_engine),
) -> list[dict]:
    return engine.sensor_event_tail(sensor_id)


@router.get("/api/v1/replay/scenarios", response_model=list[ReplayScenario])
async def replay_scenarios(engine: DeadZoneEngine = Depends(get_engine)) -> list[ReplayScenario]:
    return engine.store.scenarios()


@router.post("/api/v1/replay/control", response_model=StreamState | ErrorResponse)
async def replay_control(
    request: ReplayControlRequest,
    engine: DeadZoneEngine = Depends(get_engine),
) -> StreamState | ErrorResponse:
    response = engine.control_replay(request)
    if isinstance(response, ErrorResponse):
        return conflict(response)
    return response


@router.post("/api/v1/mode", response_model=StreamState | ErrorResponse)
async def mode_control(
    request: ModeControlRequest,
    engine: DeadZoneEngine = Depends(get_engine),
) -> StreamState | ErrorResponse:
    response = engine.set_mode(request.mode)
    if isinstance(response, ErrorResponse):
        return conflict(response)
    return response


@router.post("/api/v1/demo/reset", response_model=IntelligenceSnapshot)
async def demo_reset(engine: DeadZoneEngine = Depends(get_engine)) -> IntelligenceSnapshot:
    return engine.reset_demo()


@router.post("/api/v1/capture/start", response_model=CaptureStatus)
async def capture_start(
    request: CaptureStartRequest,
    engine: DeadZoneEngine = Depends(get_engine),
) -> CaptureStatus:
    response = await engine.start_capture(request.trace_id, request.duration_s)
    if response.disabled_reason:
        return conflict(response)
    return response


@router.post("/api/v1/capture/stop", response_model=CaptureStatus)
async def capture_stop(engine: DeadZoneEngine = Depends(get_engine)) -> CaptureStatus:
    return await engine.stop_capture()


@router.get("/api/v1/capture/status", response_model=CaptureStatus)
async def capture_status(engine: DeadZoneEngine = Depends(get_engine)) -> CaptureStatus:
    disabled = engine.capture.disabled_reason
    return engine.capture.status(disabled_reason=disabled)
