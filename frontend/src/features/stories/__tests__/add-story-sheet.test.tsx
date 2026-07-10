import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AddStorySheet } from "@/features/stories/add-story-sheet";
import type { Category, Story } from "@/features/stories/api";
import { renderWithQuery } from "@/test/utils";
import { useUiStore } from "@/stores/ui-store";

const categories: Category[] = [
  { id: 1, slug: "love", color: "#E5484D", icon: "heart", position: 1 },
  { id: 6, slug: "travel", color: "#0BA5EC", icon: "plane", position: 6 },
];

const createdStory = { id: "story-1" } as Story;

vi.mock("@/features/stories/api", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/features/stories/api")>()),
  fetchCategories: vi.fn(() => Promise.resolve(categories)),
  createStory: vi.fn(() => Promise.resolve(createdStory)),
  uploadStoryPhoto: vi.fn(() => Promise.resolve()),
}));

import { createStory } from "@/features/stories/api";

describe("AddStorySheet", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useUiStore.setState({
      mode: "compose",
      pickedLocation: { lat: 43.2, lon: 76.9 },
      openStoryId: null,
    });
  });

  async function fillRequiredFields() {
    fireEvent.click(await screen.findByRole("button", { name: /love/i }));
    fireEvent.change(screen.getByLabelText("Title"), { target: { value: "First kiss" } });
    fireEvent.change(screen.getByLabelText("Story"), { target: { value: "It rained." } });
  }

  it("keeps publish disabled until category, title and body are set", async () => {
    renderWithQuery(<AddStorySheet />);
    const publish = screen.getByRole("button", { name: "Publish" });
    expect(publish).toBeDisabled();

    await fillRequiredFields();
    expect(publish).toBeEnabled();
  });

  it("publishes with privacy-first defaults: approximate location, public, not anonymous", async () => {
    renderWithQuery(<AddStorySheet />);
    await fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: "Publish" }));

    await waitFor(() => expect(createStory).toHaveBeenCalledOnce());
    expect(createStory).toHaveBeenCalledWith(
      expect.objectContaining({
        category_id: 1,
        title: "First kiss",
        body: "It rained.",
        lat: 43.2,
        lon: 76.9,
        location_precision: "approx",
        visibility: "public",
        is_anonymous: false,
      }),
    );
  });

  it("privacy toggles switch precision to exact and visibility to private", async () => {
    renderWithQuery(<AddStorySheet />);
    await fillRequiredFields();

    fireEvent.click(screen.getByRole("radio", { name: "Exact" }));
    fireEvent.click(screen.getByRole("radio", { name: "Only me" }));
    fireEvent.click(screen.getByLabelText("Post anonymously"));
    fireEvent.click(screen.getByRole("button", { name: "Publish" }));

    await waitFor(() => expect(createStory).toHaveBeenCalledOnce());
    expect(createStory).toHaveBeenCalledWith(
      expect.objectContaining({
        location_precision: "exact",
        visibility: "private",
        is_anonymous: true,
      }),
    );
  });

  it("opens the created story and leaves compose mode after publishing", async () => {
    renderWithQuery(<AddStorySheet />);
    await fillRequiredFields();
    fireEvent.click(screen.getByRole("button", { name: "Publish" }));

    await waitFor(() => {
      expect(useUiStore.getState().mode).toBe("browse");
      expect(useUiStore.getState().openStoryId).toBe("story-1");
    });
  });
});
