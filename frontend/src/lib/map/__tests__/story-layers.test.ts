import { describe, expect, it } from "vitest";

import { pointIconSizeExpression } from "@/lib/map/story-layers";

describe("point icon size expression", () => {
  it("keeps zoom interpolation at the top level when selecting a story", () => {
    const expression = pointIconSizeExpression("story-1") as unknown[];
    expect(expression[0]).toBe("interpolate");
    expect(expression[2]).toEqual(["zoom"]);
    expect(JSON.stringify(expression).match(/interpolate/g)).toHaveLength(1);
  });
});
