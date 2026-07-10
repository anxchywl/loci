"use client";

import { useEffect, useState } from "react";

import { postTelegramAuth, type AuthUser } from "@/features/auth/api";
import { setAccessToken } from "@/lib/api";
import { resolveLocale } from "@/lib/i18n/dict";
import { initTelegram } from "@/lib/telegram/init";
import { useUiStore } from "@/stores/ui-store";

export type AuthStatus = "loading" | "authenticated" | "signed-out";

let cachedUser: AuthUser | null = null;

export function useTelegramAuth(): { status: AuthStatus; user: AuthUser | null } {
  const [status, setStatus] = useState<AuthStatus>(cachedUser ? "authenticated" : "loading");
  const [user, setUser] = useState<AuthUser | null>(cachedUser);
  const setLocale = useUiStore((state) => state.setLocale);
  const openStory = useUiStore((state) => state.openStory);

  useEffect(() => {
    if (cachedUser) return;
    const launch = initTelegram();
    if (!launch) {
      setStatus("signed-out");
      return;
    }

    setLocale(resolveLocale(launch.languageCode));
    let cancelled = false;
    postTelegramAuth(launch.initDataRaw)
      .then((response) => {
        if (cancelled) return;
        setAccessToken(response.access_token);
        cachedUser = response.user;
        setUser(response.user);
        setStatus("authenticated");
        if (launch.startParam) openStory(launch.startParam);
      })
      .catch(() => {
        if (!cancelled) setStatus("signed-out");
      });
    return () => {
      cancelled = true;
    };
  }, [setLocale, openStory]);

  return { status, user };
}
