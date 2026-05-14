# Wireframes -- DeadZone MVP Crowd Intelligence Dashboard

**Pipeline**: DeadZone MVP Crowd Intelligence UX
**Date**: 2026-05-14
**Target**: React + Leaflet + Heatmap.js, single-screen dashboard, desktop-first (1440x900)
**Inputs**: problem_spec.yaml, jobs.graph.json, ia_schema.json, task_graph.json, user_and_agent_research.md

---

## Global Nav Map

Single-screen dashboard with no page transitions. All secondary navigation uses overlays, slide-in panels, and drawers attached to the main canvas. The header is the only persistent chrome element besides the footer status bar. Spectators interact with only the heatmap and metrics bar; Investigators and Operators progressively reveal deeper layers via header controls and map clicks.

**Header anatomy** (left to right):
`[ Brand logo + "DeadZone" ] [ Mode chip (colored pill) ] [ --- spacer --- ] [ Reset icon ] [ Topology toggle ] [ Settings gear ]`

**Footer anatomy**:
`[ Connection: WS connected ] [ --- spacer --- ] [ Last frame: 14:32:07.421 ] [ v0.1.0-mvp ]`

---

## Screen 1: Dashboard (Default View, Mock Mode)

**Purpose**: Deliver instant comprehension of venue crowd density so a hackathon judge grasps the product in under 30 seconds.

**Primary actions**:
1. Observe heatmap animation and headline metrics (passive, zero-click)
2. Click a zone polygon to inspect occupancy detail
3. Scan alerts panel for active events

