# DeadZone

> Real-time crowd-intelligence platform. **Mock → Replay → Live → Mesh.**

DeadZone is an observability layer for physical spaces. Live crowd density, movement flow, congestion zones, and dead Wi-Fi areas — without attendee apps, accounts, QR codes, or interaction. Passive RF sensing only.

## Quick Start

```bash
npm run dev
```

Run this from the repo root. It starts the BLE-first FastAPI backend on <http://127.0.0.1:8000>, waits for it to become healthy, then starts the Vite dashboard on <http://127.0.0.1:3000>.

Then open <http://127.0.0.1:3000>. The dashboard defaults to `BLE/LIVE`; the only selectable modes are `BLE/LIVE` and `MOCK`.

## Modes

| Mode | Badge | What it does | Use when |
|------|-------|--------------|----------|
| **Mock** | blue | Deterministic synthetic stream. Default on first load. | Hackathon judging, rehearsal, CVD color check |
| **Replay** | amber | Recorded real event streams (concert exit, hallway, stadium ingress) | Skeptic judge wants to see real data shape |
| **Live** | green | BLE/Wi-Fi sensing on the host laptop (best-effort cross-platform) | Strong demo bonus; degrades to Replay if stream stalls |
| **Mesh** | violet | Multi-node Meshtastic LoRa relay | Outdoor / no-Wi-Fi venues (stretch) |

Provenance badge is persistent and unmissable — honest data labeling is the engineering-maturity signal.

## Architecture

```
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│ Sensor sources │──▶│   FastAPI BE   │──▶│  React FE      │
│ Mock/Replay/   │   │  + WebSocket   │   │  Leaflet +     │
│ BLE/Wi-Fi/Mesh │   │  /ws/events    │   │  Heatmap.js    │
└────────────────┘   └────────────────┘   └────────────────┘
```

- **Backend**: Python 3.11, FastAPI, asyncio, WebSockets, Bleak (BLE), Scapy (Wi-Fi passive), Meshtastic Python SDK
- **Frontend**: React + Vite + TypeScript, Leaflet for floorplans, Heatmap.js for density
- **Infrastructure**: Docker Compose (single command up)

## Repo Layout

```
backend/                   FastAPI + WebSocket server
frontend/                  Vite + React + Leaflet dashboard
docker-compose.yml         One-command dev orchestration
.lev/
├── pm/
│   ├── specs/             Backend PRD, API contract, event envelope schema, FE partner brief
│   ├── plans/             Agent task bundle
│   ├── tasks/             Tracked work (4 backend tasks with dna.yaml + execution.yaml)
│   └── handoffs/          Session continuity (BE, FE, scope workstreams)
└── ux/
    ├── 20260514-101228-deadzone-mvp-prd/         Initial UX exploration
    └── 20260514-101706-deadzone-mvp-crowd-intel/ Full 7-step UX pipeline + wireframes
```

See [`.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/summary.md`](.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/summary.md) for the design intent and [`.lev/pm/specs/deadzone-api-contract.yaml`](.lev/pm/specs/deadzone-api-contract.yaml) for the contract spine.

## Hackathon Success Criteria

| Tier | Goal |
|------|------|
| **Minimum** | Animated heatmap, replay mode, congestion visualization, `docker compose up` |
| **Strong demo** | Live BLE sensing, multi-node visualization, sensor topology display |
| **Stretch** | Meshtastic mesh, outdoor field test, live movement prediction |

## Engineering Principles

- **Deterministic first** — Mock mode produces identical visuals every run; judges need a stable demo
- **Aggregate > Identity** — Never display or transmit device identifiers; only density, motion, pressure
- **Event-driven** — `Sensor Event → Aggregation → Spatial Intelligence` everywhere, so replay/sim/ML reuse one pipe
- **Honest provenance** — Mode badge is persistent and color-coded; mocking is labeled, never hidden
- **Accessible** — WCAG AA palette (viridis + pattern overlay); no red-green-only encoding

## Status

🚧 Scaffolding stage. Backend + frontend skeletons present; mock event generator is the next milestone (see `.lev/pm/tasks/deadzone-be-mock-replay/`).

## License

Proprietary — Kingly Agency.
