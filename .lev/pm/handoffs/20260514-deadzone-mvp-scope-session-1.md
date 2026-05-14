---
status: active
workstream: deadzone
component: mvp-scope
slug: prd-ux-backend-handoff
session: 1
created_at: 2026-05-14
predecessor: null
confidence: 0.82
decisions_start: D1
related_tasks: []
related_docs: []
depends_on: []
canonical_refs: []
---

# Session Handoff: DeadZone MVP PRD Scope

## You Are Here

**Workstream:** deadzone  
**Component:** mvp-scope  
**Session:** 1  
**Status:** active

DeadZone is being shaped from the PRD into backend scope, UX artifacts, and frontend/API handoff tasks for hackathon agent execution.

## Next Agent Brief

**Long-Term Goal:** Deliver a local-first DeadZone MVP that demonstrates deterministic crowd-intelligence replay, a live dashboard, and optional real sensing adapters.

**Done Condition:** A dev agent can pick up scoped backend and frontend tasks with clear API contracts, UX constraints, and demo acceptance checks for `docker compose up` plus dashboard usage.

**Current Execution Slice:** Create session tracking, check prior art, generate UX handoff artifacts, and scope backend/API/agent tasks.

**Why This Slice Now:** The user and teammate need a shared BE/FE boundary before parallel hackathon work starts.

**Out of Scope This Session:** Full implementation, production RF privacy review, cloud deployment, and real Meshtastic field validation.

## Entity Matrix

| # | File | Path | State | Canonical Ref | Decision | Next |
|---|------|------|-------|---------------|----------|------|
| 1 | Session handoff | `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md` | modified | PRD in chat | D1 | keep current |
| 2 | UX run directory | `.lev/ux/20260514-101228-deadzone-mvp-prd/` | created | PRD in chat | D2 | use as FE context |
| 3 | API contract | `.lev/pm/specs/deadzone-api-contract.yaml` | created | UX constraint bundle | D2 | backend implements |
| 4 | Backend scope | `.lev/pm/specs/deadzone-backend-scope.yaml` | created | API contract | D1 | backend agents implement |
| 5 | FE partner brief | `.lev/pm/specs/deadzone-frontend-partner-brief.yaml` | created | UX wireframes + API contract | D2 | partner consumes |
| 6 | Agent task bundle | `.lev/pm/plans/deadzone-agent-task-bundle.yaml` | created | Backend/API/UX scope | D3 | dispatch agents |

## Roadmap To Goal

**Goal**: Produce implementation-ready backend and frontend handoff scope for the DeadZone MVP.  
**Done Condition**: UX bundle, API contract, BE task bundle, and FE partner brief exist with first-slice acceptance checks.  
**Remaining Steps**: 5

### Step 1: Scope the hackathon slice
- Confirm the MVP boundary around mock/replay/WebSocket first.
- Search for prior project artifacts before creating new ones.
- Produce UX artifacts focused on dashboard workflows and partner handoff.
- Produce backend API and event contract suitable for FastAPI/WebSocket implementation.
- Produce agent task bundles with dependencies and acceptance checks.

#### Step 2: Backend implementation
- Build mock/replay event source, aggregation loop, WebSocket stream, and REST health/config endpoints.

#### Step 3: Frontend implementation
- Build dashboard shell, heatmap layer, sensor overlay, alert rail, and replay controls against the API contract.

#### Step 4: Demo hardening
- Add Docker compose path, deterministic seed, sample replay data, and judging script.

#### Step 5: Optional sensing
- Add BLE adapter and Meshtastic adapter behind feature flags after mock/replay are stable.

## Handoff Objective

Manage the transition from PRD to executable work packages. Preserve why decisions were made, where artifacts landed, and what agents should build next.

## Checkpoints

| T+0 | Session started from user PRD and repo instructions. |
| T+1 | Loaded `work` and `ux` skills; confirmed tracked handoff is mandatory before planning. |
| T+2 | Created initial handoff and entity matrix at `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md`. |
| T+3 | Prior-art search found no existing DeadZone specs, designs, plans, decisions, docs, or beads database. |
| T+4 | Created UX run artifacts under `.lev/ux/20260514-101228-deadzone-mvp-prd/`. |
| T+5 | Created API, event envelope, backend scope, FE brief, and agent task bundle. |
| T+6 | Validated YAML/JSON artifact syntax; git status unavailable because this directory is not a git repository. |

