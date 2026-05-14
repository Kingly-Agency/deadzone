---
status: active
workstream: bmw-m-design-language
component: ux
slug: bmw-m-design-language
session: 1
created_at: 2026-05-14
predecessor: 20260514-merge-reconcile-backend-vs-ui-session-1.md
confidence: 0.7
decisions_start: D1
related_tasks: []
related_docs:
  - .lev/pm/designs/bmw-m-design-language.md
  - .lev/pm/designs/bmw-m-design-language-source.md
  - .lev/pm/handoffs/20260514-merge-reconcile-backend-vs-ui-session-1.md
  - docs/deadzone-frontend-prd.yaml
depends_on: []
canonical_refs:
  - .lev/pm/designs/bmw-m-design-language.md
---

# Session Handoff: BMW M Design Language

## You Are Here

**Workstream:** bmw-m-design-language
**Component:** ux
**Session:** 1
**Status:** active

Captured BMW M's marketing-surface design language as the canonical DeadZone visual identity. Source spec + DeadZone-mapped design doc are filed in `.lev/pm/designs/`. **No frontend code has been changed yet** — implementation is pending user direction on scope (full restyle vs phased rollout).

## Next Agent Brief

**Long-Term Goal:** DeadZone's UI carries BMW M's industrial-precision marketing language: black canvas, white BMW Type Next Latin (Inter substitute) headlines in UPPERCASE, M tricolor stripe as the brand signature, sharp rectangular silhouettes, full-bleed venue map / heatmap as the brand voltage.

**Done Condition:** Every primary component (Header, Sidebar, MetricsBar, VenueMap, HeatmapDashboard, AlertsPanel, ZoneDetail, ReplayControls, Footer) renders in the BMW M tokens. Visual review against `.lev/pm/designs/bmw-m-design-language.md` Component Map passes.

**Current Execution Slice:** Design captured. **Awaiting user decision on rollout strategy** — see Open Questions below.

**Why This Slice Now:** Before touching `styles.css` again, lock the design intent so the next implementation pass doesn't drift. The current UI was merged from a concurrent agent and has its own internally-consistent light-mode language; ripping that out is a directional change that needs explicit go-ahead.

**Out of Scope This Session:** Any CSS changes; font-license procurement; photography asset sourcing; configurator surfaces (DeadZone has no equivalent).

## Roadmap To Goal

**Goal:** BMW M visual identity applied across the DeadZone frontend.
**Done Condition:** Every component renders in tokens defined in `.lev/pm/designs/bmw-m-design-language.md` Token Map.
**Remaining Steps:** 5 phased PRs (see Phased Rollout in the design doc).

### Step 1: Token swap (current — pending user go-ahead)
- Replace `:root` CSS variables in `frontend/src/styles.css` with the BMW M token set
- Map old token names to new ones via aliases so component classes keep working
- Re-link `MODE_TOKENS` in `frontend/src/types.ts` to the new color values
- Exit criteria: every existing component renders on black canvas with white text; layout unchanged

### Step 2: Typography swap
- Add Inter Variable from Google Fonts (BMW Type Next Latin substitute)
- Apply weight + tracking rules: display 700, body 300, button 1.5px tracking
- Uppercase display headlines

### Step 3: Radius + button silhouette
- Set `--radius-*` to BMW values (mostly 0)
- Convert primary CTA to outlined-rectangle style
- Reserve `--radius-full` for icon buttons

### Step 4: M tricolor + signature components
- Add `m-stripe-divider` component (4px tricolor band)
- Apply to Header left edge, Sidebar top edge

### Step 5: Layout retune
- Bump spacing tokens (96px section padding)
- Convert MetricsBar to spec-cell row
- Convert VenueMap container to full-bleed band

## Checkpoints

