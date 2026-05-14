import { useEffect, useState } from "react";
import { HeatmapDashboard } from "./components/HeatmapDashboard";

type Mode = "mock" | "replay" | "live" | "mesh";

interface Zone {
  id: string;
  name: string;
  count: number;
  capacity: number;
  trend_5m: string;
}

interface Headline {
  total: number;
  capacity_pct: number;
  peak_zone: string;
  trend: string;
}

interface AggregateFrame {
  timestamp: number;
  mode: Mode;
  venue_id: string;
  zones: Zone[];
  headline: Headline;
}

interface CaptureStatus {
  active: boolean;
  trace_id: string | null;
  observations: number;
  backend: "ble";
  disabled_reason: string | null;
  started_at: string | null;
  latest_observation_at: string | null;
}

export default function App() {
  const [frame, setFrame] = useState<AggregateFrame | null>(null);
  const [connected, setConnected] = useState(false);
  const [capture, setCapture] = useState<CaptureStatus | null>(null);
  const [captureBusy, setCaptureBusy] = useState(false);
  const [captureError, setCaptureError] = useState<string | null>(null);

  useEffect(() => {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${proto}//${location.host}/ws/events`);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      try {
        setFrame(JSON.parse(e.data));
      } catch {
        // skip malformed frame
      }
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    refreshCapture();
    const timer = window.setInterval(refreshCapture, 2000);
    return () => window.clearInterval(timer);
  }, []);

  async function refreshCapture() {
    try {
      const response = await fetch("/api/v1/capture/status");
      if (!response.ok) throw new Error(`Capture status failed (${response.status})`);
      setCapture(await response.json());
      setCaptureError(null);
    } catch (error) {
      setCaptureError(error instanceof Error ? error.message : "Capture status unavailable");
    }
  }

  async function startCapture() {
    setCaptureBusy(true);
    setCaptureError(null);
    try {
      const response = await fetch("/api/v1/capture/start", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({}),
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.disabled_reason ?? body.message ?? "Bluetooth scan could not start");
      }
      setCapture(body);
    } catch (error) {
      setCaptureError(error instanceof Error ? error.message : "Bluetooth scan could not start");
    } finally {
      setCaptureBusy(false);
    }
  }

  async function stopCapture() {
    setCaptureBusy(true);
    setCaptureError(null);
    try {
      const response = await fetch("/api/v1/capture/stop", { method: "POST" });
      if (!response.ok) throw new Error(`Stop scan failed (${response.status})`);
      setCapture(await response.json());
    } catch (error) {
      setCaptureError(error instanceof Error ? error.message : "Bluetooth scan could not stop");
    } finally {
      setCaptureBusy(false);
    }
  }

  return (
    <HeatmapDashboard
      frame={frame}
      connected={connected}
      capture={capture}
      captureBusy={captureBusy}
      captureError={captureError}
      onStartCapture={startCapture}
      onStopCapture={stopCapture}
    />
  );
}
