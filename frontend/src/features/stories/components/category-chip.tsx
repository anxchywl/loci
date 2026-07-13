"use client";

import type { Category } from "@/features/stories/api";
import { categoryIcons } from "@/lib/icons/category-glyphs";
import { useDict } from "@/lib/i18n/use-dict";

interface CategoryChipProps {
  category: Category;
  selected: boolean;
  onClick: () => void;
}

export function CategoryChip({ category, selected, onClick }: CategoryChipProps) {
  const t = useDict();
  const Icon = categoryIcons[category.slug];
  return (
    <button
      onClick={onClick}
      aria-pressed={selected}
      className="flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-[13px] font-medium transition-colors duration-200 ease-lm lg:gap-2 lg:px-3.5 lg:py-2 lg:text-[14px]"
      style={
        selected
          ? { backgroundColor: category.color, borderColor: category.color, color: "#ffffff" }
          : {
              backgroundColor: "var(--lm-bg)",
              borderColor: "var(--lm-border)",
              color: "var(--lm-text)",
            }
      }
    >
      <Icon size={14} color={selected ? "#ffffff" : category.color} />
      {t.categories[category.slug]}
    </button>
  );
}
