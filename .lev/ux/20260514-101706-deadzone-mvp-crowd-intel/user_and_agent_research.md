# Step 1b: Synthetic User Research -- DeadZone MVP

**Pipeline**: DeadZone MVP Crowd Intelligence UX  
**Date**: 2026-05-14  
**Method**: Synthetic persona simulation against MVP concept  
**Concept under test**: Heatmap dashboard, mode switcher (Mock/Replay/Live/Mesh), sensor topology view, alerts panel

---

## 1. Persona Definitions

### P1: "Dana" -- Hackathon Judge (Generalist)

| Dimension | Value |
|---|---|
| Technical literacy | Medium -- ships product but not an infra person |
| Time pressure | **5 minutes** (strict booth rotation) |
| Risk tolerance | Demo-friendly; expects polish over depth |
| Domain expertise | None in crowd analytics; adjacent in data viz |
| Success metric | "Can I tell what this does in 30 seconds and see it work in 2 minutes?" |

**Background**: Product manager at a mid-stage startup. Judges hackathons quarterly. Has seen 200+ demos. Pattern-matches on: (a) does it load, (b) is the value prop obvious, (c) is there a wow moment. Will not read documentation. Will click whatever is most prominent.

### P2: "Raj" -- Skeptical Engineer Judge

| Dimension | Value |
|---|---|
| Technical literacy | **High** -- distributed systems background |
| Time pressure | 5 minutes (but will linger if impressed) |
| Risk tolerance | Low -- suspicious of anything that looks too polished without substance |
| Domain expertise | Adjacent -- has built IoT dashboards, knows BLE range limits |
| Success metric | "Is any of this real data, or is the whole thing a canned animation?" |

**Background**: Staff engineer at a large cloud provider. Judges technical merit. Will ask "what happens if I disconnect the Wi-Fi?" and "show me the API." Actively looks for fakes. Respects honest labeling of mocks. Will penalize unlabeled synthetic data presented as real.

### P3: "Maria" -- Venue Operations Manager

| Dimension | Value |
|---|---|
| Technical literacy | Low-to-medium -- uses dashboards daily but doesn't build them |
| Time pressure | **30 minutes** (evaluating a procurement, not a hackathon) |
| Risk tolerance | Medium -- needs reliability but understands V1 limitations |
| Domain expertise | **Deep** in venue ops -- knows crowd flow patterns intuitively |
| Success metric | "Will this tell me something I don't already know from my walkie-talkie?" |

**Background**: Operations director at a 15,000-seat arena. Manages 40 staff per event. Currently uses manual radio check-ins for crowd density. Has been burned by vendors who demo well but can't handle 50k concurrent connections. Wants actionable alerts ("Gate 3 at 85% capacity"), not pretty pictures.

### P4: "Tomasz" -- Public Safety Coordinator

| Dimension | Value |
|---|---|
| Technical literacy | Medium -- uses GIS and incident management systems |
| Time pressure | **30 minutes** (but zero tolerance for ambiguity in crisis scenarios) |
| Risk tolerance | **Extremely low** -- life-safety context |
| Domain expertise | Deep in emergency management; adjacent in crowd analytics |
| Success metric | "What happens when this system fails? Does it fail safe or fail silent?" |

**Background**: Emergency management coordinator for a mid-size city. Evaluates crowd monitoring tools for festivals and public gatherings. Regulatory mindset: needs audit trails, uptime guarantees, degradation modes. Will immediately ask about false positive rates on alerts. Has seen crowd crush incidents; this is not abstract for him.

### P5: "Kenji" -- Hackathon Developer (Team Member)

| Dimension | Value |
|---|---|
| Technical literacy | **High** -- built the system |
| Time pressure | **1 minute** (to switch modes during live demo without breaking anything) |
| Risk tolerance | High for demo; terrified of demo failure |
| Domain expertise | Medium -- understands the sensing stack but hasn't deployed at scale |
| Success metric | "Can I switch from Mock to Replay without the dashboard glitching in front of judges?" |

**Background**: CS senior building DeadZone as a capstone project. Knows every line of code. Primary anxiety: the venue Wi-Fi will drop during the Live mode demo, and the dashboard will show a blank map. Needs graceful degradation that doesn't look like a crash. Has rehearsed the 3-minute pitch 20 times.

---

## 2. Simulated Reactions to MVP Concept

### 2.1 Heatmap Dashboard

