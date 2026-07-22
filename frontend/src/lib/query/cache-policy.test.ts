import { describe, expect, it } from "vitest";

import { queryKeys } from "./cache-policy";

describe("query keys", () => {
  it("is stable for equivalent parameter objects", () => {
    expect(queryKeys.stories.map({ minLat: 1, minLon: 2, maxLat: 3, maxLon: 4, categoryId: null }))
      .toEqual(queryKeys.stories.map({ minLat: 1, minLon: 2, maxLat: 3, maxLon: 4, categoryId: null }));
  });

  it("keeps account-scoped data in explicit namespaces", () => {
    expect(queryKeys.profile.stories).toEqual(["profile", "stories"]);
    expect(queryKeys.profile.bookmarks).toEqual(["profile", "bookmarks"]);
  });
});
