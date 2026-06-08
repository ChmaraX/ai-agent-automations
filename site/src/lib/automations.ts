import { existsSync, readFileSync, readdirSync, type Dirent } from 'node:fs';
import { relative, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import { createMarkdownProcessor, type MarkdownHeading } from '@astrojs/markdown-remark';

export type AutomationEntry = {
  slug: string;
  title: string;
  description: string;
  categories: string[];
  surfaces: string[];
  tools: string[];
};

export type AutomationMetadataGroup = {
  label: string;
  values: string[];
};

export type AutomationDetailEntry = AutomationEntry & {
  headings: MarkdownHeading[];
  metadataGroups: AutomationMetadataGroup[];
  promptFileName: string;
  promptText: string;
  readmeHtml: string;
};

export type AutomationAssetEntry = {
  absolutePath: string;
  assetPath: string;
  slug: string;
};

type RawAutomationMeta = {
  title?: unknown;
  description?: unknown;
  categories?: unknown;
  surfaces?: unknown;
  tools?: unknown;
};

const automationsDir = resolve(process.cwd(), '../automations');

let markdownProcessorPromise: ReturnType<typeof createMarkdownProcessor> | undefined;

function getMarkdownProcessor() {
  markdownProcessorPromise ??= createMarkdownProcessor();
  return markdownProcessorPromise;
}

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

function readAutomationMeta(slug: string): AutomationEntry {
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
    tools: requireStringArray(parsed.tools, 'tools', slug),
  };
}

function rewriteAssetUrls(html: string, slug: string): string {
  const assetBase = `/automation-assets/${slug}/`;

  return html
    .replaceAll('src="./assets/', `src="${assetBase}`)
    .replaceAll("src='./assets/", `src='${assetBase}`)
    .replaceAll('href="./assets/', `href="${assetBase}`)
    .replaceAll("href='./assets/", `href='${assetBase}`);
}

function stripLeadingTitle(markdown: string): string {
  return markdown.replace(/^#\s+.+\n+/, '');
}

function normalizeReadmeMarkdown(markdown: string, slug: string): string {
  const assetBase = `/automation-assets/${slug}/`;

  return stripLeadingTitle(markdown).replaceAll(/(!?)\[([^\]]*)\]\(\.\/assets\/([^)]+)\)/g, (_, prefix, label, assetPath) => {
    const href = `${assetBase}${assetPath}`;
    if (prefix === '!') {
      return `<img src="${href}" alt="${label}" loading="lazy" />`;
    }

    return `[${label}](${href})`;
  });
}

function buildMetadataGroups(entry: AutomationEntry): AutomationMetadataGroup[] {
  return [
    { label: 'Categories', values: entry.categories },
    { label: 'Surfaces', values: entry.surfaces },
    { label: 'Tools', values: entry.tools },
  ];
}

export function getAutomationEntries(): AutomationEntry[] {
  return readdirSync(automationsDir, { withFileTypes: true })
    .filter((entry: Dirent) => entry.isDirectory())
    .map((entry: Dirent) => readAutomationMeta(entry.name))
    .sort((left: AutomationEntry, right: AutomationEntry) => left.slug.localeCompare(right.slug));
}

function collectAssetPaths(currentDir: string): string[] {
  return readdirSync(currentDir, { withFileTypes: true }).flatMap((entry) => {
    const absolutePath = resolve(currentDir, entry.name);
    if (entry.isDirectory()) {
      return collectAssetPaths(absolutePath);
    }

    return [absolutePath];
  });
}

export function getAutomationAssetEntries(): AutomationAssetEntry[] {
  return getAutomationEntries().flatMap((entry) => {
    const assetsDir = resolve(automationsDir, entry.slug, 'assets');
    if (!existsSync(assetsDir)) {
      return [];
    }

    return collectAssetPaths(assetsDir).map((absolutePath) => ({
      slug: entry.slug,
      absolutePath,
      assetPath: relative(assetsDir, absolutePath).split('\\').join('/'),
    }));
  });
}

export async function getAutomationDetailEntry(slug: string): Promise<AutomationDetailEntry> {
  const entry = readAutomationMeta(slug);
  const readmePath = resolve(automationsDir, slug, 'README.md');
  const promptFileName = `${slug}.md`;
  const promptPath = resolve(automationsDir, slug, promptFileName);

  let readmeMarkdown = '';
  try {
    readmeMarkdown = readFileSync(readmePath, 'utf8');
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    fail(`${slug}: unable to read README.md (${reason}).`);
  }

  let promptText = '';
  try {
    promptText = readFileSync(promptPath, 'utf8').trim();
  } catch (error) {
    const reason = error instanceof Error ? error.message : String(error);
    fail(`${slug}: unable to read ${promptFileName} (${reason}).`);
  }

  const markdownProcessor = await getMarkdownProcessor();
  const rendered = await markdownProcessor.render(normalizeReadmeMarkdown(readmeMarkdown, slug), {
    fileURL: pathToFileURL(readmePath),
  });

  return {
    ...entry,
    metadataGroups: buildMetadataGroups(entry),
    headings: rendered.metadata.headings,
    promptFileName,
    promptText,
    readmeHtml: rewriteAssetUrls(rendered.code, slug),
  };
}