### Layout -- Populated / Success State

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌──────────┐                          ↺ Reset  ◎ Topology  ⚙ Settings │
│                           │ ● MOCK   │                                                          │
│                           └──────────┘                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  1,247 attendees   │   72% capacity   │   Peak: Hall B   │   ↗ rising (5m trend)                │
├──────────────────────────────────────────────────────────────┬────────────────────────────────────┤
│                                                             │  ALERTS              1 active      │
│                                                             ├────────────────────────────────────┤
│                         ┌─────────────────────┐             │  ▲ WARN  Hall B at 85% capacity   │
│                         │                     │             │    Zone B  ·  14:31:42             │
│                         │    ░░▒▒▓▓██▓▓▒▒░░   │             │    [ Acknowledge ]                 │
│                         │   ░░▒▒▓▓████▓▓▒▒░   │             ├────────────────────────────────────┤
│                         │  ░░▒▒▓▓██████▓▓▒░   │             │  ● INFO  Replay scenario loaded   │
│          VENUE          │ ░░▒▒▓▓████████▓▓░   │  Legend     │    System  ·  14:30:12  ✓ ack'd   │
│        FLOORPLAN        │  ░▒▒▓▓██████▓▓▒░░   │  ┌──┐      ├────────────────────────────────────┤
│         (Leaflet        │   ░▒▒▓▓████▓▓▒░░    │  │██│ High  │                                    │
│          canvas)        │    ░░▒▒▓▓██▓▓▒░░    │  │▓▓│      │                                    │
│                         │     ░░▒▒▓▓▓▒▒░░     │  │▒▒│      │                                    │
│                         │      ░░▒▒▒▒░░░      │  │░░│ Low   │                                    │
│                         └─────────────────────┘  │  │      │                                    │
│                                                  └──┘      │                                    │
│                                                  ppl/m^2   │                                    │
│                                                  (sim.)    │                                    │
│                                                             │                                    │
├──────────────────────────────────────────────────────────────┴────────────────────────────────────┤
│  ● Connected (WebSocket)                              Last frame: 14:32:07.421          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### State Variant: Loading (Skeleton)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌──────────┐                          ↺ Reset  ◎ Topology  ⚙ Settings │
│                           │ ● MOCK   │                                                          │
│                           └──────────┘                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ████████████████   │   ████████████   │   ██████████████   │   ████████████████████             │
├──────────────────────────────────────────────────────────────┬────────────────────────────────────┤
│                                                             │  ALERTS                            │
│                                                             ├────────────────────────────────────┤
│                                                             │  ┌────────────────────────────┐    │
│                                                             │  │ ████████████████████████   │    │
│                     ┌───────────────────────┐               │  │ ██████████  ·  ██████████  │    │
│                     │                       │               │  └────────────────────────────┘    │
│                     │   ░ ░ ░ ░ ░ ░ ░ ░ ░  │               │  ┌────────────────────────────┐    │
│                     │   ░   Connecting...  ░ │               │  │ ████████████████████████   │    │
│                     │   ░   ░ ░ ░ ░ ░ ░ ░  │               │  │ ██████████  ·  ██████████  │    │
│                     │                       │               │  └────────────────────────────┘    │
│                     └───────────────────────┘               │                                    │
│                                                             │                                    │
├──────────────────────────────────────────────────────────────┴────────────────────────────────────┤
│  ○ Connecting...                                      Last frame: --:--:--.---          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### State Variant: Empty (No Data Yet)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌──────────┐                          ↺ Reset  ◎ Topology  ⚙ Settings │
│                           │ ● MOCK   │                                                          │
│                           └──────────┘                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  0 attendees       │   0% capacity    │   Peak: --         │   -- no trend data                  │
├──────────────────────────────────────────────────────────────┬────────────────────────────────────┤
│                                                             │  ALERTS                            │
│                                                             ├────────────────────────────────────┤
│                                                             │                                    │
│                     ┌───────────────────────┐               │     No active alerts --            │
│                     │                       │               │     system nominal.                 │
│                     │     VENUE FLOORPLAN    │               │                                    │
│                     │                       │               │     Waiting for first               │
│                     │   Awaiting sensor      │               │     sensor event...                │
│                     │   reports...           │               │                                    │
│                     │                       │               │                                    │
│                     └───────────────────────┘               │                                    │
│                                                             │                                    │
├──────────────────────────────────────────────────────────────┴────────────────────────────────────┤
│  ● Connected (WebSocket)                              Last frame: --:--:--.---          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### State Variant: Error (Connection Issue)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌──────────┐                          ↺ Reset  ◎ Topology  ⚙ Settings │
│                           │ ● MOCK   │                                                          │
│                           └──────────┘                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ╔══════════════════════════════════════════════════════════════════════════════════════════════╗  │
│ ║  ⚠  Connection issue -- retrying every 5s...                            [ Retry now ]      ║  │
│ ╚══════════════════════════════════════════════════════════════════════════════════════════════╝  │
├──────────────────────────────────────────────────────────────┬────────────────────────────────────┤
│                                                             │  ALERTS                            │
│                                                             ├────────────────────────────────────┤
│                     ┌───────────────────────┐               │                                    │
│                     │                       │               │     Connection lost.                │
│                     │   Last-known state     │               │     Displaying last-known          │
│                     │   (faded / dimmed)     │               │     alert state.                   │
│                     │                       │               │                                    │
│                     │   ░░▒▒▓▓██▓▓▒▒░░      │               │                                    │
│                     │   (50% opacity)        │               │                                    │
│                     │                       │               │                                    │
│                     └───────────────────────┘               │                                    │
│                                                             │                                    │
├──────────────────────────────────────────────────────────────┴────────────────────────────────────┤
│  ✕ Disconnected (retrying...)                         Last frame: 14:31:52.103          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### State Variant: Stale (Data Stream Paused)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌───────────────┐                     ↺ Reset  ◎ Topology  ⚙ Settings │
│                           │ ⊘ LIVE (stale)│                                                     │
│                           └───────────────┘                                                     │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  1,247 attendees   │   72% capacity   │   Peak: Hall B   │   -- stale (>30s since last update)  │
├──────────────────────────────────────────────────────────────┬────────────────────────────────────┤
│                                                             │  ALERTS              2 active      │
│                                                             ├────────────────────────────────────┤
│                                                             │  ▲ WARN  Sensor stream stalled    │
│                     ┌───────────────────────┐               │    System  ·  14:33:22             │
│                     │                       │               │    [ Switch to Replay ]             │
│                     │   ░░▒▒▓▓██▓▓▒▒░░      │               │    [ Retry Live ]                  │
│                     │   (dimmed, pulsing     │               │    [ Dismiss ]                     │
│                     │    amber border)       │               ├────────────────────────────────────┤
│                     │                       │               │  ▲ WARN  Hall B at 85% capacity   │
│                     │                       │               │    Zone B  ·  14:31:42             │
│                     └───────────────────────┘               │                                    │
│                                                             │                                    │
├──────────────────────────────────────────────────────────────┴────────────────────────────────────┤
│  ⚠ Stale (no data for 34s)                            Last frame: 14:32:48.901          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen 2: Zone Detail Slide-In