### ⚡ CHECKPOINT 1 — Scope Initialized

**Current State:** PRD scoping is active before implementation.  
**Context:** User is handling backend, partner is handling frontend, and tasks need to be agent-ready.  
**Files Loaded:** `/Users/jean-patricksmith/.agents/skills/work/SKILL.md`, `/Users/jean-patricksmith/.agents/skills/ux/SKILL.md`, `/Users/jean-patricksmith/.agents/skills/work/templates/handoff.md`  
**Files Modified:** `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md`  
**Understanding:** Deterministic mock/replay mode is the first implementation boundary; live BLE/Meshtastic are optional after demo stability.  
**Progress:** Work tracking has started and the first entity is registered.  
**Next Steps:** Run prior-art search, generate UX artifacts, then write API/task bundles.

### ⚡ CHECKPOINT 2 — Prior Art Clear

**Current State:** No reusable local DeadZone artifacts exist beyond this session handoff.  
**Context:** Required searches checked `.lev/pm`, docs/specs, docs/design, `docs/ARCHITECTURE.md`, and `bd search`.  
**Files Loaded:** `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md`  
**Files Modified:** `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md`  
**Understanding:** This is a greenfield scope in an empty local project directory.  
**Progress:** Work gate Step 4 is complete.  
**Next Steps:** Generate UX artifacts and write backend/API handoff files.

### ⚡ CHECKPOINT 3 — Handoff Artifacts Created

**Current State:** Backend/API/UX task scope is ready for agent dispatch.  
**Context:** User needs BE scope while FE partner can take UI tasks from UX and API contracts.  
**Files Loaded:** UX skill, work skill, interactive visualization and UX audit skill references.  
**Files Modified:** `.lev/ux/20260514-101228-deadzone-mvp-prd/*`, `.lev/pm/specs/deadzone-api-contract.yaml`, `.lev/pm/specs/deadzone-event-envelope.schema.json`, `.lev/pm/specs/deadzone-backend-scope.yaml`, `.lev/pm/specs/deadzone-frontend-partner-brief.yaml`, `.lev/pm/plans/deadzone-agent-task-bundle.yaml`, `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md`  
**Understanding:** The first shippable slice is a deterministic aggregate intelligence stream, not live RF capture.  
**Progress:** Created implementation-ready contracts and task routing.  
**Next Steps:** Start BE-01/BE-02 and FE-01 in parallel, then integrate through BE-05 and FE-02.

### ⚡ CHECKPOINT 4 — Validation Complete

**Current State:** Artifact syntax is valid.  
**Context:** Agents can parse YAML/JSON files before implementation.  
**Files Loaded:** All created YAML and JSON artifacts.  
**Files Modified:** `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md`  
**Understanding:** This is not currently a git repository, so session close cannot include repo commit/push here.  
**Progress:** Ruby YAML parsing and Python JSON parsing passed.  
**Next Steps:** Use the task bundle to dispatch implementation agents.

## Timeline

