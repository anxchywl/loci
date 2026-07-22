"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState, type ReactNode } from "react";

import { ThemeProvider } from "@/components/theme-provider";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: (failureCount, error) => {
              const status = (error as { status?: number }).status;
              return status !== 401 && status !== 403 && status !== 404 && failureCount < 1;
            },
            staleTime: 15_000,
            gcTime: 5 * 60_000,
            refetchOnWindowFocus: false,
            refetchOnReconnect: true,
            refetchOnMount: false,
          },
          mutations: { retry: false },
        },
      }),
  );
  useEffect(() => {
    const revalidate = () => {
      if (document.visibilityState === "visible" && navigator.onLine) {
        void queryClient.invalidateQueries({ refetchType: "active" });
      }
    };
    const onVisibility = () => { if (document.visibilityState === "visible") revalidate(); };
    const onOnline = () => revalidate();
    const interval = window.setInterval(revalidate, 30_000);
    document.addEventListener("visibilitychange", onVisibility);
    window.addEventListener("online", onOnline);
    return () => {
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", onVisibility);
      window.removeEventListener("online", onOnline);
    };
  }, [queryClient]);

  return <QueryClientProvider client={queryClient}><ThemeProvider />{children}</QueryClientProvider>;
}
