import { useEffect, useRef, useState } from "react";
import type { Alert } from "../types";

interface ToastItem {
  id: string;
  alert: Alert;
  expiresAt: number;
}

export function AlertToast({ alerts }: { alerts: Alert[] }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const seenRef = useRef(new Set<string>());

  useEffect(() => {
    const critical = alerts.filter((a) => a.severity === "critical" && a.status === "active");
    const newOnes = critical.filter((a) => !seenRef.current.has(a.id));

    if (newOnes.length > 0) {
      const now = Date.now();
      const newToasts = newOnes.map((a) => ({
        id: a.id,
        alert: a,
        expiresAt: now + 6000,
      }));
      newOnes.forEach((a) => seenRef.current.add(a.id));
      setToasts((prev) => [...prev, ...newToasts]);
    }
  }, [alerts]);

  // Auto-dismiss
  useEffect(() => {
    if (toasts.length === 0) return;
    const id = setInterval(() => {
      const now = Date.now();
      setToasts((prev) => prev.filter((t) => t.expiresAt > now));
    }, 500);
    return () => clearInterval(id);
  }, [toasts.length]);

  const dismiss = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((t, index) => {
        // Only show top 3 to avoid infinite stacking
        if (index > 2) return null;
        return (
        <div 
          key={t.id} 
          className="toast critical"
          style={{
            position: index === 0 ? "relative" : "absolute",
            top: index * 12,
            left: 0,
            right: 0,
            zIndex: toasts.length - index,
            transform: `scale(${1 - index * 0.04})`,
            opacity: 1 - index * 0.15,
            pointerEvents: index === 0 ? "auto" : "none",
          }}
        >
          <div className="toast-icon">⚠️</div>
          <div className="toast-content">
            <div className="toast-title">Critical Alert</div>
            <div className="toast-message">{t.alert.message}</div>
          </div>
          <button className="toast-dismiss" onClick={() => dismiss(t.id)} title="Dismiss">
            ✕
          </button>
        </div>
      )})}
    </div>
  );
}
