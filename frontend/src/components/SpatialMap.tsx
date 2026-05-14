import { useMemo, useEffect, useState } from "react";
import { useStore } from "../store";

// Simple seeded PRNG to keep particles stable between renders
function mulberry32(a: number) {
  return function() {
    var t = a += 0x6D2B79F5;
    t = Math.imul(t ^ t >>> 15, t | 1);
    t ^= t + Math.imul(t ^ t >>> 7, t | 61);
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  }
}

function densityColor(pct: number): string {
  if (pct < 0.25) return "#34d399"; // emerald-400
  if (pct < 0.5) return "#fbbf24"; // amber-400
  if (pct < 0.75) return "#f97316"; // orange-500
  if (pct < 0.9) return "#ef4444"; // red-500
  return "#b91c1c"; // red-700
}

interface RealDevice {
  hash: string;
  zone_id: string;
  rssi: number | null;
}

export function SpatialMap({
  selectedZone,
  onZoneClick,
}: {
  selectedZone: string | null;
  onZoneClick: (zoneId: string) => void;
}) {
  const { snapshot } = useStore();
  const [tick, setTick] = useState(0);
  const [realDevices, setRealDevices] = useState<RealDevice[]>([]);

  // Slow drift animation tick
  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 3000);
    return () => clearInterval(interval);
  }, []);

  // Poll real BLE events
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch("/api/v1/sensors/local-ble-scanner/events?limit=1000");
        if (res.ok) {
          const data = await res.json();
          // Keep only latest event per beacon_hash
          const latestMap = new Map<string, RealDevice>();
          for (const ev of data) {
            if (!latestMap.has(ev.beacon_hash)) {
              latestMap.set(ev.beacon_hash, {
                hash: ev.beacon_hash,
                zone_id: ev.zone_id,
                rssi: ev.rssi
              });
            }
          }
          setRealDevices(Array.from(latestMap.values()));
        }
      } catch (e) {
        console.error("Failed to fetch real BLE events for map", e);
      }
    };
    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!snapshot) {
    return (
      <div className="venue-map" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div className="empty-state">Loading spatial map...</div>
      </div>
    );
  }

  const { zones, venue } = snapshot;
  const zoneMap = new Map(zones.map((z) => [z.zone_id, z]));

  return (
    <div className="spatial-map-container" style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden', background: '#e5e7eb' }}>
      {/* Offline Architectural Floor Plan Background */}
      <img 
        src="/map.png" 
        alt="Venue Floor Plan" 
        style={{ width: '100%', height: '100%', objectFit: 'contain', opacity: 1, position: 'absolute', top: 0, left: 0 }} 
      />

      {/* SVG Particle Overlay */}
      <svg 
        viewBox="0 0 100 100" 
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 1 }}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <filter id="heat-glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {venue.zones.map((vz) => (
          <ZoneOverlay
            key={vz.id}
            vz={vz}
            z={zoneMap.get(vz.id)}
            tick={tick}
            selectedZone={selectedZone}
            onZoneClick={onZoneClick}
            realDevices={realDevices.filter(d => d.zone_id === vz.id)}
          />
        ))}
      </svg>
      <div
        className="spatial-map-disclaimer"
        title="The floorplan is illustrative. RSSI tells us distance from the scanner, not direction — so a device's position inside its zone is approximate. Zone labels show 'active beacons / estimated devices'."
      >
        ⓘ Illustrative floorplan · RSSI ≈ distance (not direction) · labels: <em>active / estimated</em>
      </div>
    </div>
  );
}

