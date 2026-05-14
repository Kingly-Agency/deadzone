import { useStore } from "../store";

export function Footer() {
  const { snapshot, connected } = useStore();

  const lastFrame = snapshot?.stream.clock.timestamp;
  const freshness = snapshot?.stream.freshness ?? "offline";

  let statusText = "Disconnected";
  let dotClass = "offline";
  if (connected) {
    if (freshness === "live" || freshness === "fresh") {
      statusText = "Connected";
      dotClass = "online";
    } else if (freshness === "stale") {
      statusText = "Stale";
      dotClass = "stale";
    } else {
      statusText = "Connected";
      dotClass = "online";
    }
  } else {
    statusText = "Reconnecting…";
    dotClass = "offline";
  }

  return (
    <footer className="footer">
      <div className="footer-left">
        <span className="footer-copy">© 2026 DeadZone</span>
        <span className="footer-divider">·</span>
        <span className="footer-version">v0.1.0</span>
      </div>
      <div className="footer-center">
        <span className="footer-timestamp">
          Last frame: {lastFrame ? new Date(lastFrame).toLocaleTimeString(undefined, { hour12: false, fractionalSecondDigits: 3 }) : "—"}
        </span>
      </div>
      <div className="footer-right">
        <span className={`connection-dot ${dotClass}`} />
        <span className="footer-status">{statusText}</span>
      </div>
    </footer>
  );
}