**Purpose**: Give operators zone-level numeric occupancy, trend direction, and zone-scoped alerts so they can make staffing or routing decisions without leaving the dashboard.

**Primary actions**:
1. Read numeric occupancy and percentage capacity for the selected zone
2. Check 5-minute trend sparkline to assess whether zone is filling or draining
3. View and acknowledge zone-scoped alerts

### Layout -- Populated

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌──────────┐                          ↺ Reset  ◎ Topology  ⚙ Settings │
│                           │ ● MOCK   │                                                          │
│                           └──────────┘                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  1,247 attendees   │   72% capacity   │   Peak: Hall B   │   ↗ rising (5m trend)                │
├───────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│                                           │  ZONE DETAIL: Hall B                          [  X ] │
│                                           ├───────────────────────────────────────────────────────┤
│                                           │                                                      │
│              ┌────────────────┐           │  Occupancy       437 / 500                           │
│              │                │           │  Capacity         87%  ████████▓░                     │
│              │  ░░▒▒▓▓████▓▓  │           │  Trend (5m)      ↗ rising (+12%)                     │
│              │  ░▒▒▓▓██████▓  │           │                                                      │
│              │  ░▒▒▓▓██████▓  │           │  Sparkline:                                          │
│   (zone      │  ░░▒▒▓▓████▓▓  │           │    ╭─╮                                               │
│   highlighted│  ░░▒▒▓▓██▓▓▒░  │           │   ╭╯ ╰╮  ╭──╮                                       │
│   with thick │                │           │  ─╯    ╰──╯  ╰╮                                      │
│   outline)   └────────────────┘           │                ╰─  (now)                             │
│                                           │  -5m ──────────────────── now                        │
│                                           ├───────────────────────────────────────────────────────┤
│                                           │  ZONE ALERTS                                         │
│                                           │  ▲ WARN  Hall B at 85% capacity                     │
│                                           │    14:31:42  [ Acknowledge ]                         │
│                                           │                                                      │
│                                           │  Threshold: 400 / 500 (80%)                          │
│                                           │  Rule: count > 80% capacity for > 60s                │
│                                           │                                                      │
├───────────────────────────────────────────┴───────────────────────────────────────────────────────┤
│  ● Connected (WebSocket)                              Last frame: 14:32:07.421          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### State Variant: No Recent Data

```
│  ZONE DETAIL: Loading Dock C                    [  X ] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Occupancy       --                                     │
│  Capacity        --                                     │
│  Trend (5m)      -- insufficient data                   │
│                                                         │
│  Sparkline:                                             │
│    ·       ·                                            │
│       ·                       (< 5min of data)          │
│  -5m ──────────────────────── now                       │
│                                                         │
│  Awaiting sensor reports.                               │
│  Last seen: 14:28:03                                    │
│                                                         │
```

### State Variant: Zone with Acknowledged Alert

```
│  ZONE ALERTS                                            │
│  ✓ WARN  Hall B at 85% capacity          (acknowledged) │
│    14:31:42  ·  ack'd by operator at 14:32:01           │
│                                                         │
│  No further active alerts for this zone.                │
│                                                         │
```

