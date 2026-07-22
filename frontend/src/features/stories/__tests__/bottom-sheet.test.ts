import { describe, expect, it } from "vitest";

import { swipeDirection } from "@/features/stories/components/bottom-sheet";

describe("story sheet swipe direction", () => {
  it("maps a left swipe to next", () => {
    expect(swipeDirection(-100, 10)).toBe("next");
  });

  it("maps a right swipe to previous", () => {
    expect(swipeDirection(100, 10)).toBe("prev");
  });

  it("ignores short and predominantly vertical gestures", () => {
    expect(swipeDirection(50, 0)).toBeNull();
    expect(swipeDirection(100, 140)).toBeNull();
  });
});
