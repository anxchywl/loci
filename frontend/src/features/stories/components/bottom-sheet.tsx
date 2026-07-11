"use client";

import { ChevronLeft } from "lucide-react";
import { type ReactNode, useEffect, useRef, useState } from "react";

interface BottomSheetProps {
  open: boolean;
  onClose: () => void;
  onBack?: () => void;
  title?: string;
  isEditing?: boolean;
  activeFieldId?: string | null;
  keyboardInset?: number;
  children: ReactNode;
}

export function BottomSheet({
  open,
  onClose,
  onBack,
  title,
  isEditing = false,
  activeFieldId = null,
  keyboardInset = 0,
  children,
}: BottomSheetProps) {
  const [startY, setStartY] = useState<number | null>(null);
  const [dragY, setDragY] = useState(0);
  const sheetRef = useRef<HTMLDivElement>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    setStartY(e.touches[0].clientY);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (startY === null) return;
    const currentY = e.touches[0].clientY;
    const diff = currentY - startY;
    if (diff > 0) {
      setDragY(diff);
    }
  };

  const handleTouchEnd = () => {
    if (dragY > 60) {
      onClose();
    }
    setStartY(null);
    setDragY(0);
  };

  useEffect(() => {
    if (!isEditing || !activeFieldId) return;

    const frame = requestAnimationFrame(() => {
      const field = Array.from(
        sheetRef.current?.querySelectorAll<HTMLElement>("[data-keyboard-field]") ?? [],
      ).find((candidate) => candidate.dataset.keyboardField === activeFieldId);
      field?.scrollIntoView?.({ behavior: "smooth", block: "center" });
    });

    return () => cancelAnimationFrame(frame);
  }, [activeFieldId, isEditing]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40" role="dialog" aria-modal="true">
      <button
        aria-label="close"
        className="absolute inset-0 bg-black/30"
        onClick={onClose}
      />
      <div
        ref={sheetRef}
        className={`absolute inset-x-0 bottom-0 max-h-[85dvh] overflow-y-auto rounded-t-sheet bg-bg pb-[env(safe-area-inset-bottom)] shadow-[0_-8px_32px_rgba(0,0,0,0.18)] motion-safe:animate-sheet-up transition-[height,transform,max-height] duration-250 ease-lm ${isEditing ? "keyboard-sheet-editing" : ""}`}
        style={{
          "--lm-keyboard-inset": `${keyboardInset}px`,
          ...(dragY > 0 ? { transform: `translateY(${dragY}px)`, transition: "none" } : {}),
        } as React.CSSProperties}
      >
        <div 
          className="sticky top-0 z-10 flex flex-col items-center justify-center bg-bg pt-3"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <div className="mb-3 h-1.5 w-12 shrink-0 rounded-full bg-border/80" />
          {(title || onBack) ? (
            <div className="relative flex w-full min-h-[32px] items-center justify-center pb-3">
              {onBack && (
                <button
                  aria-label="back"
                  onClick={onBack}
                  className="absolute left-2 flex h-8 w-8 items-center justify-center bg-transparent text-muted transition-colors hover:text-accent focus-visible:text-accent active:scale-95"
                >
                  <ChevronLeft size={24} />
                </button>
              )}
              {title && (
                <div className={`keyboard-sheet-title px-12 text-[17px] font-semibold text-center ${isEditing ? "keyboard-sheet-title-hidden" : ""}`}>
                  {title}
                </div>
              )}
            </div>
          ) : (
            <div className="pb-1" />
          )}
        </div>
        <div className="px-4 pb-6">{children}</div>
      </div>
    </div>
  );
}