---

## Screen 3: Sensor Topology Overlay

**Purpose**: Let investigators and operators verify sensor placement, coverage gaps, and individual sensor health to validate the sensing architecture is real and defensible.

**Primary actions**:
1. Toggle topology overlay on/off from the header
2. Identify coverage gaps via diagonal hatch pattern on uncovered areas
3. Click a sensor node to drill into raw event stream (last 10 events)

### Layout -- Topology ON, Sensor Selected

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌──────────┐                     ↺ Reset  [◎ Topology] ⚙ Settings     │
│                           │ ● MOCK   │                              (active/lit)                 │
│                           └──────────┘                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  1,247 attendees   │   72% capacity   │   Peak: Hall B   │   ↗ rising (5m trend)                │
├───────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│                                           │  SENSOR TOPOLOGY                              [  X ] │
│                                           ├───────────────────────────────────────────────────────┤
│                                           │  8 sensors  ·  6 online  ·  2 degraded              │
│     ┌─────────────────────────────┐       │                                                      │
│     │                             │       │  SENSOR LIST                                         │
│     │   (S1)●       ●(S2)        │       │  ┌────────────────────────────────────────────┐      │
│     │        ╲     ╱              │       │  │ ● S1  BLE     online   bat: 82%           │      │
│     │         ╲   ╱               │       │  │ ● S2  WiFi    online   bat: --            │      │
│     │    (S3)● ╲ ╱   ╱╱╱╱╱╱╱╱    │       │  │ ● S3  BLE     online   bat: 67%           │      │
│     │          ╳   ╱╱ coverage╱   │       │  │ ◐ S4  BLE     degraded bat: 23%           │      │
│     │         ╱ ╲ ╱╱╱ gap  ╱╱╱   │       │  │ ● S5  Mesh    online   bat: 91%           │      │
│     │   (S4)◐   ╱╱╱╱╱╱╱╱╱╱╱╱    │       │  │ ● S6  WiFi    online   bat: --            │      │
│     │       ╱ ╲    ●(S5)         │       │  │ ◐ S7  BLE     degraded bat: 11% ⚠         │      │
│     │  (S6)●   ●(S7)  ●(S8)     │       │  │ ● S8  BLE     online   bat: 55%    [sel]  │      │
│     │                             │       │  └────────────────────────────────────────────┘      │
│     └─────────────────────────────┘       ├───────────────────────────────────────────────────────┤
│                                           │  SELECTED: S8 (BLE Beacon)                          │
│     Legend:                               │  Status:    online                                    │
│     ● online  ◐ degraded  ○ offline      │  Battery:   55%                                      │
│     ╱╱╱ uncovered area (hatched)          │  Last seen: 14:32:06 (1s ago)                        │
│                                           │  RSSI:      -67 dBm                                  │
│                                           │                                                      │
│                                           │  RAW EVENT TAIL (last 10)                            │
│                                           │  14:32:06.421  rssi:-67  zone:Hall-B   cnt:3        │
│                                           │  14:32:04.198  rssi:-69  zone:Hall-B   cnt:2        │
│                                           │  14:32:02.003  rssi:-68  zone:Hall-B   cnt:4        │
│                                           │  14:31:59.811  rssi:-71  zone:Hall-B   cnt:2        │
│                                           │  14:31:57.622  rssi:-66  zone:Hall-B   cnt:5        │
│                                           │  ... (5 more)                                        │
├───────────────────────────────────────────┴───────────────────────────────────────────────────────┤
│  ● Connected (WebSocket)                              Last frame: 14:32:07.421          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### State Variant: No Sensors Discovered (Live Mode)

