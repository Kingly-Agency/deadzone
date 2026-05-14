---
type: design
created: 2026-05-14T11:50:00
updated: 2026-05-14T11:50:00
status: draft
domain: ux
confidence: 0.95
author: claude
related_tasks: []
related_docs:
  - .lev/pm/handoffs/20260514-merge-reconcile-backend-vs-ui-session-1.md
  - docs/deadzone-frontend-prd.yaml
related_specs: []
---

# Design: BMW M Design Language for DeadZone

## Executive Summary

Adopt BMW M's marketing-surface design language as DeadZone's visual identity: near-pure black canvas, white BMW Type Next Latin headlines in UPPERCASE, M tricolor stripe (blue-light → blue-dark → red) as the sparing brand accent, sharp rectangular silhouettes (border-radius mostly zero), and full-bleed photography as the primary brand voltage. This replaces the current light-mode sidebar layout's chrome-heavy aesthetic with an industrial-precision marketing language that treats the venue map and density visualization as the equivalent of BMW's "full-bleed automotive photography" — the data IS the brand voltage.

The current light-mode UI (merged from concurrent agent commit `c7e7a75`) is functional but generic-SaaS. BMW M's editorial signature — heavy display 700 against light body 300, uppercase letterspaced labels, zero-radius rectangles, M-stripe accents — gives DeadZone a distinct visual point of view that matches the "industrial-grade crowd intelligence" positioning in the frontend PRD.

## Problem Framing

### Current State

`frontend/src/styles.css` defines a light-mode design system:
- Surface stack: `#F8FAFC` (bg) → `#FFFFFF` (surface) → `#F1F5F9` / `#E2E8F0`
- Text on light: `#0F172A` / `#475569` / `#94A3B8`
- Inter font, 14px base
- Border radius: `--radius` 12px / `--radius-sm` 8px / `--radius-pill` 999px
- Mode color tokens: mock `#3B82F6`, ble `#10B981`, mesh `#8B5CF6`, etc.

The current visual is competent but reads as "another logging dashboard." It does not signal "crowd intelligence at venue scale" or carry brand voltage beyond utility.

### Target State

DeadZone runs on a near-pure black canvas (`#000`) with white BMW Type Next Latin headlines in UPPERCASE, body in BMW Type Next Latin Light at 300 weight. The M tricolor stripe (`#0066b1` → `#1c69d4` → `#e22718`) marks brand-identity moments (logo, motorsport-style chrome, model-detail headers). Rectangles dominate (radius zero almost everywhere); circles are reserved for icon buttons. Spacing is generous and grid-aligned (`section` 96px, `xxl` 64px, `xl` 40px).

The venue heatmap takes BMW's "full-bleed automotive photography" role — it fills entire bands edge-to-edge as the brand's primary voltage. Spec cells (`#0d0d0d` background) carry zone metrics with display-sm headline + label-uppercase below — the BMW spec-table treatment fits DeadZone's "estimated devices / capacity / pressure score" data shape perfectly.

## Token Map

### Colors

| Token | Hex | Use |
|---|---|---|
| `--canvas` | `#000000` | Default page floor |
| `--surface-soft` | `#0d0d0d` | Spec cells, footer strips |
| `--surface-card` | `#1a1a1a` | Cards, secondary buttons, icon-button backgrounds |
| `--surface-elevated` | `#262626` | Nested cards inside dark bands |
| `--carbon-gray` | `#2b2b2b` | Technical-spec cards (carbon-fiber tone) |
| `--hairline` | `#3c3c3c` | 1px dividers on dark |
| `--hairline-strong` | `#262626` | One-step elevation borders |
| `--on-dark` | `#ffffff` | All headline + primary text |
| `--body` | `#bbbbbb` | Default running text |
| `--body-strong` | `#e6e6e6` | Lead paragraphs |
| `--muted` | `#7e7e7e` | Footer links, breadcrumbs, captions |
| `--m-blue-light` | `#0066b1` | M tricolor stop 1 |
| `--m-blue-dark` | `#1c69d4` | M tricolor stop 2 (= heritage BMW blue) |
| `--m-red` | `#e22718` | M tricolor stop 3 |
| `--electric-blue` | `#0653b6` | EV accent (M xDrive electric) |
| `--warning` | `#f4b400` | Technical-warning callouts |
| `--success` | `#0fa336` | Order-confirmation states |

