---
status: completed
workstream: be-prd
component: support-fe-build
slug: combine-lev-context
session: 1
created_at: 2026-05-14
predecessor: null
confidence: 0.35
decisions_start: D1
related_tasks: []
related_docs: []
depends_on: []
canonical_refs: []
---

# Session Handoff: BE PRD Support For FE Build

## You Are Here

**Workstream:** be-prd  
**Component:** support-fe-build  
**Session:** 1  
**Status:** completed

Combined existing `.lev/` context into a consolidated backend PRD YAML plus execution-ready `$propose` task artifacts that support a frontend build.

## Next Agent Brief

**Long-Term Goal:** Produce a complete backend product requirements and execution plan from all relevant `.lev/` information, including replay, mock, real data, and mesh context, so frontend implementation can proceed against stable backend expectations.

**Done Condition:** Every relevant `.lev/` source has been inventoried, prior art has been checked, requirements are mapped to concrete backend capabilities, and execution-ready `$propose` task artifacts exist or are clearly identified as blocked by a named missing input.

**Current Execution Slice:** Inventory `.lev/` and existing PM/design/spec artifacts, then determine whether enough source context exists to emit `.lev/pm/tasks/<task-id>/{dna.yaml,execution.yaml}` artifacts without another alignment question.

**Why This Slice Now:** The objective asks to combine all `.lev/` information; no reliable PRD or task emission can happen until the source set and prior art are known.

**Out of Scope This Session:** Implementing backend or frontend code, rebasing git history, broad unrelated repo cleanup, and saving non-handoff markdown unless explicitly requested.

## Entity Matrix

| # | File | Path | State | Canonical Ref | Decision | Next |
|---|------|------|-------|---------------|----------|------|
| 1 | .lev | .lev/ | captured | user objective | D1 | synthesize |
| 2 | handoff | .lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md | modified | work skill | D1 | complete |
| 3 | DeadZone PM specs | deadzone/.lev/pm/specs/ | loaded | prior art | D2 | extend |
| 4 | DeadZone agent plan | deadzone/.lev/pm/plans/deadzone-agent-task-bundle.yaml | loaded | prior art | D2 | convert to propose |
| 5 | DeadZone UX canonical run | deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/ | loaded | prior art | D2 | merge |
| 6 | DeadZone richer UX run | .lev/ux/20260514-101706-deadzone-mvp-crowd-intel/ | loaded | user objective | D2 | merge |
| 7 | Consolidated backend PRD | deadzone/.lev/pm/specs/deadzone-backend-prd.yaml | created | D2 | D3 | use for exec |
| 8 | Contract spine propose task | deadzone/.lev/pm/tasks/deadzone-be-contract-spine/ | created | PRD | D3 | exec-ready |
| 9 | Intelligence/alerts propose task | deadzone/.lev/pm/tasks/deadzone-be-intelligence-alerts/ | created | PRD | D3 | exec-ready |
| 10 | Mock/replay propose task | deadzone/.lev/pm/tasks/deadzone-be-mock-replay/ | created | PRD | D3 | exec-ready |
| 11 | Live/mesh propose task | deadzone/.lev/pm/tasks/deadzone-be-live-mesh/ | created | PRD | D3 | exec-ready |

## Roadmap To Goal

**Goal**: Convert `.lev/` source context into backend PRD/propose artifacts for frontend build readiness.  
**Done Condition**: Source inventory, prior-art report, requirement synthesis, and task artifacts/checklist are all backed by concrete file evidence.  
**Remaining Steps**: 0

### Step 1: Inventory, synthesize, emit, audit
- Completed `.lev/` inventory and prior-art scan.
- Resolved canonical PM home to `deadzone/.lev`.
- Created `deadzone/.lev/pm/specs/deadzone-backend-prd.yaml`.
- Created four `$propose` task folders with `dna.yaml` and `execution.yaml`.
- Validated YAML syntax and `$propose` structural fields.
- Completion audit found no missing objective requirements.

## Handoff Objective

Maintain a deterministic trail while combining `.lev/` source material into backend PRD/propose artifacts. Record files loaded, what each established, and how each finding affected task emission.

## Checkpoints

| T+0 | Session started — user objective and local `work`/`propose` skill instructions loaded. |

### ⚡ CHECKPOINT 1 — Handoff Created

