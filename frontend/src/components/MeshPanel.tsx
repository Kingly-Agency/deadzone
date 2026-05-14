import { useEffect, useState, useCallback } from "react";
import {
  meshClient,
  MeshClientError,
  type MeRoleResponse,
  type DiscoveredGateway,
  type MeshSnapshot,
} from "../lib/mesh-client";
import styles from "./MeshPanel.module.css";

const URL_RE = /^https?:\/\/.+/;

function roleBadgeText(me: MeRoleResponse): string {
  switch (me.role) {
    case "hosting_and_joined":
      return "Hosting";
    case "hosting":
      return "Hosting";
    case "joined":
      return "Joined";
    default:
      return "Idle";
  }
}

export function MeshPanel() {
  const [me, setMe] = useState<MeRoleResponse | null>(null);
  const [discovered, setDiscovered] = useState<DiscoveredGateway[]>([]);
  const [snapshot, setSnapshot] = useState<MeshSnapshot | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pasteUrl, setPasteUrl] = useState("");

  // ---------- Refresh helpers ----------

  const refreshMe = useCallback(async () => {
    try {
      const data = await meshClient.me();
      setMe(data);
    } catch (err) {
      if (err instanceof MeshClientError) setError(err.message);
    }
  }, []);

  const refreshDiscover = useCallback(async () => {
    try {
      const data = await meshClient.discover();
      setDiscovered(data.filter((g) => !g.is_self));
    } catch (err) {
      if (err instanceof MeshClientError) setError(err.message);
    }
  }, []);

  const refreshState = useCallback(async () => {
    try {
      const data = await meshClient.state();
      setSnapshot(data);
    } catch (err) {
      if (err instanceof MeshClientError) setError(err.message);
    }
  }, []);

  // ---------- Polls ----------

  // Always poll /mesh/me every 2s
  useEffect(() => {
    refreshMe();
    const t = window.setInterval(refreshMe, 2000);
    return () => window.clearInterval(t);
  }, [refreshMe]);

  // Poll /mesh/discover every 3s while idle
  useEffect(() => {
    if (!me || me.role !== "idle") return;
    refreshDiscover();
    const t = window.setInterval(refreshDiscover, 3000);
    return () => window.clearInterval(t);
  }, [me?.role, refreshDiscover]);

  // Poll /mesh/state every 2s while hosting
  useEffect(() => {
    if (!me || !me.hosting) return;
    refreshState();
    const t = window.setInterval(refreshState, 2000);
    return () => window.clearInterval(t);
  }, [me?.hosting, refreshState]);

  // ---------- Action handlers ----------

  const handleHost = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const data = await meshClient.host({ beacon: true });
      setMe(data);
    } catch (err) {
      setError(err instanceof MeshClientError ? err.message : "Failed to host");
    } finally {
      setBusy(false);
    }
  }, []);

  const handleUnhost = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const data = await meshClient.unhost();
      setMe(data);
      setSnapshot(null);
    } catch (err) {
      setError(err instanceof MeshClientError ? err.message : "Failed to stop hosting");
    } finally {
      setBusy(false);
    }
  }, []);

  const handleJoin = useCallback(async (gatewayUrl: string) => {
    setBusy(true);
    setError(null);
    try {
      const data = await meshClient.join({ gateway_url: gatewayUrl });
      setMe(data);
    } catch (err) {
      setError(err instanceof MeshClientError ? err.message : "Failed to join");
    } finally {
      setBusy(false);
    }
  }, []);

  const handleLeave = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const data = await meshClient.leave();
      setMe(data);
    } catch (err) {
      setError(err instanceof MeshClientError ? err.message : "Failed to leave");
    } finally {
      setBusy(false);
    }
  }, []);

  const handleJoinPasted = useCallback(() => {
    if (URL_RE.test(pasteUrl)) {
      handleJoin(pasteUrl);
      setPasteUrl("");
    }
  }, [pasteUrl, handleJoin]);

  // ---------- Derived state ----------

  const isIdle = !me || me.role === "idle";
  const isHosting = me?.hosting ?? false;
  const isJoined = me?.joined ?? false;

  // ---------- Render ----------

  return (
    <section className={styles.panel} aria-label="Mesh control panel">
      {/* Header */}
      <div className={styles.header}>
        <h2 className={styles.title}>Mesh</h2>
        {me && me.role !== "idle" && (
          <span className={styles.roleBadge}>{roleBadgeText(me)}</span>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className={styles.errorBanner} role="alert">
          <span>{error}</span>
          <button
            className={styles.errorDismiss}
            onClick={() => setError(null)}
            aria-label="Dismiss error"
          >
            &times;
          </button>
        </div>
      )}

      {/* Primary actions */}
      <div className={styles.actions}>
        {isIdle && (
          <>
            <button
              className={styles.primaryButton}
              disabled={busy}
              onClick={handleHost}
              aria-label="Host mesh"
            >
              Host Mesh
            </button>
            <button
              className={styles.secondaryButton}
              disabled={busy}
              onClick={refreshDiscover}
              aria-label="Refresh discovery"
            >
              Refresh
            </button>
          </>
        )}
        {isHosting && (
          <button
            className={styles.primaryButton}
            disabled={busy}
            onClick={handleUnhost}
            aria-label="Stop hosting"
          >
            Stop Hosting
          </button>
        )}
        {!isHosting && isJoined && (
          <button
            className={styles.primaryButton}
            disabled={busy}
            onClick={handleLeave}
            aria-label="Leave mesh"
          >
            Leave Mesh
          </button>
        )}
      </div>

      {/* ---- IDLE body ---- */}
      {isIdle && (
        <>
          <p className={styles.sectionLabel}>Discovered Gateways</p>
          <div className={styles.discoveredList}>
            {discovered.length === 0 && (
              <p className={styles.emptyDiscovery}>
                No gateways found on this network yet.
              </p>
            )}
            {discovered.map((g) => (
              <div key={g.gateway_id} className={styles.discoveredRow}>
                <div className={styles.peerInfo}>
                  <span className={styles.peerId}>{g.gateway_id}</span>
                  <span className={styles.peerUrl}>{g.gateway_url}</span>
                </div>
                <button
                  className={styles.joinButton}
                  disabled={busy}
                  onClick={() => handleJoin(g.gateway_url)}
                  aria-label={`Join ${g.gateway_id}`}
                >
                  Join
                </button>
              </div>
            ))}
          </div>

          {/* Paste fallback */}
          <div className={styles.pasteRow}>
            <input
              className={styles.pasteInput}
              type="url"
              placeholder="http://10.0.0.7:8001"
              value={pasteUrl}
              onChange={(e) => setPasteUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleJoinPasted();
              }}
              aria-label="Gateway URL"
            />
            <button
              className={styles.joinButton}
              disabled={busy || !URL_RE.test(pasteUrl)}
              onClick={handleJoinPasted}
              aria-label="Join pasted gateway"
            >
              Join
            </button>
          </div>
        </>
      )}

      {/* ---- HOSTING body ---- */}
      {isHosting && snapshot && (
        <>
          <div className={styles.statsRow}>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Nodes</span>
              <span className={styles.statValue}>{snapshot.nodes.length}</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Devices</span>
              <span className={styles.statValue}>
                {snapshot.zones_merged.reduce((s, z) => s + z.estimated_devices, 0)}
              </span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Mesh Links</span>
              <span className={styles.statValue}>{snapshot.mesh_links.length}</span>
            </div>
          </div>

          {snapshot.zones_merged.length > 0 && (
            <>
              <p className={styles.sectionLabel}>Merged Zones</p>
              {snapshot.zones_merged.map((z) => (
                <div key={z.zone_id} className={styles.zoneRow}>
                  <span className={styles.zoneName}>{z.zone_id}</span>
                  <span className={styles.zoneDevices}>
                    {z.estimated_devices} devices
                  </span>
                  <span className={styles.zoneTrend}>{z.trend}</span>
                </div>
              ))}
            </>
          )}
        </>
      )}

      {/* ---- JOINED body (non-hosting) ---- */}
      {!isHosting && isJoined && me && (
        <div className={styles.connectedBlock}>
          <span className={styles.connectedLabel}>Connected to</span>
          <span className={styles.connectedGateway}>
            {me.joined_gateway_id ?? "unknown"}
          </span>
          <span className={styles.connectedUrl}>{me.joined_url}</span>
          <div className={styles.connectedStats}>
            <span>
              Sent:{" "}
              <span className={styles.connectedStatValue}>
                {me.packets_sent}
              </span>
            </span>
            <span>
              Buffered:{" "}
              <span className={styles.connectedStatValue}>{me.buffered}</span>
            </span>
          </div>
        </div>
      )}
    </section>
  );
}
