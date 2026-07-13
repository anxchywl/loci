import type { Metadata, Viewport } from "next";
import Script from "next/script";
import "maplibre-gl/dist/maplibre-gl.css";
import "./globals.css";

import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "Loci",
  icons: {
    icon: [{ url: "/favicon.svg?v=7", type: "image/svg+xml" }],
    shortcut: "/favicon.svg?v=7",
    apple: "/favicon.svg?v=7",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  userScalable: false,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // telegram-web-app.js stamps theme css vars on <html> before hydration
    <html lang="en" suppressHydrationWarning>
      <head>
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
