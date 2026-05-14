---
status: completed
workstream: fe-prd
component: deadzone-ux-synthesis
slug: combine-two-ux-runs
session: 1
created_at: 2026-05-14
predecessor: null
confidence: 0.94
decisions_start: D1
related_tasks: []
related_docs:
  - docs/deadzone-frontend-prd.yaml
depends_on: []
canonical_refs:
  - .lev/ux/
---

# Session Handoff: FE PRD Deadzone UX Synthesis

## You Are Here

**Workstream:** fe-prd
**Component:** deadzone-ux-synthesis
**Session:** 1
**Status:** completed

The two DeadZone `.lev/ux` runs have been combined into `docs/deadzone-frontend-prd.yaml`, validated against BE tasks/contracts, committed, and pushed.

## Next Agent Brief

**Long-Term Goal:** Produce an exhaustive compare/contrast synthesis of the two `.lev/ux` runs and turn it into a frontend PRD for implementation planning.

**Done Condition:** Both UX runs are inventoried or a missing-run gap is explicitly proven, their artifacts are compared by requirement area, conflicts and shared decisions are resolved into frontend product requirements, and the PRD is delivered without violating the local markdown-save restriction.

**Current Execution Slice:** Complete; no active execution slice remains.

**Why This Slice Now:** The objective depends on comparing two concrete UX runs; synthesis before both source sets are found would be incomplete.

**Out of Scope This Session:** Git history changes, code implementation, destructive cleanup, broad unrelated repo inventory, and saving non-handoff markdown unless explicitly asked.

## Entity Matrix

| # | File | Path | State | Canonical Ref | Decision | Next |
|---|------|------|-------|---------------|----------|------|
| 1 | Rich UX run | .lev/ux/20260514-101706-deadzone-mvp-crowd-intel/ | loaded | user objective | D2 | synthesize |
| 2 | Canonical DeadZone UX run | deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/ | loaded | prior art | D2 | synthesize |
| 3 | FE PRD handoff | .lev/pm/handoffs/20260514-fe-prd-deadzone-ux-synthesis-session-1.md | created | work skill | D1 | keep updated |
| 4 | FE partner brief | deadzone/.lev/pm/specs/deadzone-frontend-partner-brief.yaml | loaded | prior art | D2 | supersede/extend |
| 5 | API contract | deadzone/.lev/pm/specs/deadzone-api-contract.yaml | loaded | prior art | D2 | bind PRD |
| 6 | FE PRD | docs/deadzone-frontend-prd.yaml | completed | current objective | D2/D3 | pushed |

## Roadmap To Goal

**Goal**: Produce a frontend PRD from an exhaustive comparison of two `.lev/ux` runs.
**Done Condition**: Source inventory, compare/contrast matrix, resolved FE requirements, gaps, and completion audit are all backed by concrete file evidence.
**Remaining Steps**: 0

### Step 1: Validate, commit, and push
- Complete: `docs/deadzone-frontend-prd.yaml` parses as YAML.
- Complete: API mode enum alignment passed against `.lev/pm/specs/deadzone-api-contract.yaml`.
- Complete: backend task coverage passed against `.lev/pm/plans/deadzone-agent-task-bundle.yaml`.
- Complete: committed and pushed to `origin/main`.

#### Step 2: Exhaustive compare/contrast
- Compare request, domain, problem spec, IA, task graph, FSM, components, wireframes, and constraints.
- Separate agreements, conflicts, omissions, and stronger source choices.

#### Step 3: Produce FE PRD
- Deliver frontend requirements, information architecture, interaction flows, components, states, accessibility, and acceptance criteria.
- Avoid saved markdown unless the user explicitly authorizes it.

#### Step 4: Completion audit
- Map the objective to evidence and identify any uncovered requirement before closing.

## Handoff Objective

Maintain a deterministic trail for combining `.lev/ux` sources into a frontend PRD. Record source files loaded, what each established, comparison decisions, output choices, and unresolved evidence gaps.

## Checkpoints