| Time | Checkpoint |
|------|------------|
| T+0 | Session start — PRD and local instructions loaded |
| T+1 | Work and UX skill requirements loaded |
| T+2 | Handoff created |
| T+3 | Prior-art search completed with no reusable project artifacts |
| T+4 | UX artifacts created |
| T+5 | API/backend/FE/task artifacts created |
| T+6 | Syntax validation completed |
| T+7 | UX pipeline rerun: full 7-step at `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/` (wireframes, constraint_bundle, gate=proceed) |
| T+8 | Repo init + private push to https://github.com/Kingly-Agency/deadzone (commit c4152c3) |
| T+9 | README + backend/ (FastAPI /ws/events placeholder) + frontend/ (Vite+React shell) + docker-compose.yml committed and pushed (commit cc68011) |
| T+10 | App smoke-tested: 10/10 backend tests pass, FE typechecks + vite-builds, BE/FE wire-compatible; primary gap = no demo path without bleak+trace |
| T+11 | Mesh scoping discussion: real Meshtastic needs LoRa boards; Option B (WiFi-faked mesh) chosen for 2-laptop test in this session |
| T+12 | /subagent-driven-development invoked: 14 tasks created, batches 0/1/2/3 dispatched with subagents under spec-then-quality review gates |
| T+13 | Batch 0 (spec+task-DNA+models+transport): 1 round of fixes (`__all__` exports, MeshLink field alignment), then APPROVED; transport critical buffer-duplication bugs caught + fixed |
| T+14 | Batch 1 (gateway+node): APPROVED_WITH_NOTES (link window 2s vs spec 1s/5s — tunable; non-blocking) |
| T+15 | Batch 2 (satellite-app+tests+README): APPROVED; 29/29 mesh tests + 13/13 existing tests = 42 green |
| T+16 | Batch 3 (CLI __main__.py): help-check ok; `python -m app.mesh gateway` + `python -m app.mesh node --gateway URL --node-id NAME` work |

### ⚡ CHECKPOINT 3 — WiFi-faked mesh ready to commit (uncommitted on disk)

**Current State:** All 11 mesh artifacts on disk, 42/42 tests green, zero conflict with parallel BE-agent work (no edits to main.py, engine.py, routes.py, ws.py, domain/models.py, sources/mesh.py, or pyproject.toml). Not yet committed — awaiting user go-ahead since `/subagent-driven-development` session is paused on a stack-decision question that the user resolved ("Python BE is fine, was just checking we hadn't slipped a Node BE in").

**Context:** Real Meshtastic mesh requires LoRa hardware (ESP32 boards, ~$30-50 each + firmware day). Not viable before demo. **Option B (WiFi-faked mesh)** = standalone FastAPI satellite on port 8001; N node processes POST 1Hz zone-aggregate packets to gateway over plain HTTP. Aggregate-only across wire (no raw BLE MAC, no beacon_hash, no RSSI — privacy salt stays local per node). Honest demo claim: "Mesh transport simulated via WiFi; sensing is real BLE on two independent nodes."

**Files Created (all uncommitted, all under `backend/app/mesh/` or `.lev/`):**
- `backend/app/mesh/__init__.py` — package re-exports
- `backend/app/mesh/models.py` — Pydantic v2 wire types (AggregatePacket with `schema` alias, NodeState, MergedZone, MeshLink, MeshSnapshot, GatewayHealth, AggregateAccepted, ZoneAggregate, Position)
- `backend/app/mesh/transport.py` — stdlib `urllib`-based async HTTP client with tri-state SendResult (ok/drop/retry), bounded retry buffer, seq stamping
- `backend/app/mesh/gateway.py` — in-memory MeshGateway with SUM/MAX/urgency-tiebreak/MIN merge, stale-after-3s, offline-after-10s, mesh_link inference within 2s window
- `backend/app/mesh/node.py` — MeshNode tick loop + Scanner protocol + deterministic sinusoidal MockNodeScanner
- `backend/app/mesh/app.py` — FastAPI factory exposing GET /mesh/healthz, POST /mesh/aggregate, GET /mesh/state, GET /mesh/nodes (CORS for localhost:3000)
- `backend/app/mesh/__main__.py` — argparse CLI: `python -m app.mesh gateway --port 8001` / `python -m app.mesh node --gateway URL --node-id NAME`
- `backend/app/mesh/README.md` — 213-line runbook for 2-laptop test
- `backend/tests/test_mesh.py` — 29 tests across 7 classes (wire protocol, gateway merge, stale/offline lifecycle, privacy invariants, transport buffering, mock determinism, HTTP integration)
- `.lev/pm/specs/deadzone-mesh-wifi.yaml` — feature spec (source of truth for merge rules, packet contract, privacy model, failure modes, done_criteria, out_of_scope)
- `.lev/pm/tasks/deadzone-be-mesh-wifi/{dna.yaml,execution.yaml}` — task DNA

