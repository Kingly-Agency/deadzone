/* DeadZone stream store — React context for snapshot, config, and WebSocket state. */

import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { api } from "./api";
import type {
  AppConfig,
  IntelligenceSnapshot,
  StreamEnvelope,
  Mode,
} from "./types";

// ── Store shape ─────────────────────────────────────────────────────────

interface StoreState {
  config: AppConfig | null;
  snapshot: IntelligenceSnapshot | null;
  connected: boolean;
  sequence: number;
  error: string | null;
  acknowledgedAlerts: Set<string>;
}

interface StoreActions {
  switchMode: (mode: Mode) => Promise<void>;
  reset: () => Promise<void>;
  acknowledgeAlert: (id: string) => void;
}

type Store = StoreState & StoreActions;

const StoreCtx = createContext<Store | null>(null);

export function useStore(): Store {
  const s = useContext(StoreCtx);
  if (!s) throw new Error("useStore must be inside <StoreProvider>");
  return s;
}

// ── Provider ────────────────────────────────────────────────────────────

export function StoreProvider({ children }: { children: ReactNode }) {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [snapshot, setSnapshot] = useState<IntelligenceSnapshot | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [acknowledgedAlerts, setAcknowledgedAlerts] = useState<Set<string>>(new Set());
  const seqRef = useRef(0);
  const wsRef = useRef<WebSocket | null>(null);

  // ── Startup sequence: config → snapshot → WebSocket ───────────────
  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const cfg = await api.config();
        if (cancelled) return;
        setConfig(cfg);

        const snap = await api.snapshot();
        if (cancelled) return;
        setSnapshot(snap);
        seqRef.current = snap.stream.sequence;
      } catch (e) {
        if (!cancelled) setError(String(e));
      }

      // Open WebSocket
      if (!cancelled) connectWs();
    })();

    return () => {
      cancelled = true;
      wsRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function connectWs() {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${proto}//${location.host}/ws/live`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      // Auto-reconnect after 3s
      setTimeout(() => connectWs(), 3000);
    };
    ws.onerror = () => setConnected(false);

    ws.onmessage = (e) => {
      try {
        const env: StreamEnvelope = JSON.parse(e.data);
        // Sequence-aware: ignore out-of-order messages
        if (env.sequence <= seqRef.current) return;
        seqRef.current = env.sequence;

        if (env.type === "snapshot" && env.payload) {
          setSnapshot(env.payload);
        }
      } catch {
        // skip malformed
      }
    };
  }

  const switchMode = useCallback(async (mode: Mode) => {
    try {
      await api.switchMode(mode);
      const snap = await api.snapshot();
      setSnapshot(snap);
      const cfg = await api.config();
      setConfig(cfg);
    } catch (e) {
      setError(String(e));
    }
  }, []);

  const reset = useCallback(async () => {
    try {
      const snap = await api.reset();
      setSnapshot(snap);
      seqRef.current = snap.stream.sequence;
      setAcknowledgedAlerts(new Set());
    } catch (e) {
      setError(String(e));
    }
  }, []);

  const acknowledgeAlert = useCallback((id: string) => {
    setAcknowledgedAlerts((prev) => new Set(prev).add(id));
  }, []);

  const store: Store = {
    config,
    snapshot,
    connected,
    sequence: seqRef.current,
    error,
    acknowledgedAlerts,
    switchMode,
    reset,
    acknowledgeAlert,
  };

  return <StoreCtx.Provider value={store}>{children}</StoreCtx.Provider>;
}
