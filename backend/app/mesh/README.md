# DeadZone Mesh (WiFi-faked)

Standalone satellite FastAPI service (port 8001) that lets two laptops simulate a Meshtastic mesh network over plain WiFi. Each laptop runs an independent BLE scanner and posts zone-aggregate packets to a shared gateway at 1 Hz. No LoRa hardware required. The honest demo claim: **mesh transport simulated via WiFi; sensing is real BLE on two independent nodes.** This exists so hackathon judges can see distributed multi-node sensing today, while the packet shape stays forward-compatible with real Meshtastic hardware later.

## Quick Start -- Two-Laptop Test (1-click via UI)

Both laptops need the repo cloned and the backend dependencies installed once.

### Pre-flight (one-time per laptop)

```bash
git clone https://github.com/Kingly-Agency/deadzone.git
cd deadzone/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### Run the demo

**Both laptops**, in three separate terminals each:

```bash
# Terminal 1: mesh satellite (gateway + UDP discovery)
cd deadzone/backend && source .venv/bin/activate
python -m app.mesh satellite

# Terminal 2: main backend (BLE capture + dashboard data)
cd deadzone/backend && source .venv/bin/activate
uvicorn app.main:app --port 8000  # or whatever the BE agent wires

# Terminal 3: frontend
cd deadzone/frontend
npm install && npm run dev
```

Open `http://localhost:3000` on each laptop.

### 1-click join flow

- **Your laptop** (the host): Sidebar -> **Mesh** -> click **Host Mesh**. Status shows "Hosting" with your laptop already counted as 1 node.
- **Partner's laptop**: Sidebar -> **Mesh** -> wait ~3s. Your gateway appears in **Discovered**. Click **Join** next to it. Done.
- Verify on either laptop: GET `/mesh/state` shows 2 nodes, merged zones with both contributing.

### If discovery doesn't work

UDP broadcast can be blocked by:
- macOS Firewall (System Settings -> Network -> Firewall -> Off, or allow Python)
- Enterprise / public WiFi with client isolation
- Different subnets

**Fallback: paste the gateway URL manually.** The Mesh panel has a "Paste URL" field. Find your gateway's LAN IP on the hosting laptop:

```bash
ipconfig getifaddr en0   # macOS WiFi
ip addr | grep "inet "   # Linux
```

Paste `http://<that-ip>:8001` into the field on the partner's UI and click Join.

## Architecture

- **N nodes + 1 gateway.** Pure HTTP POST at 1 Hz with aggregate packets.
- **Aggregate-only across the wire.** No raw BLE MAC, no `beacon_hash`, no RSSI samples.
- **Stdlib HTTP transport** (`urllib.request`). No new dependencies beyond FastAPI/uvicorn.
- **Standalone FastAPI app on port 8001**, separate from the main DeadZone backend on port 8000.
- **Zero coupling.** No imports from `app.main`, `app.runtime`, `app.api`, `app.sources`, or `app.spatial`.

## Why "WiFi-faked"?

Real Meshtastic uses LoRa radios (ESP32 boards, ~$30-50 each). That is not realistic before demo day. WiFi-faked mesh proves the **topology, merge math, and dashboard integration** today. The same packet shape (`deadzone.mesh.aggregate.v1`) and gateway contract are forward-compatible with swapping the `urllib` transport for the `meshtastic` Python SDK later.

Be honest in the demo: the badge should say **`MESH (WiFi)`** not `MESH (LoRa)`.

## CLI (Advanced)

The UI is built on these CLI commands. They're stable and supported for scripting / headless demos:

### `satellite` (recommended)

All-in-one: gateway + UDP beacon broadcaster + listener. The UI drives lifecycle via HTTP.

```bash
python -m app.mesh satellite [--port 8001] [--beacon-port 8002] [--gateway-id NAME] [--no-discovery]
```

### `gateway` (advanced)

Gateway-only (no discovery beacons). Useful if you want to run multiple gateways on one host for testing.

```bash
python -m app.mesh gateway --port 8001 [--gateway-id NAME]
```

### `node` (advanced)

Standalone node that POSTs aggregates to a known gateway URL. Bypasses the UI and the satellite's runtime; useful for headless multi-node demos.

```bash
python -m app.mesh node --gateway http://HOST:8001 --node-id NAME [--interval 1.0] [--position X Y] [--seed 1337]
```

## Endpoints

All endpoints are under the `/mesh` prefix.

| Method | Path | Purpose |
|---|---|---|
| GET | /mesh/healthz | Liveness + node_count |
| POST | /mesh/aggregate | Receive a node's aggregate packet |
| GET | /mesh/state | Full MeshSnapshot (merged zones, mesh links, sensors) |
| GET | /mesh/nodes | List of NodeState |
| POST | /mesh/host | Become a gateway (auto-joins self) |
| POST | /mesh/unhost | Stop hosting |
| POST | /mesh/join | Start a node coroutine pointing at a remote gateway |
| POST | /mesh/leave | Cancel the node coroutine |
| GET | /mesh/me | Current role + status |
| GET | /mesh/discover | Recently-heard peer gateways |