**Critical bugs caught during review (would have shipped if not caught):**
1. Transport buffer duplicated packets on 5xx (each `_send` failure both returned False AND re-appended without popleft).
2. 4xx response during buffer replay permanently blocked the buffer.
3. Seq counter drift between fresh-packet attempts and buffer replays.
All fixed via tri-state SendResult rewrite where `post()` and `_drain_buffer` own the buffer lifecycle; `_send` is pure I/O classification.

**Outstanding non-blocking items:**
- Mesh link window: code uses single 2s window; spec says 1s creation + 5s expiry. Tunable; pragmatic 2s for WiFi jitter. Either update spec or split into two constants in follow-up.
- MockNodeScanner never emits `"spiking"` trend — cosmetic.
- A separate BE agent has been modifying `app/main.py`, `app/api/*`, `app/runtime/engine.py`, `app/sources/*`, `pyproject.toml` (added bleak to main deps, added `deadzone-backend`/`deadzone-permissions`/`deadzone-scan` console scripts). FE agent also modified `frontend/src/App.tsx`, `HeatmapDashboard.tsx`, `index.html`, `styles.css` to add Bluetooth capture controls + Google Fonts. Mesh remained zero-conflict.

**Two-laptop test runbook (ready now):**
```bash
# laptop A (gateway):
cd backend && python -m app.mesh gateway --port 8001
# laptop A (own node):
python -m app.mesh node --gateway http://localhost:8001 --node-id laptop-A
# laptop B:
python -m app.mesh node --gateway http://<A-lan-ip>:8001 --node-id laptop-B
# verify:
curl http://<A-lan-ip>:8001/mesh/state | jq
```

**Next Steps:**
1. Final whole-slice review pass (one reviewer over all 11 files at once).
2. Git commit + push to https://github.com/Kingly-Agency/deadzone (will be commit ~4 on main).
3. Decide whether to reconcile the link-window deviation in the spec or the code (follow-up task).
4. Optional: wire real BLE Scanner via DI from the main backend's `app/sources/ble.py` (BE-agent territory; mesh is ready to accept it via the Scanner protocol).
5. Optional: add `/mesh/state` proxy in main BE's `/api/v1/snapshot` so FE only needs one URL (BE-agent territory).

### ⚡ CHECKPOINT 2 — Scaffolds shipped, repo live

**Current State:** Private repo `Kingly-Agency/deadzone` is live on `main` (origin up-to-date). Two commits: `c4152c3` (initial `.lev/` PRD + UX artifacts) and `cc68011` (README + backend/ + frontend/ + docker-compose). Backend ships a 1Hz placeholder WebSocket frame stream; frontend renders a persistent ProvenanceBadge + HeadlineMetricsBar + density zone bars + non-empty alerts zero-state + viridis legend — exactly the LC-1..LC-4 + LC-6 constraints from the latest UX run.

**Context:** UX pipeline rerun produced wireframes-included artifacts. User moved both into `deadzone/.lev/` and created the GH repo. Two consecutive `/ux` runs now coexist in `.lev/ux/`: `20260514-101228-deadzone-mvp-prd` (initial) and `20260514-101706-deadzone-mvp-crowd-intel` (full 7-step with wireframes).

**Files Loaded:** scaffold templates from session memory; existing `.lev/pm/specs/` for partner brief reference.
**Files Modified/Created:**
- `README.md` (created)
- `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/app/main.py`, `backend/Dockerfile`, `backend/README.md` (created)
- `frontend/package.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/components/HeatmapDashboard.tsx`, `frontend/src/styles.css`, `frontend/Dockerfile`, `frontend/README.md` (created)
- `docker-compose.yml` (created)
- `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/*` (moved in from incubator root)
- `.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md`, `20260514-fe-prd-deadzone-ux-synthesis-session-1.md` (moved in from incubator root)

**Understanding:** The repo now matches the BE/FE boundary specified in `.lev/pm/specs/deadzone-api-contract.yaml` and `.lev/pm/specs/deadzone-frontend-partner-brief.yaml`. Backend placeholder is intentionally minimal — real mock-replay generator lands in `.lev/pm/tasks/deadzone-be-mock-replay/`. Frontend dashboard renders the constraint-bundle UX intent (mode badge, headline metrics, density bars, non-empty alerts state, viridis ramp) but does NOT yet integrate Leaflet floorplan + Heatmap.js — that lands when the venue floorplan asset arrives.

