"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type QueryKey,
} from "@tanstack/react-query";

import {
  addBookmark,
  addReaction,
  createStory,
  deleteStory,
  fetchBboxStories,
  fetchCategories,
  fetchComments,
  fetchStory,
  fetchTrending,
  postComment,
  removeBookmark,
  removeReaction,
  reportStory,
  searchStories,
  uploadStoryPhoto,
  type BboxParams,
  type CreateStoryInput,
  type Story,
} from "@/features/stories/api";

export function useCategories() {
  return useQuery({ queryKey: ["categories"], queryFn: fetchCategories, staleTime: Infinity });
}

export function useBboxStories(params: BboxParams | null) {
  return useQuery({
    queryKey: ["stories", "bbox", params],
    queryFn: () => fetchBboxStories(params!),
    enabled: params !== null,
    placeholderData: (previous) => previous,
  });
}

export function useTrending(enabled: boolean) {
  return useQuery({ queryKey: ["stories", "trending"], queryFn: fetchTrending, enabled });
}

export function useSearch(query: string) {
  return useQuery({
    queryKey: ["stories", "search", query],
    queryFn: () => searchStories(query),
    enabled: query.trim().length >= 2,
    placeholderData: (previous) => previous,
  });
}

export function useStory(id: string | null) {
  return useQuery({
    queryKey: ["story", id],
    queryFn: () => fetchStory(id!),
    enabled: id !== null,
  });
}

export function useComments(storyId: string | null) {
  return useQuery({
    queryKey: ["comments", storyId],
    queryFn: () => fetchComments(storyId!),
    enabled: storyId !== null,
  });
}

export function useCreateStory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateStoryInput & { photos: File[] }) => {
      const { photos, ...payload } = input;
      const story = await createStory(payload);
      for (const file of photos) {
        await uploadStoryPhoto(story.id, file);
      }
      return story;
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["stories"] });
    },
  });
}

export function useDeleteStory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteStory,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["stories"] });
    },
  });
}

function patchStory(
  queryClient: ReturnType<typeof useQueryClient>,
  storyId: string,
  patch: (story: Story) => Story,
): { key: QueryKey; previous: Story | undefined } {
  const key: QueryKey = ["story", storyId];
  const previous = queryClient.getQueryData<Story>(key);
  if (previous) queryClient.setQueryData(key, patch(previous));
  return { key, previous };
}

export function useReaction(storyId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (reacted: boolean) =>
      reacted ? removeReaction(storyId) : addReaction(storyId),
    onMutate: (reacted: boolean) =>
      patchStory(queryClient, storyId, (story) => ({
        ...story,
        viewer_reacted: !reacted,
        reaction_count: story.reaction_count + (reacted ? -1 : 1),
      })),
    onError: (_error, _variables, context) => {
      if (context?.previous) queryClient.setQueryData(context.key, context.previous);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["story", storyId] });
    },
  });
}

export function useBookmark(storyId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (bookmarked: boolean) =>
      bookmarked ? removeBookmark(storyId) : addBookmark(storyId),
    onMutate: (bookmarked: boolean) =>
      patchStory(queryClient, storyId, (story) => ({
        ...story,
        viewer_bookmarked: !bookmarked,
      })),
    onError: (_error, _variables, context) => {
      if (context?.previous) queryClient.setQueryData(context.key, context.previous);
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["story", storyId] });
    },
  });
}

export function usePostComment(storyId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: string) => postComment(storyId, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["comments", storyId] });
      void queryClient.invalidateQueries({ queryKey: ["story", storyId] });
    },
  });
}

export function useReportStory(storyId: string) {
  return useMutation({ mutationFn: (reason: string | null) => reportStory(storyId, reason) });
}