| T+0 | User pasted full BMW M design language spec |
| T+1 | Created `.lev/pm/designs/` directory (didn't exist yet) |
| T+2 | Filed source spec verbatim at `.lev/pm/designs/bmw-m-design-language-source.md` (immutable reference) |

### ⚡ CHECKPOINT 1 — Captured BMW M and mapped to DeadZone

**Current State:** Two design docs filed: verbatim source + DeadZone-mapped variant with token map, component map (BMW M ↔ DeadZone component-by-component), decisions, phased rollout plan, risks.
**Context:** User asked "add this as the design language" — ambiguous between (a) save the spec, (b) apply it, or (c) both. Took the conservative route: save first, ask before touching CSS.
**Files Loaded:** `frontend/src/styles.css` (token survey), source spec from user message.
**Files Modified:**
- created: `.lev/pm/designs/bmw-m-design-language.md` (DeadZone-mapped variant, ~250 lines)
- created: `.lev/pm/designs/bmw-m-design-language-source.md` (verbatim source, ~150 lines)
**Understanding:** Current `styles.css` is a light-mode language (white surfaces, Inter, 12px radius). BMW M is its inverse: black canvas, BMW Type Next Latin (Inter substitute), 0px radius. The DeadZone-mapped doc translates BMW M's "full-bleed automotive photography" role to DeadZone's venue map / heatmap — the data IS the brand voltage. M tricolor stays brand-identity-only; never used as button fill or chart color (preserves brand discipline).
**Progress:** Design captured + phased rollout drafted (5 PRs). Implementation paused at gate.
**Next Steps:** User confirms rollout strategy before any CSS changes. Likely Phase 1 token swap as the first PR.

## Decisions Log

### D1: Capture before apply

**When:** T+0
**Context:** "Add this as the design language" could mean save the spec or apply it immediately. The current `styles.css` is internally consistent and freshly merged from a concurrent agent; ripping it out without explicit go-ahead would discard their work twice in one day.
**Decision:** Save the spec as canonical design artifact, draft the DeadZone-mapped translation, then ask the user about implementation scope before touching code.
**Rationale:** Per the executing-actions-with-care default: hard-to-reverse work (full-app restyle) gets explicit confirmation. The design doc is reversible; the restyle is much less so.
**Impact:** Implementation is paused; design is locked.
**Code Refs:**
- `.lev/pm/designs/bmw-m-design-language.md` (mapped variant)
- `.lev/pm/designs/bmw-m-design-language-source.md` (verbatim)
**Promotion:** stay in handoff
**Follow-up Required:**
- [ ] User confirms rollout scope (see Open Questions Q1)

### D2: Inter as the BMW Type Next Latin substitute

**When:** T+1
**Context:** BMW Type Next Latin is licensed. We can't ship it without a license.
**Decision:** Document Inter Variable at weights 700/300 with display tracking -0.5px as the substitute, per the source spec's "Note on Font Substitutes" section.
**Rationale:** Source spec explicitly names Inter as the open-source replacement. Tracking adjustment is needed because BMW Type's natural cap-height handles display spacing differently.
**Impact:** Editorial signature (weight contrast 700 vs 300, uppercase tracking 1.5px) survives the substitution. The font face won't be pixel-identical but the design language reads as intended.
**Promotion:** stay in handoff

### D3: Density ramp redshifted (no cool blue end)

**When:** T+1
**Context:** Current heatmap viridis ramp goes `#440154` → `#3B528B` → `#21908C` → `#5DC863` → `#FDE725` (cool purple → blue → green → yellow). BMW M discourages introducing brand colors outside the M tricolor.
**Decision:** Replace the viridis ramp with a near-black-to-M-red ramp: `#0d0d0d` → `#3c3c3c` → `#7e7e7e` → `#f4b400` → `#e22718`. Empty zones are near-black (canvas), hot zones are M-red (crisis signal).
**Rationale:** Aligns the heatmap with brand discipline — M-red gets reserved for "real crowd-pressure crisis," matching BMW's "motorsport-pace callouts" treatment. The viridis cool end (blue/green) reads as off-brand on a BMW M surface.
**Impact:** All zones at saturation read as a sea of M-red — that's the intended "this is a real situation" signal.
**Promotion:** stay in handoff once implemented

## Code Context

### Files Loaded Into Context

| Order | File | Why Loaded | Key Understanding | Why It Matters |
|---|---|---|---|---|
| 1 | `frontend/src/styles.css` | Current token system survey | Light-mode tokens (`--bg` #F8FAFC, Inter, `--radius` 12px) are the inverse of BMW M | Phase 1 token swap touches this file primarily |
| 2 | `frontend/src/types.ts` | Mode token mapping survey | `MODE_TOKENS` lives here as a `Record<Mode, {color, label, badge}>` | Phase 1 also re-links these colors |
| 3 | `frontend/src/components/Sidebar.tsx` | Component reference | Logo SVG uses inline `linearGradient` (#6366F1 → #8B5CF6) — off-brand for BMW M | Will need swap to M-stripe in Phase 4 |
| 4 | `frontend/src/App.tsx` | Layout reference | Layout is `app-layout` flexbox: sidebar + (Header / MetricsBar / main-content / Footer) | Phase 5 layout retune touches this file's class names indirectly |

### Files Created

| File | Change Type | Lines | Status | Notes |
|---|---|---|---|---|
| `.lev/pm/designs/bmw-m-design-language.md` | added | +250 | complete | DeadZone-mapped variant |
| `.lev/pm/designs/bmw-m-design-language-source.md` | added | +150 | complete | Verbatim source — immutable |
| `.lev/pm/handoffs/20260514-bmw-m-design-language-session-1.md` | added | (this) | complete | Session handoff |

## Open Questions

### Immediate (Next Session)

1. **Rollout scope:** Full restyle now, phased 5-PR rollout, or design-only-and-defer? Recommend phased — see "Phased Rollout" in the design doc.
2. **Photography assets:** BMW M depends heavily on cinematic automotive photography. We have none. Should the venue map / heatmap fully substitute, or do we source venue-photography stock for hero bands?
3. **M-stripe colors:** Literal BMW (blue-light → blue-dark → red) or DeadZone-native (e.g., m-blue-light → mesh purple → m-red)? Literal feels stronger; native feels more honest.
4. **Wordmark:** "DeadZone" as the brand mark — keep current type or commission a custom wordmark inspired by BMW's roundel + M tricolor?

### Short-term (This Week)

1. Add Inter Variable from Google Fonts to `frontend/index.html` as the first concrete step.
2. Decide whether the current light-mode merge stays available behind a flag for stakeholder comparison.
3. Run a stakeholder review of `.lev/pm/designs/bmw-m-design-language.md` before locking implementation.

## Entity Matrix

| # | File | Path | State | Impact | Canonical Ref | Decision | Next |
|---|---|---|---|---|---|---|---|
| 1 | bmw-m-design-language.md | `.lev/pm/designs/bmw-m-design-language.md` | created | 5 | self | D1 | stakeholder review |
| 2 | bmw-m-design-language-source.md | `.lev/pm/designs/bmw-m-design-language-source.md` | created | 5 | self | D1 | immutable |
| 3 | styles.css | `frontend/src/styles.css` | loaded | 5 | bmw-m-design-language | — | Phase 1 token swap |
| 4 | types.ts | `frontend/src/types.ts` | loaded | 4 | bmw-m-design-language | D3 | re-link MODE_TOKENS |
| 5 | App.tsx | `frontend/src/App.tsx` | loaded | 3 | bmw-m-design-language | — | Phase 5 layout retune |
| 6 | Header.tsx | `frontend/src/components/Header.tsx` | planned | 4 | bmw-m-design-language | — | top-nav treatment |
| 7 | Sidebar.tsx | `frontend/src/components/Sidebar.tsx` | planned | 4 | bmw-m-design-language | — | M-stripe top edge |
| 8 | HeatmapDashboard.tsx | `frontend/src/components/HeatmapDashboard.tsx` | planned | 4 | bmw-m-design-language | D3 | density ramp redshift |
| 9 | MetricsBar.tsx | `frontend/src/components/MetricsBar.tsx` | planned | 4 | bmw-m-design-language | — | convert to spec-cell row |

## Meta

### Active Blockers

| Blocker | Impact | Waiting On | ETA | Workaround |
|---|---|---|---|---|
| User decision on rollout scope | High — blocks implementation | User | Unknown | Design doc is shareable as-is for stakeholder review |

### Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Stakeholders push back on "outage-looking" black canvas | Medium | Medium | Frame as "BMW M industrial-precision" not "dark mode"; show wireframes before code |
| Phased rollout produces 5 PRs that conflict with concurrent backend work | High | Low | Coordinate timing; each phase is isolated to frontend files |
| All-caps headlines fail screen-reader UX | Low | Medium | Use CSS `text-transform: uppercase` so underlying text stays sentence-case |
| Inter doesn't carry BMW Type's editorial weight at large display sizes | Medium | Low | -0.5px tracking adjustment at display-xl; accept the substitute gap |

### Learned Patterns

#### What Worked

1. **Saving the source spec verbatim alongside the mapped variant** — Two-file pattern: `*-source.md` (immutable, exactly what the user provided) + `*.md` (project-mapped translation). Lets future agents trust the source while editing the translation freely.
2. **Pausing implementation at the design gate** — User said "add as design language"; could have meant "save it" or "apply it." Saving the design + asking before touching CSS respects the "executing actions with care" principle for hard-to-reverse work.

### Context For Next Session

#### Mental Model

**Project State:** DeadZone MVP — backend (BLE auto-start, full envelope dispatch, capture endpoints) and frontend (light-mode sidebar UI + Heatmap page) both functional and pushed. BMW M design language captured but not applied.

**Current Focus:** Lock the visual identity. The current light-mode UI works but reads as generic SaaS; BMW M gives DeadZone a brand point of view.

**Critical Knowledge:**
1. Two design docs in `.lev/pm/designs/` — `bmw-m-design-language.md` (mapped) and `bmw-m-design-language-source.md` (immutable source).
2. No CSS has been changed yet. `frontend/src/styles.css` is still the light-mode language from commit `c7e7a75`.
3. The Heatmap page (commit `8122910`) uses scoped `.heatmap-page-*` class names — easy to retune in Phase 1.
4. Phased rollout in the design doc is recommended over one big PR — 5 PRs map to 5 review-sized chunks.

#### Quick Start Commands

```bash
cd /Users/jean-patricksmith/digital/kingly/apps/incubator/deadzone
cat .lev/pm/designs/bmw-m-design-language.md | less   # mapped variant
cat .lev/pm/designs/bmw-m-design-language-source.md | less   # source
git status                          # expect: clean
```

#### Configuration State

**Environment:**
- Frontend dev: vite on :3000
- Backend: FastAPI on :8000 (auto-starts BLE capture in `ble` mode)

### System Prompt for Next Agent

You are resuming a design workstream. The BMW M design language is captured in `.lev/pm/designs/`. The user previously asked for it to be added; the prior agent saved the spec but did NOT apply it (deliberate gate before hard-to-reverse work).

Before doing anything:
1. Read `.lev/pm/designs/bmw-m-design-language.md` — the DeadZone-mapped variant.
2. Confirm with the user which rollout phase to execute (see Phased Rollout section in the design doc, or Open Questions in this handoff).
3. Only after confirmation: start with Phase 1 (token swap in `frontend/src/styles.css`).

Return a context confidence score after reading the design doc plus this handoff.

### Context Confidence Score

**Context Confidence:** 0.7

Missing: user direction on rollout scope; whether photography assets will be sourced; whether the current light-mode UI needs to remain available behind a flag.

## Validation Checklist

### Session Completeness
- [x] 3+ chronological checkpoints (3)
- [x] Files worked + loaded explicitly listed
- [x] Understanding + importance captured
- [x] Decisions include rationale (D1, D2, D3)
- [x] Open items prioritized

### Knowledge Transfer
- [x] Critical paths documented
- [x] Patterns captured
- [x] Next-agent system prompt included
- [x] Context confidence score included
- [x] Sufficient for cold-start continuation