```
│  SENSOR TOPOLOGY                              [  X ] │
├───────────────────────────────────────────────────────┤
│  0 sensors discovered                                │
│                                                       │
│     ┌───────────────────────────────┐                │
│     │                               │                │
│     │   No sensors found.           │                │
│     │   Check BLE permissions and   │                │
│     │   verify gateway is running.  │                │
│     │                               │                │
│     │   [ Diagnostics guide ]       │                │
│     │   [ Switch to Mock mode ]     │                │
│     │                               │                │
│     └───────────────────────────────┘                │
│                                                       │
```

### State Variant: Error (Topology Fetch Failed)

```
│  SENSOR TOPOLOGY                              [  X ] │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ⚠  Unable to load sensor topology.                  │
│     Error: gateway timeout (5s)                       │
│                                                       │
│     [ Retry ]   [ Switch to Mock ]                    │
│                                                       │
```

---

## Screen 4: Replay Scenario Picker (Drawer)

**Purpose**: Let users choose a pre-recorded crowd scenario and scrub through it for deterministic demo playback, training exercises, or regression testing.

**Primary actions**:
1. Select one of four built-in scenarios
2. Adjust playback speed (0.25x -- 4x)
3. Scrub to a specific timestamp

### Layout -- Choosing State

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  DeadZone                 ┌───────────┐                         ↺ Reset  ◎ Topology  ⚙ Settings │
│                           │ ◉ REPLAY  │                                                         │
│                           └───────────┘                                                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  -- attendees      │   --% capacity   │   Peak: --         │   -- awaiting scenario              │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│                            (heatmap canvas -- awaiting scenario selection)                       │
│                                                                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─ REPLAY: Choose a scenario ────────────────────────────────────────────────────────────── ▼ ─┐ │
│ │                                                                                              │ │
│ │  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐│ │
│ │  │ ▶ Convention       │  │ ▶ Concert Exit     │  │ ▶ Hallway          │  │ ▶ Stadium         ││ │
│ │  │   Morning Rush     │  │   Rush             │  │   Congestion       │  │   Evacuation      ││ │
│ │  │                    │  │                    │  │                    │  │                    ││ │
│ │  │   5:00 duration    │  │   3:30 duration    │  │   4:15 duration    │  │   6:00 duration   ││ │
│ │  │   1,842 events     │  │   3,201 events     │  │   967 events       │  │   5,411 events    ││ │
│ │  │   #arrival #peak   │  │   #egress #surge   │  │   #bottleneck      │  │   #emergency      ││ │
│ │  └────────────────────┘  └────────────────────┘  └────────────────────┘  └──────────────────┘│ │
│ │                                                                                              │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ● Connected (WebSocket)                              Last frame: --:--:--.---          v0.1.0  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### State Variant: Playing (Scrubber Visible)

```
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ┌─ REPLAY: Concert Exit Rush ──────────────────────────────────────────────────────── 1:42/3:30 ┐│
│ │                                                                                              │ │
│ │   ❚❚ Pause     ◀◀ -15s     [ 0.25x  0.5x  (1x)  2x  4x ]     +15s ▶▶     ◼ Stop          │ │
│ │                                                                                              │ │
│ │   ├────────────────●──────────────────────────────────────────────────────────────────────┤   │ │
│ │   0:00           1:42                                                               3:30     │ │
│ │                    ▲                                                                         │ │
│ │                  (now)                                                                       │ │
│ │                                                                                              │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
```

### State Variant: Paused

```
│ ┌─ REPLAY: Concert Exit Rush ──────────────────────────────────────────────── PAUSED  1:42/3:30 ┐│
│ │                                                                                              │ │
│ │   ▶ Play      ◀◀ -15s     [ 0.25x  0.5x  (1x)  2x  4x ]     +15s ▶▶     ◼ Stop           │ │
│ │                                                                                              │ │
│ │   ├────────────────●──────────────────────────────────────────────────────────────────────┤   │ │
│ │   0:00           1:42                                                               3:30     │ │
│ │                                                                                              │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
```

### State Variant: Error / Load Failed