**Progress:** Ship-ready scaffold. `docker compose up` should produce a working dashboard within a minute on a clean clone (backend builds python:3.11-slim image, frontend builds node:20-alpine). Untested end-to-end in CI.

**Next Steps:**
1. Verify `docker compose up` actually boots end-to-end on a clean checkout (build, connect, render first frame).
2. Pick up `.lev/pm/tasks/deadzone-be-mock-replay/` — replace the 1Hz placeholder with the deterministic generator + 90s alert event.
3. Decide floorplan source for the venue (PNG/SVG path); then wire Leaflet + Heatmap.js into `HeatmapDashboard.tsx`.
4. Convert the 4 `.lev/pm/tasks/deadzone-be-*` items into GitHub Issues so the repo Issues tab tracks them.

## Decisions Log

### D1: Prioritize deterministic mock/replay before live sensing

**When:** 2026-05-14  
**Context:** Hackathon judges need a stable local demo and RF permissions vary by machine.  
**Decision:** Scope the first backend slice around mock events, replay events, aggregation, and WebSocket delivery.  
**Rationale:** This satisfies the minimum success criteria and gives frontend work a stable contract.  
**Impact:** BLE, Wi-Fi passive scanning, and Meshtastic are adapter interfaces or stretch tasks, not blockers.  
**Code Refs:** `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md`  
**Canonical Ref:** Pending API/task artifacts.

**Alternatives Considered:**
- Live sensing first: rejected because cross-platform permissions can derail the demo.
- Dashboard first without contracts: rejected because partner handoff would be unstable.
- Deterministic event pipeline first: selected because it supports replay, simulation, and later adapters.

**Promotion:** stay in handoff

**Follow-up Required:**
- [x] Write API/event contract.
- [x] Write UX constraint bundle.
- [x] Write agent task bundle.

### D2: Use aggregate dashboard contracts as the FE/BE boundary

**When:** 2026-05-14  
**Context:** FE partner needs stable payloads while backend implementation is still being scoped.  
**Decision:** Define REST snapshot endpoints and WebSocket envelopes around `IntelligenceSnapshot`, `ZoneAggregate`, `FlowVector`, `Alert`, `SensorNode`, and `StreamState`.  
**Rationale:** The frontend should render venue intelligence directly, not infer it from raw RSSI packets.  
**Impact:** Backend owns aggregation; frontend owns visualization and state handling.  
**Code Refs:** `.lev/pm/specs/deadzone-api-contract.yaml`, `.lev/pm/specs/deadzone-event-envelope.schema.json`  
**Canonical Ref:** `.lev/pm/specs/deadzone-api-contract.yaml`

**Alternatives Considered:**
- Raw event stream only: rejected because FE would reimplement backend intelligence under time pressure.
- REST polling only: rejected because real-time demo needs visible stream updates.
- Aggregate REST + WebSocket envelopes: selected because it supports immediate render and live updates.

**Promotion:** stay in handoff

**Follow-up Required:**
- [ ] Implement Pydantic models from the contract.
- [ ] Generate/handwrite TypeScript types from the same contract.

### D3: Package implementation as parallel BE and FE agent tasks

**When:** 2026-05-14  
**Context:** User plans to pass scoped work to dev agents and a frontend partner.  
**Decision:** Create a machine-readable task bundle with dependency order and acceptance checks.  
**Rationale:** Parallel tracks are safe only where contracts are explicit; BE-01 and FE-01 can start immediately, while BE-02/BE-05 unlock contract-hardening work.  
**Impact:** Agents should work from `.lev/pm/plans/deadzone-agent-task-bundle.yaml` instead of reinterpreting the PRD.  
**Code Refs:** `.lev/pm/plans/deadzone-agent-task-bundle.yaml`  
**Canonical Ref:** `.lev/pm/plans/deadzone-agent-task-bundle.yaml`

