# DeadZone UX Summary

[86% confident] Build the first screen as an operations dashboard, not a landing page. The MVP value is visible when judges immediately see mode, stream health, density, flow, alerts, and replay controls.

## Problem + Success

DeadZone needs a local deterministic demo of physical-space intelligence. Success means `docker compose up` leads to a dashboard that streams mock/replay data, renders heatmap movement, shows congestion alerts, and exposes sensor/mesh status without live hardware.

## Key Tradeoffs

- Deterministic replay beats live sensing for the first slice.
- Aggregate zone intelligence beats raw event visualization.
- Mesh topology is useful for the story, but the heatmap and alerts must own the first viewport.
- Diagnostics matter, but they should stay in a drawer or secondary tab.

## Screen List

1. Operations Dashboard
2. Replay Lab
3. Sensor Mesh

## Smallest Shippable Slice

Implement the backend snapshot/WebSocket contract plus the Operations Dashboard with mock mode, one replay scenario, density zones, flow vectors, and an alert rail.

→ Next: Build from `.lev/pm/specs/deadzone-api-contract.yaml` and `.lev/pm/plans/deadzone-agent-task-bundle.yaml`.

→ Related: Use `.lev/ux/20260514-101228-deadzone-mvp-prd/constraint_bundle.yaml` as the compressed FE agent context.

💡 Tip: The trust layer is not the sensor adapter; it is visible provenance. Always show whether data is mock, replay, live, stale, or offline.
