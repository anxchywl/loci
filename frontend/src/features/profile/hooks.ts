"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchMyBookmarks, fetchMyStories } from "@/features/profile/api";
import { cachePolicy, queryKeys } from "@/lib/query/cache-policy";

export function useMyStories(enabled: boolean) {
  return useQuery({ queryKey: queryKeys.profile.stories, queryFn: fetchMyStories, enabled, ...cachePolicy.profile });
}

export function useMyBookmarks(enabled: boolean) {
  return useQuery({ queryKey: queryKeys.profile.bookmarks, queryFn: fetchMyBookmarks, enabled, ...cachePolicy.profile });
}
