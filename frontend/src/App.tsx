import { useState, useEffect, useCallback } from "react";
import { StoreProvider, useStore } from "./store";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { MetricsBar } from "./components/MetricsBar";
import { VenueMap } from "./components/VenueMap";
import { AlertsPanel } from "./components/AlertsPanel";
import { ZoneDetail } from "./components/ZoneDetail";
import { AlertToast } from "./components/AlertToast";
import { Footer } from "./components/Footer";
import { ReplayControls } from "./components/ReplayControls";
import { HeatmapDashboard } from "./components/HeatmapDashboard";
import "./styles.css";

function Dashboard() {
  const { snapshot, reset } = useStore();
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState("dashboard");

  // R key to reset
  const handleKey = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "r" || e.key === "R") {
        const tag = (e.target as HTMLElement)?.tagName;
        if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
        reset();
      }
    },
    [reset]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [handleKey]);

  const alerts = snapshot?.alerts ?? [];

  const handleZoneClick = (zoneId: string) => {
    setSelectedZone(zoneId === selectedZone ? null : zoneId);
  };

  return (
    <div className="app-layout">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        selectedZone={selectedZone}
        onZoneClick={handleZoneClick}
        activeSection={activeSection}
        onSectionChange={setActiveSection}
      />

      <div className="app-main">
        <Header />
        <MetricsBar />

        <div className="main-content">
          {activeSection === "heatmap" ? (
            <HeatmapDashboard />
          ) : (
            <>
              <div className="canvas-wrap">
                <VenueMap
                  selectedZone={selectedZone}
                  onZoneClick={handleZoneClick}
                />
                <ReplayControls />
              </div>
              {selectedZone ? (
                <ZoneDetail zoneId={selectedZone} onClose={() => setSelectedZone(null)} />
              ) : (
                <AlertsPanel onViewZone={(z) => setSelectedZone(z)} />
              )}
            </>
          )}
        </div>

        <Footer />
      </div>

      <AlertToast alerts={alerts} />
    </div>
  );
}

export default function App() {
  return (
    <StoreProvider>
      <Dashboard />
    </StoreProvider>
  );
}
