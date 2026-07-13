import { create } from "zustand";

import { defaultLocale, type Locale } from "@/lib/i18n/dict";

type HomeMode = "browse" | "pick-location" | "compose";

export type Theme = "auto" | "light" | "dark";
export type MapLabelDensity = "none" | "countries" | "all";
export type MapStyle = "clean" | "bright" | "dark";

interface UiState {
  locale: Locale;
  theme: Theme;
  mode: HomeMode;
  pickedLocation: { lat: number; lon: number } | null;
  openStoryId: string | null;
  trendingOpen: boolean;
  categoryFilter: number | null;
  // "clustered" groups nearby pins into counted circles; "all" keeps every pin
  // visible and scales them down with zoom (Queering-the-Map style)
  showAllPins: boolean;
  mapLabelDensity: MapLabelDensity;
  mapStyle: MapStyle;
  mapViewOpen: boolean;
  toast: string | null;
  panRequest: { lat: number; lon: number; zoom?: number; id: number } | null;
  setLocale: (locale: Locale) => void;
  setTheme: (theme: Theme) => void;
  startPickLocation: () => void;
  pickLocation: (lat: number, lon: number) => void;
  cancelCompose: () => void;
  finishCompose: () => void;
  openStory: (id: string) => void;
  closeStory: () => void;
  setTrendingOpen: (open: boolean) => void;
  setCategoryFilter: (id: number | null) => void;
  hydrateShowAllPins: () => void;
  toggleShowAllPins: () => void;
  setShowAllPins: (show: boolean) => void;
  setMapLabelDensity: (density: MapLabelDensity) => void;
  setMapStyle: (style: MapStyle) => void;
  setMapViewOpen: (open: boolean) => void;
  showToast: (message: string) => void;
  clearToast: () => void;
  requestPanTo: (lat: number, lon: number, zoom?: number) => void;
  hydratePreferences: () => void;
}

function loadPref<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;
  try { return (localStorage.getItem(key) as T) ?? fallback; } catch { return fallback; }
}

export const useUiStore = create<UiState>((set) => ({
  // persisted preferences are applied after mount so SSR and the first client
  // render use the same strings and theme
  locale: defaultLocale,
  theme: "auto",
  mode: "browse",
  pickedLocation: null,
  openStoryId: null,
  trendingOpen: false,
  categoryFilter: null,
  // starts false on server AND first client render to avoid a hydration
  // mismatch; the persisted value is applied after mount via hydrateShowAllPins()
  showAllPins: false,
  mapLabelDensity: "all",
  mapStyle: "clean",
  mapViewOpen: false,
  toast: null,
  panRequest: null,
  setLocale: (locale) => { localStorage.setItem("loci_locale", locale); set({ locale }); },
  setTheme: (theme) => { localStorage.setItem("loci_theme", theme); set({ theme }); },
  hydratePreferences: () =>
    set({
      locale: loadPref("loci_locale", defaultLocale) as Locale,
      theme: loadPref("loci_theme", "auto") as Theme,
      // reopen the story sheet the user was reading before the reload
      openStoryId: loadPref<string>("loci_open_story", "") || null,
    }),
  startPickLocation: () =>
    set({ mode: "pick-location", openStoryId: null, trendingOpen: false }),
  pickLocation: (lat, lon) => set({ mode: "compose", pickedLocation: { lat, lon } }),
  cancelCompose: () => set({ mode: "browse", pickedLocation: null }),
  finishCompose: () => set({ mode: "browse", pickedLocation: null }),
  openStory: (id) => {
    try { localStorage.setItem("loci_open_story", id); } catch { /* ignore */ }
    set({ openStoryId: id, trendingOpen: false });
  },
  closeStory: () => {
    try { localStorage.removeItem("loci_open_story"); } catch { /* ignore */ }
    set({ openStoryId: null });
  },
  setTrendingOpen: (open) => set({ trendingOpen: open }),
  setCategoryFilter: (id) => set({ categoryFilter: id }),
  hydrateShowAllPins: () =>
    set({ showAllPins: loadPref<string>("loci_show_all_pins", "0") === "1" }),
  toggleShowAllPins: () =>
    set((state) => {
      const next = !state.showAllPins;
      try { localStorage.setItem("loci_show_all_pins", next ? "1" : "0"); } catch { /* ignore */ }
      return { showAllPins: next };
    }),
  setShowAllPins: (showAllPins) => set({ showAllPins }),
  setMapLabelDensity: (mapLabelDensity) => set({ mapLabelDensity }),
  setMapStyle: (mapStyle) => set({ mapStyle }),
  setMapViewOpen: (mapViewOpen) => set({ mapViewOpen }),
  showToast: (message) => set({ toast: message }),
  clearToast: () => set({ toast: null }),
  requestPanTo: (lat, lon, zoom) =>
    set({ panRequest: { lat, lon, zoom, id: Date.now() } }),
}));
