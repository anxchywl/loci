import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { Story } from "@/features/stories/api";
import { ReactionButton } from "@/features/stories/components/reaction-button";
import { renderWithQuery } from "@/test/utils";

vi.mock("@/features/stories/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/stories/api")>()),
  addReaction: vi.fn(),
  removeReaction: vi.fn(),
}));

import { addReaction } from "@/features/stories/api";

const story = {
  id: "story-1",
  reaction_count: 3,
  viewer_reacted: false,
} as Story;

function renderButton() {
  const view = renderWithQuery(
    <ReactionButton storyId={story.id} reacted={story.viewer_reacted} count={story.reaction_count} />,
  );
  view.queryClient.setQueryData(["story", story.id], story);
  return view;
}

describe("ReactionButton", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("optimistically increments the cached count before the request resolves", async () => {
    let resolveRequest: () => void = () => {};
    vi.mocked(addReaction).mockImplementation(
      () => new Promise((resolve) => (resolveRequest = () => resolve())),
    );

    const { queryClient } = renderButton();
    fireEvent.click(screen.getByRole("button", { name: "react" }));

    await waitFor(() => {
      const cached = queryClient.getQueryData<Story>(["story", story.id]);
      expect(cached?.reaction_count).toBe(4);
      expect(cached?.viewer_reacted).toBe(true);
    });

    resolveRequest();
    await waitFor(() => expect(addReaction).toHaveBeenCalledWith("story-1"));
  });

  it("rolls the cache back when the request fails", async () => {
    vi.mocked(addReaction).mockRejectedValue(new Error("nope"));

    const { queryClient } = renderButton();
    fireEvent.click(screen.getByRole("button", { name: "react" }));

    await waitFor(() => {
      const cached = queryClient.getQueryData<Story>(["story", story.id]);
      expect(cached?.reaction_count).toBe(3);
      expect(cached?.viewer_reacted).toBe(false);
    });
  });
});
