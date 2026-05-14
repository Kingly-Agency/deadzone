# DeadZone Mesh (WiFi-faked)

Standalone satellite FastAPI service (port 8001) that lets two laptops simulate a Meshtastic mesh network over plain WiFi. Each laptop runs an independent BLE scanner and posts zone-aggregate packets to a shared gateway at 1 Hz. No LoRa hardware required. The honest demo claim: **mesh transport simulated via WiFi; sensing is real BLE on two independent nodes.** This exists so hackathon judges can see distributed multi-node sensing today, while the packet shape stays forward-compatible with real Meshtastic hardware later.

## Quick Start -- Two-Laptop Test

Total setup time: under 10 minutes.

```
┌──────────────┐  HTTP POST /mesh/aggregate  ┌──────────────────┐
│  Node A       │ ──────────────────────────▶ │  Gateway         │
│  (laptop 1)   │                             │  (laptop 1)      │
│  BLE scanner  │                             │  FastAPI :8001   │
└──────────────┘                             │                  │
┌──────────────┐  HTTP POST /mesh/aggregate  │  ┌────────────┐  │
│  Node B       │ ──────────────────────────▶ │  │ MergeEngine│  │
│  (laptop 2)   │                             │  └────────────┘  │
│  BLE scanner  │                             └──────────────────┘
```

1. **Pick the gateway laptop.** Any one of the two.

2. **Find the gateway laptop's LAN IP:**
   ```bash
   # macOS
   ipconfig getifaddr en0
   # Linux
   ip addr show | grep 'inet ' | grep -v 127.0.0.1
   ```

3. **Start the gateway** (on the gateway laptop, from `deadzone/backend/`):
   ```bash
   uvicorn app.mesh.app:app --host 0.0.0.0 --port 8001
   ```

4. **Verify the gateway is up:**
   ```bash
   curl http://localhost:8001/mesh/healthz
   # {"ok":true,"gateway_id":"mesh-gateway-local","uptime_s":1.2,"node_count":0}
   ```

5. **Start a node on each laptop** (including the gateway laptop), from `deadzone/backend/`:
   ```bash
   # Gateway laptop
   python -c "import asyncio; from app.mesh.node import MeshNode, MockNodeScanner; from app.mesh.transport import AggregateClient; asyncio.run(MeshNode(node_id='laptop-A', client=AggregateClient('http://localhost:8001'), scanner=MockNodeScanner()).run())"

   # Partner's laptop (replace <gateway-lan-ip>)
   python -c "import asyncio; from app.mesh.node import MeshNode, MockNodeScanner; from app.mesh.transport import AggregateClient; asyncio.run(MeshNode(node_id='laptop-B', client=AggregateClient('http://<gateway-lan-ip>:8001'), scanner=MockNodeScanner()).run())"
   ```

6. **Check mesh state** from either machine:
   ```bash
   curl http://<gateway-ip>:8001/mesh/state | jq
   # Should show 2 nodes with merged zones
   ```

## Architecture

- **N nodes + 1 gateway.** Pure HTTP POST at 1 Hz with aggregate packets.
- **Aggregate-only across the wire.** No raw BLE MAC, no `beacon_hash`, no RSSI samples.
- **Stdlib HTTP transport** (`urllib.request`). No new dependencies beyond FastAPI/uvicorn.
- **Standalone FastAPI app on port 8001**, separate from the main DeadZone backend on port 8000.
- **Zero coupling.** No imports from `app.main`, `app.runtime`, `app.api`, `app.sources`, or `app.spatial`.

## Why "WiFi-faked"?

Real Meshtastic uses LoRa radios (ESP32 boards, ~$30-50 each). That is not realistic before demo day. WiFi-faked mesh proves the **topology, merge math, and dashboard integration** today. The same packet shape (`deadzone.mesh.aggregate.v1`) and gateway contract are forward-compatible with swapping the `urllib` transport for the `meshtastic` Python SDK later.

Be honest in the demo: the badge should say **`MESH (WiFi)`** not `MESH (LoRa)`.

## CLI

No `__main__.py` exists yet. Run the gateway via `uvicorn` and nodes via Python:

```bash
# Gateway
uvicorn app.mesh.app:app --host 0.0.0.0 --port 8001

# Node (mock scanner, from deadzone/backend/)
python -c "
import asyncio; from app.mesh.node import MeshNode, MockNodeScanner; from app.mesh.transport import AggregateClient
asyncio.run(MeshNode(node_id='my-node', client=AggregateClient('http://<host>:8001'), scanner=MockNodeScanner(seed=1337)).run())
"
```

Key constructor parameters: `MeshNode(node_id, client, scanner, interval_s=1.0, position=None)` and `AggregateClient(gateway_url, timeout_s=2.0, buffer_size=60)`.

## Endpoints

All endpoints are under the `/mesh` prefix.

### `GET /mesh/healthz`

Gateway liveness. Returns `GatewayHealth`: `{"ok": true, "gateway_id": "...", "uptime_s": 42.3, "node_count": 2}`. Status: **200**.

### `POST /mesh/aggregate`

Ingest one aggregate packet from a node. Request body: `AggregatePacket` (see [Packet shape](#packet-shape)). Response `AggregateAccepted`:
```json
{"accepted": true, "last_seq": 17, "node_id": "laptop-A", "received_at": "2026-05-14T22:01:03.456Z"}
```
Status: **200** accepted, **400** malformed, **422** Pydantic validation error.

### `GET /mesh/state`

Full merged mesh snapshot. Returns `MeshSnapshot` with fields: `gateway_id`, `updated_at`, `uptime_s`, `nodes` (list of `NodeState`), `zones_merged` (list of `MergedZone`), `mesh_links` (list of `MeshLink`), and `metrics` dict (`node_count`, `live_count`, `stale_count`, `offline_count`, `total_estimated_devices`, `merged_zone_count`, `mesh_link_count`). Status: **200**.

### `GET /mesh/nodes`

List all known nodes with lifecycle status. Returns `list[NodeState]` -- each entry has: `node_id`, `status` (`live`|`stale`|`offline`), `position`, `last_seen`, `latency_ms`, `packets_received`, `scanner_kind`, `scanner_status`, `last_freshness`. Status: **200**.

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

## Out of scope

- Real Meshtastic LoRa hardware integration
- Wiring mesh state into `/api/v1/snapshot` of the main backend (separate BE task)
- Frontend changes -- FE can call `/mesh/state` directly or via proxy
- Auth, HTTPS, encryption -- LAN demo only

## Pre-flight checklist for the partner

- [ ] Same WiFi network as the gateway laptop
- [ ] Firewall allows inbound TCP 8001 on the gateway laptop
- [ ] `pip install -e '.[sensors]'` from `backend/` if using real BLE scanner
- [ ] macOS Bluetooth permission granted to the terminal app

## Troubleshooting

| Error                               | Fix                                                                    |
|--------------------------------------|------------------------------------------------------------------------|
| `Gateway unreachable`                | Check LAN IP, check firewall, `ping <gateway-ip>`                     |
| `Connection refused on 8001`         | Gateway not running, or wrong host in the URL                          |
| `BLE permission denied (macOS)`      | System Settings > Privacy & Security > Bluetooth > enable Terminal/iTerm |
| Different counts on two nodes        | Each node sees a non-overlapping cohort; SUM is naive but acceptable for MVP |
