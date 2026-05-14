"""WebSocket endpoint for live streaming."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.runtime import engine

ws_router = APIRouter()


@ws_router.websocket("/ws/live")
async def ws_live(ws: WebSocket) -> None:
    """Stream aggregate intelligence snapshots to connected clients."""
    await ws.accept()
    engine.register_client(ws)

    # Send initial snapshot if available
    if engine.latest_snapshot:
        import json
        from datetime import datetime, timezone

        from app.models import EnvelopeType, StreamEnvelope

        envelope = StreamEnvelope(
            type=EnvelopeType.snapshot,
            sequence=0,
            timestamp=datetime.now(timezone.utc),
            mode=engine.mode,
            payload=engine.latest_snapshot.model_dump(mode="json"),
        )
        await ws.send_text(json.dumps(envelope.model_dump(mode="json")))

    try:
        # Keep connection alive — the engine broadcasts to registered clients
        while True:
            # We still need to receive to detect disconnects
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        engine.unregister_client(ws)