**Alternatives Considered:**
- One large implementation task: rejected because it blocks hackathon parallelism.
- FE-only handoff: rejected because backend contracts are the main coordination risk.
- Dependency-scoped tasks: selected because it allows safe parallel execution.

**Promotion:** stay in handoff

**Follow-up Required:**
- [ ] Dispatch BE-01 and FE-01 first.
- [ ] Gate FE-02 on BE-02/BE-05 contract shape.

## Code Context

### Files Modified

| File | Change Type | Lines | Status | Notes |
|------|-------------|-------|--------|-------|
| `.lev/pm/handoffs/20260514-deadzone-mvp-scope-session-1.md` | added/modified | ~230 | complete | Tracks this PRD scoping session |
| `.lev/ux/20260514-101228-deadzone-mvp-prd/` | added | 13 files | complete | UX pipeline artifacts and FE constraint bundle |
| `.lev/pm/specs/deadzone-api-contract.yaml` | added | ~450 | complete | REST/WebSocket API contract |
| `.lev/pm/specs/deadzone-event-envelope.schema.json` | added | ~50 | complete | Minimal JSON schema for stream envelopes |
| `.lev/pm/specs/deadzone-backend-scope.yaml` | added | ~95 | complete | Backend architecture and MVP boundary |
| `.lev/pm/specs/deadzone-frontend-partner-brief.yaml` | added | ~55 | complete | FE partner implementation brief |
| `.lev/pm/plans/deadzone-agent-task-bundle.yaml` | added | ~250 | complete | Agent task dependency bundle |

**Total Changes:**
- Files added: 20
- Files modified: 1
- Files deleted: 0
- Lines changed: planning artifacts only

### Files Loaded Into Context

| Order | File | Why Loaded | Key Understanding | Why It Matters |
|------|------|------------|-------------------|----------------|
| 1 | `/Users/jean-patricksmith/.agents/skills/work/SKILL.md` | Required by repo instruction | Handoff and prior-art gates are mandatory | Controls session process |
| 2 | `/Users/jean-patricksmith/.agents/skills/ux/SKILL.md` | User requested UX skill | UX pipeline produces handoff artifacts for FE agents | Controls UI planning artifacts |
| 3 | `/Users/jean-patricksmith/.agents/skills/work/templates/handoff.md` | Required template | Handoff must preserve decisions, files, and timeline | Enables continuity |
| 4 | `/Users/jean-patricksmith/.agents/skills-db/design-ux/interactive-visualization-creator/SKILL.md` | UX enrichment | Visualization should teach through semantic layers and device-aware quality | Guides heatmap/flow UI |
| 5 | `/Users/jean-patricksmith/.agents/skills-db/design-ux/ux-audit/SKILL.md` | UX enrichment | Visibility, error states, and accessibility need explicit checks | Guides UI validation |

### ⚡ CHECKPOINT 4 — 1-click mesh shipped + live demo verified

**Current State:** Mesh + 1-click UI is fully landed on `origin/main` (HEAD `35b3d70`). Three local services running (`uvicorn :8000`, `python -m app.mesh satellite :8001`, `npm run dev :3000`); end-to-end UI flow verified via agent-browser:
- Sidebar shows Mesh nav button (⌬ icon)
- MeshPanel renders in idle state — no 500 error
- Click "HOST MESH" → role flips to "Hosting", auto-self-joins
- Stats live: 1 node, 31 estimated devices across 3 zones (near-scanner, mid-field, far-field), 0 mesh_links (only 1 node — peers needed)
- API confirms `packets_sent` increments at 1Hz; `beacon_active: true`

**Files Created (committed to remote in commits `00003fe`, `3b3859f`, `585a940`):**
- Backend: `app/mesh/runtime.py`, `discovery.py`, `api_extra.py` (6 new endpoints); modified `app.py` (lifespan wiring), `models.py` (5 new models), `__main__.py` (`satellite` subcommand), `README.md` (UI-first rewrite)
- Frontend: `lib/mesh-client.ts`, `components/MeshPanel.tsx`, `components/MeshPanel.module.css`, `vite-env.d.ts`; modified `vite.config.ts` (`/mesh` proxy), `App.tsx` + `Sidebar.tsx` (mesh nav + activeSection branch)
- Tests: `tests/test_mesh_runtime.py` (24 tests; full suite 67/0 green)
- Spec: `.lev/pm/specs/deadzone-mesh-wifi.yaml` extended with `discovery` + `ui_driven_lifecycle` sections + DC-MESH-07