**DeadZone-specific mappings:**
- Mode tokens override the current `MODE_TOKENS`: `live`/`ble` → `--m-red`, `mock` → `--muted`, `replay` → `--warning`, `mesh` → `--m-blue-dark`, `wifi` → `--m-blue-light`, `hybrid` → white.
- Density ramp inherits viridis (already in heatmap), but stripped of the cool blue end — start at near-black `#0d0d0d` and ramp to `--m-red` for hot zones. Saves the M-red impact for crowd-pressure crisis moments.
- Severity tokens: critical → `--m-red`, warning → `--warning`, info → `--m-blue-light`.

### Typography

Font stack: `"BMW Type Next Latin", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`. Fallback: **Inter** at 700/300 with display tracking adjusted to -0.5px.

| Token | Size | Weight | Tracking | Use |
|---|---|---|---|---|
| `--display-xl` | 80px | 700 | 0 | Hero h1 ("LIVE CROWD INTELLIGENCE.") |
| `--display-lg` | 56px | 700 | 0 | Section heads |
| `--display-md` | 40px | 700 | 0 | Model/zone names |
| `--display-sm` | 32px | 700 | 0 | CTA-band heads, page titles, spec values |
| `--title-lg` | 24px | 700 | 0 | Card titles |
| `--title-md` | 20px | 400 | 0 | Card sub-titles |
| `--title-sm` | 18px | 400 | 0 | Spec callouts, intro paragraphs |
| `--label-uppercase` | 14px | 700 | 1.5px | Category tabs, "VIEW MORE" labels |
| `--body-md` | 16px | 300 | 0 | Default body (BMW Type Next Latin Light) |
| `--body-sm` | 14px | 300 | 0 | Footer body, fine print |
| `--caption` | 12px | 400 | 0.5px | Photo captions |
| `--button` | 14px | 700 | 1.5px | All button labels — uppercase, letterspaced |
| `--nav-link` | 14px | 400 | 0.5px | Top-nav menu items |

### Spacing

Base unit 4px. Tokens:
`--space-xxs` 4 · `--space-xs` 8 · `--space-sm` 12 · `--space-md` 16 · `--space-lg` 24 · `--space-xl` 40 · `--space-xxl` 64 · `--space-section` 96.

### Radius

| Token | Value | Use |
|---|---|---|
| `--radius-none` | 0px | Default for everything: buttons, cards, photo containers, spec cells, inputs |
| `--radius-sm` | 4px | Small toggle pills (rare) |
| `--radius-full` | 9999px | Circular icon buttons only (carousel arrows, chatbot launcher) |

## Component Map (DeadZone ↔ BMW M)

| DeadZone component | BMW M equivalent | Treatment |
|---|---|---|
| `Header.tsx` | `top-nav` | 64px tall, black, DeadZone wordmark + M-tricolor stripe at left, nav links in `--nav-link` |
| `Sidebar.tsx` | hamburger sheet (mobile-style, always-visible) | Black, `--label-uppercase` nav items, 4px M-stripe at top edge |
| `MetricsBar.tsx` | spec-cell row | Each metric becomes a `spec-cell` — value in `--display-sm`, label in `--label-uppercase` |
| `VenueMap.tsx` | `hero-photo-band` | Full-bleed map fills the band edge-to-edge; zones overlay with `--m-red` density gradient |
| `HeatmapDashboard.tsx` (new) | spec-table page | Spec cells for metrics; zone bars on `--surface-soft` with `--m-red` density fill |
| `AlertsPanel.tsx` | magazine-article-card column | Each alert is a card on `--canvas` with hairline border, category label in `--label-uppercase` |
| `ZoneDetail.tsx` | model-card detail | Zone name in `--display-md`, spec grid below in spec-cells |
| `ReplayControls.tsx` | button-icon row | Play/pause/restart as 48×48 `--radius-full` icon buttons |
| `AlertToast.tsx` | cookie-consent-card analogue | Right-side card, `--canvas` + hairline, `--button` actions |
| `Footer.tsx` | `footer` | Black, 4-col link list at desktop, `--body-sm` |

## Design Decisions

### D1: Inter as the BMW Type Next Latin substitute
We won't ship the licensed BMW Type Next Latin (we don't have a license). Inter Variable at 700/300 with display tracking -0.5px is the documented fallback. Acceptable — most viewers won't notice; the editorial signature (weight contrast 700 vs 300, uppercase tracking 1.5px) survives.

### D2: M tricolor stripe gets exactly three roles
1. `Header.tsx` left edge: 4px stripe under the wordmark
2. Section-divider role between major bands when emphasis is needed
3. Sidebar top edge: 4px stripe between brand mark and nav

Never used as button fill, surface fill, or chart color. Discipline here protects the brand voltage.

