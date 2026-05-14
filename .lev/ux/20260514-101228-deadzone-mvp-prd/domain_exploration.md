# Domain Exploration

## Domain Personas

### Venue Operations Lead

This person is responsible for keeping people moving through entrances, halls, food courts, and exits during live events. Their daily pain is not lack of data; it is late, fragmented, or anecdotal data. Radio calls arrive after the crowd has already changed shape. Camera feeds are useful but require staff attention and can create privacy concerns. They care about fast situational awareness, plain-language alerts, and confidence that the system is not crying wolf. They do not want a dashboard that looks impressive but hides whether readings are stale, simulated, or live.

### Event Network / RF Technician

This person knows that BLE, Wi-Fi, and LoRa data can be messy, permission-bound, and hardware-specific. They are skeptical of density claims unless the data mode, sensor health, packet latency, and confidence are visible. What frustrates them is demo software that treats a sensor stream as magic and then fails silently when a radio disappears. They want mode control, replayability, logs, and adapter boundaries, plus clear privacy posture around aggregate data only.

### Hackathon Judge

This person has five minutes to understand whether the product is real, useful, and technically credible. They are not going to install drivers, pair devices, or inspect logs before the demo. They need the first screen to answer: what space is being observed, where are people building up, what changed, and why should I believe it? Their frustration is demos that depend on perfect staging or verbal explanation. They reward immediate clarity, deterministic behavior, and a visible upgrade path.

## Open-Ended Concerns

- Operators want fewer abstract charts and more actionable pressure signals: where, severity, trend, and suggested next observation.
- RF technicians want live/sim/replay labels, stale-data handling, and explicit sensor health before trusting derived intelligence.
- Judges want instant visible motion and a crisp story: simulation proves UX, replay proves reproducibility, adapters prove extensibility.

## Comparison With Intended Problem

There is strong overlap with the PRD. The MVP should stay deterministic-first, but the dashboard must make data provenance visible. The most important adjustment is treating mode, freshness, and confidence as first-class UI/API entities rather than buried implementation details.
