import { useState, useEffect, useCallback, useRef } from "react";
import { StoreProvider, useStore } from "./store";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { MetricsBar } from "./components/MetricsBar";
import { SpatialMap } from "./components/SpatialMap";
import { AlertsPanel } from "./components/AlertsPanel";
import { ZoneDetail } from "./components/ZoneDetail";
import { AlertToast } from "./components/AlertToast";
import { Footer } from "./components/Footer";
import { HeatmapDashboard } from "./components/HeatmapDashboard";
import { ConfigurationScreen } from "./components/ConfigurationScreen";
import { MeshPanel } from "./components/MeshPanel";
import { Drawer } from "./components/Drawer";
import { DeviceEventTable } from "./components/DeviceEventTable";
import "./styles.css";

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(
    () => typeof window !== "undefined" && window.matchMedia(query).matches
  );
  useEffect(() => {
    const mq = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [query]);
  return matches;
}

function Dashboard() {
  const { snapshot, reset } = useStore();
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState("dashboard");
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);

  const isNarrow = useMediaQuery("(max-width: 1024px)");

  // Refs for focus-return targets
  const bellRef = useRef<HTMLButtonElement>(null);
  const menuBtnRef = useRef<HTMLButtonElement>(null);
  // Ref for inert on main content while a drawer is open
  const mainRef = useRef<HTMLDivElement>(null);

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

  // Auto-open alerts drawer when a zone is selected on mobile/tablet
  useEffect(() => {
    if (isNarrow && selectedZone) {
      setIsAlertsOpen(true);
      setIsMobileNavOpen(false);
    }
  }, [selectedZone, isNarrow]);

  // Body scroll lock while any drawer is open on mobile/tablet
  useEffect(() => {
    const locked = isNarrow && (isMobileNavOpen || isAlertsOpen);
    document.body.style.overflow = locked ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobileNavOpen, isAlertsOpen, isNarrow]);

  // inert on main content while a drawer is open (hides from AT)
  useEffect(() => {
    const el = mainRef.current;
    if (!el) return;
    if (isNarrow && (isMobileNavOpen || isAlertsOpen)) {
      el.setAttribute("inert", "");
    } else {
      el.removeAttribute("inert");
    }
  }, [isNarrow, isMobileNavOpen, isAlertsOpen]);

  const openNav = useCallback(() => {
    setIsMobileNavOpen(true);
    setIsAlertsOpen(false);
  }, []);
  const closeNav = useCallback(() => setIsMobileNavOpen(false), []);

  const openAlerts = useCallback(() => {
    setIsAlertsOpen(true);
    setIsMobileNavOpen(false);
  }, []);
  const closeAlerts = useCallback(() => setIsAlertsOpen(false), []);

  const handleBellClick = useCallback(() => {
    if (isNarrow) {
      isAlertsOpen ? closeAlerts() : openAlerts();
    }
  }, [isNarrow, isAlertsOpen, openAlerts, closeAlerts]);

  const handleZoneClick = useCallback(
    (zoneId: string) => {
      const next = zoneId === selectedZone ? null : zoneId;
      setSelectedZone(next);
      if (isNarrow && next) {
        setIsAlertsOpen(true);
        setIsMobileNavOpen(false);
      } else if (isNarrow && !next) {
        // Deselecting a zone: keep alerts open but show AlertsPanel
      }
    },
    [selectedZone, isNarrow]
  );

  const handleViewZone = useCallback(
    (zoneId: string) => {
      setSelectedZone(zoneId);
      if (isNarrow) {
        setIsAlertsOpen(true);
        setIsMobileNavOpen(false);
      }
    },
    [isNarrow]
  );

  const alerts = snapshot?.alerts ?? [];

  return (
    <div className="app-layout">
      {/* Desktop sidebar — part of layout flow */}
      {!isNarrow && (
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          selectedZone={selectedZone}
          onZoneClick={handleZoneClick}
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          isDrawerMode={false}
          onNavItemClick={() => {}}
        />
      )}

      {/* Mobile/tablet left nav drawer */}
      {isNarrow && (
        <Drawer
          open={isMobileNavOpen}
          onClose={closeNav}
          side="left"
          label="Navigation"
          width={300}
          triggerRef={menuBtnRef as React.RefObject<HTMLElement>}
        >
          <Sidebar
            collapsed={false}
            onToggle={closeNav}
            selectedZone={selectedZone}
            onZoneClick={handleZoneClick}
            activeSection={activeSection}
            onSectionChange={(s) => {
              setActiveSection(s);
              closeNav();
            }}
            isDrawerMode={true}
            onNavItemClick={closeNav}
          />
        </Drawer>
      )}

      {/* Main content — gets inert while a drawer is open */}
      <div className="app-main" ref={mainRef}>
        <Header
          onMenuToggle={openNav}
          onBellClick={handleBellClick}
          isMobileNavOpen={isMobileNavOpen}
          isAlertsOpen={isAlertsOpen}
          isNarrow={isNarrow}
          bellRef={bellRef}
          menuBtnRef={menuBtnRef}
        />
        <MetricsBar />

        <div className="main-content">
          {activeSection === "heatmap" ? (
            <HeatmapDashboard />
          ) : activeSection === "configuration" ? (
            <ConfigurationScreen />
          ) : activeSection === "mesh" ? (
            <MeshPanel />
          ) : activeSection === "sensors" ? (
            <DeviceEventTable />
          ) : (
            <>
              <div className="canvas-wrap">
                <SpatialMap
                  selectedZone={selectedZone}
                  onZoneClick={handleZoneClick}
                />
              </div>
              {/* Desktop right column only — on narrow viewports, these live in the right drawer */}
              {!isNarrow &&
                (selectedZone ? (
                  <ZoneDetail
                    zoneId={selectedZone}
                    onClose={() => setSelectedZone(null)}
                  />
                ) : (
                  <AlertsPanel onViewZone={handleViewZone} />
                ))}
            </>
          )}
        </div>

        <Footer />
      </div>

      {/* Mobile/tablet right drawer — alerts or zone detail */}
      {isNarrow && (
        <Drawer
          open={isAlertsOpen}
          onClose={closeAlerts}
          side="right"
          label={selectedZone ? "Zone detail" : "Alerts"}
          width={360}
          triggerRef={bellRef as React.RefObject<HTMLElement>}
        >
          <div className="drawer-inner">
            {selectedZone ? (
              <ZoneDetail
                zoneId={selectedZone}
                onClose={() => {
                  setSelectedZone(null);
                  closeAlerts();
                }}
              />
            ) : (
              <AlertsPanel onViewZone={handleViewZone} />
            )}
          </div>
        </Drawer>
      )}

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
