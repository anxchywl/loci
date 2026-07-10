import { dict } from "@/lib/i18n/dict";
import { useUiStore } from "@/stores/ui-store";

export function useDict() {
  const locale = useUiStore((state) => state.locale);
  return dict[locale];
}
