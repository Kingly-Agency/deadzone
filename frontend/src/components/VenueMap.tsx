import { useEffect, useRef } from "react";
import { useStore } from "../store";
import type { ZoneAggregate } from "../types";

function densityColor(pct: number): string {
  if (pct < 0.25) return "var(--density-0)";
  if (pct < 0.5) return "var(--density-1)";
  if (pct < 0.75) return "var(--density-2)";
  if (pct < 0.9) return "var(--density-3)";
  return "var(--density-4)";
}

const TREND_ARROWS: Record<string, string> = {
  falling: "↘",
  stable: "→",
  rising: "↗",
  spiking: "⬆",
};

export function VenueMap({
  selectedZone,
  onZoneClick,
}: {
  selectedZone: string | null;
  onZoneClick: (zoneId: string) => void;
}) {
  const { snapshot } = useStore();
  const mapContainerRef = useRef<HTMLDivElement>(null);

  // ResizeObserver: invalidates Leaflet map size on container resize.
  // Currently the map is a CSS grid; this hook is wired for future Leaflet integration
  // and also handles any layout reflows (e.g. sidebar drawer open/close).
  useEffect(() => {
    const el = mapContainerRef.current;
    if (!el) return;

    const ro = new ResizeObserver(() => {
      // Future Leaflet: mapRef.current?.invalidateSize();
      // Dispatch a synthetic resize so any embedded Leaflet instance recalculates
      window.dispatchEvent(new Event("resize"));
    });

    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  if (!snapshot) {
    return (
      <div
        className="venue-map"
        ref={mapContainerRef}
        style={{ display: "flex", alignItems: "center", justifyContent: "center" }}
      >
        <div className="empty-state">
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ opacity: 0.5, marginBottom: 12, color: "var(--text-dim)" }}
          >
            <path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z" />
            <path d="M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z" />
            <path d="M12 2v2" />
            <path d="M12 20v2" />
            <path d="m4.93 4.93 1.41 1.41" />
            <path d="m17.66 17.66 1.41 1.41" />
            <path d="M2 12h2" />
            <path d="M20 12h2" />
            <path d="m6.34 17.66-1.41 1.41" />
            <path d="m19.07 4.93-1.41 1.41" />
          </svg>
          <div>Connecting to sensors…</div>
        </div>
      </div>
    );
  }

  const { zones, venue } = snapshot;
  const zoneMap = new Map(zones.map((z) => [z.zone_id, z]));

  return (
    <div className="venue-map" ref={mapContainerRef}>
      {/* Grid columns/rows are now controlled by CSS (responsive) */}
      <div className="zone-grid">
        {venue.zones.map((vz) => {
          const z = zoneMap.get(vz.id);
          if (!z) return null;
          return (
            <ZoneCard
              key={vz.id}
              zone={z}
              name={vz.name}
              selected={selectedZone === vz.id}
              onClick={() => onZoneClick(vz.id)}
            />
          );
        })}
      </div>

      {/* Density legend */}
      <div className="legend">
        <span>density</span>
        <div className="legend-ramp">
          {[0.1, 0.3, 0.5, 0.7, 0.85, 0.95].map((p) => (
            <span key={p} style={{ background: densityColor(p) }} />
          ))}
        </div>
        <span>low → high</span>
      </div>
    </div>
  );
}

function ZoneCard({
  zone,
  name,
  selected,
  onClick,
}: {
  zone: ZoneAggregate;
  name: string;
  selected: boolean;
  onClick: () => void;
}) {
  const pct = zone.density;
  const color = densityColor(pct);

  return (
    <div
      className={`zone-card ${selected ? "selected" : ""}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") onClick(); }}
      aria-label={`${name}: ${zone.estimated_devices} devices, ${Math.round(pct * 100)}% density`}
      aria-pressed={selected}
    >
      <div className="zone-accent" style={{ background: color }} />
      <div className="zone-header">
        <span className="zone-name">{name}</span>
        <span className="zone-trend" style={{ color }}>
          {TREND_ARROWS[zone.trend] ?? "→"}
        </span>
      </div>

      <div className="zone-stats">
        <div className="zone-stat">
          <div className="zone-stat-label">Devices</div>
          <div className="zone-stat-value">{zone.estimated_devices.toLocaleString()}</div>
        </div>
        <div className="zone-stat">
          <div className="zone-stat-label">Capacity</div>
          <div className="zone-stat-value">{Math.round(pct * 100)}%</div>
        </div>
        <div className="zone-stat">
          <div className="zone-stat-label">Pressure</div>
          <div
            className="zone-stat-value"
            style={{ color: zone.pressure_score > 0.7 ? "var(--severity-critical)" : "inherit" }}
          >
            {Math.round(zone.pressure_score * 100)}%
          </div>
        </div>
      </div>

      <div className="zone-bar-wrap">
        <div className="zone-bar-header">
          <span>Utilization</span>
          <span>{Math.round(pct * 100)}%</span>
        </div>
        <div className="zone-bar-track">
          <div
            className="zone-bar-fill"
            style={{ width: `${pct * 100}%`, background: color }}
          />
        </div>
      </div>
    </div>
  );
}
