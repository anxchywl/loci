import maplibregl, { Map as MapLibreMap } from "maplibre-gl";

import { categoryGlyphSvg } from "@/lib/icons/category-glyphs";
import type { CategorySlug } from "@/lib/i18n/dict";

export const MAP_STYLE_URL = "https://tiles.openfreemap.org/styles/positron";

export const DEFAULT_CENTER: [number, number] = [76.889709, 43.238949];
export const DEFAULT_ZOOM = 11;

export interface CategoryStyle {
  id: number;
  slug: CategorySlug;
  color: string;
}

export function createMap(container: HTMLElement): MapLibreMap {
  return new maplibregl.Map({
    container,
    style: MAP_STYLE_URL,
    center: DEFAULT_CENTER,
    zoom: DEFAULT_ZOOM,
    attributionControl: false,
  });
}

function rasterizeSvg(svg: string, size: number): Promise<ImageBitmap> {
  const blob = new Blob([svg], { type: "image/svg+xml" });
  const url = URL.createObjectURL(blob);
  return new Promise((resolve, reject) => {
    const image = new Image(size, size);
    image.onload = () => {
      URL.revokeObjectURL(url);
      createImageBitmap(image, { resizeWidth: size, resizeHeight: size })
        .then(resolve)
        .catch(reject);
    };
    image.onerror = reject;
    image.src = url;
  });
}

export async function addCategoryGlyphImages(
  map: MapLibreMap,
  categories: CategoryStyle[],
): Promise<void> {
  await Promise.all(
    categories.map(async (category) => {
      const imageId = `glyph-${category.id}`;
      if (map.hasImage(imageId)) return;
      const bitmap = await rasterizeSvg(categoryGlyphSvg(category.slug), 48);
      if (!map.hasImage(imageId)) {
        map.addImage(imageId, bitmap, { pixelRatio: 2 });
      }
    }),
  );
}

export function colorMatchExpression(
  categories: CategoryStyle[],
): maplibregl.ExpressionSpecification {
  const pairs = categories.flatMap((category) => [category.id, category.color]);
  return ["match", ["get", "category_id"], ...pairs, "#888888"] as never;
}
