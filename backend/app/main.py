from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as routes_router
from app.api.ws import router as ws_router
from app.runtime.engine import DeadZoneEngine
from app.settings import load_settings

settings = load_settings()
engine = DeadZoneEngine(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="DeadZone", version=settings.version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_router)
app.include_router(ws_router)
