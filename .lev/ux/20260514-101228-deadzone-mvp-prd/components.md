# Components

## Reusable Components

| Component | Purpose | Props / Data |
|---|---|---|
| `StreamStatusStrip` | Shows mode, connection, freshness, sequence, and replay clock. | `mode`, `connected`, `freshness`, `sequence`, `clock`, `sourceLabel` |
| `ScenarioTransport` | Controls replay scenario, play/pause, restart, speed, and scrubber. | `scenarios`, `activeScenario`, `playbackState`, `speed`, `position` |
| `VenueMapCanvas` | Main spatial surface for venue zones, heat layer, vectors, and selection. | `venue`, `zones`, `selectedZoneId`, `qualityTier` |
| `DensityHeatLayer` | Renders density and pressure gradients. | `zoneAggregates`, `densityScale`, `pressureScale` |
| `FlowVectorLayer` | Renders movement direction and magnitude. | `flowVectors`, `selectedZoneId` |
| `SensorNodeOverlay` | Shows sensors, node health, latency, and selected node state. | `nodes`, `meshLinks`, `showLabels`, `selectedNodeId` |
| `AlertRail` | Prioritized alert list with filters and details. | `alerts`, `selectedAlertId`, `filters` |
| `MetricStrip` | Compact summary of total estimated devices, hot zones, alert count, and offline sensors. | `snapshotMetrics` |
| `LayerControl` | Toggles heatmap, vectors, sensors, topology, and labels. | `visibleLayers`, `disabledReasons` |
| `DiagnosticsDrawer` | Secondary technical view for stream envelopes and adapter state. | `streamState`, `adapterStatuses`, `recentEvents` |
| `TopologyPanel` | Mesh-style node/link view for distributed sensor story. | `nodes`, `meshLinks`, `gatewayNodeId` |
| `EmptyStatePanel` | Stable empty/offline/stale explanations. | `state`, `reason`, `primaryAction` |

## Screens To Components

| Screen | Components |
|---|---|
| Operations Dashboard | `StreamStatusStrip`, `MetricStrip`, `VenueMapCanvas`, `DensityHeatLayer`, `FlowVectorLayer`, `SensorNodeOverlay`, `AlertRail`, `LayerControl`, `DiagnosticsDrawer` |
| Replay Lab | `StreamStatusStrip`, `ScenarioTransport`, `VenueMapCanvas`, `AlertRail`, `DiagnosticsDrawer` |
| Sensor Mesh | `StreamStatusStrip`, `TopologyPanel`, `SensorNodeOverlay`, `LayerControl`, `DiagnosticsDrawer` |

## Implementation Notes

- Keep high-frequency stream data in refs or an external store; avoid React state churn for every raw event.
- Render aggregates at dashboard cadence, not per packet, unless a component is explicitly diagnostic.
- Use semantic color: red critical, amber warning, cyan active stream, green healthy, neutral gray offline.
- Color must never be the only state signal; pair with labels, icons, shape, or line style.
- Support reduced motion by freezing nonessential blob movement while retaining state changes.
