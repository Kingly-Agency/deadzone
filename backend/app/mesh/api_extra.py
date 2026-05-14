"""Extra mesh endpoints for UI-driven host/join lifecycle and gateway discovery.

These routes are mounted onto the satellite FastAPI app via include_router.
They read app.state.runtime (MeshRuntime) and app.state.discovery (DiscoveryService).

NOTE: The request/response models defined inline at the top of this file
will move to ``app.mesh.models`` in Batch B. Keeping them here as a draft so
this file is self-contained for Batch A review.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status

from app.mesh.models import (
    DiscoveredGatewayResponse,
    HostRequest,
    JoinRequest,
    MeRoleResponse,
    MeshRole,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _require_runtime(request: Request):
    """Return ``app.state.runtime`` or raise 503."""
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="mesh runtime not initialized",
        )
    return runtime


def _require_discovery(request: Request):
    """Return ``app.state.discovery`` or raise 503."""
    discovery = getattr(request.app.state, "discovery", None)
    if discovery is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="mesh discovery service not initialized",
        )
    return discovery


def _me_response(request: Request) -> MeRoleResponse:
    """Build a ``MeRoleResponse`` from current runtime + discovery state."""
    runtime = _require_runtime(request)
    discovery = getattr(request.app.state, "discovery", None)
    beacon_active = discovery.is_broadcasting if discovery else False
    listening = discovery.listener.active if discovery else False
    peer_count = len(discovery.peers()) if discovery else 0
    return MeRoleResponse(
        role=runtime.role,
        hosting=runtime.hosting,
        beacon_active=beacon_active,
        joined=runtime.joined_url is not None,
        joined_url=runtime.joined_url,
        joined_gateway_id=runtime.joined_gateway_id,
        node_id=runtime.node_id,
        packets_sent=runtime.node_packets_sent,
        buffered=runtime.node_buffered,
        gateway_id=runtime.gateway_id,
        listening=listening,
        discovered_peer_count=peer_count,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/mesh/host", response_model=MeRoleResponse)
async def mesh_host(req: HostRequest, request: Request) -> MeRoleResponse:
    """Start hosting the mesh gateway and optionally begin beacon broadcasting."""
    runtime = _require_runtime(request)
    discovery = _require_discovery(request)
    await runtime.host()
    if req.beacon:
        discovery.start_broadcasting()
    else:
        await discovery.stop_broadcasting()
    return _me_response(request)


@router.post("/mesh/unhost", response_model=MeRoleResponse)
async def mesh_unhost(request: Request) -> MeRoleResponse:
    """Stop hosting and stop beacon broadcasting."""
    runtime = _require_runtime(request)
    discovery = _require_discovery(request)
    await runtime.unhost()
    await discovery.stop_broadcasting()
    return _me_response(request)


@router.post("/mesh/join", response_model=MeRoleResponse)
async def mesh_join(req: JoinRequest, request: Request) -> MeRoleResponse:
    """Join a remote gateway as a mesh node."""
    runtime = _require_runtime(request)
    # If already joined elsewhere, leave first to avoid double-running.
    if runtime.joined_url is not None:
        await runtime.leave()
    try:
        await runtime.join(
            gateway_url=req.gateway_url,
            node_id=req.node_id,
            position=tuple(req.position) if req.position else None,
            scanner=req.scanner,
            seed=req.seed,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc),
        )
    return _me_response(request)


@router.post("/mesh/leave", response_model=MeRoleResponse)
async def mesh_leave(request: Request) -> MeRoleResponse:
    """Leave the currently joined gateway."""
    runtime = _require_runtime(request)
    await runtime.leave()
    return _me_response(request)


@router.get("/mesh/me", response_model=MeRoleResponse)
async def mesh_me(request: Request) -> MeRoleResponse:
    """Return the current mesh role and status."""
    return _me_response(request)


@router.get("/mesh/discover", response_model=list[DiscoveredGatewayResponse])
async def mesh_discover(request: Request) -> list[DiscoveredGatewayResponse]:
    """Return all discovered peer gateways from beacon listening."""
    discovery = _require_discovery(request)
    now = datetime.now(timezone.utc)
    out: list[DiscoveredGatewayResponse] = []
    for peer in discovery.peers():
        out.append(
            DiscoveredGatewayResponse(
                gateway_id=peer.gateway_id,
                gateway_url=peer.gateway_url,
                version=peer.version,
                last_seen_s_ago=(now - peer.last_seen).total_seconds(),
                first_seen=peer.first_seen,
                beacon_count=peer.beacon_count,
            )
        )
    return out


__all__ = ["router"]