| Persona | Reaction |
|---|---|
| **Dana** | "Oh, this is a heatmap -- I get it immediately. The colors are intuitive. But what am I supposed to DO with this information? I need a headline number or status badge, not just a gradient." |
| **Raj** | "Nice visualization. What's the update frequency? Is this polling or WebSocket? ... Wait, is this the same data every time I reload? (checks network tab) Ah, it's mock data. Label it." |
| **Maria** | "The heatmap is pretty but I need numbers. How many people at Gate 3? What's the trend -- is it filling or draining? I manage by zones, not by color gradients." |
| **Tomasz** | "Heatmaps are decorative unless they're calibrated. What's the unit? People per square meter? Signal strength? These are very different things. And where's the legend?" |
| **Kenji** | "The heatmap renders in 200ms -- good. But if I switch to Live mode and there's no data, it shows an empty map. I need a skeleton state or 'awaiting sensors' indicator." |

### 2.2 Mode Switcher (Mock / Replay / Live / Mesh)

| Persona | Reaction |
|---|---|
| **Dana** | "Four modes? I don't care about modes. Just show me the best version. If I have to pick, I'll pick wrong and think the product is broken. Auto-select for me." |
| **Raj** | "THIS is what I wanted to see. The fact that you have a Mock mode and label it honestly is a huge signal of engineering maturity. Let me toggle between them -- does the data change? Show me Replay with a known scenario." |
| **Maria** | "Mock and Replay mean nothing to me. I want 'Demo' and 'Production.' Rename these. And what happens if Live sensors go offline -- does it fall back to Replay automatically?" |
| **Tomasz** | "The mode switcher implies the system can run without real sensors. That's useful for training exercises. But in production, I need to know: is this real data or simulated? Make the distinction impossible to miss." |
| **Kenji** | "The switcher works but the transition between modes causes a 400ms flash of empty state. I need a crossfade or at minimum a loading skeleton. If a judge sees a white screen for half a second, they'll think it crashed." |

### 2.3 Sensor Topology View

| Persona | Reaction |
|---|---|
| **Dana** | "I don't know what I'm looking at. Are these Wi-Fi routers? Bluetooth beacons? Why do I care where they are? Skip this screen in the demo." |
| **Raj** | "Now we're talking. Show me signal coverage overlap. What's the triangulation accuracy? Can I click a sensor and see its raw feed? This is the technical depth that separates a real project from a Figma mockup." |
| **Maria** | "I need to know where my blind spots are. If a sensor goes down, which zones lose coverage? Show me the gap, not just the nodes." |
| **Tomasz** | "Sensor health is critical. I need red/yellow/green status per sensor, battery level for BLE beacons, and last-seen timestamp. If a sensor hasn't reported in 60 seconds, I need to know immediately." |
| **Kenji** | "The topology SVG takes 1.2 seconds to render with 50 nodes. For the demo we have 8 mock sensors so it's fine, but I should mention scalability in the pitch." |

### 2.4 Alerts Panel

| Persona | Reaction |
|---|---|
| **Dana** | "Alerts are good -- they prove the system is intelligent, not just a display. Show me one firing during the demo. If no alert fires in 5 minutes, I'll think the feature doesn't work." |
| **Raj** | "What's the alert logic? Threshold-based or ML? Can I see the rule configuration? And what's the false positive rate -- even a rough number?" |
| **Maria** | "Alerts need to go somewhere -- my phone, a radio dispatch, a PA system. A panel on a screen nobody's watching is useless. Show me the integration story." |
| **Tomasz** | "Alert fatigue is my number one concern. If this system sends 50 alerts per hour, my team will ignore all of them. I need severity levels, acknowledgment workflow, and escalation paths." |
| **Kenji** | "I'll pre-seed a mock alert that fires 90 seconds into the demo. That gives me time to set context before the 'wow' moment. But I need to make sure it only fires once -- repeating alerts during a demo look buggy." |

---

## 3. Convergence Map (Signal)

These findings appeared across 4+ of 5 personas:

| # | Convergent Finding | Personas | UX Implication |
|---|---|---|---|
| C1 | **The heatmap needs a legend and units** -- everyone asked "what do the colors mean?" or "what's the unit?" | All 5 | Hard requirement: persistent legend with unit label (people/m^2 in Replay/Live, "simulated" badge in Mock) |
| C2 | **Mode labeling must be honest and unmissable** -- even the generalist judge wants to know if data is real | All 5 | Mode indicator must be persistent (not just in the switcher), colored, and use plain language |
| C3 | **At least one alert must fire during a 5-minute demo** -- otherwise the alerts panel looks inert | Dana, Raj, Kenji, Maria | Demo mode should guarantee a timed alert event; alerts panel should never appear empty (show "No active alerts -- system nominal" not blank) |
| C4 | **Empty/loading states are perceived as broken** -- white flashes, blank maps, and empty panels all read as crashes | All 5 | Every panel needs a skeleton/loading state and a meaningful zero-state message |
| C5 | **Headline metrics beat gradients** -- a single "72% capacity" number communicates faster than a heatmap alone | Dana, Maria, Tomasz, Kenji | Add a summary bar or hero metric above the heatmap |

