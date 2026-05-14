/* DeadZone API client */

const BASE = "";

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`GET ${path}: ${r.status}`);
  return r.json();
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!r.ok) throw new Error(`POST ${path}: ${r.status}`);
  return r.json();
}

import type {
  AppConfig,
  CaptureStatus,
  IntelligenceSnapshot,
  RawSensorEvent,
  ReplayScenario,
  StreamState,
  ZoneAggregate,
  SensorNode,
} from "./types";

export const api = {
  config:          ()                                      => get<AppConfig>("/api/v1/config"),
  snapshot:        ()                                      => get<IntelligenceSnapshot>("/api/v1/snapshot"),
  zones:           ()                                      => get<ZoneAggregate[]>("/api/v1/zones"),
  zone:            (id: string)                            => get<ZoneAggregate>(`/api/v1/zones/${id}`),
  sensors:         ()                                      => get<SensorNode[]>("/api/v1/sensors"),
  sensorEvents:    (id: string)                            => get<RawSensorEvent[]>(`/api/v1/sensors/${id}/events`),
  replayScenarios: ()                                      => get<ReplayScenario[]>("/api/v1/replay/scenarios"),
  replayControl:   (body: Record<string, unknown>)         => post<StreamState>("/api/v1/replay/control", body),
  switchMode:      (mode: string)                          => post<StreamState>("/api/v1/mode", { mode }),
  reset:           ()                                      => post<IntelligenceSnapshot>("/api/v1/demo/reset"),
  captureStatus:   ()                                      => get<CaptureStatus>("/api/v1/capture/status"),
  startCapture:    ()                                      => post<CaptureStatus>("/api/v1/capture/start", {}),
  stopCapture:     ()                                      => post<CaptureStatus>("/api/v1/capture/stop"),
};