```
│ ┌─ REPLAY: Choose a scenario ────────────────────────────────────────────────────────────── ▼ ─┐ │
│ │                                                                                              │ │
│ │  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐  ┌──────────────────┐│ │
│ │  │ ▶ Convention       │  │ ⚠ Concert Exit     │  │ ▶ Hallway          │  │ ▶ Stadium         ││ │
│ │  │   Morning Rush     │  │   Rush             │  │   Congestion       │  │   Evacuation      ││ │
│ │  │                    │  │                    │  │                    │  │                    ││ │
│ │  │   5:00 duration    │  │   Unable to load   │  │   4:15 duration    │  │   6:00 duration   ││ │
│ │  │   1,842 events     │  │   scenario file.   │  │   967 events       │  │   5,411 events    ││ │
│ │  │   #arrival #peak   │  │   [ Retry ]        │  │   #bottleneck      │  │   #emergency      ││ │
│ │  └────────────────────┘  └────────────────────┘  └────────────────────┘  └──────────────────┘│ │
│ │                                                                                              │ │
│ └──────────────────────────────────────────────────────────────────────────────────────────────┘ │
```

---

## Screen 5: Mode Switcher Dropdown

**Purpose**: Let technical users switch between data sources (Mock/Replay/Live/Mesh) while maintaining honest provenance labeling visible at all times.

**Primary actions**:
1. Select a data mode
2. Understand availability of each mode (green dot = ready, gray = unavailable)

### Layout -- Open State

```
                            ┌──────────┐
                            │ ● MOCK   │ (clicked)
                            └──────────┘
                            ┌──────────────────────────────────┐
                            │                                  │
                            │  ● Mock                     ✓    │
                            │    Simulated data, seeded RNG    │
                            │  ──────────────────────────────  │
                            │  ◉ Replay                        │
                            │    Recorded scenario playback    │
                            │  ──────────────────────────────  │
                            │  ○ Live                (no hw)   │
                            │    Real-time BLE/WiFi sensors    │
                            │  ──────────────────────────────  │
                            │  ○ Mesh                (no gw)   │
                            │    Meshtastic mesh network       │
                            │                                  │
                            └──────────────────────────────────┘

                            Legend:
                            ● = active     ◉ = available
                            ○ = unavailable (greyed, with reason)
```

### State Variant: Hovering Disabled (Live Unavailable)

```
                            ┌──────────────────────────────────┐
                            │                                  │
                            │  ● Mock                     ✓    │
                            │    Simulated data, seeded RNG    │
                            │  ──────────────────────────────  │
                            │  ◉ Replay                        │
                            │    Recorded scenario playback    │
                            │  ──────────────────────────────  │
                            │ ┌──────────────────────────────┐ │
                            │ │ ○ Live          (unavailable)│ │
                            │ │   No sensors detected.       │ │
                            │ │   Connect BLE/WiFi hardware  │ │
                            │ │   to enable Live mode.       │ │
                            │ └──────────────────────────────┘ │
                            │  ──────────────────────────────  │
                            │  ○ Mesh                (no gw)   │
                            │    Meshtastic mesh network       │
                            │                                  │
                            └──────────────────────────────────┘
```

**Mode color tokens** (per LC-2):
- Mock: `blue-500` pill
- Replay: `amber-500` pill
- Live: `green-500` pill
- Mesh: `purple-500` pill

---

## Screen 6: Alerts Panel (Always Visible, Right Rail)

**Purpose**: Surface zone-level crowd events with severity badges so operators and judges can see the system is intelligent and responsive, not just a static display.

**Primary actions**:
1. Scan active alerts by severity (critical > warn > info)
2. Click an alert to highlight its zone on the heatmap
3. Acknowledge an alert to mark it handled

### Layout -- Populated (Multiple Alerts)

