import type { AuthUser } from "@/features/auth/api";
import type { Story } from "@/features/stories/api";
import { apiFetch } from "@/lib/api";

export function fetchMe(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/profile/me");
}

export function fetchMyStories(): Promise<Story[]> {
  return apiFetch<Story[]>("/profile/me/stories");
}

export function fetchMyBookmarks(): Promise<Story[]> {
  return apiFetch<Story[]>("/profile/me/bookmarks");
}
