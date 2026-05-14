# Wireframes

## Global Nav Map

Primary tabs: Operations Dashboard, Replay Lab, Sensor Mesh.

Secondary controls stay contextual: scenario transport, layer toggles, diagnostics drawer, and selected alert/node details.

## Screen 1: Operations Dashboard

Purpose: Give a judge or operator immediate spatial awareness of crowd density, movement, alerts, and stream provenance.

Primary actions:
- Change mode between mock and replay.
- Select an alert to focus the affected zone.
- Toggle layers for heatmap, flow, sensors, and topology.

Layout:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ StreamStatusStrip: MODE replay | connected | seed | clock | freshness        │
├──────────────────────────────────────────────────────────────────────────────┤
│ MetricStrip: est devices | hot zones | active alerts | offline sensors       │
├───────────────────────────────────────────────────────────────┬──────────────┤
│                                                               │ AlertRail    │
│ VenueMapCanvas                                                │              │
│ - DensityHeatLayer                                            │ Critical     │
│ - FlowVectorLayer                                             │ Warning      │
│ - SensorNodeOverlay                                           │ Resolved     │
│                                                               │              │
│ [LayerControl] [selected zone drawer floats over lower left]  │ Details      │
├───────────────────────────────────────────────────────────────┴──────────────┤
│ ScenarioTransport compact: scenario | play/pause | speed | timeline          │
└──────────────────────────────────────────────────────────────────────────────┘
```

State variants:
- Loading: skeleton venue map, disabled transport, connecting badge.
- Streaming: live blobs, vectors, alerts, and freshness clock.
- Stale: preserve last map, dim animated layers, show stale badge and reconnect attempt.
- Empty: show venue zones and "no pressure detected" summary.
- Error: inline backend error with retry and diagnostics drawer entry.

## Screen 2: Replay Lab

Purpose: Make the deterministic demo controllable and explainable.

Primary actions:
- Choose scenario.
- Play, pause, restart, and scrub.
- Change replay speed.

Layout:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ StreamStatusStrip                                                           │
├──────────────────────┬───────────────────────────────────────────────────────┤
│ Scenario list        │ VenueMapCanvas + timeline ghost trails                │
│ - convention crowd   │                                                       │
│ - concert exit rush  │                                                       │
│ - hallway stall      │                                                       │
│ - stadium ingress    │                                                       │
├──────────────────────┴───────────────────────────────────────────────────────┤
│ ScenarioTransport full width: restart | back | play | speed | scrubber       │
└──────────────────────────────────────────────────────────────────────────────┘
```

State variants:
- Idle: scenario cards with duration and story.
- Loading scenario: preserve dashboard shell with scenario spinner.
- Ready: first frame visible, play highlighted.
- Playing: clock and timeline active.
- Ended: final frame held with restart action.
- Error: scenario-specific error, fallback to mock mode.

## Screen 3: Sensor Mesh

Purpose: Show how local sensors and future Meshtastic nodes compose into distributed venue intelligence.

Primary actions:
- Inspect node health.
- Toggle mesh links.
- Open diagnostics for adapter state.

Layout:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ StreamStatusStrip                                                           │
├───────────────────────────────────────────────┬──────────────────────────────┤
│ TopologyPanel                                 │ Node details                 │
│ - gateway node                                │ status, latency, battery     │
│ - sensor nodes                                │ last packet, source mode     │
│ - link quality                                │ adapter availability         │
├───────────────────────────────────────────────┴──────────────────────────────┤
│ DiagnosticsDrawer collapsed: recent packets, dropped frames, adapter errors  │
└──────────────────────────────────────────────────────────────────────────────┘
```

State variants:
- Available: nodes and links visible.
- Adapter disabled: mock topology visible with disabled reason.
- Empty: no nodes configured.
- Partial outage: offline nodes remain visible with clear status.
- Error: topology failed but main dashboard remains usable.

## Mobile Behavior

- Operations Dashboard becomes map-first with bottom sheets for alerts and transport.
- AlertRail collapses into a bottom tab with count badges.
- LayerControl becomes an icon toolbar with labels in tooltips/sheets.
- Touch targets must be at least 44px.
- Motion quality reduces automatically; heatmap remains readable.
