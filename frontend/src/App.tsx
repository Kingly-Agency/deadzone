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

export default function App() {
  const [frame, setFrame] = useState<AggregateFrame | null>(null);
  const [connected, setConnected] = useState(false);

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

  return <HeatmapDashboard frame={frame} connected={connected} />;
}
