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

## Open Questions

### Immediate

1. Which frontend stack is already preferred for this repo once implementation starts?
2. Should FE use Leaflet/Heatmap.js exactly as the PRD says, or start with a simpler coordinate-plane canvas if faster?

### Short-term

1. Which venue map should the MVP use: abstract floorplan, GeoJSON venue image, or simple coordinate plane?
2. Which live sensor adapter is most likely to be demoed after replay: BLE or Meshtastic?
