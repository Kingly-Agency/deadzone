import { useEffect, useRef, type ReactNode, type RefObject } from "react";

const FOCUSABLE =
  'button:not([disabled]),[href],input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';

export interface DrawerProps {
  open: boolean;
  onClose: () => void;
  side: "left" | "right";
  label: string;
  width?: number | string;
  children: ReactNode;
  triggerRef?: RefObject<HTMLElement>;
}

export function Drawer({
  open,
  onClose,
  side,
  label,
  width = 320,
  children,
  triggerRef,
}: DrawerProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const savedFocus = useRef<Element | null>(null);

  // Focus management: save current focus on open, restore on close
  useEffect(() => {
    if (open) {
      savedFocus.current = document.activeElement;
      requestAnimationFrame(() => {
        panelRef.current?.querySelector<HTMLElement>(FOCUSABLE)?.focus();
      });
    } else {
      const target = (triggerRef?.current ?? savedFocus.current) as HTMLElement | null;
      target?.focus();
    }
  }, [open, triggerRef]);

  // Esc handler + focus trap
  useEffect(() => {
    if (!open) return;

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key === "Tab") {
        const panel = panelRef.current;
        if (!panel) return;
        const els = Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE));
        if (!els.length) return;
        const first = els[0];
        const last = els[els.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <>
      {/* Scrim: aria-hidden, click to close */}
      <div className="drawer-scrim" aria-hidden="true" onClick={onClose} />

      {/* Drawer panel */}
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        className={`drawer drawer--${side}`}
        style={{ width: typeof width === "number" ? `${width}px` : width }}
      >
        {children}
      </div>
    </>
  );
}
