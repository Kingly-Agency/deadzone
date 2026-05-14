import { useState, useEffect } from "react";
import { useStore } from "../store";
import type { RawSensorEvent } from "../types";

export function DeviceEventTable() {
  const { snapshot } = useStore();
  const [events, setEvents] = useState<RawSensorEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchEvents = async () => {
    try {
      const res = await fetch("/api/v1/sensors/local-ble-scanner/events?limit=100");
      if (res.ok) {
        const data = await res.json();
        // reverse to show newest first
        setEvents(data.reverse());
      }
    } catch (e) {
      console.error("Failed to fetch events", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => clearInterval(interval);
  }, []);

  const getZoneName = (zoneId: string) => {
    return snapshot?.venue.zones.find((z) => z.id === zoneId)?.name || zoneId;
  };

  return (
    <div className="devices-panel">
      <div className="devices-header">
        <h2>Live Device Stream</h2>
        <p>Raw BLE advertisements from local scanner (Last 100 hits)</p>
      </div>

      <div className="devices-table-wrap">
        {loading ? (
          <div className="empty-state">Loading data...</div>
        ) : events.length === 0 ? (
          <div className="empty-state">No devices detected.</div>
        ) : (
          <table className="devices-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Device ID (MAC Hash)</th>
                <th>Zone</th>
                <th>RSSI</th>
                <th>Count</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev, i) => (
                <tr key={`${ev.timestamp}-${ev.beacon_hash}-${i}`}>
                  <td>{new Date(ev.timestamp).toLocaleTimeString([], { hour12: false, second: "2-digit" })}</td>
                  <td className="mono">{ev.beacon_hash?.substring(0, 12)}...</td>
                  <td>{getZoneName(ev.zone_id)}</td>
                  <td>
                    <div className="rssi-bar-wrap">
                      <div 
                        className="rssi-bar-fill"
                        style={{ 
                          width: `${Math.max(0, Math.min(100, (ev.rssi! + 100) * 1.5))}%`,
                          background: ev.rssi! > -60 ? "var(--density-3)" : ev.rssi! > -80 ? "var(--density-2)" : "var(--density-1)"
                        }}
                      />
                      <span>{ev.rssi} dBm</span>
                    </div>
                  </td>
                  <td>{ev.device_count || 1}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
