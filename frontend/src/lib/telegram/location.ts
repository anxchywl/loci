export type LocateOutcome =
  | { kind: "located"; lat: number; lon: number }
  | { kind: "settings-opened" }
  | { kind: "denied" }
  | { kind: "unsupported" };

interface TelegramLocationData {
  latitude?: number;
  longitude?: number;
}

interface TelegramLocationManager {
  isInited: boolean;
  isLocationAvailable: boolean;
  isAccessRequested: boolean;
  isAccessGranted: boolean;
  init: (callback?: () => void) => unknown;
  getLocation: (callback: (data: TelegramLocationData | null) => void) => unknown;
  openSettings: () => unknown;
}

interface TelegramWebAppLocation {
  version?: string;
  LocationManager?: TelegramLocationManager;
}

// LocationManager landed in Bot API 8.0; on older clients init/getLocation
// silently no-op and their callbacks never fire, so we must not await them.
const MIN_VERSION = [8, 0];

// Telegram resolves its callbacks over a postMessage bridge that can go quiet
// (client backgrounded, permission dialog dismissed by swipe). Never hang on it.
const BRIDGE_TIMEOUT_MS = 20_000;

function versionAtLeast(version: string | undefined): boolean {
  if (!version) return false;
  const parts = version.split(".").map((part) => Number.parseInt(part, 10) || 0);
  for (let i = 0; i < MIN_VERSION.length; i += 1) {
    const actual = parts[i] ?? 0;
    if (actual > MIN_VERSION[i]) return true;
    if (actual < MIN_VERSION[i]) return false;
  }
  return true;
}

function locationManager(): TelegramLocationManager | null {
  if (typeof window === "undefined") return null;
  const tg = (window as unknown as { Telegram?: { WebApp?: TelegramWebAppLocation } }).Telegram
    ?.WebApp;
  if (!tg?.LocationManager || !versionAtLeast(tg.version)) return null;
  return tg.LocationManager;
}

function withTimeout<T>(run: (resolve: (value: T) => void) => void, fallback: T): Promise<T> {
  return new Promise<T>((resolve) => {
    let settled = false;
    const settle = (value: T) => {
      if (settled) return;
      settled = true;
      resolve(value);
    };
    const timer = setTimeout(() => settle(fallback), BRIDGE_TIMEOUT_MS);
    run((value) => {
      clearTimeout(timer);
      settle(value);
    });
  });
}

function ensureInited(lm: TelegramLocationManager): Promise<boolean> {
  if (lm.isInited) return Promise.resolve(true);
  return withTimeout<boolean>((resolve) => lm.init(() => resolve(true)), false);
}

function readLocation(lm: TelegramLocationManager): Promise<LocateOutcome> {
  return withTimeout<LocateOutcome>(
    (resolve) =>
      lm.getLocation((data) => {
        if (data && typeof data.latitude === "number" && typeof data.longitude === "number") {
          resolve({ kind: "located", lat: data.latitude, lon: data.longitude });
        } else {
          resolve({ kind: "denied" });
        }
      }),
    { kind: "denied" },
  );
}

function browserLocation(): Promise<LocateOutcome> {
  if (typeof navigator === "undefined" || !navigator.geolocation) {
    return Promise.resolve({ kind: "unsupported" });
  }
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) =>
        resolve({
          kind: "located",
          lat: position.coords.latitude,
          lon: position.coords.longitude,
        }),
      (error) =>
        resolve(error.code === error.PERMISSION_DENIED ? { kind: "denied" } : { kind: "unsupported" }),
      { enableHighAccuracy: true, timeout: BRIDGE_TIMEOUT_MS },
    );
  });
}

export async function locate(): Promise<LocateOutcome> {
  const lm = locationManager();
  if (!lm) return browserLocation();

  try {
    if (!(await ensureInited(lm))) return browserLocation();

    // Desktop and web clients report no location hardware; the browser API still works there.
    if (!lm.isLocationAvailable) return browserLocation();

    // A prior denial sticks until cleared in Telegram's own settings — getLocation
    // would just resolve null forever, so send the user there instead.
    if (lm.isAccessRequested && !lm.isAccessGranted) {
      lm.openSettings();
      return { kind: "settings-opened" };
    }

    return await readLocation(lm);
  } catch {
    return browserLocation();
  }
}
