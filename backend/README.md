# DeadZone Backend

FastAPI + WebSocket server. Streams `AggregateFrame` events at 1 Hz on `/ws/events`.

## Run

```bash
# from this directory
pip install -e .
uvicorn app.main:app --reload --port 8000
```

Or from the repo root:

```bash
docker compose up backend
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/healthz` | Liveness + active mode + version |
| GET | `/modes` | Active mode + available modes |
| WS | `/ws/events` | Aggregate frame stream (1 Hz placeholder) |

## Environment

| Var | Default | Notes |
|-----|---------|-------|
| `DEADZONE_MODE` | `mock` | One of `mock`, `replay`, `live`, `mesh` |

## Tasks landing here

- `.lev/pm/tasks/deadzone-be-contract-spine/` — event envelope + WebSocket protocol
- `.lev/pm/tasks/deadzone-be-mock-replay/` — deterministic mock generator + replay engine
- `.lev/pm/tasks/deadzone-be-live-mesh/` — BLE/Wi-Fi/Meshtastic adapters
- `.lev/pm/tasks/deadzone-be-intelligence-alerts/` — alert rule engine