**Critical bugs caught during multi-batch review (would have shipped):**
1. Transport buffer duplicated packets on 5xx (no popleft before re-append)
2. 4xx during replay permanently blocked the buffer
3. Seq counter drift between fresh/replayed packets
4. Missing public `gateway_id` on MeshRuntime (would have crashed every endpoint)
5. `_self_join` exception path could leave `_hosting=True` with no node running
6. FE agent's responsive-drawer refactor twice reverted the MeshPanel integration — re-integrated, currently durable (the latest parallel-agent iteration keeps MeshPanel intact)

**Architecture decisions made along the way:**
- WiFi-faked mesh (HTTP POST), not real Meshtastic LoRa — honest demo claim baked into UI badge and README
- Single satellite per laptop handles BOTH gateway + node roles (state machine: idle | hosting | joined | hosting_and_joined)
- Auto-self-join when hosting (your laptop counts as a node immediately, no second click)
- UDP broadcast discovery on port 8002 (3s interval, 30s TTL) with manual-paste fallback
- Privacy invariant: aggregate-only across wire — raw BLE MACs, salted beacon_hashes, RSSI samples NEVER leave a node
- Standalone satellite on `:8001`, separate from main BE on `:8000` — zero coupling to BE-agent territory (`app/main.py`, `routes.py`, `engine.py`, `pyproject.toml` all untouched)

**Verifier results:**
- Backend pytest: 67/67 passing
- Frontend typecheck + build: clean (49 modules, 187KB JS gzipped to 57KB)
- agent-browser end-to-end: dashboard → mesh nav → click "HOST MESH" → role=Hosting, stats live
- Live API: `/mesh/me` shows packets_sent=61 after ~1min, freshness=live, hosting=true

**Outstanding non-blocking items:**
- Mesh link window: code uses 2s; spec says 1s create / 5s expire. Tunable; pragmatic for WiFi jitter. Reconcile in a follow-up.
- MockNodeScanner never emits "spiking" trend — cosmetic.
- Macs don't loopback UDP broadcast to localhost — single-laptop `/mesh/discover` shows empty list. Two-laptop LAN discovery works. Manual-paste fallback is always available.
- Working tree on disk has a parallel-agent's WIP refactor (re-adds ConfigurationScreen route, removes ReplayControls). MeshPanel integration is preserved in their refactor. Their commit will land cleanly.

**Two-laptop test runbook (partner can do this after `git pull`):**
```bash
# Each laptop, three terminals:
cd backend && source .venv/bin/activate && uvicorn app.main:app --port 8000
cd backend && source .venv/bin/activate && python -m app.mesh satellite
cd frontend && npm run dev

# Open http://localhost:3000 -> Sidebar -> Mesh
# Host laptop: click "HOST MESH"
# Partner laptop: wait 3s, click "Join" next to discovered gateway
# (or paste http://<host-lan-ip>:8001 if UDP blocked)
```

**Next Steps:**
1. Reconcile the spec/code link-window deviation (medium priority, follow-up).
2. Optional: wire real BLE Scanner via DI from `app.sources.ble` so mesh nodes use real sensing (BE-agent coordination).
3. Optional: add a friendlier "Satellite offline" banner in MeshPanel when /mesh/me returns connection error (currently shows raw "500").
4. Optional: bundle satellite startup into the existing `npm run dev` script so all 3 services boot together.

## Open Questions

### Immediate

1. Which frontend stack is already preferred for this repo once implementation starts?
2. Should FE use Leaflet/Heatmap.js exactly as the PRD says, or start with a simpler coordinate-plane canvas if faster?

### Short-term

1. Which venue map should the MVP use: abstract floorplan, GeoJSON venue image, or simple coordinate plane?
2. Which live sensor adapter is most likely to be demoed after replay: BLE or Meshtastic?
