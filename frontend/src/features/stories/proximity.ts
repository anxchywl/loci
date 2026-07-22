import type { AdjacentPin } from "@/stores/ui-store";

interface LatLon {
  id: string;
  lat: number;
  lon: number;
}

// squared degree distance with longitude weighted by cos(lat), so ordering
// approximates ground distance away from the equator. good enough for
// nearest-first ordering; not a true geodesic and not antimeridian-aware
function squaredDistance(
  a: { lat: number; lon: number },
  b: { lat: number; lon: number },
  cosLat: number,
): number {
  return (a.lat - b.lat) ** 2 + ((a.lon - b.lon) * cosLat) ** 2;
}

// order the visible pins nearest-first around a fixed anchor point. keeping the
// anchor fixed as the user hops between stories is what makes prev/next a stable
// nearest→farthest tour instead of re-centring on each story (which ping-pongs
// between the two closest pins)
export function sortPinsByAnchor(pins: LatLon[], anchor: { lat: number; lon: number }): AdjacentPin[] {
  const cosLat = Math.cos((anchor.lat * Math.PI) / 180);
  return [...pins]
    .sort((a, b) => squaredDistance(a, anchor, cosLat) - squaredDistance(b, anchor, cosLat))
    .map((p) => ({ id: p.id, lat: p.lat, lon: p.lon }));
}

// order the visible pins nearest-first around the open story. returns [] when
// the open story isn't among the pins (opened off-screen / from a list, or a
// clustered view) so callers never surface stale or unrelated neighbours
export function sortPinsByProximity(pins: LatLon[], currentId: string): AdjacentPin[] {
  const current = pins.find((p) => p.id === currentId);
  if (!current) return [];
  return sortPinsByAnchor(pins, { lat: current.lat, lon: current.lon });
}

// nearest untraversed neighbours on either side of the open story in a
// proximity-ordered list. null at the ends and when the story isn't present
export function adjacentNeighbors(
  pins: AdjacentPin[],
  currentId: string | null,
): { prev: AdjacentPin | null; next: AdjacentPin | null } {
  const index = currentId ? pins.findIndex((p) => p.id === currentId) : -1;
  if (index < 0) return { prev: null, next: null };
  return {
    prev: index > 0 ? pins[index - 1] : null,
    next: index < pins.length - 1 ? pins[index + 1] : null,
  };
}

export function circularNeighbors(
  pins: AdjacentPin[],
  currentId: string | null,
): { prev: AdjacentPin | null; next: AdjacentPin | null } {
  const index = currentId ? pins.findIndex((p) => p.id === currentId) : -1;
  if (index < 0 || pins.length < 2) return { prev: null, next: null };
  return {
    prev: pins[(index - 1 + pins.length) % pins.length],
    next: pins[(index + 1) % pins.length],
  };
}
