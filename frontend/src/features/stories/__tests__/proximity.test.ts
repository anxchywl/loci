import { describe, expect, it } from "vitest";

import {
  adjacentNeighbors,
  circularNeighbors,
  sortPinsByAnchor,
  sortPinsByProximity,
} from "@/features/stories/proximity";

const pins = [
  { id: "far", lat: 10, lon: 10 },
  { id: "here", lat: 0, lon: 0 },
  { id: "near", lat: 0.1, lon: 0 },
  { id: "mid", lat: 1, lon: 0 },
];

describe("sortPinsByProximity", () => {
  it("orders visible pins nearest-first around the open story", () => {
    const order = sortPinsByProximity(pins, "here").map((p) => p.id);
    expect(order).toEqual(["here", "near", "mid", "far"]);
  });

  it("weights longitude by cos(lat) so east-west distance shrinks near the poles", () => {
    // at 60°N, cos(lat)=0.5, so 1° of longitude ≈ 0.5° of latitude on the ground
    const polar = [
      { id: "open", lat: 60, lon: 0 },
      { id: "east", lat: 60, lon: 1.6 }, // ~0.8° effective
      { id: "north", lat: 61, lon: 0 }, // 1.0° effective
    ];
    const order = sortPinsByProximity(polar, "open").map((p) => p.id);
    expect(order).toEqual(["open", "east", "north"]);
  });

  it("returns [] when the open story is not among the pins (stale/off-screen)", () => {
    expect(sortPinsByProximity(pins, "deleted")).toEqual([]);
  });

  it("returns just the story when it is the only visible pin", () => {
    const solo = [{ id: "only", lat: 5, lon: 5 }];
    expect(sortPinsByProximity(solo, "only").map((p) => p.id)).toEqual(["only"]);
  });
});

describe("sortPinsByAnchor", () => {
  it("orders pins nearest-first around a fixed anchor point", () => {
    const order = sortPinsByAnchor(pins, { lat: 0, lon: 0 }).map((p) => p.id);
    expect(order).toEqual(["here", "near", "mid", "far"]);
  });

  it("keeps a stable order as the user hops outward (no ping-pong)", () => {
    // anchor is the first opened story ("here"). Walking next → near → mid → far,
    // the ordering must not re-centre on the current story: from "near", the next
    // story must still be "mid" (farther from the anchor), never back to "here".
    const anchor = { lat: 0, lon: 0 };
    const tour = sortPinsByAnchor(pins, anchor);
    expect(adjacentNeighbors(tour, "near").next?.id).toBe("mid");
    expect(adjacentNeighbors(tour, "mid").next?.id).toBe("far");
    // contrast: re-centring on the current story sorts around "near", so its
    // own "next" becomes "here" — a backward hop, the ping-pong we avoid
    expect(adjacentNeighbors(sortPinsByProximity(pins, "near"), "near").next?.id).toBe("here");
  });
});

describe("adjacentNeighbors", () => {
  const ordered = sortPinsByProximity(pins, "here"); // here, near, mid, far

  it("returns null prev at the first story and a next", () => {
    const { prev, next } = adjacentNeighbors(ordered, "here");
    expect(prev).toBeNull();
    expect(next?.id).toBe("near");
  });

  it("returns both neighbours in the middle", () => {
    const { prev, next } = adjacentNeighbors(ordered, "mid");
    expect(prev?.id).toBe("near");
    expect(next?.id).toBe("far");
  });

  it("returns null next at the last story", () => {
    const { prev, next } = adjacentNeighbors(ordered, "far");
    expect(prev?.id).toBe("mid");
    expect(next).toBeNull();
  });

  it("returns no neighbours for a missing or null story id", () => {
    expect(adjacentNeighbors(ordered, "gone")).toEqual({ prev: null, next: null });
    expect(adjacentNeighbors(ordered, null)).toEqual({ prev: null, next: null });
  });

  it("returns no neighbours when only one story is visible", () => {
    const solo = sortPinsByProximity([{ id: "only", lat: 0, lon: 0 }], "only");
    expect(adjacentNeighbors(solo, "only")).toEqual({ prev: null, next: null });
  });
});

describe("circularNeighbors", () => {
  const ordered = sortPinsByProximity(pins, "here");

  it("wraps previous from the first story to the last", () => {
    expect(circularNeighbors(ordered, "here").prev?.id).toBe("far");
  });

  it("wraps next from the last story to the first", () => {
    expect(circularNeighbors(ordered, "far").next?.id).toBe("here");
  });

  it("hides navigation when only one story is available", () => {
    expect(circularNeighbors([{ id: "only", lat: 0, lon: 0 }], "only")).toEqual({ prev: null, next: null });
  });
});
