import { readFileSync, readdirSync, type Dirent } from 'node:fs';
import { resolve } from 'node:path';

export type AutomationEntry = {
  slug: string;
  title: string;
  description: string;
  categories: string[];
  surfaces: string[];
};

type RawAutomationMeta = {
  title?: unknown;
  description?: unknown;
  categories?: unknown;
  surfaces?: unknown;
};

const automationsDir = resolve(process.cwd(), '../automations');

function fail(message: string): never {
  throw new Error(`Automation metadata error: ${message}`);
}

function requireString(value: unknown, field: string, slug: string): string {
  if (typeof value !== 'string') {
    fail(`${slug}: "${field}" must be a string.`);
  }

  const trimmed = value.trim();
  if (!trimmed) {
    fail(`${slug}: "${field}" must not be empty.`);
  }

  return trimmed;
}

function requireStringArray(value: unknown, field: string, slug: string): string[] {
  if (!Array.isArray(value)) {
    fail(`${slug}: "${field}" must be an array of strings.`);
  }

  if (value.length === 0) {
    fail(`${slug}: "${field}" must not be empty.`);
  }

  return value.map((item) => requireString(item, `${field}[]`, slug));
}

export function getAutomationEntries(): AutomationEntry[] {
  return readdirSync(automationsDir, { withFileTypes: true })
    .filter((entry: Dirent) => entry.isDirectory())
    .map((entry: Dirent): AutomationEntry => {
      const slug = entry.name;
      const metaPath = resolve(automationsDir, slug, 'meta.json');
      let parsed: RawAutomationMeta;

      try {
        parsed = JSON.parse(readFileSync(metaPath, 'utf8')) as RawAutomationMeta;
      } catch (error) {
        const reason = error instanceof Error ? error.message : String(error);
        fail(`${slug}: unable to read or parse meta.json (${reason}).`);
      }

      return {
        slug,
        title: requireString(parsed.title, 'title', slug),
        description: requireString(parsed.description, 'description', slug),
        categories: requireStringArray(parsed.categories, 'categories', slug),
        surfaces: requireStringArray(parsed.surfaces, 'surfaces', slug),
      };
    })
    .sort((left: AutomationEntry, right: AutomationEntry) => left.slug.localeCompare(right.slug));
}