**Current State:** Required work handoff is active before repository analysis.  
**Context:** User objective asks to combine all `.lev/` information into backend PRD/propose artifacts supporting frontend build.  
**Files Loaded:** `/Users/jean-patricksmith/.agents/skills/work/SKILL.md`, `/Users/jean-patricksmith/.agents/skills/propose/SKILL.md`, `/Users/jean-patricksmith/.agents/skills/work/templates/handoff.md`  
**Files Modified:** `.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md` created.  
**Understanding:** `$work` requires a tracked handoff and `$propose` requires source context, scoring, slice review, and cold-start-ready artifacts before emission.  
**Progress:** Session tracking is initialized; next action is `.lev/` inventory and prior art.  
**Next Steps:** Inspect `.lev/`, run prior-art searches, then update this handoff with findings.

### ⚡ CHECKPOINT 2 — Prior Art And Source Set Resolved

**Current State:** Canonical backend PM artifacts were found under `deadzone/.lev`, while `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/` supplied the richer UX progression inside the DeadZone tree.  
**Context:** The user asked to combine all `.lev/` information for backend PRD/propose artifacts supporting FE work.  
**Files Loaded:** `deadzone/.lev/pm/specs/deadzone-backend-scope.yaml`, `deadzone/.lev/pm/specs/deadzone-api-contract.yaml`, `deadzone/.lev/pm/specs/deadzone-event-envelope.schema.json`, `deadzone/.lev/pm/specs/deadzone-frontend-partner-brief.yaml`, `deadzone/.lev/pm/plans/deadzone-agent-task-bundle.yaml`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/constraint_bundle.yaml`, `deadzone/.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/*`  
**Files Modified:** `deadzone/.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md` updated.  
**Understanding:** Existing PM artifacts already define the FE/BE boundary; the newer UX run adds missing reset, mode switch, raw event tail, richer Replay, Live, and Mesh behavior.  
**Progress:** Decided to extend `deadzone/.lev` rather than creating a competing root PM tree.  
**Next Steps:** Emit YAML PRD and `$propose` artifacts.

### ⚡ CHECKPOINT 3 — PRD And Propose Artifacts Created

**Current State:** Full backend PRD and four execution-ready `$propose` task folders exist.  
**Context:** Work is planning/proposal scope only; no backend/frontend implementation was requested in this turn.  
**Files Loaded:** All source files named in Checkpoint 2 plus `/Users/jean-patricksmith/.agents/skills/propose/SKILL.md`.  
**Files Modified:** `deadzone/.lev/pm/specs/deadzone-backend-prd.yaml`, `deadzone/.lev/pm/tasks/deadzone-be-contract-spine/{dna.yaml,execution.yaml}`, `deadzone/.lev/pm/tasks/deadzone-be-intelligence-alerts/{dna.yaml,execution.yaml}`, `deadzone/.lev/pm/tasks/deadzone-be-mock-replay/{dna.yaml,execution.yaml}`, `deadzone/.lev/pm/tasks/deadzone-be-live-mesh/{dna.yaml,execution.yaml}`, `deadzone/.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md`.  
**Understanding:** The backend PRD is split into contract spine, intelligence/alerts, mock/replay, and live/mesh tasks because those map cleanly to FE build dependencies and avoid one oversized execution unit.  
**Progress:** YAML parse validation passed for all nine created YAML artifacts; structural `$propose` validation passed for 4 task folders and 10 slices.  
**Next Steps:** Execute the task folders when implementation begins.

### ⚡ CHECKPOINT 4 — Completion Audit

**Current State:** Objective satisfied by artifact evidence.  
**Context:** Audit mapped explicit prompt requirements to concrete files and validation commands.  
**Files Loaded:** `deadzone/.lev/pm/specs/deadzone-backend-prd.yaml`, all `deadzone/.lev/pm/tasks/*/{dna.yaml,execution.yaml}` files.  
**Files Modified:** `deadzone/.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md`.  
**Understanding:** The artifacts cover all required modes: Mock, Replay, Live/real-data adapters, and Mesh, plus FE contract needs and verifiers.  
**Progress:** No uncovered requirement remains. Git status could not be reported because neither `incubator` nor `deadzone` is a git repository.  
**Next Steps:** Mark active thread goal complete.

## Timeline

| Time | Checkpoint |
|------|------------|
| T+0 | Session start — objective and skill instructions loaded |
| T+1 | Handoff created and entity matrix seeded |
| T+2 | Prior art found canonical DeadZone PM/UX artifacts under `deadzone/.lev/` |
| T+3 | Consolidated backend PRD and four propose task folders created |
| T+4 | YAML and `$propose` structural validation passed |

## Decisions Log

### D1: Use source-first propose flow

**When:** 2026-05-14 session start  
**Context:** Objective asks for combined `.lev/` information and `$propose` artifacts, but current root only exposed `.lev/ux` before inventory.  
**Decision:** Inventory and prior-art scan all relevant `.lev/` sources before emitting task artifacts.  
**Rationale:** `$propose` requires source refs, acceptance, constraints, deterministic verifiers, and cold-start context; emitting artifacts before source inventory would leave executor choices unresolved.  
**Impact:** Work proceeds through source inventory, requirement synthesis, and gate scoring before writes beyond the handoff.  
**Code Refs:** `.lev/`  
**Canonical Ref:** `.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md`

**Alternatives Considered:**
- Emit a single broad task immediately: rejected because it would fail determinism and cold-start gates.
- Ask for clarification immediately: deferred until source inventory shows concrete missing inputs.
- Chosen option: inventory first, then emit artifacts only where evidence satisfies gates.

**Promotion:** stay in handoff

**Follow-up Required:**
- [x] Inventory `.lev/`.
- [x] Run prior-art searches.
- [x] Score readiness for `$propose` artifact emission.

### D2: Extend `deadzone/.lev` as canonical PM home

**When:** 2026-05-14  
**Context:** Root `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/` contains a richer UX pass, while `deadzone/.lev/pm/specs/` already contains backend scope, API contract, event schema, FE brief, and an agent task bundle.  
**Decision:** Create `$propose` task folders under `deadzone/.lev/pm/tasks/` and cite both UX runs plus the existing PM specs.  
**Rationale:** The implementation target and canonical API/task prior art are already inside `deadzone/.lev`; duplicating a root PM tree would split source of truth.  
**Impact:** New propose artifacts should extend `deadzone/.lev/pm/specs/*` and `deadzone/.lev/pm/plans/deadzone-agent-task-bundle.yaml`, while the root handoff records this session.  
**Code Refs:** `deadzone/.lev/pm/specs/deadzone-backend-scope.yaml`, `deadzone/.lev/pm/specs/deadzone-api-contract.yaml`, `deadzone/.lev/pm/plans/deadzone-agent-task-bundle.yaml`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/problem_spec.yaml`  
**Canonical Ref:** `deadzone/.lev/pm/tasks/`

**Alternatives Considered:**
- Write a root-level PM task tree: rejected because it would compete with existing `deadzone/.lev` artifacts.
- Write a markdown backend PRD: rejected because local instruction says not to save markdown unless explicitly asked.
- Chosen option: emit YAML propose artifacts in the existing DeadZone PM tree.

**Promotion:** stay in handoff

**Follow-up Required:**
- [x] Emit `dna.yaml` and `execution.yaml` artifacts.
- [x] Audit coverage against both UX runs and existing PM specs.

### D3: Split backend PRD into four execution-ready propose tasks

**When:** 2026-05-14  
**Context:** The combined source set spans FE/BE contract, aggregate intelligence, mock/replay demo path, and live/mesh credibility path.  
**Decision:** Emit four task folders: `deadzone-be-contract-spine`, `deadzone-be-intelligence-alerts`, `deadzone-be-mock-replay`, and `deadzone-be-live-mesh`.  
**Rationale:** These are independent enough for execution routing while still covering the full backend PRD. Each folder has `dna.yaml`, `execution.yaml`, verifier commands, write scopes, constraints, and cold-start context.  
**Impact:** Implementation agents can execute the backend in contract-first order and the frontend partner has a stable PRD/contract target.  
**Code Refs:** `deadzone/.lev/pm/specs/deadzone-backend-prd.yaml`, `deadzone/.lev/pm/tasks/deadzone-be-contract-spine/execution.yaml`, `deadzone/.lev/pm/tasks/deadzone-be-intelligence-alerts/execution.yaml`, `deadzone/.lev/pm/tasks/deadzone-be-mock-replay/execution.yaml`, `deadzone/.lev/pm/tasks/deadzone-be-live-mesh/execution.yaml`  
**Canonical Ref:** `deadzone/.lev/pm/specs/deadzone-backend-prd.yaml`

**Alternatives Considered:**
- One umbrella execution task: rejected because it would mix contract, source engines, and live adapters into a cold-start-hostile unit.
- A markdown PRD only: rejected because it would not satisfy `$propose` artifact requirements and local markdown restrictions.
- Chosen option: YAML PRD plus four `$propose` folders.

**Promotion:** stay in handoff

**Follow-up Required:**
- [x] Validate YAML parsing.
- [x] Validate required `$propose` structural fields.

## Code Context

### Files Modified

| File | Change Type | Lines | Status | Notes |
|------|-------------|-------|--------|-------|
| .lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md | added/modified | ~230 | complete | Required session handoff |
| deadzone/.lev/pm/specs/deadzone-backend-prd.yaml | added | ~200 | complete | Consolidated backend PRD and source map |
| deadzone/.lev/pm/tasks/deadzone-be-contract-spine/dna.yaml | added | ~45 | complete | Contract-spine task DNA |
| deadzone/.lev/pm/tasks/deadzone-be-contract-spine/execution.yaml | added | ~180 | complete | Contract-spine execution plan |
| deadzone/.lev/pm/tasks/deadzone-be-intelligence-alerts/dna.yaml | added | ~40 | complete | Intelligence/alerts task DNA |
| deadzone/.lev/pm/tasks/deadzone-be-intelligence-alerts/execution.yaml | added | ~175 | complete | Intelligence/alerts execution plan |
| deadzone/.lev/pm/tasks/deadzone-be-mock-replay/dna.yaml | added | ~45 | complete | Mock/replay task DNA |
| deadzone/.lev/pm/tasks/deadzone-be-mock-replay/execution.yaml | added | ~250 | complete | Mock/replay execution plan |
| deadzone/.lev/pm/tasks/deadzone-be-live-mesh/dna.yaml | added | ~42 | complete | Live/mesh task DNA |
| deadzone/.lev/pm/tasks/deadzone-be-live-mesh/execution.yaml | added | ~250 | complete | Live/mesh execution plan |

**Total Changes:**
- Files added: 9
- Files modified: 1
- Files deleted: 0
- Lines changed: planning artifacts only

### Files Loaded Into Context

| Order | File | Why Loaded | Key Understanding | Why It Matters |
|------|------|------------|-------------------|----------------|
| 1 | /Users/jean-patricksmith/.agents/skills/work/SKILL.md | Required by AGENTS/work routing | Handoff, tracking, alignment, prior art, routing are hard gates | Defines session process |
| 2 | /Users/jean-patricksmith/.agents/skills/propose/SKILL.md | User requested `$propose` artifacts | dna.yaml/execution.yaml require scored, execution-ready vertical slices | Defines artifact contract |
| 3 | /Users/jean-patricksmith/.agents/skills/work/templates/handoff.md | Handoff template | Session continuity must record loaded files, findings, decisions, timeline | Defines this file structure |
| 4 | deadzone/.lev/pm/specs/deadzone-backend-scope.yaml | Existing backend scope prior art | Mock/replay/WebSocket are must-ship; live adapters are optional/disabled by default | Prevents duplicate PRD scope |
| 5 | deadzone/.lev/pm/specs/deadzone-api-contract.yaml | Existing FE/BE contract | REST and WebSocket payload schemas are already defined around aggregate intelligence | Provides backend contract spine |
| 6 | deadzone/.lev/pm/plans/deadzone-agent-task-bundle.yaml | Existing agent plan | BE/FE dependency graph exists but is not `$propose` dna/execution format | Input for task conversion |
| 7 | .lev/ux/20260514-101706-deadzone-mvp-crowd-intel/ | Richer UX run | Adds explicit Mock/Replay/Live/Mesh progression, timing, provenance, topology, reset, and degradation behavior | Fills full PRD coverage gaps |

## Open Questions

### Immediate (Next Session)

1. None for this objective; execution can start from `deadzone/.lev/pm/tasks/deadzone-be-contract-spine/`.

### Short-term (This Week)

1. Implement the contract spine first, then intelligence/alerts, mock/replay, and live/mesh.
2. Add a git boundary before close/sync workflows, because `incubator` and `deadzone` are not git repositories.
