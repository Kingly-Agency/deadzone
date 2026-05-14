from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.mesh.gateway import MeshGateway
from app.mesh.models import (
    AggregateAccepted,
    AggregatePacket,
    GatewayHealth,
    MeshSnapshot,
    NodeState,
)

logger = logging.getLogger(__name__)

DEFAULT_GATEWAY_ID = os.environ.get("DEADZONE_MESH_GATEWAY_ID", "mesh-gateway-local")
DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:3000",
]


def create_app(*, gateway_id: str = DEFAULT_GATEWAY_ID, cors_origins: list[str] | None = None) -> FastAPI:
    """Build a fresh FastAPI app with its own MeshGateway instance.

    The CLI entry point should call this and pass the resulting app to uvicorn.
    Tests call this and pass the app to httpx/Starlette's TestClient.
    """

    gateway = MeshGateway(gateway_id=gateway_id)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("mesh gateway '%s' starting", gateway_id)
        try:
            yield
        finally:
            logger.info("mesh gateway '%s' stopping", gateway_id)

    app = FastAPI(
        title="DeadZone Mesh Gateway",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins or DEFAULT_CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Pin gateway onto app.state so tests can introspect / reset
    app.state.gateway = gateway

    def get_gateway() -> MeshGateway:
        return app.state.gateway  # type: ignore[no-any-return]

    @app.get("/mesh/healthz", response_model=GatewayHealth)
    async def mesh_healthz(g: MeshGateway = Depends(get_gateway)) -> GatewayHealth:
        return g.health()

    @app.post("/mesh/aggregate", response_model=AggregateAccepted)
    async def mesh_aggregate(
        packet: AggregatePacket,
        g: MeshGateway = Depends(get_gateway),
    ) -> AggregateAccepted:
        try:
            seq = g.ingest(packet)
        except Exception as exc:  # pragma: no cover - validation handled by pydantic
            logger.exception("ingest failed")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
        return AggregateAccepted(
            accepted=True,
            last_seq=seq,
            node_id=packet.node_id,
            received_at=datetime.now(timezone.utc),
        )

    @app.get("/mesh/state", response_model=MeshSnapshot)
    async def mesh_state(g: MeshGateway = Depends(get_gateway)) -> MeshSnapshot:
        return g.snapshot()

    @app.get("/mesh/nodes", response_model=list[NodeState])
    async def mesh_nodes(g: MeshGateway = Depends(get_gateway)) -> list[NodeState]:
        return g.nodes()

    return app


# Convenience module-level app for `uvicorn app.mesh.app:app` usage.
app = create_app()


__all__ = ["create_app", "app", "DEFAULT_CORS_ORIGINS", "DEFAULT_GATEWAY_ID"]
