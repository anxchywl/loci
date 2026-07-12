/**
 * Loci brand mark — mirrors the canonical app icon at src/app/icon.svg
 * (which Next.js also serves as the favicon). Rendered as a small rounded
 * tile so it reads as the real app icon rather than a generic map pin.
 */
export function AppIcon({ size = 16 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <rect width="512" height="512" rx="112" fill="#ffffff" />
      <g transform="translate(128, 104) scale(10.6667)">
        <path
          d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 15.007 4 10a8 8 0 0 1 16 0"
          fill="#18181b"
        />
        <circle cx="12" cy="10" r="4.5" fill="#ffffff" />
        <circle cx="12" cy="10" r="3.5" fill="#3390ec" opacity="0.2" />
        <circle cx="12" cy="10" r="2.25" fill="#3390ec" opacity="0.5" />
        <circle cx="12" cy="10" r="1.25" fill="#3390ec" />
      </g>
    </svg>
  );
}