| T+0 | Session resumed from active objective -- current goal is FE PRD, not the stale backend PRD handoff. |
| T+1 | Work and UX skill instructions loaded -- handoff and UX artifact workflow are governing process. |
| T+2 | Existing backend handoff loaded -- relevant as stale context only, not the current goal artifact. |
| T+4 | Prior-art scan found the paired DeadZone UX run and existing DeadZone PM specs under `deadzone/.lev/`. |
| T+6 | User requested docs location and push; PRD target moved to `docs/deadzone-frontend-prd.yaml`. |
| T+7 | Backend compatibility check found and resolved the UX `Live` mode mismatch with API modes `ble`, `wifi`, and `hybrid`. |
| T+8 | Docs PRD and handoff update committed and pushed to `origin/main` at `9111e54`. |

### CHECKPOINT 1 -- FE Handoff Created

**Current State:** A scoped FE PRD handoff is active before synthesis work.
**Context:** The active objective asks to combine two `.lev/ux` runs exhaustively and produce the FE PRD.
**Files Loaded:** `/Users/jean-patricksmith/.agents/skills/work/SKILL.md`, `/Users/jean-patricksmith/.agents/skills/ux/SKILL.md`, `.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md`, `/Users/jean-patricksmith/.agents/skills/work/templates/handoff.md`
**Files Modified:** `.lev/pm/handoffs/20260514-fe-prd-deadzone-ux-synthesis-session-1.md` created.
**Understanding:** The prior handoff targeted backend PRD support and is not aligned to the FE PRD objective; a new handoff keeps this work scoped.
**Progress:** Session tracking is initialized for the current goal.
**Next Steps:** Locate the second `.lev/ux` run, perform prior-art scans, and load the source artifacts.

### CHECKPOINT 2 -- Source Set Confirmed

