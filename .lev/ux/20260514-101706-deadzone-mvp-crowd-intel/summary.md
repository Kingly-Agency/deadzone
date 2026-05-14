# DeadZone MVP — UX Pipeline Summary

**Run:** `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/`
**Date:** 2026-05-14
**Mode:** AUTO (full 7-step pipeline)
**Gate decision:** **proceed** (validated twice: Step 0b domain exploration + Step 1b synthetic user research)

---

## Problem & Success Criteria

Hackathon judges need to verify in **5 minutes** that a passive-RF crowd-intelligence platform actually works — not just animates. DeadZone packages a Mock → Replay → Live → Mesh progression behind a single `docker compose up`, with honest data provenance so skeptics can drill into sensing, and headline metrics so generalists grasp it in 30 seconds. Aggregate-only telemetry. Cross-platform. Deterministic demo path.

Success means: heatmap legible in 30s, at least one alert fires by 90s, mode switch under 400ms with no white flash, skeptic can drill into raw events in ≤3 clicks, operator gets numeric zone occupancy (not just gradient) above the fold, reset works without page reload.

`[90% confident]` Synthetic research surfaced strong convergence across 5 personas on these criteria; the open risk is whether the Wi-Fi-irony framing (E5) lands as insight or flaw in the live pitch.

---

## Wireframe Screen List (Ordered)

1. **Dashboard** (default) — heatmap + headline metrics + alerts right rail + persistent ModeChip
2. **Zone Detail** — slide-in panel triggered by zone click; numeric count + trend sparkline
3. **Sensor Topology** — toggle overlay on heatmap; coverage gaps in diagonal hatch
4. **Replay Scenario Picker** — bottom drawer with 4 scenarios + scrubber
5. **Mode Switcher Dropdown** — header chip popover with availability dots
6. **Alerts Panel** — always-visible right rail; severity badges; non-empty zero state
7. **Demo Reset** — toast for Mock/Replay; confirm modal for Live/Mesh

---

## Key Tradeoffs

| Tension | Resolution |
|---|---|
| Spectator wants modes hidden vs Investigator wants them surfaced | Auto-select best mode on load; expose switcher via header chip (secondary, not loud) |
| Topology as proof-of-engineering vs noise to generalist | Collapsible **toggle overlay**, default off |
| Alert depth: one-dramatic vs severity-ack workflow | MVP: severity badge + visual-only ack. Post-MVP: routing/escalation (mentioned in pitch) |
| Provenance: subtle vs prominent | Always-on ProvenanceBadge, color-coded, never banner-loud |
| Degradation: silent fallback vs explicit failure | Silent in Mock/Replay (Kenji); explicit in Live/Mesh (Tomasz) |

---

## Smallest Shippable Slice

**Goal:** demo-quality MVP that satisfies Spectator job (`job-1-glance`) and Developer job (`job-4-rehearse`) only.

1. AppShell + Header (brand, ModeChip=MOCK badge, Reset button)
2. Mock event generator with seeded RNG and 90s alert event
3. WebSocket pipeline (one direction: server → client)
4. HeatmapLayer + Legend + HeadlineMetricsBar
5. AlertsPanel with non-empty zero state ("No active alerts — system nominal")
6. Reset (R key) without page reload

`[85% confident]` That slice covers a 5-minute Spectator demo. It does NOT cover Investigator drill-down (mode switching, topology) or Operator zone-detail. Ship the slice, run end-to-end with a judge stand-in **before** adding Replay/Live/Topology.

→ **Next:** start building the smallest slice; spike a 30s prototype of HeadlineMetricsBar + HeatmapLayer + Legend to verify Leaflet + Heatmap.js perf on a 1440x900 viewport
→ **Related:** if you need a `.pen` wireframe deliverable, the `pencil` MCP tool can render `wireframes.md` ASCII as a design file at `.lev/ux/.../wireframes.pen`

---

## Open Questions

1. **Wi-Fi-irony framing** — is the pitch deck planning to address this head-on? Without it, Raj-class judges may downgrade. (E5, AP-5)
2. **Floorplan source** — what venue is being demoed? Need a real floorplan PNG/SVG by demo day. (Affects Heatmap layer + zone polygons in `ia_schema.json`)
3. **Replay scenario provenance** — synthetic-recorded or actually-recorded? Investigator personas (Raj, Kwame) specifically reward genuine recordings. (Affects credibility of Replay mode)
4. **Color-blind validation** — viridis palette is specified, but the demo should be eyeballed by a CVD simulator (e.g., Sim Daltonism) before judging. (LC-5, AP-4)
5. **Multi-agency / role-based views** — Carla's `job-7-share-picture` is explicitly post-MVP, but if the pitch mentions enterprise expansion, this is the highest-value adjacency to call out.

---

## Pipeline Cross-Reference

| Step | Artifact | Notes |
|---|---|---|
| -1 | `request.txt` | Original PRD |
| 0 (prior art) | inline | Empty incubator repo; no prior UX runs to extend |
| 0.5 (lev-ref) | inline | Patterns applied to this summary (confidence, → Next, → Related, 💡 Tip) |
| 0.6 (skills-db) | `routed_skills.json` | 3 skills selected: interactive-visualization-creator, ui-ux-pro-max, design-doc-mermaid |
| 0b (domain) | `domain_exploration.md` | 3 unconstrained personas (festival ops, researcher, public-safety) → **proceed** |
| 1 (problem) | `problem_spec.yaml` | 7 success criteria, scope.in/out crisp |
| 1b (research) | `study_design.yaml`, `user_and_agent_research.md` | 5 personas × concept; 5 convergences, 5 divergences, 5 edge cases → **proceed** |
| 2 (JTBD) | `jobs.graph.json` | 7 jobs (5 MVP, 2 post-MVP), 4 user types |
| 3 (tasks) | `task_graph.json` | 8 tasks with happy_path + failure_modes |
| 4 (IA) | `ia_schema.json` | 8 entities, 8 relationships, single-screen nav |
| 5 (FSM) | `interaction_fsm.json` | 8 screens × ~80 transitions, 90s alert event, R-key global |
| 6 (components) | `components.md` | 37 components, 6 composition rules, design tokens |
| 7 (wireframes) | `wireframes.md` | 7 screens, ASCII frames per state variant |
| 8 (constraint) | `constraint_bundle.yaml` | <6K target compressed bundle for agent handoff |

---

## 💡 Tip

The most surprising research finding was **AP-5 (Wi-Fi irony)** — judges may read "Wi-Fi-dependent dead-Wi-Fi-zone detector" as either a fatal flaw or a brilliant product insight. The framing happens in the **pitch**, not the product. If you only ship great UX, Raj-class judges will still ding it. **Bake the answer into the talk track:** "Live mode uses Wi-Fi where available; Mesh mode is precisely the answer to what happens when Wi-Fi isn't." Then the demo's graceful Live→Replay fallback **becomes** the proof.

---

**Confidence:** synthetic (all personas constructed, not interviewed). Validate against a real judge stand-in before demo day if at all possible.
