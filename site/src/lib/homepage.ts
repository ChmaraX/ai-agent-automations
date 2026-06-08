import type { AutomationEntry } from './automations';

export type FilterOption = {
  label: string;
  count: number;
};

export type HomepageData = {
  automations: AutomationEntry[];
  categories: FilterOption[];
  surfaces: FilterOption[];
};

function toFilterOptions(labels: string[]): FilterOption[] {
  const counts = new Map<string, number>();

  for (const label of labels) {
    counts.set(label, (counts.get(label) ?? 0) + 1);
  }

  return [...counts.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([label, count]) => ({ label, count }));
}

export function buildHomepageData(automations: AutomationEntry[]): HomepageData {
  return {
    automations,
    categories: toFilterOptions(automations.flatMap((entry) => entry.categories)),
    surfaces: toFilterOptions(automations.flatMap((entry) => entry.surfaces)),
  };
}
