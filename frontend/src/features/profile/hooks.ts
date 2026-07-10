"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchMyBookmarks, fetchMyStories } from "@/features/profile/api";

export function useMyStories(enabled: boolean) {
  return useQuery({ queryKey: ["profile", "stories"], queryFn: fetchMyStories, enabled });
}

export function useMyBookmarks(enabled: boolean) {
  return useQuery({ queryKey: ["profile", "bookmarks"], queryFn: fetchMyBookmarks, enabled });
}
