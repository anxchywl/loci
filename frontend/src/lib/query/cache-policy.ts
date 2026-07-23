import type { BboxParams, ClusterParams, NearbyParams } from "@/features/stories/api";

export const queryKeys = {
  categories: ["categories"] as const,
  story: (id: string) => ["story", id] as const,
  comments: (storyId: string) => ["comments", storyId] as const,
  stories: {
    root: ["stories"] as const,
    bbox: (params: BboxParams) => ["stories", "bbox", params] as const,
    map: (params: BboxParams) => ["stories", "map", params] as const,
    worldMap: (categoryId: number | null) => ["stories", "world-map", categoryId] as const,
    clusters: (params: ClusterParams) => ["stories", "map-clusters", params] as const,
    trending: ["stories", "trending"] as const,
    nearby: (params: NearbyParams) => ["stories", "nearby", params] as const,
    search: (query: string) => ["stories", "search", query] as const,
  },
  profile: {
    root: ["profile"] as const,
    stories: ["profile", "stories"] as const,
    bookmarks: ["profile", "bookmarks"] as const,
  },
  admin: ["admin"] as const,
} as const;

export const cachePolicy = {
  categories: { staleTime: Infinity, gcTime: 24 * 60 * 60 * 1000 },
  story: { staleTime: 30_000, gcTime: 10 * 60_000 },
  comments: { staleTime: 15_000, gcTime: 5 * 60_000 },
  map: { staleTime: 30_000, gcTime: 5 * 60_000 },
  clusters: { staleTime: 60_000, gcTime: 5 * 60_000 },
  discovery: { staleTime: 30_000, gcTime: 5 * 60_000 },
  profile: { staleTime: 15_000, gcTime: 5 * 60_000 },
} as const;
