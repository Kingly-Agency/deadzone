# Synthetic User And Agent Research

## Per-Persona Findings

### Judge Five-Minute Evaluator

The judge needs the first 10 seconds to show motion, heat, alerts, and deterministic replay state. The strongest credibility signal is not live BLE; it is visible replay controls, a named scenario, a seed, and a clear "mock/replay/live" mode badge.

### Venue Ops Commander

The operator values alert prioritization over raw event volume. The UI should answer: where is pressure rising, how severe is it, how long has it persisted, and which sensor observations support it. Identity-like language is a product risk.

### Frontend Partner

The frontend partner needs stable envelope types, explicit loading/empty/error/stale states, and mock data that matches production payload shape. If the backend streams raw RSSI events directly, the UI will waste time re-deriving aggregate views.

## Convergence Map

- All personas need a dense operations dashboard, not a landing page.
- All personas need provenance: mock, replay, live, adapter-disabled, stale, or offline.
- All personas prefer aggregate intelligence objects over raw device packets.
- All personas benefit from a replay timeline because it makes the demo explainable.

## Divergence Map

- Judges tolerate theatrical animation if deterministic; operators prefer restrained severity signals.
- RF technicians and frontend implementers need raw-ish diagnostics, but those should be secondary panels, not the main view.
- Mesh topology is exciting for story value but should not compete with the heatmap in the minimum viable screen.

## Edge Cases

- If WebSocket disconnects, the UI must preserve the last known snapshot and mark it stale instead of going blank.
- If no sensors are active, mock/replay mode should still show the venue model and an empty sensor state.
- If replay speed changes, timestamps and alert durations must remain coherent.

## JTBD Integration Notes

- Convergent concerns become layout constraints: visible mode, freshness, stream health, and replay controls.
- Divergent reactions become secondary views: operations dashboard first, topology and diagnostics behind tabs or panels.
- Edge cases become API states and validation checks.

## Self-Invalidation Gate

gate_decision: proceed

Reason: The synthetic personas produced actionable convergence around deterministic replay, aggregate-first intelligence, and visible data provenance. No persona surfaced a better first problem than the PRD's deterministic venue-intelligence demo.