## Packet shape

Wire format for `POST /mesh/aggregate`. The `schema` field is always `deadzone.mesh.aggregate.v1`.

```json
{
  "schema": "deadzone.mesh.aggregate.v1",
  "node_id": "laptop-A",
  "position": { "x": 1.0, "y": 2.5 },
  "timestamp": "2026-05-14T22:01:02.123Z",
  "uptime_s": 37.2,
  "zones": [
    {
      "zone_id": "near-scanner",
      "estimated_devices": 12,
      "density": 0.48,
      "trend": "rising",
      "confidence": 0.35
    },
    {
      "zone_id": "mid-field",
      "estimated_devices": 7,
      "density": 0.29,
      "trend": "stable",
      "confidence": 0.35
    }
  ],
  "freshness": "live",
  "scanner_kind": "ble",
  "scanner_status": "online"
}
```

Note: `schema` is the JSON key; the Pydantic field name is `schema_id` (aliased to avoid shadowing Python's `schema` builtin).

## Beacon shape

```json
{
  "schema": "deadzone.mesh.beacon.v1",
  "gateway_id": "main-gateway",
  "gateway_url": "http://10.0.0.7:8001",
  "version": "0.1.0",
  "broadcast_at": "2026-05-14T18:45:00Z"
}
```

UDP, port 8002 by default, broadcast to 255.255.255.255, every 3 seconds. Listener TTL: 30s.

## Privacy model

**What NEVER leaves a node:**
- Raw BLE MAC addresses from scanned devices
- `beacon_hash` (the salted per-device token used for local dedup)
- RSSI samples or raw signal-strength readings
- Trace JSONL files or raw scan event logs
- The node's local privacy salt

**What DOES leave a node (aggregate-only):**
- Per-zone estimated device counts
- Per-zone density and trend
- Per-zone confidence score
- Node metadata: `node_id`, `uptime_s`, `scanner_kind`, `scanner_status`
- Self-assessed `freshness`

Each node generates a random privacy salt at startup, used to hash raw BLE MACs into `beacon_hash` tokens for local deduplication. The salt never leaves the node process.

## Merge rules

The gateway merges zone data across all nodes with `status == "live"`:

| Field               | Strategy       | Details                                                              |
|---------------------|----------------|----------------------------------------------------------------------|
| `estimated_devices` | **SUM**        | Assumes each node sees a non-overlapping device cohort               |
| `density`           | **MAX**        | Highest density reported by any contributing node                    |
| `trend`             | **Majority vote** | Ties broken by urgency: `spiking > rising > falling > stable`     |
| `confidence`        | **MIN**        | Conservative -- takes the lowest confidence across contributing nodes |

**Node lifecycle:**
- **live** -- packet received within the last 3 seconds
- **stale** -- no packet for 3-10 seconds; node shown but degraded
- **offline** -- no packet for 10+ seconds; excluded from merge inputs

**Mesh links:** two nodes are linked if both report the same `zone_id` within a 2-second window. Links expire after the window passes with no co-observation.

## Failure modes

| Scenario            | Behavior                                                                                             |
|---------------------|------------------------------------------------------------------------------------------------------|
| **Gateway down**    | Node buffers up to 60 packets (oldest evicted). Drains buffer oldest-first when gateway returns.     |
| **Node down**       | Gateway marks stale after 3s, offline after 10s. Dashboard shows degraded ring.                      |
| **Clock skew**      | Gateway uses receive-time for ordering; node timestamp stored for diagnostics only.                  |
| **Different subnets** | HTTP POST fails. Use explicit IP for `--gateway`. Put both laptops on the same WiFi or hotspot.    |
| **Beacon discovery fails** | UDP blocked by firewall or client isolation. Use the Paste URL fallback in the UI.            |

## Out of scope

- Real Meshtastic LoRa hardware integration
- Wiring mesh state into `/api/v1/snapshot` of the main backend (separate BE task)
- Frontend changes -- FE can call `/mesh/state` directly or via proxy
- Auth, HTTPS, encryption -- LAN demo only

## Troubleshooting

| Error                               | Fix                                                                    |
|--------------------------------------|------------------------------------------------------------------------|
| `Gateway unreachable`                | Check LAN IP, check firewall, `ping <gateway-ip>`                     |
| `Connection refused on 8001`         | Gateway not running, or wrong host in the URL                          |
| `BLE permission denied (macOS)`      | System Settings > Privacy & Security > Bluetooth > enable Terminal/iTerm |
| Different counts on two nodes        | Each node sees a non-overlapping cohort; SUM is naive but acceptable for MVP |
| Discovered list is empty on partner's laptop | UDP blocked. Use the Paste URL fallback in the UI. Or try a phone hotspot. |
| POST /mesh/join returns 400         | gateway_url is malformed. Use the exact `http://IP:8001` shape.        |
