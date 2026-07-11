"use client";

import { BookmarkX, MapPinned, RotateCw } from "lucide-react";

import type { Story } from "@/features/stories/api";
import { StoryListItem } from "@/features/stories/components/story-list-item";
import { useCategories, useResubmitStory } from "@/features/stories/hooks";
import { useMyBookmarks, useMyStories } from "@/features/profile/hooks";
import { useDict } from "@/lib/i18n/use-dict";

interface PanelProps {
  authenticated: boolean;
  onOpen: (story: Story) => void;
}

function EmptyState({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="flex min-h-40 flex-col items-center justify-center gap-2 py-12 text-center animate-fade-in">
      {icon}
      <span className="text-[13px] text-muted">{text}</span>
    </div>
  );
}

/** Author's own stories with moderation status + resubmit for rejected ones. */
export function MyStoriesPanel({ authenticated, onOpen }: PanelProps) {
  const t = useDict();
  const { data: categories = [] } = useCategories();
  const { data: stories, isLoading } = useMyStories(authenticated);
  const resubmit = useResubmitStory();

  if (!authenticated) {
    return <EmptyState icon={<MapPinned size={24} className="text-muted" />} text={t.openInTelegram} />;
  }
  if (isLoading && !stories) {
    return <div className="py-12 text-center text-[13px] text-muted">{t.loading}</div>;
  }
  if (!stories || stories.length === 0) {
    return <EmptyState icon={<MapPinned size={24} className="text-muted" />} text={t.noStoriesYet} />;
  }

  return (
    <div className="px-1 animate-fade-in">
      {stories.map((story) => (
        <div key={story.id}>
          <StoryListItem
            story={story}
            categories={categories}
            onOpen={() => onOpen(story)}
            showStatus
          />
          {story.moderation_status === "rejected" && (
            <button
              onClick={() => resubmit.mutate(story.id)}
              disabled={resubmit.isPending}
              className="mb-2 flex items-center gap-1.5 text-[13px] font-medium text-accent disabled:opacity-50"
            >
              <RotateCw size={14} /> {t.resubmit}
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

/** Stories the viewer has bookmarked. */
export function SavedPanel({ authenticated, onOpen }: PanelProps) {
  const t = useDict();
  const { data: categories = [] } = useCategories();
  const { data: stories, isLoading } = useMyBookmarks(authenticated);

  if (!authenticated) {
    return <EmptyState icon={<BookmarkX size={24} className="text-muted" />} text={t.openInTelegram} />;
  }
  if (isLoading && !stories) {
    return <div className="py-12 text-center text-[13px] text-muted">{t.loading}</div>;
  }
  if (!stories || stories.length === 0) {
    return <EmptyState icon={<BookmarkX size={24} className="text-muted" />} text={t.noSavedYet} />;
  }

  return (
    <div className="px-1 animate-fade-in">
      {stories.map((story) => (
        <StoryListItem
          key={story.id}
          story={story}
          categories={categories}
          onOpen={() => onOpen(story)}
        />
      ))}
    </div>
  );
}
