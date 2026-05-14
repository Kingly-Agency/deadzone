---
status: active
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
**Status:** active

Combining existing `.lev/` context into execution-ready backend PRD/propose artifacts that support a frontend build.

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
| 2 | handoff | .lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md | created | work skill | D1 | keep updated |
| 3 | DeadZone PM specs | deadzone/.lev/pm/specs/ | loaded | prior art | D2 | extend |
| 4 | DeadZone agent plan | deadzone/.lev/pm/plans/deadzone-agent-task-bundle.yaml | loaded | prior art | D2 | convert to propose |
| 5 | DeadZone UX canonical run | deadzone/.lev/ux/20260514-101228-deadzone-mvp-prd/ | loaded | prior art | D2 | merge |
| 6 | DeadZone richer UX run | .lev/ux/20260514-101706-deadzone-mvp-crowd-intel/ | loaded | user objective | D2 | merge |

## Roadmap To Goal

**Goal**: Convert `.lev/` source context into backend PRD/propose artifacts for frontend build readiness.  
**Done Condition**: Source inventory, prior-art report, requirement synthesis, and task artifacts/checklist are all backed by concrete file evidence.  
**Remaining Steps**: 5

### Step 1: Inventory and prior art
- List `.lev/` files and directory structure.
- Run required prior-art searches for backend PRD, replay, mock, real data, mesh, and FE build support.
- Identify existing designs/specs/plans/tasks/decisions that should be extended instead of duplicated.
- Exit when source candidates and gaps are explicit.

#### Step 2: Synthesize backend requirement map
- Combine replay, mock, real-data, and mesh sources into backend capability groups.
- Map each capability to source refs, FE dependency, verifier, and unresolved gaps.

#### Step 3: Emit or update propose artifacts
- Create execution-ready task folders only if `$propose` gates pass.
- Otherwise, capture the smallest alignment question or blocked-input list.

#### Step 4: Completion audit
- Map objective requirements to files and command evidence.
- Verify emitted artifacts cover every requirement, not just proxy manifests.

#### Step 5: Close handoff
- Update session state, decisions, timeline, and next actions.

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

## Timeline

| Time | Checkpoint |
|------|------------|
| T+0 | Session start — objective and skill instructions loaded |
| T+1 | Handoff created and entity matrix seeded |
| T+2 | Prior art found canonical DeadZone PM/UX artifacts under `deadzone/.lev/` |

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
- [ ] Score readiness for `$propose` artifact emission.

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
- [ ] Emit `dna.yaml` and `execution.yaml` artifacts.
- [ ] Audit coverage against both UX runs and existing PM specs.

## Code Context

### Files Modified

| File | Change Type | Lines | Status | Notes |
|------|-------------|-------|--------|-------|
| .lev/pm/handoffs/20260514-be-prd-support-fe-build-session-1.md | added | +120 | in_progress | Required session handoff |

**Total Changes:**
- Files added: 1
- Files modified: 0
- Files deleted: 0
- Lines changed: +120 / -0

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

1. Does `.lev/` contain enough backend-specific source context to auto-emit execution-ready artifacts?
2. Which FE build expectations should be treated as canonical if `.lev/` has conflicting UX/product notes?

### Short-term (This Week)

1. Should the backend PRD become a dedicated spec/design artifact if the markdown ban is explicitly waived?
2. Which implementation repo owns the backend once the PRD/propose artifacts are ready?