---

## 4. Divergence Map (Tensions)

| # | Tension | Camp A | Camp B | Design Tradeoff |
|---|---|---|---|---|
| D1 | **Mode switcher visibility** | Dana + Maria: hide modes, auto-select | Raj + Tomasz: modes are a feature, show them prominently | Solution: auto-select best available mode on load, but expose switcher as a secondary control for technical users |
| D2 | **Sensor topology: show or hide** | Dana: skip it, it's noise | Raj + Tomasz: it's the proof of real engineering | Solution: topology as a collapsible panel or tab, not front-and-center. Expand on click for technical audiences |
| D3 | **Alert detail level** | Dana + Kenji: one dramatic alert is enough | Maria + Tomasz: need severity, ack workflow, escalation | Solution: MVP shows simple alerts with severity badge; detail/ack is a post-MVP feature documented in the pitch |
| D4 | **Data provenance labeling** | Dana: don't care, just make it look good | Raj + Tomasz: mislabeled mock data is disqualifying | Solution: always show provenance, but make it subtle (badge, not a banner) so non-technical viewers aren't confused |
| D5 | **Graceful degradation vs. explicit failure** | Kenji: seamless fallback so demo never breaks | Tomasz: explicit failure indication, never hide a problem | Solution: in Mock/Replay, silent fallback; in Live/Mesh, explicit "sensor offline" indicator with fallback option |

---

## 5. Edge Cases (Unexpected Reactions)

| # | Edge Case | Persona | Description | UX Risk |
|---|---|---|---|---|
| E1 | **Demo loop anxiety** | Kenji | "What if a judge walks up mid-demo and I can't reset cleanly?" Needs a one-click reset to initial demo state without reloading the page | If reset requires page reload, risk of Docker/WebSocket reconnection delay in front of judge |
| E2 | **Heatmap as liability** | Tomasz | "In a real incident, a heatmap showing crowd density could cause panic if displayed on a public screen. Access control isn't optional." | MVP should note that production deployment requires auth; hackathon demo is exempt but the pitch should mention it |
| E3 | **Color accessibility** | Maria | "My assistant is red-green colorblind. The default heatmap palette is unusable for him." | Heatmap palette must avoid red-green only encoding; use viridis or plasma with shape/pattern overlay at critical thresholds |
| E4 | **Replay data as test suite** | Raj | "If I can record a real event and replay it, this is also a regression testing tool. Have you thought about that?" -- unexpected positive framing | Replay mode has dual value: demo AND testing. Mention in pitch; consider export/import of replay files |
| E5 | **Wi-Fi dependency irony** | Raj | "A system that detects dead Wi-Fi zones... needs Wi-Fi to function. That's either brilliant irony or a fatal flaw. Which is it?" | Pitch must address this head-on: Mesh/BLE modes exist precisely for Wi-Fi-independent operation; the irony is the product insight |

---

## 6. UX Implications Mapping

### 6.1 Convergent Concerns --> Layout Constraints

```yaml
layout_constraints:
  - id: LC-1
    source: C1, C5
    constraint: "Heatmap must include a persistent color legend with unit label AND a summary metric bar showing top-line numbers (total occupancy, peak zone, trend arrow)"
    priority: P0

  - id: LC-2
    source: C2
    constraint: "Active data mode must be indicated by a persistent badge visible in all views, using color coding (blue=Mock, amber=Replay, green=Live, purple=Mesh) and plain-language label"
    priority: P0

  - id: LC-3
    source: C4
    constraint: "Every panel must define three states: loading (skeleton), empty (meaningful zero-state message), and populated. No panel may ever render as blank white space"
    priority: P0

  - id: LC-4
    source: C3
    constraint: "Demo/Mock mode must include a timed event sequence that triggers at least one alert within 90 seconds of load, ensuring the alerts panel is never inert during a judge visit"
    priority: P0

  - id: LC-5
    source: E3
    constraint: "Heatmap color palette must be accessible (WCAG AA). Use viridis/plasma palette; avoid red-green only encoding. Critical thresholds should use pattern overlay in addition to color"
    priority: P1
```