```
┌────────────────────────────────────┐
│  ALERTS                  2 active  │
├────────────────────────────────────┤
│                                    │
│  ▲▲ CRITICAL  Hall A evacuation   │
│     threshold exceeded             │
│     Zone A  ·  14:33:01            │
│     [ Acknowledge ]  [ View zone ] │
│                                    │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│                                    │
│  ▲ WARN  Hall B at 85% capacity   │
│    Zone B  ·  14:31:42             │
│    [ Acknowledge ]  [ View zone ]  │
│                                    │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│                                    │
│  ● INFO  Replay scenario loaded    │
│    System  ·  14:30:12  ✓ ack'd    │
│                                    │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  1 active, 1 acknowledged          │
│                                    │
└────────────────────────────────────┘
```

### State Variant: Empty

```
┌────────────────────────────────────┐
│  ALERTS                  0 active  │
├────────────────────────────────────┤
│                                    │
│                                    │
│     No active alerts --            │
│     system nominal.                │
│                                    │
│     Monitoring 6 zones             │
│     across 8 sensors.              │
│                                    │
│                                    │
└────────────────────────────────────┘
```

### State Variant: Toast Emerging (Critical Alert)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ╔════════════════════════════════════════════════════════════════════════════════╗               │
│  ║  ▲▲ CRITICAL  Hall A evacuation threshold exceeded     [ View ]  [ Dismiss ] ║               │
│  ║     Zone A  ·  14:33:01                                  auto-dismiss in 6s  ║               │
│  ╚════════════════════════════════════════════════════════════════════════════════╝               │
│                                                                                                  │
│                (toast appears above main content, auto-dismisses after 6s)                       │
│                                                                                                  │
```

### State Variant: Post-Acknowledge

```
┌────────────────────────────────────┐
│  ALERTS                  1 active  │
├────────────────────────────────────┤
│                                    │
│  ▲ WARN  Hall B at 85% capacity   │
│    Zone B  ·  14:31:42             │
│    [ Acknowledge ]  [ View zone ]  │
│                                    │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  ACKNOWLEDGED                      │
│                                    │
│  ✓ CRITICAL  Hall A evacuation     │
│    Zone A  ·  14:33:01  (greyed)   │
│    ack'd 14:33:15                  │
│                                    │
│  ✓ INFO  Replay scenario loaded    │
│    System  ·  14:30:12  (greyed)   │
│    ack'd 14:30:14                  │
│                                    │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  1 active, 2 acknowledged          │
│                                    │
└────────────────────────────────────┘
```

---

## Screen 7: Demo Reset Confirmation

**Purpose**: Allow developers to restart the demo timeline without page reload, with confirmation severity appropriate to the active mode.

**Primary actions**:
1. Trigger reset via `R` key or header reset icon
2. Confirm (for Live/Mesh) or auto-proceed (for Mock/Replay)

### Layout -- Toast (Mock / Replay Mode)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│     ┌────────────────────────────────────────────────────────────┐                               │
│     │  ↺  Demo timeline reset to t=0.  Alerts cleared.          │                               │
│     │     Auto-dismiss in 2s...                                  │                               │
│     └────────────────────────────────────────────────────────────┘                               │
│                                                                                                  │
│     (toast appears top-center, auto-dismiss 2s, heatmap fades to t=0 in 400ms)                  │
│                                                                                                  │
```

