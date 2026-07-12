"use client";

import { Minus, Plus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

interface PhotoEditorProps {
  file: File;
  onCancel: () => void;
  onApply: (file: File) => void;
  cancelLabel: string;
  applyLabel: string;
  title: string;
}

export function PhotoEditor({ file, onCancel, onApply, cancelLabel, applyLabel, title }: PhotoEditorProps) {
  const [scale, setScale] = useState(1);
  const [url, setUrl] = useState<string | null>(null);
  const [imageSize, setImageSize] = useState({ width: 1, height: 1 });
  const objectUrl = useMemo(() => URL.createObjectURL(file), [file]);

  useEffect(() => {
    setUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [objectUrl]);

  const apply = () => {
    if (!url) return;
    const image = new Image();
    image.onload = () => {
      const cropSize = Math.min(image.naturalWidth, image.naturalHeight);
      const sourceX = (image.naturalWidth - cropSize / scale) / 2;
      const sourceY = (image.naturalHeight - cropSize / scale) / 2;
      const sourceSize = cropSize / scale;
      const canvas = document.createElement("canvas");
      canvas.width = 1200;
      canvas.height = 1200;
      const context = canvas.getContext("2d");
      if (!context) return;
      context.drawImage(image, sourceX, sourceY, sourceSize, sourceSize, 0, 0, 1200, 1200);
      canvas.toBlob((blob) => {
        if (blob) onApply(new File([blob], file.name.replace(/\.[^.]+$/, ".jpg"), { type: "image/jpeg" }));
      }, "image/jpeg", 0.84);
    };
    image.src = url;
  };

  return (
    <div className="photo-editor motion-safe:animate-story-state">
      <div className="mb-4 flex items-center justify-center text-[17px] font-semibold">{title}</div>
      <div className="photo-editor-canvas">
        {url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={url}
            alt=""
            draggable={false}
            onLoad={(event) => setImageSize({ width: event.currentTarget.naturalWidth, height: event.currentTarget.naturalHeight })}
            className="photo-editor-image"
            style={{
              width: imageSize.width >= imageSize.height ? `${Math.max(100, (imageSize.width / imageSize.height) * 100 * scale)}%` : "auto",
              height: imageSize.height > imageSize.width ? `${Math.max(100, (imageSize.height / imageSize.width) * 100 * scale)}%` : "auto",
            }}
          />
        )}
        <div className="photo-editor-frame" aria-hidden="true">
          <span /><span /><span /><span />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-3 text-muted">
        <Minus size={15} />
        <input aria-label={title} type="range" min="1" max="3" step="0.02" value={scale} onChange={(event) => setScale(Number(event.target.value))} className="h-1 flex-1 accent-[var(--lm-accent)]" />
        <Plus size={15} />
      </div>
      <div className="mt-4 flex gap-2">
        <button type="button" onClick={onCancel} className="flex-1 rounded border border-border py-2.5 text-[14px] font-medium text-muted transition-colors duration-150 ease-lm hover:bg-surface">{cancelLabel}</button>
        <button type="button" onClick={apply} className="flex-1 rounded bg-accent py-2.5 text-[14px] font-semibold text-accent-text transition-transform duration-150 ease-lm active:scale-[0.98]">{applyLabel}</button>
      </div>
    </div>
  );
}