function ZoneOverlay({ 
  vz, 
  z, 
  tick, 
  selectedZone, 
  onZoneClick,
  realDevices
}: { 
  vz: any; 
  z: any; 
  tick: number; 
  selectedZone: string | null; 
  onZoneClick: (zoneId: string) => void; 
  realDevices: RealDevice[];
}) {
  const density = Math.max(0, Math.min(1, z?.density || 0));
  const color = density > 0 ? densityColor(density) : 'rgba(255,255,255,0.1)';
  const pointsStr = vz.polygon.map((p: any) => `${p.x},${p.y}`).join(" ");
  const isSelected = selectedZone === vz.id;

  // Calculate bounding box for scattering
  const minX = Math.min(...vz.polygon.map((p: any) => p.x));
  const maxX = Math.max(...vz.polygon.map((p: any) => p.x));
  const minY = Math.min(...vz.polygon.map((p: any) => p.y));
  const maxY = Math.max(...vz.polygon.map((p: any) => p.y));
  const width = maxX - minX;
  const height = maxY - minY;

  // Generate stable but drifting particles from real BLE devices
  const particles = useMemo(() => {
    return realDevices.map((dev) => {
      // Use the MAC hash to generate a stable string hash for the seed
      let stringHash = 0;
      // Fallback if backend hasn't restarted to include beacon_hash
      const hashStr = dev.hash || `fallback-${Math.random()}`;
      for (let i = 0; i < hashStr.length; i++) {
        stringHash = (stringHash << 5) - stringHash + hashStr.charCodeAt(i);
        stringHash |= 0;
      }
      const rng = mulberry32(Math.abs(stringHash));
      return {
        id: hashStr,
        baseX: minX + rng() * width,
        baseY: minY + rng() * height,
        speedX: (rng() - 0.5) * 2,
        speedY: (rng() - 0.5) * 2,
        size: rng() * 1.5 + 0.5,
        opacity: rng() * 0.5 + 0.5
      };
    });
  }, [realDevices, minX, minY, width, height]);

  return (
    <g onClick={() => onZoneClick(vz.id)} style={{ cursor: 'pointer' }}>
      {/* Zone Area Fill */}
      <polygon 
        points={pointsStr}
        fill={color}
        fillOpacity={isSelected ? 0.15 : 0.05}
        stroke={isSelected ? color : "rgba(0,0,0,0.1)"}
        strokeWidth={isSelected ? 0.5 : 0.2}
        strokeDasharray="1,1"
        style={{ transition: 'all 0.5s ease' }}
      />
      
      {/* Device Particles */}
      <g filter={density > 0 ? "url(#heat-glow)" : undefined}>
        {particles.map((p) => {
          // Apply gentle drift using the tick
          const driftX = Math.sin(tick * p.speedX) * 2;
          const driftY = Math.cos(tick * p.speedY) * 2;
          // Keep inside bounds
          const finalX = Math.max(minX + 1, Math.min(maxX - 1, p.baseX + driftX));
          const finalY = Math.max(minY + 1, Math.min(maxY - 1, p.baseY + driftY));

          return (
            <circle
              key={p.id}
              cx={finalX}
              cy={finalY}
              r={p.size}
              fill={color}
              opacity={isSelected ? 1 : p.opacity}
              style={{ transition: 'all 3s linear' }}
            >
              <title>{p.id}</title>
            </circle>
          );
        })}
      </g>

      {/* Subdued Zone Label Overlay */}
      <rect 
        x={minX + 2} 
        y={minY + 2} 
        width="10" 
        height="3" 
        fill="rgba(0,0,0,0.6)" 
        rx="0.5" 
        style={{ pointerEvents: 'none' }}
      />
      <text
        x={minX + 7}
        y={minY + 4}
        fill="#fff"
        fontSize="1.6"
        fontWeight="600"
        textAnchor="middle"
        style={{ pointerEvents: 'none', letterSpacing: '0.05em' }}
      >
        {z?.estimated_devices != null && z.estimated_devices !== realDevices.length
          ? `${realDevices.length}/${z.estimated_devices}`
          : `${realDevices.length} ${realDevices.length === 1 ? 'dev' : 'devs'}`}
      </text>
    </g>
  );
}
