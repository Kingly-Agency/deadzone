# Step 6: Component Inventory -- DeadZone MVP

**Pipeline**: DeadZone MVP Crowd Intelligence UX
**Date**: 2026-05-14
**Stack**: React + Leaflet + Heatmap.js (single-screen dashboard)
**Grounded in**: problem_spec.yaml, jobs.graph.json, ia_schema.json, user_and_agent_research.md, task_graph.json

---

## Design Tokens

### Color Palette

**Density ramp (viridis-based)** -- used for heatmap and sparkline fills:

| Token | Hex | Usage |
|---|---|---|
| `--density-0` | `#440154` | Empty / zero occupancy |
| `--density-1` | `#3b528b` | Low occupancy |
| `--density-2` | `#21918c` | Moderate occupancy |
| `--density-3` | `#5ec962` | High occupancy |
| `--density-4` | `#fde725` | At/above capacity |

Viridis selected per E3 (Maria's colorblind assistant) and LC-5 (WCAG AA). No red-green-only encoding at any step.

**Mode color tokens**:

| Token | Hex | Mode | Evidence |
|---|---|---|---|
| `--mode-mock` | `#4A90D9` | Mock | Blue -- neutral, clearly synthetic (LC-2, D4) |
| `--mode-replay` | `#D4A843` | Replay | Amber -- historical/archived connotation (LC-2) |
| `--mode-live` | `#2D9F4E` | Live | Green -- active/real signal (LC-2, Raj: "engineering maturity") |
| `--mode-mesh` | `#7B4FBF` | Mesh | Purple -- alternative-path signal (LC-2) |

### Severity Tokens

| Token | Hex | Pattern overlay | Usage |
|---|---|---|---|
| `--severity-info` | `#4A90D9` | None | Informational alerts |
| `--severity-warn` | `#D4A843` | Diagonal hatch (45deg, 4px) | Approaching capacity (AP-4) |
| `--severity-critical` | `#C94444` | Cross-hatch (45deg+135deg, 4px) | At/exceeding capacity (AP-4) |

Critical uses `#C94444` (distinguishable from green even in deuteranopia) plus mandatory pattern overlay so color is never the sole channel.

### Spacing Scale

| Token | Value | Usage |
|---|---|---|
| `--space-xs` | 4px | Inline gaps, icon padding |
| `--space-sm` | 8px | Compact element spacing |
| `--space-md` | 16px | Standard panel padding, card gaps |
| `--space-lg` | 24px | Section separation |
| `--space-xl` | 32px | Major section breaks |

### Type Scale

| Token | Size | Weight | Usage |
|---|---|---|---|
| `--text-xs` | 11px / 0.6875rem | 400 | Timestamps, provenance labels |
| `--text-sm` | 13px / 0.8125rem | 400 | Secondary labels, badge text |
| `--text-md` | 15px / 0.9375rem | 400 | Body text, list items |
| `--text-lg` | 20px / 1.25rem | 600 | Card titles, section headers |
| `--text-xl` | 28px / 1.75rem | 700 | Headline metrics (C5: "numbers beat gradients") |
| `--text-xxl` | 36px / 2.25rem | 700 | Hero metric (total occupancy) |

Font stack: `'Inter', system-ui, -apple-system, sans-serif`. Monospace for raw events: `'JetBrains Mono', 'Fira Code', monospace`.

### WCAG AA Targets

| Criterion | Target | Verification method |
|---|---|---|
| Text contrast (normal) | >= 4.5:1 against background | All text tokens tested on `--bg-surface` (#1a1a2e) and `--bg-panel` (#252540) |
| Text contrast (large) | >= 3:1 | Headline metrics, section headers |
| Non-text contrast | >= 3:1 | Mode badge borders, chart lines, heatmap legend swatches against map tile |
| Focus indicators | 2px solid, >= 3:1 contrast | All interactive elements |
| Motion | `prefers-reduced-motion` respected | Heatmap animation, crossfade transitions, sparkline animation |

Dark background palette: `--bg-canvas: #0f0f23`, `--bg-surface: #1a1a2e`, `--bg-panel: #252540`, `--bg-elevated: #303050`. Light text: `--text-primary: #e8e8f0`, `--text-secondary: #a0a0b8`.

---

## Component Inventory

### Layout

#### AppShell
- **Purpose**: Root layout container. Manages global keyboard listeners (R for reset, M for mode switch, T for topology toggle), CSS custom property injection, and the three-column responsive grid.
- **Key props/data**: `mode: Mode`, `connectionStatus: ConnectionState`, `children`
- **States**: `initializing` (first paint, before WebSocket), `connected`, `degraded` (stale data), `disconnected`
- **Accessibility**: Provides `<main>` landmark, sets `lang` attribute, hosts `AriaLiveAlerts` region. Keyboard shortcuts listed in `KeyboardHintRow`.
- **Evidence**: task-1-land requires skeleton within 200ms; AppShell owns the transition from skeleton to populated.

#### Header
- **Purpose**: Persistent top bar containing brand mark, ModeChip + ProvenanceBadge, topology toggle, reset button, settings gear. Visible in every state.
- **Key props/data**: `mode: Mode`, `resetCount: number`, `topologyOpen: boolean`
- **States**: `default`, `alert-active` (pulse indicator on alerts icon)
- **Accessibility**: `role="banner"`, contains skip-nav link to MainCanvas.
- **Evidence**: LC-2 (persistent mode badge), AP-1 (reset button accessible here).

#### MetricsBar
- **Purpose**: Above-the-fold summary strip showing headline numbers. Directly addresses C5 ("headline metrics beat gradients") and job-3-act (Maria: "how many people at Gate 3").
- **Key props/data**: `totalOccupancy: number`, `peakZone: { name, count, capacity }`, `trendDirection: 'rising' | 'falling' | 'stable'`, `alertCount: number`
- **States**: `skeleton` (loading), `populated`, `stale` (data older than 30s, shows StaleDataIndicator)
- **Accessibility**: Uses `aria-label` per metric with human-readable trend direction ("rising" not just an arrow glyph). Updates announced via `AriaLiveAlerts` when values cross thresholds.
- **Evidence**: C5 (5/5 personas), LC-1.

#### AlertsPanel
- **Purpose**: Collapsible right-side panel listing active and acknowledged alerts. Shows severity badges, zone links, timestamps. Handles the critical MVP requirement that at least one alert fires within 90 seconds (LC-4, C3).
- **Key props/data**: `alerts: Alert[]`, `onAcknowledge: (id) => void`, `onHighlightZone: (zoneId) => void`
- **States**: `skeleton`, `empty` (shows AlertsEmptyState: "No active alerts -- system nominal"), `populated`, `overflow` (scroll with count badge)
- **Accessibility**: `role="log"`, `aria-live="polite"`. New critical alerts announced via `aria-live="assertive"` in AriaLiveAlerts.
- **Evidence**: C3 (alert within 90s), D3 (simple severity badges for MVP), task-5-acknowledge-alert.

#### MainCanvas
- **Purpose**: Central map viewport hosting the Leaflet map and all visualization overlays. Takes remaining space after Header and MetricsBar.
- **Key props/data**: `floorplanUrl: string`, `zones: Zone[]`, `mode: Mode`, `overlayMode: 'heatmap' | 'topology'`
- **States**: `loading` (skeleton with venue outline), `populated`, `error` (ErrorBoundary catches Leaflet failures)
- **Accessibility**: `role="application"` with `aria-roledescription="venue map"`. Arrow keys pan, +/- zoom. `Escape` closes any open overlay.
- **Evidence**: job-1-glance (heatmap must animate within 2s).

#### Drawer
- **Purpose**: Slide-in side panel used for ZoneDetailCard, SensorDetailCard, and replay ScenarioPicker. Pushes or overlays MainCanvas depending on viewport width.
- **Key props/data**: `isOpen: boolean`, `position: 'right' | 'bottom'`, `title: string`, `children`
- **States**: `closed`, `opening` (300ms slide), `open`, `closing`
- **Accessibility**: Contains FocusTrap when open. `Escape` closes. `aria-modal="true"` when overlay mode.
- **Evidence**: task-3-inspect-zone (zone detail slides in), task-6-inspect-topology (sensor detail).

#### Popover
- **Purpose**: Small floating panel for settings, mode dropdown, and keyboard hints. Anchored to trigger element.
- **Key props/data**: `anchorRef: RefObject`, `isOpen: boolean`, `children`
- **States**: `closed`, `open`
- **Accessibility**: FocusTrap when open. `Escape` closes. `aria-haspopup` on trigger.
- **Evidence**: ia_schema.json navigation.secondary (settings as popover).

---

### Map / Viz

#### HeatmapLayer
- **Purpose**: Leaflet overlay rendering crowd density using heatmap.js. Viridis palette mapped to density values. **Never renders without Legend** (composition rule).
- **Key props/data**: `densityData: { lat, lng, value }[]`, `maxValue: number`, `radius: number`, `mode: Mode`
- **States**: `loading` (SkeletonPanel with venue outline), `empty` ("Awaiting sensor data" with map tiles visible), `populated`, `stale` (opacity reduced + StaleDataIndicator)
- **Accessibility**: `aria-hidden="true"` on the canvas element (visual-only); equivalent data communicated via MetricsBar and ZoneDetailCard text. Respects `prefers-reduced-motion` (disables animation, shows static frame).
- **Evidence**: C1 (legend required), LC-1, LC-5, job-1-glance.

#### ZoneOverlay
- **Purpose**: Leaflet polygon overlay drawing zone boundaries on the map. Clickable to open ZoneDetailCard in Drawer.
- **Key props/data**: `zones: Zone[]`, `selectedZoneId: string | null`, `onSelect: (zoneId) => void`
- **States**: `default` (translucent fill), `selected` (thicker border, highlighted fill), `alert-active` (pulsing border for zone with active critical alert)
- **Accessibility**: Each zone is a `role="button"` in the SVG with `aria-label="{zone name}, {count} occupants, {percent}% capacity"`. Keyboard navigable with Tab.
- **Evidence**: task-3-inspect-zone, job-3-act.

#### MovementVectors
- **Purpose**: Animated directional arrows overlaid on the heatmap showing crowd flow direction. Provides the "wow moment" from job-1-glance.
- **Key props/data**: `vectors: { from, to, magnitude }[]`, `animationSpeed: number`
- **States**: `hidden` (no data or reduced motion), `animated`, `static` (reduced motion fallback: arrows without animation)
- **Accessibility**: `aria-hidden="true"` (decorative). Flow direction communicated textually in ZoneDetailCard ("flow: inbound" / "outbound").
- **Evidence**: job-1-glance wow_moment.

#### SensorNode
- **Purpose**: Map marker representing a single sensor. Color indicates health (green/amber/red following severity tokens). Clickable to open SensorDetailCard.
- **Key props/data**: `sensor: Sensor`, `isSelected: boolean`, `onClick: () => void`
- **States**: `healthy` (green), `degraded` (amber, last seen >30s ago), `offline` (red, last seen >60s), `mock` (dashed border + "mock" micro-label)
- **Accessibility**: `role="button"`, `aria-label="{sensor type} sensor {id}, status: {health}, last seen: {time}"`.
- **Evidence**: task-6-inspect-topology, Tomasz: "sensor health is critical".

#### CoverageGapHatch
- **Purpose**: Diagonal hatch pattern overlay drawn on map areas not covered by any sensor. Uses SVG pattern fill, not color-only, per AP-4.
- **Key props/data**: `gaps: Polygon[]`, `patternId: string`
- **States**: `none` (no gaps), `visible`
- **Accessibility**: `aria-label="Coverage gap: {area description}"` on parent group. Hatching distinguishable from zone fills regardless of color vision.
- **Evidence**: E3 (AP-4), Maria: "where are my blind spots", job-5-validate-coverage.

#### Legend
- **Purpose**: Persistent heatmap color legend with unit label. Always co-rendered with HeatmapLayer (composition rule). Shows viridis gradient bar with min/max values and unit.
- **Key props/data**: `unit: string` ("people/m^2" in Replay/Live, "simulated density" in Mock), `min: number`, `max: number`, `mode: Mode`
- **States**: `populated` (single state -- always visible when HeatmapLayer is rendered)
- **Accessibility**: Each color stop has `aria-label` with value. Unit label is visible text, not tooltip-only.
- **Evidence**: C1 (all 5 personas), LC-1, Tomasz: "where's the legend?".

#### Scrubber
- **Purpose**: Timeline scrubber for Replay mode. Shows elapsed time, total duration, playback speed control, and event density sparkline along the timeline.
- **Key props/data**: `currentTime: number`, `duration: number`, `speed: number`, `eventDensity: number[]`, `onSeek: (time) => void`, `onSpeedChange: (speed) => void`
- **States**: `hidden` (non-replay modes), `loading` (scenario loading), `playing`, `paused`, `scrubbing`
- **Accessibility**: `role="slider"`, `aria-valuemin`, `aria-valuemax`, `aria-valuenow`, `aria-valuetext="3 minutes 42 seconds of 12 minutes"`. Speed buttons are labeled.
- **Evidence**: task-4-trigger-replay-scenario, job-4-rehearse.

---

### Mode + Provenance

#### ModeChip
- **Purpose**: Persistent badge in Header showing the active data mode. Color-coded per mode tokens. **Never renders without ProvenanceBadge** (composition rule). Clicking opens ModeDropdown.
- **Key props/data**: `mode: Mode`, `onClick: () => void`
- **States**: `default`, `warning` (degraded connection in Live/Mesh -- adds warning ring per task-8-handle-degradation), `switching` (300ms crossfade during mode transition)
- **Accessibility**: `role="button"`, `aria-expanded` (controls ModeDropdown), `aria-label="Current mode: {mode label}. Click to switch."`.
- **Evidence**: LC-2 (persistent, unmissable), C2 (all 5 personas), D4 resolution.

#### ProvenanceBadge
- **Purpose**: Plain-language label clarifying data source for the active mode. Renders adjacent to ModeChip. Examples: "simulated data", "recorded: convention scenario", "live sensors (8 active)", "mesh network (3 gateways)".
- **Key props/data**: `mode: Mode`, `sourceDescription: string`, `sensorCount?: number`
- **States**: `default`, `stale` (appends "-- last update 45s ago" in Live/Mesh)
- **Accessibility**: `role="status"`, `aria-live="polite"` (announces mode changes). Visible text, not tooltip.
- **Evidence**: C2, D4, Raj: "engineering maturity signal", job-2-trust.

#### ModeDropdown
- **Purpose**: Dropdown from ModeChip listing four modes with availability status. Auto-selects best available on load (D1 resolution: Dana + Maria satisfied). Technical users can override.
- **Key props/data**: `modes: { id, label, available, reason? }[]`, `activeMode: string`, `onSelect: (modeId) => void`
- **States**: `closed`, `open`
- **Accessibility**: `role="listbox"`, `aria-activedescendant`. Unavailable modes are `aria-disabled` with reason tooltip. Arrow keys navigate.
- **Evidence**: D1 (auto-select + expose), task-2-switch-mode.

#### ModeAvailabilityIndicator
- **Purpose**: Green/gray dot beside each mode option in ModeDropdown indicating whether the data source is reachable. Gray with tooltip when unavailable (e.g., "Gateway not reachable").
- **Key props/data**: `available: boolean`, `reason?: string`
- **States**: `available` (green dot), `unavailable` (gray dot + reason)
- **Accessibility**: `aria-label="{available|unavailable}: {reason}"`. Not color-only: dot uses filled vs outline shape.
- **Evidence**: task-2-switch-mode failure_modes.

---

### Data Display

#### HeadlineMetric
- **Purpose**: Single large-format metric in MetricsBar. Shows value, label, and optional trend arrow. Named after user intent ("headline" = above-the-fold summary for Dana's 30-second scan) rather than visual treatment.
- **Key props/data**: `value: string | number`, `label: string`, `trend?: 'rising' | 'falling' | 'stable'`, `unit?: string`
- **States**: `skeleton` (animated placeholder), `populated`, `stale` (dimmed + clock icon)
- **Accessibility**: `aria-label="{label}: {value} {unit}, trend {direction}"`. Trend conveyed by text + arrow icon, not arrow alone.
- **Evidence**: C5, LC-1, job-3-act.

#### ZoneDetailCard
- **Purpose**: Detailed zone panel in Drawer. Shows zone name, current count, capacity percentage, 5-min trend sparkline, active alerts for this zone, and flow direction.
- **Key props/data**: `zone: Zone`, `alerts: Alert[]`, `sparklineData: number[]`, `flowDirection: 'inbound' | 'outbound' | 'stable'`
- **States**: `skeleton`, `empty` ("Awaiting sensor reports" + last-seen timestamp), `populated`, `error`
- **Accessibility**: Heading level reflects Drawer context. Sparkline has `aria-label` with trend summary. Zone link to map highlight via `aria-controls`.
- **Evidence**: task-3-inspect-zone, job-3-act, Maria: "how many people at Gate 3".

#### TrendSparkline
- **Purpose**: Compact inline sparkline showing 5-minute occupancy trend for a zone. Renders as SVG line chart within ZoneDetailCard.
- **Key props/data**: `data: number[]`, `width: number`, `height: number`, `thresholdLine?: number`
- **States**: `loading` (flat gray line placeholder), `sparse` (dots instead of line, label "< 5min of data"), `populated`
- **Accessibility**: `role="img"`, `aria-label="5-minute trend: {direction}, from {start} to {end}"`. Not interactive.
- **Evidence**: task-3-inspect-zone, job-3-act wow_moment.

#### SensorDetailCard
- **Purpose**: Sensor drill-down in Drawer. Shows sensor ID, type (BLE/WiFi/Mesh), health, battery, last-seen, RSSI sample, and raw event tail (last 10 events). Satisfies Raj's "show me the API" need.
- **Key props/data**: `sensor: Sensor`, `rawEvents: Event[]`
- **States**: `skeleton`, `empty` ("No events recorded"), `populated`, `mock` (shows "simulated sensor" badge)
- **Accessibility**: Raw event list is a `<table>` with proper headers. Timestamps use `<time>` element.
- **Evidence**: task-6-inspect-topology, job-6-investigate, Raj: "show me the API".

#### RawEventTail
- **Purpose**: Scrolling list of the last 10 raw telemetry events for a sensor. Monospace font, timestamp + RSSI + device type (aggregate). Never shows device identifiers (privacy constraint from problem_spec).
- **Key props/data**: `events: Event[]`, `maxItems: number`
- **States**: `empty` ("Listening..."), `streaming` (new events prepend with brief highlight), `paused`
- **Accessibility**: `role="log"`, `aria-live="polite"` with throttled announcements (max 1 per 5s to avoid screen reader flooding).
- **Evidence**: job-6-investigate, ia_schema.json Event entity note ("aggregate-only").

---

### Alerts

#### AlertBadge
- **Purpose**: Compact severity indicator used inline in AlertListItem and MetricsBar. Shows icon + color + optional count.
- **Key props/data**: `severity: 'info' | 'warn' | 'critical'`, `count?: number`
- **States**: `default`, `pulsing` (new unacknowledged critical alert)
- **Accessibility**: `aria-label="{severity}: {count} alerts"`. Uses icon shape (circle/triangle/diamond) in addition to color per AP-4.
- **Evidence**: D3, task-5-acknowledge-alert.

#### AlertListItem
- **Purpose**: Single alert row in AlertsPanel. Shows severity badge, message, zone link, timestamp, acknowledge button.
- **Key props/data**: `alert: Alert`, `onAcknowledge: () => void`, `onHighlightZone: () => void`
- **States**: `active`, `acknowledged` (grayed, moved to bottom), `expired`
- **Accessibility**: Acknowledge button has `aria-label="Acknowledge alert: {message}"`. Zone link announces zone name.
- **Evidence**: task-5-acknowledge-alert happy_path.

#### AlertToast
- **Purpose**: Transient notification surfacing critical alerts. Auto-dismisses after 6 seconds. Appears at top-right, overlays map.
- **Key props/data**: `alert: Alert`, `duration: number`, `onDismiss: () => void`
- **States**: `entering` (slide-in), `visible`, `exiting` (fade-out)
- **Accessibility**: `role="alert"`, `aria-live="assertive"`. Focus not stolen (toast is supplementary to AlertsPanel). Dismissable via `Escape` or close button.
- **Evidence**: task-5-acknowledge-alert ("Toast briefly surfaces critical alerts, auto-dismiss 6s").

#### AlertsEmptyState
- **Purpose**: Meaningful zero-state for AlertsPanel. Shows "No active alerts -- system nominal" with a subtle check icon. Prevents blank panel perception (C4).
- **Key props/data**: `acknowledgedCount?: number`
- **States**: `no-alerts` ("System nominal"), `all-acknowledged` ("All {n} alerts acknowledged")
- **Accessibility**: Visible text, not just an icon.
- **Evidence**: C4 (all 5 personas), task-5-acknowledge-alert failure_modes.

---

### Controls

#### ScenarioPicker
- **Purpose**: Grid/list of available replay scenarios shown when Mode = Replay. Each scenario has name, duration, event count, thumbnail.
- **Key props/data**: `scenarios: Scenario[]`, `selectedId: string | null`, `onSelect: (id) => void`
- **States**: `loading` (skeleton cards), `populated`, `empty` ("No scenarios available -- check data directory"), `error`
- **Accessibility**: `role="radiogroup"`. Each scenario is `role="radio"`. Arrow keys navigate. Enter selects.
- **Evidence**: task-4-trigger-replay-scenario, ia_schema.json Scenario entity.

#### PlaybackControls
- **Purpose**: Play/pause, speed selector (0.25x - 4x), and elapsed/total time display for Replay mode. Appears alongside Scrubber.
- **Key props/data**: `isPlaying: boolean`, `speed: number`, `onTogglePlay: () => void`, `onSpeedChange: (speed) => void`
- **States**: `playing`, `paused`, `loading` (scenario loading)
- **Accessibility**: Play/pause is `aria-label="Pause playback"` / `"Resume playback"`. Speed selector is `role="spinbutton"`.
- **Evidence**: task-4-trigger-replay-scenario.

#### ResetButton
- **Purpose**: Resets demo timeline to t=0 without page reload. Clears alerts, restarts mock event sequence, re-arms 90s alert. Discreet placement in Header to avoid accidental activation.
- **Key props/data**: `mode: Mode`, `onReset: () => void`
- **States**: `default`, `confirming` (in Live mode: shows confirm modal before reset), `resetting` (brief 400ms fade)
- **Accessibility**: `aria-label="Reset demo timeline"`. Keyboard shortcut `R` documented in KeyboardHintRow. In Live mode, confirm dialog is focus-trapped.
- **Evidence**: E1, AP-1, task-7-reset-demo, job-4-rehearse.

#### KeyboardHintRow
- **Purpose**: Compact row showing available keyboard shortcuts. Toggled via `?` key or settings. Keeps demo operators (Kenji) confident in shortcuts without cluttering Spectator view.
- **Key props/data**: `shortcuts: { key, action }[]`, `isVisible: boolean`
- **States**: `hidden`, `visible`
- **Accessibility**: `role="complementary"`, `aria-label="Keyboard shortcuts"`. Each shortcut pair uses `<kbd>` element.
- **Evidence**: task-7-reset-demo (R key), AP-1.

---

### Feedback

#### SkeletonPanel
- **Purpose**: Animated placeholder matching the shape of the panel it replaces. Used during initial load, mode switch transitions, and data fetch. Prevents white-flash perception (C4).
- **Key props/data**: `variant: 'metric' | 'card' | 'map' | 'list'`, `lines?: number`
- **States**: `animating` (pulse animation), `static` (reduced motion: gray blocks without animation)
- **Accessibility**: `aria-hidden="true"`, `aria-busy="true"` on parent container. Screen readers see the parent's loading label, not the skeleton shapes.
- **Evidence**: C4 (all 5 personas), LC-3, Kenji: "400ms flash of empty state".

#### EmptyState
- **Purpose**: Meaningful zero-state message with icon and optional action. Used when a panel has no data but is not in error. Never shows blank white space.
- **Key props/data**: `icon: ReactNode`, `message: string`, `action?: { label, onClick }`
- **States**: Single visible state (this IS the state).
- **Accessibility**: Message is visible text (not just icon). Action button, if present, has descriptive label.
- **Evidence**: C4, LC-3, task-6-inspect-topology failure_modes.

#### ErrorBoundary
- **Purpose**: React error boundary catching render failures in any panel. Shows a recoverable error message with retry action instead of crashing the entire dashboard.
- **Key props/data**: `fallback: ReactNode`, `onRetry?: () => void`, `reportError?: (error) => void`
- **States**: `normal` (renders children), `error` (renders fallback with error summary and retry)
- **Accessibility**: Error message is `role="alert"`. Retry button is focusable.
- **Evidence**: LC-3, problem_spec constraint: "Graceful degradation".

#### StaleDataIndicator
- **Purpose**: Visual indicator that displayed data is older than the freshness threshold (30s). Shows elapsed time since last update. Used in MetricsBar, HeatmapLayer, and ZoneDetailCard.
- **Key props/data**: `lastUpdated: Date`, `thresholdMs: number`
- **States**: `fresh` (hidden), `stale` (visible with elapsed time), `disconnected` (shows ConnectionStatus instead)
- **Accessibility**: `role="status"`, `aria-live="polite"`. Text reads "Data from {N}s ago".
- **Evidence**: task-8-handle-degradation, D5 resolution, Tomasz: "never hide a problem".

#### ConnectionStatus
- **Purpose**: Footer element showing WebSocket connection state. Provides transparency about data pipeline health.
- **Key props/data**: `state: 'connected' | 'reconnecting' | 'disconnected'`, `lastFrameTimestamp: Date`
- **States**: `connected` (green dot + "Connected"), `reconnecting` (amber dot + "Reconnecting..." with attempt count), `disconnected` (red dot + "Disconnected" with retry button)
- **Accessibility**: `role="status"`, `aria-live="polite"`. State conveyed by label text + icon shape, not color alone.
- **Evidence**: task-1-land failure_modes, task-8-handle-degradation.

---

### Accessibility

#### FocusTrap
- **Purpose**: Traps keyboard focus within Drawer, Popover, and confirm dialogs. Returns focus to trigger element on close.
- **Key props/data**: `isActive: boolean`, `returnFocusRef: RefObject`
- **States**: `inactive`, `active`
- **Accessibility**: Implements WAI-ARIA dialog pattern. Tab cycles within trapped region. Escape deactivates.
- **Evidence**: Drawer and Popover patterns require modal focus management.

#### AriaLiveAlerts
- **Purpose**: Hidden live region announcing state changes to screen readers. Throttled to prevent flooding. Handles: mode switches, new alerts, threshold crossings, connection state changes.
- **Key props/data**: `announcements: { message, priority: 'polite' | 'assertive' }[]`
- **States**: Always mounted (invisible). Receives announcements via context.
- **Accessibility**: Dual regions: `aria-live="polite"` (mode changes, data updates) and `aria-live="assertive"` (critical alerts, disconnection).
- **Evidence**: C2 (mode changes announced), C3 (alert fires announced), WCAG AA.

#### ColorBlindToggle
- **Purpose**: Settings control switching heatmap palette to high-contrast alternatives. Options: viridis (default), plasma, cividis, grayscale. Persisted to localStorage.
- **Key props/data**: `palette: string`, `onChangePalette: (palette) => void`
- **States**: `default` (viridis), user-selected alternative
- **Accessibility**: `role="radiogroup"` with preview swatch per option. Selection persists across sessions.
- **Evidence**: E3, AP-4, LC-5.

---

## Screen -> Components Mapping

Screens derived from ia_schema.json navigation and task_graph.json task flows. All screens are overlays/panels on the single-page dashboard -- no page transitions.

| Screen | Components |
|---|---|
| **Dashboard** (default) | AppShell, Header, ModeChip, ProvenanceBadge, MetricsBar (HeadlineMetric x3), MainCanvas, HeatmapLayer, Legend, ZoneOverlay, MovementVectors, AlertsPanel (AlertBadge, AlertListItem, AlertsEmptyState), AlertToast, ConnectionStatus, SkeletonPanel, EmptyState, ErrorBoundary, AriaLiveAlerts |
| **Zone Detail** (Drawer) | Drawer, FocusTrap, ZoneDetailCard, TrendSparkline, AlertBadge, SkeletonPanel, EmptyState, ErrorBoundary |
| **Topology** (overlay toggle) | MainCanvas (overlay swap), SensorNode, CoverageGapHatch, Legend (unit changes to "signal strength"), SkeletonPanel, EmptyState, ErrorBoundary |
| **Sensor Detail** (Drawer) | Drawer, FocusTrap, SensorDetailCard, RawEventTail, SkeletonPanel, EmptyState, ErrorBoundary |
| **Replay Picker** (Drawer) | Drawer, FocusTrap, ScenarioPicker, SkeletonPanel, EmptyState, ErrorBoundary |
| **Replay Playback** (controls bar) | Scrubber, PlaybackControls |
| **Alerts Panel** (expanded) | AlertsPanel, AlertListItem, AlertBadge, AlertsEmptyState, SkeletonPanel, ErrorBoundary |
| **Mode Switcher** (Popover) | Popover, FocusTrap, ModeDropdown, ModeAvailabilityIndicator |
| **Settings** (Popover) | Popover, FocusTrap, ColorBlindToggle, KeyboardHintRow |
| **Demo Reset** (inline) | ResetButton, AlertToast (confirmation) |

---

## Naming Principles

Components are named after **user intent**, not visual treatment or implementation pattern:

- **HeadlineMetric** (not BigNumber or StatCard) -- named for the JTBD: the metric that headlines the dashboard for a 30-second booth scan (C5, job-1-glance).
- **ProvenanceBadge** (not InfoChip or StatusTag) -- named for the domain concept it communicates: data provenance, the trust signal Raj and Tomasz require (C2, job-2-trust). "Provenance" is the term of art.
- **CoverageGapHatch** (not EmptyZonePattern) -- named for what it reveals to the operator: a gap in sensor coverage that needs remediation (job-5-validate-coverage). "Hatch" describes the visual technique because it carries accessibility meaning (pattern, not color-only).
- **StaleDataIndicator** (not WarningBanner or TimerBadge) -- named for the exact condition it signals. An operator seeing "stale" knows the system is not crashed, just delayed (D5, task-8-handle-degradation).
- **AlertsEmptyState** (not NoAlertsPlaceholder) -- follows the composition convention: `{Domain}EmptyState` is the zero-state variant of its parent panel. Predictable naming reduces cognitive load during development.

General rule: if a component name does not tell a new developer *what user problem it solves*, rename it.

---

## Composition Rules

### 1. All panels MUST compose: SkeletonPanel + EmptyState + ErrorBoundary + populated content

Every panel that fetches or depends on data follows this four-state rendering pattern:

```
<ErrorBoundary fallback={<ErrorState onRetry={refetch} />}>
  {isLoading ? <SkeletonPanel variant="..." /> :
   isEmpty   ? <EmptyState message="..." /> :
               <PopulatedContent data={data} />}
</ErrorBoundary>
```

**Why**: C4 (all 5 personas perceive blank panels as broken), LC-3. This is a P0 layout constraint -- no exceptions.

Applies to: MetricsBar, AlertsPanel, ZoneDetailCard, SensorDetailCard, ScenarioPicker, RawEventTail, HeatmapLayer (within MainCanvas).

### 2. HeatmapLayer never renders without Legend

```
<MainCanvas>
  <HeatmapLayer data={density} />
  <Legend unit={mode === 'mock' ? 'simulated density' : 'people/m²'} />
</MainCanvas>
```

**Why**: C1 (all 5 personas asked "what do the colors mean?"). Legend is not optional -- if HeatmapLayer mounts, Legend mounts. If density data is empty, HeatmapLayer shows its EmptyState and Legend is hidden (no gradient to label).

### 3. ModeChip never renders without ProvenanceBadge

```
<Header>
  <ModeChip mode={activeMode} />
  <ProvenanceBadge mode={activeMode} source={sourceDescription} />
</Header>
```

**Why**: C2 (honest mode labeling must be unmissable), D4 resolution (always show provenance via badge). The color-coded chip alone is insufficient -- the plain-language provenance label is what satisfies Raj's trust requirement and prevents Dana's confusion.

### 4. AlertToast only surfaces for severity = critical

Info and warn alerts appear in AlertsPanel only. Critical alerts additionally trigger an AlertToast. This prevents alert fatigue (Tomasz, D3) while ensuring life-safety-level events are unmissable.

### 5. Topology overlay swaps, never layers on, the heatmap

When topology is toggled on, HeatmapLayer opacity transitions to 0 and SensorNode + CoverageGapHatch render. They never composite simultaneously -- the cognitive load of overlapping visual layers was identified as a risk in D2 (Dana: "I don't know what I'm looking at").

### 6. Mode switch uses crossfade, never white flash

All mode transitions go through: current view (300ms fade out) -> SkeletonPanel (if data not ready) -> new view (300ms fade in). The SkeletonPanel intermediary prevents the white-flash perception that Kenji flagged in the synthetic research.