### Layout -- Modal (Live / Mesh Mode)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                  │
│                         ┌──────────────────────────────────────────┐                             │
│                         │                                          │                             │
│                         │  ⚠  Reset in Live Mode                  │                             │
│                         │                                          │                             │
│                         │  Resetting will disconnect active        │                             │
│                         │  sensor streams. Live data will be       │                             │
│                         │  interrupted until sensors reconnect.    │                             │
│                         │                                          │                             │
│                         │  Estimated reconnection: ~5-10 seconds   │                             │
│                         │                                          │                             │
│                         │        [ Cancel ]    [ Reset anyway ]    │                             │
│                         │                                          │                             │
│                         └──────────────────────────────────────────┘                             │
│                                                                                                  │
│     (modal with backdrop overlay, focus-trapped, Esc = Cancel)                                  │
│                                                                                                  │
```

### State Variant: Pending (Waiting for User)

```
│                         │        [ Cancel ]    [ Reset anyway ]    │
```

### State Variant: Confirmed / In-Progress

```
│                         │  ↺  Resetting...                         │
│                         │  ████████████░░░░░░░░                    │
│                         │  Disconnecting sensors...                │
```

### State Variant: Success

```
│                         │  ✓  Reset complete.                      │
│                         │     Mock timeline at t=0.                │
│                         │     Auto-closing in 1s...                │
```

---

## Pencil Note

If desired, the `pencil` MCP tool could render this as a .pen file at `.lev/ux/20260514-101706-deadzone-mvp-crowd-intel/wireframes.pen` for higher-fidelity visual output with proper box rendering and spatial layout.

---

## Key Non-Obvious Choices

| Decision | Rationale | Research Source |
|---|---|---|
| **Headline metrics bar above heatmap, not overlaid** | Operators need numeric readout (capacity %, trend arrow) without parsing gradients. Placing it in a dedicated bar ensures it is always visible above the fold regardless of zoom level. | C5 ("headline metrics beat gradients" -- Dana, Maria, Tomasz, Kenji), C1 (legend + units requirement) |
| **Mode chip in header center, not sidebar** | Auto-selects best available mode on load (Spectators never touch it), but is prominent enough for Investigators to find within 3 seconds. Balances D1 tension between "hide modes" and "modes are a feature." | D1 (Dana+Maria vs Raj+Tomasz), D4 (provenance labeling), LC-2 |
| **Topology as toggle overlay, not separate page** | Keeps single-screen model intact. Spectators never see it; Investigators toggle it in one click. Diagonal hatch pattern for coverage gaps uses shape, not just color absence. | D2 (Dana: "skip it" vs Raj: "proof of engineering"), AP-4 (color-only encoding risk), LC-5 |
| **Alerts panel always visible in right rail** | Guarantees that timed alerts (90s in Mock mode) are visible without user action, proving system intelligence to judges. Empty state shows "system nominal" message, never blank. | C3 (alert must fire in 5min), C4 (empty = broken), LC-3, LC-4 |
| **Three-state (loading/empty/populated) for every panel** | Every persona interpreted blank panels as crashes. Skeleton loading states give confidence that the system is working; zero-state messages explain what is expected. | C4 (all 5 personas), LC-3 |
| **Toast for Mock/Replay reset, modal for Live/Mesh reset** | Mock/Replay resets are non-destructive (deterministic replay restarts). Live/Mesh resets disconnect real hardware, requiring explicit confirmation. Matches D5 tension between seamless fallback and explicit failure. | D5 (Kenji: seamless vs Tomasz: explicit), AP-1 (demo reset anxiety), E1 |
| **Viridis palette with pattern overlay at critical thresholds** | Avoids red-green-only encoding (8% male color-blind population). Pattern overlay (hatching) at critical capacity provides a second visual channel beyond color gradient. | E3 (Maria's colorblind assistant), AP-4, LC-5, C1 |
| **Right-side slide-in panel for zone detail (not bottom sheet)** | At 1440x900, a right panel preserves full heatmap height (critical for spatial orientation). Bottom sheets obscure the map on landscape displays. Panel width is ~40% of viewport, leaving 60% for heatmap context. | C5 (numbers above the fold), job-3 (zone occupancy without leaving ops room) |
| **Replay drawer slides up from bottom, not right rail** | Replay controls (scrubber, speed, scenario cards) are temporally oriented and benefit from full-width layout. The scrubber is unusable in a narrow right rail. This also avoids conflicting with Zone Detail or Topology panels that use the right rail. | AP-5 (replay as dual-use: demo + testing), job-4 (deterministic playback) |
| **Coverage gap hatching instead of just color absence** | Absence of heatmap color in a zone could mean "no people" or "no sensor coverage" -- ambiguous. Diagonal hatch pattern explicitly marks uncovered areas, giving operators actionable information about blind spots. | D2, E3, LC-5, job-5 (validate coverage gaps) |
