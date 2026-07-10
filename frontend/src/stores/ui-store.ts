import { create } from "zustand";

import { defaultLocale, type Locale } from "@/lib/i18n/dict";

type HomeMode = "browse" | "pick-location" | "compose";

interface UiState {
  locale: Locale;
  mode: HomeMode;
  pickedLocation: { lat: number; lon: number } | null;
  openStoryId: string | null;
  trendingOpen: boolean;
  categoryFilter: number | null;
  toast: string | null;
  panRequest: { lat: number; lon: number; zoom?: number; id: number } | null;
  setLocale: (locale: Locale) => void;
  startPickLocation: () => void;
  pickLocation: (lat: number, lon: number) => void;
  cancelCompose: () => void;
  finishCompose: () => void;
  openStory: (id: string) => void;
  closeStory: () => void;
  setTrendingOpen: (open: boolean) => void;
  setCategoryFilter: (id: number | null) => void;
  showToast: (message: string) => void;
  clearToast: () => void;
  requestPanTo: (lat: number, lon: number, zoom?: number) => void;
}

export const useUiStore = create<UiState>((set) => ({
  locale: defaultLocale,
  mode: "browse",
  pickedLocation: null,
  openStoryId: null,
  trendingOpen: false,
  categoryFilter: null,
  toast: null,
  panRequest: null,
  setLocale: (locale) => set({ locale }),
  startPickLocation: () =>
    set({ mode: "pick-location", openStoryId: null, trendingOpen: false }),
  pickLocation: (lat, lon) => set({ mode: "compose", pickedLocation: { lat, lon } }),
  cancelCompose: () => set({ mode: "browse", pickedLocation: null }),
  finishCompose: () => set({ mode: "browse", pickedLocation: null }),
  openStory: (id) => set({ openStoryId: id, trendingOpen: false }),
  closeStory: () => set({ openStoryId: null }),
  setTrendingOpen: (open) => set({ trendingOpen: open }),
  setCategoryFilter: (id) => set({ categoryFilter: id }),
  showToast: (message) => set({ toast: message }),
  clearToast: () => set({ toast: null }),
  requestPanTo: (lat, lon, zoom) =>
    set({ panRequest: { lat, lon, zoom, id: Date.now() } }),
}));