### D3: Mode color remapping
The current `MODE_TOKENS` (mock blue, ble green, mesh purple) gets overridden:
- `live` and `ble` → `--m-red` (the brand's "this is the real thing" signal)
- `replay` → `--warning` (#f4b400) — preserves the "recorded, not live" reading
- `mock` → `--muted` (#7e7e7e) — explicitly low-voltage; mock should not feel as urgent as live
- `mesh` → `--m-blue-dark` (heritage blue, distributed-grid feel)
- `wifi` → `--m-blue-light`
- `hybrid` → `--on-dark` (white = "everything on")

### D4: Density ramp stays viridis-derived, but redshifted
Current heatmap viridis ramp: `#440154` → `#3B528B` → `#21908C` → `#5DC863` → `#FDE725`. New ramp removes the cool blues (off-brand) and ends at `--m-red`:
`#0d0d0d` (empty) → `#3c3c3c` (low) → `#7e7e7e` (medium) → `#f4b400` (high) → `#e22718` (critical).
This makes `--m-red` zones read as a brand-aligned crisis signal.

### D5: No light-mode toggle
BMW M has no light-mode marketing surface. DeadZone will follow — no theme toggle, no light variant. The black canvas is the brand. Users on bright displays can dim their monitor.

## Phased Rollout

This is a major restyle. Recommend phasing to keep PRs reviewable:

### Phase 1: Token swap (1 PR)
- Replace `:root` CSS variables in `styles.css` with the BMW M token set
- Map old token names to new ones via aliases so component classes keep working
- Re-link `MODE_TOKENS` in `types.ts` to the new color values
- Result: every existing component renders on black canvas with white text. Layout unchanged.

### Phase 2: Typography swap (1 PR)
- Add Inter Variable from Google Fonts (replace BMW Type Next placeholder)
- Apply weight + tracking rules: display 700, body 300, button 1.5px tracking
- Uppercase display headlines: page titles, section heads
- Result: editorial signature in place

### Phase 3: Radius + button silhouette (1 PR)
- Set `--radius-*` to BMW values (mostly 0)
- Strip rounded corners from cards, inputs, buttons
- Convert primary CTA to outlined-rectangle style
- Reserve `--radius-full` for icon buttons (replay controls, etc.)
- Result: visual language locked

### Phase 4: M tricolor + signature components (1 PR)
- Add `--m-stripe-divider` component (4px tricolor band)
- Apply to Header left edge, Sidebar top edge
- Convert mode badge to M-stripe-flanked treatment
- Result: brand-identity moments

### Phase 5: Layout retune (1 PR)
- Bump spacing tokens to BMW values (96px section padding)
- Convert MetricsBar to spec-cell row
- Convert VenueMap container to full-bleed band
- Result: editorial rhythm

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Heavy weight + black canvas readability on low-end displays | Medium | Medium | Use `--body` (#bbbbbb) not pure white for body — already in palette |
| Stakeholders read "black background" as "outage" / "dark mode novelty" | Medium | Low | Front-load the BMW reference; show wireframes before code |
| All-caps headlines fight accessibility / screen readers | Low | Medium | Use CSS `text-transform: uppercase` (preserves underlying text case); pair with `aria-label` overrides where needed |
| Map / heatmap chart palettes need bespoke tuning per page | High | Medium | Phase 5 includes per-page tuning; don't try to ship in one PR |
| Inter doesn't match BMW Type at large display sizes | Medium | Low | -0.5px tracking adjustment at display-xl; accept the gap as a known substitute trade-off |

## Open Questions

1. Do we have any photography assets, or is the venue-map visualization the only "hero" content we render? (BMW M depends heavily on cinematic photography; we may need to lean even harder on data-viz as the photo substitute.)
2. Should the M-stripe stay literal BMW (blue → blue → red) or adapt to DeadZone-native colors (e.g., `--m-blue-light` → `--m-blue-dark` → `--mode-mesh`)?
3. Is "DeadZone" wordmark typography in scope, or just CSS-level? Custom wordmark would need a design pass beyond CSS.
4. Configurator / order surfaces are out of scope per BMW source spec — does DeadZone have any equivalent (e.g., venue setup wizard) that needs special treatment?

## Known Gaps (from source spec)

Per the source document's "Known Gaps" section:
- BMW Type Next Latin not licensed for us — Inter substitute documented
- Exact M tricolor stops are from public BMW brand guidelines; treat as canonical
- Animation/transition timings not documented in source — we'll design these ourselves
- Form validation states not in source — we'll extend the system as needed
- Configurator surface not analyzed in source — we don't have an equivalent surface anyway
