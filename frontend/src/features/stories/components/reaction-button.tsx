"use client";

import { Heart } from "lucide-react";

import { useReaction } from "@/features/stories/hooks";

interface ReactionButtonProps {
  storyId: string;
  reacted: boolean;
  count: number;
  disabled?: boolean;
}

export function ReactionButton({ storyId, reacted, count, disabled }: ReactionButtonProps) {
  const mutation = useReaction(storyId);
  return (
    <button
      aria-label="react"
      aria-pressed={reacted}
      disabled={disabled}
      onClick={() => mutation.mutate(reacted)}
      className="flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-[13px] font-medium transition-transform duration-150 ease-lm active:scale-95 disabled:opacity-50"
    >
      <Heart
        size={16}
        fill={reacted ? "#E5484D" : "none"}
        color={reacted ? "#E5484D" : "currentColor"}
      />
      <span data-testid="reaction-count">{count}</span>
    </button>
  );
}
