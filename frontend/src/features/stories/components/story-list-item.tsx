"use client";

import { Heart } from "lucide-react";

import { authorLabel, formatDistance, type Category, type Story } from "@/features/stories/api";
import { categoryIcons } from "@/lib/icons/category-glyphs";
import { useDict } from "@/lib/i18n/use-dict";
import { useUiStore } from "@/stores/ui-store";

interface StoryListItemProps {
  story: Story;
  categories: Category[];
  onOpen: (id: string) => void;
  showStatus?: boolean;
  /** approximate distance from the viewer; shown by the Nearby list */
  distanceMeters?: number;
}

const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

/** Compact age of a story ("23h"), localized via Intl. */
function useRelativeTime(iso: string): string {
  const locale = useUiStore((s) => s.locale);
  const elapsed = Date.now() - new Date(iso).getTime();
  const format = (value: number, unit: Intl.RelativeTimeFormatUnit) =>
    new Intl.RelativeTimeFormat(locale, { numeric: "always", style: "narrow" })
      .format(-value, unit);

  if (elapsed < HOUR) return format(Math.max(1, Math.round(elapsed / MINUTE)), "minute");
  if (elapsed < DAY) return format(Math.round(elapsed / HOUR), "hour");
  if (elapsed < 30 * DAY) return format(Math.round(elapsed / DAY), "day");
  return format(Math.round(elapsed / (30 * DAY)), "month");
}

export function StoryListItem({
  story,
  categories,
  onOpen,
  showStatus = false,
  distanceMeters,
}: StoryListItemProps) {
  const t = useDict();
  const locale = useUiStore((s) => s.locale);
  const age = useRelativeTime(story.created_at);
  const category = categories.find((c) => c.id === story.category_id);
  const Icon = category ? categoryIcons[category.slug] : null;
  const author = authorLabel(story.author);

  const statusLabel =
    story.moderation_status === "pending"
      ? t.statusPending
      : story.moderation_status === "rejected"
        ? t.statusRejected
        : t.statusApproved;
  // status is carried by one word in its own color — no filled band, no chip
  const statusColor =
    story.moderation_status === "rejected"
      ? "text-[#E5484D]"
      : story.moderation_status === "pending"
        ? "text-amber-600 dark:text-amber-500"
        : "text-emerald-600 dark:text-emerald-500";

  return (
    <button
      onClick={() => onOpen(story.id)}
      className="flex w-full items-start gap-3 border-b border-border py-3 text-left transition-colors duration-150 ease-lm last:border-b-0 active:bg-surface"
    >
      {category && Icon && (
        <span
          className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
          style={{ backgroundColor: category.color }}
        >
          <Icon size={16} color="#ffffff" />
        </span>
      )}
      <span className="min-w-0 flex-1">
        <span className="flex items-baseline gap-2">
          <span className="min-w-0 flex-1 truncate text-[15px] font-semibold">{story.title}</span>
          {showStatus && (
            <span className="shrink-0 whitespace-nowrap text-[12px] text-muted">{age}</span>
          )}
        </span>
        <span className="block truncate text-[13px] text-muted">{story.body}</span>
        <span className="mt-1 flex items-center gap-3 text-[13px] text-muted">
          {showStatus && (
            <span className={`shrink-0 font-medium ${statusColor}`}>{statusLabel}</span>
          )}
          {distanceMeters !== undefined && (
            <span className="shrink-0 font-medium">{formatDistance(distanceMeters, locale)}</span>
          )}
          <span className="flex items-center gap-1">
            <Heart size={13} /> {story.reaction_count}
          </span>
          {author && <span className="truncate">{author}</span>}
        </span>
        {showStatus && story.moderation_status === "rejected" && story.rejection_reason && (
          <span className="story-rejection mt-1 block text-[12px] text-[#E5484D]">
            {t.reasonLabel}: {story.rejection_reason}
          </span>
        )}
      </span>
    </button>
  );
}
