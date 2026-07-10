import {
  Baby,
  Briefcase,
  Camera,
  Ghost,
  GraduationCap,
  Heart,
  Mountain,
  Plane,
  Smile,
  Sparkles,
  Trophy,
  Users,
  type LucideIcon,
} from "lucide-react";
import { icons as lucideIconData } from "lucide";

import type { CategorySlug } from "@/lib/i18n/dict";

// react components for ui chrome and the raw node data for map marker rasterization
// come from the same lucide set — DESIGN.md pins the slug → glyph mapping
export const categoryIcons: Record<CategorySlug, LucideIcon> = {
  love: Heart,
  happy_moments: Smile,
  dreams: Sparkles,
  education: GraduationCap,
  career: Briefcase,
  travel: Plane,
  friendship: Users,
  childhood: Baby,
  achievements: Trophy,
  beautiful_places: Mountain,
  memories: Camera,
  urban_legends: Ghost,
};

const glyphNames: Record<CategorySlug, keyof typeof lucideIconData> = {
  love: "Heart",
  happy_moments: "Smile",
  dreams: "Sparkles",
  education: "GraduationCap",
  career: "Briefcase",
  travel: "Plane",
  friendship: "Users",
  childhood: "Baby",
  achievements: "Trophy",
  beautiful_places: "Mountain",
  memories: "Camera",
  urban_legends: "Ghost",
};

type IconAttrs = Record<string, string | number>;
type IconChild = readonly [string, IconAttrs];
// lucide exports each icon as the full element tuple, children at index 2 —
// not as a bare list of children
type IconNode = readonly [string, IconAttrs, readonly IconChild[]];

function nodeToSvgBody(children: readonly IconChild[]): string {
  return children
    .map(([tag, attrs]) => {
      const rendered = Object.entries(attrs)
        .map(([key, value]) => `${key}="${value}"`)
        .join(" ");
      return `<${tag} ${rendered}/>`;
    })
    .join("");
}

export function categoryGlyphSvg(slug: CategorySlug, color = "#ffffff"): string {
  const node = lucideIconData[glyphNames[slug]] as unknown as IconNode;
  const children = node[2] ?? [];
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" ` +
    `stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">` +
    nodeToSvgBody(children) +
    `</svg>`
  );
}
