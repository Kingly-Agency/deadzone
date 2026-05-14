/**
 * Typed client for the DeadZone mesh satellite (port 8001 via /mesh proxy).
 *
 * Endpoints used:
 *   GET  /mesh/me             current role + status
 *   GET  /mesh/state          full MeshSnapshot
 *   GET  /mesh/nodes          list of NodeState
 *   GET  /mesh/discover       recently-heard peer gateways
 *   GET  /mesh/healthz        liveness
 *   POST /mesh/host           become a gateway (auto-self-joins)
 *   POST /mesh/unhost         stop hosting
 *   POST /mesh/join           start node coroutine pointed at remote gateway
 *   POST /mesh/leave          stop the node coroutine
 */

export type MeshRole = "idle" | "hosting" | "joined" | "hosting_and_joined";
export type Trend = "falling" | "stable" | "rising" | "spiking";
export type NodeStatus = "live" | "stale" | "offline";

export interface MeRoleResponse {
  role: MeshRole;
  hosting: boolean;
  beacon_active: boolean;
  joined: boolean;
  joined_url: string | null;
  joined_gateway_id: string | null;
  node_id: string | null;
  packets_sent: number;
  buffered: number;
  gateway_id: string;
  listening: boolean;
  discovered_peer_count: number;
}

export interface DiscoveredGateway {
  gateway_id: string;
  gateway_url: string;
  version: string;
  last_seen_s_ago: number;
  first_seen: string; // ISO8601
  beacon_count: number;
  is_self: boolean;
}

export interface NodeStateResponse {
  node_id: string;
  status: NodeStatus;
  position: { x: number; y: number } | null;
  last_seen: string;
  latency_ms: number | null;
  packets_received: number;
  scanner_kind: "ble" | "wifi";
  scanner_status: "online" | "degraded" | "offline" | "adapter_disabled";
  last_freshness: "live" | "fresh" | "stale" | "offline";
}

export interface MergedZone {
  zone_id: string;
  estimated_devices: number;
  density: number;
  trend: Trend;
  confidence: number;
  contributing_nodes: string[];
}

export interface MeshLink {
  source_node: string;
  target_node: string;
  shared_zones: string[];
  inferred_at: string;
}

export interface MeshSnapshot {
  gateway_id: string;
  updated_at: string;
  uptime_s: number;
  nodes: NodeStateResponse[];
  zones_merged: MergedZone[];
  mesh_links: MeshLink[];
  metrics: Record<string, number>;
}

export interface GatewayHealth {
  ok: boolean;
  gateway_id: string;
  uptime_s: number;
  node_count: number;
}

export interface JoinRequest {
  gateway_url: string;
  node_id?: string | null;
  position?: [number, number] | null;
  scanner?: "mock";
  seed?: number;
}

export interface HostRequest {
  gateway_id?: string | null;
  beacon?: boolean;
}

export class MeshClientError extends Error {
  status: number;
  body: unknown;
  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      ...init,
      headers: {
        "content-type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch (err) {
    throw new MeshClientError(
      err instanceof Error ? err.message : "network error",
      0,
      null,
    );
  }
  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    const message =
      typeof body === "object" &&
      body &&
      "detail" in body &&
      typeof (body as { detail: unknown }).detail === "string"
        ? (body as { detail: string }).detail
        : `mesh request failed (${response.status})`;
    throw new MeshClientError(message, response.status, body);
  }
  return body as T;
}

export const meshClient = {
  // Reads
  health: () => fetchJson<GatewayHealth>("/mesh/healthz"),
  me: () => fetchJson<MeRoleResponse>("/mesh/me"),
  state: () => fetchJson<MeshSnapshot>("/mesh/state"),
  nodes: () => fetchJson<NodeStateResponse[]>("/mesh/nodes"),
  discover: () => fetchJson<DiscoveredGateway[]>("/mesh/discover"),

  // Writes
  host: (req: HostRequest = {}) =>
    fetchJson<MeRoleResponse>("/mesh/host", {
      method: "POST",
      body: JSON.stringify(req),
    }),
  unhost: () =>
    fetchJson<MeRoleResponse>("/mesh/unhost", {
      method: "POST",
      body: "{}",
    }),
  join: (req: JoinRequest) =>
    fetchJson<MeRoleResponse>("/mesh/join", {
      method: "POST",
      body: JSON.stringify(req),
    }),
  leave: () =>
    fetchJson<MeRoleResponse>("/mesh/leave", {
      method: "POST",
      body: "{}",
    }),
};

export default meshClient;
