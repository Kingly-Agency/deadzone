from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.runtime.engine import DeadZoneEngine

router = APIRouter()


def get_engine() -> DeadZoneEngine:
    from app.main import engine

    return engine


@router.websocket("/ws/live")
async def ws_live(ws: WebSocket) -> None:
    await ws.accept()
    engine = get_engine()
    try:
        while True:
            await engine.ensure_live_ble_capture()
            for envelope in engine.envelopes():
                await ws.send_text(envelope.model_dump_json())
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return


@router.websocket("/ws/events")
async def ws_events(ws: WebSocket) -> None:
    await ws.accept()
    engine = get_engine()
    try:
        while True:
            await engine.ensure_live_ble_capture()
            await ws.send_json(engine.legacy_frame())
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
