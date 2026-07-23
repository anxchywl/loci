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
  const statusStrip =
    story.moderation_status === "rejected"
      ? "bg-[#E5484D]/15 text-[#C62A2F] dark:text-[#FF9592]"
      : story.moderation_status === "pending"
        ? "bg-amber-500/20 text-amber-800 dark:text-amber-300"
        : "bg-emerald-500/20 text-emerald-800 dark:text-emerald-300";

  // Author-facing card: thumbnail, title block, age, and a full-width footer
  // in the moderation colour — the layout the companion Flutter app uses.
  if (showStatus) {
    const thumb = story.photos[0]?.thumb_url ?? story.photos[0]?.url ?? null;
    return (
      <button
        onClick={() => onOpen(story.id)}
        className="mb-2.5 block w-full overflow-hidden rounded-xl border border-border text-left transition-transform duration-150 ease-lm active:scale-[0.995]"
      >
        <span className="flex items-start gap-3 p-3">
          <span
            className="flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-surface"
            style={category ? { backgroundColor: `${category.color}14` } : undefined}
          >
            {thumb ? (
              /* eslint-disable-next-line @next/next/no-img-element */
              <img src={thumb} alt="" className="h-full w-full object-cover" />
            ) : (
              Icon && <Icon size={20} color={category?.color} strokeWidth={1.75} />
            )}
          </span>
          <span className="min-w-0 flex-1">
            <span className="flex items-baseline gap-2">
              <span className="min-w-0 flex-1 truncate text-[15px] font-semibold">{story.title}</span>
              <span className="shrink-0 whitespace-nowrap text-[12px] text-muted">{age}</span>
            </span>
            <span className="mt-0.5 block truncate text-[13px] text-muted">{story.body}</span>
            <span className="mt-1.5 flex items-center gap-3 text-[12px] text-muted">
              <span className="flex items-center gap-1">
                <Heart size={12} /> {story.reaction_count}
              </span>
              {author && <span className="truncate">{author}</span>}
            </span>
          </span>
        </span>
        <span className={`block px-3 py-2 text-[13px] font-medium ${statusStrip}`}>
          {statusLabel}
          {story.moderation_status === "rejected" && story.rejection_reason && (
            <span className="story-rejection mt-0.5 block text-[12px] font-normal opacity-90">
              {t.reasonLabel}: {story.rejection_reason}
            </span>
          )}
        </span>
      </button>
    );
  }

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
        <span className="block truncate text-[15px] font-semibold">{story.title}</span>
        <span className="block truncate text-[13px] text-muted">{story.body}</span>
        <span className="mt-1 flex items-center gap-3 text-[13px] text-muted">
          {distanceMeters !== undefined && (
            <span className="shrink-0 font-medium">{formatDistance(distanceMeters, locale)}</span>
          )}
          <span className="flex items-center gap-1">
            <Heart size={13} /> {story.reaction_count}
          </span>
          {author && <span className="truncate">{author}</span>}
        </span>
      </span>
    </button>
  );
}