**Current State:** Both DeadZone UX runs and the local PM contract specs are loaded for synthesis.
**Context:** Root `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/` is the richer product/interaction pass; `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/` is the canonical implementation handoff pass.
**Files Loaded:** `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/summary.md`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/problem_spec.yaml`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/constraint_bundle.yaml`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/jobs.graph.json`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/task_graph.json`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/ia_schema.json`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/interaction_fsm.json`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/components.md`, `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/wireframes.md`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/summary.md`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/problem_spec.yaml`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/constraint_bundle.yaml`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/jobs.graph.json`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/task_graph.json`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/ia_schema.json`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/interaction_fsm.json`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/components.md`, `deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/wireframes.md`, `deadzone/.lev/pm/specs/deadzone-frontend-partner-brief.yaml`, `deadzone/.lev/pm/specs/deadzone-api-contract.yaml`, `deadzone/.lev/pm/specs/deadzone-backend-scope.yaml`, `deadzone/.lev/pm/specs/deadzone-event-envelope.schema.json`, `deadzone/.lev/pm/plans/deadzone-agent-task-bundle.yaml`.
**Files Modified:** `.lev/pm/handoffs/20260514-fe-prd-deadzone-ux-synthesis-session-1.md`.
**Understanding:** The first run anchors stable API/implementation scope and three-screen IA; the second run adds richer single-screen progressive disclosure, 4-mode provenance, detailed FSM, accessibility, and demo timing requirements.
**Progress:** Source inventory and prior-art requirements are complete; consumer-stack UX runs were inspected and excluded as unrelated.
**Next Steps:** Create the YAML FE PRD in the canonical DeadZone PM spec directory and validate it.

### CHECKPOINT 3 -- Docs PRD Backend-Compatible

**Current State:** FE PRD is in docs and explicitly checked against backend tasks and contracts.
**Context:** User requested the artifact be placed in `docs/`, pushed, and made compatible with BE tasks.
**Files Loaded:** `docs/deadzone-frontend-prd.yaml`, `.lev/pm/plans/deadzone-agent-task-bundle.yaml`, `.lev/pm/specs/deadzone-api-contract.yaml`, `.lev/pm/specs/deadzone-backend-scope.yaml`, `.lev/pm/specs/deadzone-event-envelope.schema.json`.
**Files Modified:** `docs/deadzone-frontend-prd.yaml`, `.lev/pm/handoffs/20260514-fe-prd-deadzone-ux-synthesis-session-1.md`.
**Understanding:** The backend API mode enum is `mock`, `replay`, `ble`, `wifi`, `mesh`, `hybrid`; `Live Sensors` must stay a UI grouping label, not a wire value.
**Progress:** Added `backend_task_compatibility`, mapped BE-01 through BE-06 to FE requirements, and named the three backend-required replay scenarios.
**Next Steps:** None; goal is complete.

### CHECKPOINT 4 -- Pushed

**Current State:** Work is complete and published.
**Context:** User requested `docs/`, push, and BE task compatibility.
**Files Loaded:** `docs/deadzone-frontend-prd.yaml`, `.lev/pm/plans/deadzone-agent-task-bundle.yaml`, `.lev/pm/specs/deadzone-api-contract.yaml`, git status and push output.
**Files Modified:** `.lev/pm/handoffs/20260514-fe-prd-deadzone-ux-synthesis-session-1.md`.
**Understanding:** The pushed PRD is in docs and contract-compatible; a final handoff update records completion after push.
**Progress:** Commit `9111e54` pushed to `origin/main`; final handoff status changed to completed.
**Next Steps:** None.

## Timeline

| Time | Checkpoint |
|------|------------|
| T+0 | Active objective received -- combine two `.lev/ux` runs and produce FE PRD |
| T+1 | `$work` and `$ux` skills loaded |
| T+2 | Existing backend handoff identified as stale for this goal |
| T+3 | FE PRD handoff created |
| T+4 | `.lev/ux`, `deadzone/.lev/ux`, and `consumer-stack/.lev/ux` scanned |
| T+5 | DeadZone UX pair and PM specs loaded for synthesis |
| T+6 | User requested docs placement and push |
| T+7 | Docs PRD made backend-compatible |
| T+8 | Commit `9111e54` pushed to `origin/main` |

## Decisions Log

### D1: Create a separate FE PRD handoff

**When:** 2026-05-14
**Context:** The only existing handoff describes backend PRD/propose work, while the active goal is a frontend PRD from UX runs.
**Decision:** Create a new handoff for FE PRD synthesis instead of mutating the backend handoff.
**Rationale:** The source artifacts and deliverable differ enough that reusing the backend handoff would make completion evidence ambiguous.
**Impact:** Current work is tracked under `fe-prd/deadzone-ux-synthesis`; the backend handoff remains untouched.
**Code Refs:** `.lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md`
**Canonical Ref:** `.lev/pm/handoffs/20260514-fe-prd-deadzone-ux-synthesis-session-1.md`

**Alternatives Considered:**
- Reuse the backend handoff: rejected because it states the wrong long-term goal.
- Ask for clarification before tracking: rejected because the active objective is already specific enough to begin source inventory.
- Chosen option: create a scoped FE handoff and continue.

**Promotion:** stay in handoff

**Follow-up Required:**
- [ ] Locate or disprove the second UX run in the current workspace.
- [ ] Compare source artifacts exhaustively.
- [ ] Produce FE PRD on an allowed output surface.

### D2: Use YAML instead of markdown for the FE PRD artifact

**When:** 2026-05-14
**Context:** The objective asks for a FE PRD, but local instructions prohibit saving new markdown unless explicitly asked. Existing DeadZone PM artifacts are YAML specs under `deadzone/.lev/pm/specs/`.
**Decision:** Produce the FE PRD as YAML, extending the existing FE partner brief and binding to the API contract.
**Rationale:** YAML satisfies the artifact requirement without creating a new markdown document.
**Impact:** FE implementation agents should use the new PRD as the consolidated source, with the older FE partner brief treated as a shorter implementation brief.
**Code Refs:** `deadzone/.lev/pm/specs/deadzone-frontend-partner-brief.yaml`, `deadzone/.lev/pm/specs/deadzone-api-contract.yaml`
**Canonical Ref:** `docs/deadzone-frontend-prd.yaml`

**Alternatives Considered:**
- Save a markdown PRD: rejected by local instruction.
- Deliver only in chat: rejected because the active goal calls for a produced PRD and existing PM specs are file-based.
- Chosen option: create a YAML PRD artifact and place it under `docs/` per user request.

**Promotion:** stay in handoff

**Follow-up Required:**
- [x] Create `docs/deadzone-frontend-prd.yaml`.
- [x] Validate YAML syntax.
- [x] Audit objective coverage against both UX runs.

### D3: Treat Live as a UI grouping, not a backend mode

**When:** 2026-05-14
**Context:** UX-B uses "Live" in the product story, but `.lev/pm/specs/deadzone-api-contract.yaml` defines backend `Mode` as `mock`, `replay`, `ble`, `wifi`, `mesh`, and `hybrid`.
**Decision:** The FE PRD must use backend mode values exactly and may group `ble`, `wifi`, and `hybrid` under the UI label `Live Sensors`.
**Rationale:** This keeps the FE PRD compatible with BE tasks and prevents agents from implementing an unsupported `live` wire value.
**Impact:** Mode dropdown, fixtures, reset behavior, and disabled-mode handling are contract-safe.
**Code Refs:** `.lev/pm/specs/deadzone-api-contract.yaml`, `.lev/pm/plans/deadzone-agent-task-bundle.yaml`, `docs/deadzone-frontend-prd.yaml`
**Canonical Ref:** `docs/deadzone-frontend-prd.yaml`

**Alternatives Considered:**
- Add `live` to the contract: rejected because the task is FE PRD compatibility, not BE contract mutation.
- Hide live sensing entirely: rejected because UX/pitch still needs the live progression.
- Chosen option: use `Live Sensors` as display grouping over concrete backend modes.

**Promotion:** stay in handoff

**Follow-up Required:**
- [x] Validate PRD mode enum against API mode enum.
- [x] Map BE tasks to FE requirements.
- [x] Push docs update.

## Code Context

### Files Modified

| File | Change Type | Lines | Status | Notes |
|------|-------------|-------|--------|-------|
| docs/deadzone-frontend-prd.yaml | modified | ~40 | complete | Added BE task compatibility and contract-safe mode mapping |
| .lev/pm/handoffs/20260514-fe-prd-deadzone-ux-synthesis-session-1.md | modified | ~65 | complete | Updated user request, decisions, validation, and push status |

**Total Changes:**
- Files added: 0
- Files modified: 2
- Files deleted: 0
- Lines changed: +135 / -0

### Files Loaded Into Context

| Order | File | Why Loaded | Key Understanding | Why It Matters |
|------|------|------------|-------------------|----------------|
| 1 | /Users/jean-patricksmith/.agents/skills/work/SKILL.md | Required by repo instruction | Work requires handoff, entity tracking, alignment, prior art, and route before execution | Governs process |
| 2 | /Users/jean-patricksmith/.agents/skills/ux/SKILL.md | Goal is UX-run synthesis and FE PRD | `.lev/ux` runs contain request, problem, IA, FSM, components, wireframes, constraints, and summary artifacts | Defines source set |
| 3 | .lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md | Check existing handoff | Existing active handoff is backend-focused and stale for this FE PRD goal | Avoids blending goals |
| 4 | /Users/jean-patricksmith/.agents/skills/work/templates/handoff.md | Follow local template | Required sections and timeline conventions confirmed | Shapes this handoff |
| 5 | deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/ | Source UX run | Canonical first pass: dashboard/replay/mesh screens, API-aligned component boundaries, and partner handoff | Anchors implementation scope |
| 6 | .lev/ux/20260514-101706-deadzone-mvp-crowd-intel/ | Source UX run | Richer pass: single-screen progressive disclosure, 4 modes, detailed state machine, accessibility, and demo timing | Adds exhaustive PRD detail |
| 7 | deadzone/.lev/pm/specs/deadzone-api-contract.yaml | Contract prior art | FE must render `IntelligenceSnapshot` plus WebSocket `StreamEnvelope` updates and preserve sequence/freshness semantics | Defines FE/BE boundary |
| 8 | deadzone/.lev/pm/specs/deadzone-frontend-partner-brief.yaml | FE prior art | Existing brief already states dashboard-first, source/freshness visibility, state rules, and acceptance checks | New PRD should supersede with richer detail |
| 9 | docs/deadzone-frontend-prd.yaml | Current deliverable | Docs PRD now maps BE-01 through BE-06 and uses the exact backend mode enum | Satisfies docs placement and BE compatibility request |

## Open Questions

### Immediate (Next Session)

1. None; docs PRD is pushed.
2. None; both DeadZone UX runs are present under `.lev/ux/`.

### Short-term (This Week)

1. Which app under the incubator owns implementation after the FE PRD is accepted?
2. Should FE requirements feed into `$propose` task artifacts after the PRD is complete?