### 6.2 Convergent Excitement --> JTBD Motivation Language

```yaml
motivation_language:
  - jtbd: "When I walk up to a hackathon booth, I want to immediately see a live, updating visualization so I can assess technical capability in under 30 seconds"
    evidence: "Dana, Raj, Kenji all converge on 'instant legibility' as the primary wow factor"

  - jtbd: "When I evaluate crowd monitoring tools, I want to distinguish real sensing from canned demos so I can trust the system's production viability"
    evidence: "Raj and Tomasz both reward honest mode labeling; Raj explicitly calls it 'engineering maturity signal'"

  - jtbd: "When I manage a venue, I want zone-level occupancy numbers with trend direction so I can make staffing decisions without leaving the ops room"
    evidence: "Maria's core ask; Tomasz agrees numbers beat gradients for operational decisions"

  - jtbd: "When I demo my project, I want deterministic event sequences so I can rehearse a pitch that always lands the same way"
    evidence: "Kenji's primary anxiety; Dana confirms that a timed alert 'proves the system is intelligent'"
```

### 6.3 Divergent Reactions --> User Types

```yaml
user_types:
  - id: spectator
    label: "Spectator (Glanceable)"
    personas: [Dana]
    needs: "Instant comprehension, headline metrics, minimal controls, wow moment"
    mode_preference: "Auto-selected, modes hidden"
    topology_preference: "Hidden"
    alert_depth: "Single dramatic event"

  - id: investigator
    label: "Investigator (Drill-Down)"
    personas: [Raj, Kenji]
    needs: "Mode switching, raw data access, sensor detail, API visibility"
    mode_preference: "Prominently switchable"
    topology_preference: "Visible, interactive"
    alert_depth: "Rule inspection, threshold config"

  - id: operator
    label: "Operator (Action-Oriented)"
    personas: [Maria, Tomasz]
    needs: "Zone numbers, trend arrows, alert routing, degradation visibility"
    mode_preference: "Demo vs Production only"
    topology_preference: "Coverage gaps, sensor health"
    alert_depth: "Severity, ack, escalation, integration hooks"
```

### 6.4 Edge Cases --> Anti-Patterns

```yaml
anti_patterns:
  - id: AP-1
    source: E1
    pattern: "No demo reset button"
    risk: "Judge arrives mid-demo, sees post-alert state with no way to restart cleanly"
    mitigation: "Add a discreet reset-to-start control (keyboard shortcut or hidden button) that resets mock timeline without page reload"

  - id: AP-2
    source: E2
    pattern: "Public-facing density display without access control"
    risk: "Production deployment leaks real-time crowd density to unauthorized viewers, potential panic vector"
    mitigation: "MVP: note in pitch deck. V2: auth layer. Never default to public access in production config"

  - id: AP-3
    source: E5
    pattern: "Wi-Fi-dependent Wi-Fi dead zone detector"
    risk: "System fails precisely when it's most needed (during connectivity outages)"
    mitigation: "Pitch addresses this directly: BLE/Mesh modes are the answer. Demo should show graceful degradation from Live to Mesh"

  - id: AP-4
    source: E3
    pattern: "Color-only encoding for critical thresholds"
    risk: "8% of male users cannot distinguish red-green heatmap gradients"
    mitigation: "Use accessible palette (viridis) plus pattern/icon overlay at critical thresholds"

  - id: AP-5
    source: E4
    pattern: "Replay mode only framed as demo tool"
    risk: "Misses dual-use value (regression testing, training exercises) that resonates with technical judges"
    mitigation: "Frame Replay as 'scenario playback' with import/export, mention testing and training use cases in pitch"
```

---

## 7. Gate Decision

**gate_decision: proceed**

**Rationale**: The synthetic research reveals strong convergence on core UX requirements (legend, mode labeling, loading states, timed alerts, headline metrics) with manageable divergences that map cleanly to three user types (Spectator, Investigator, Operator). No findings suggest the concept is fundamentally misaligned with user needs. The edge cases are addressable within MVP scope (E1, E3, E4, E5) or explicitly deferred to post-MVP (E2). The problem statement holds: the primary design challenge is progressive disclosure -- showing a glanceable dashboard to Dana while letting Raj drill into sensor topology -- which is a well-understood UX pattern.

**Risk to monitor**: The Wi-Fi irony (E5) must be addressed in the pitch, not just the product. If judges perceive it as a flaw rather than a feature insight, the demo loses credibility regardless of UX quality.
