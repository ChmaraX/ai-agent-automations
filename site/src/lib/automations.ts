import { existsSync, readFileSync, readdirSync, type Dirent } from 'node:fs';
import { relative, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

import { createMarkdownProcessor, type MarkdownHeading } from '@astrojs/markdown-remark';
import { siteConfig } from '../data/site.ts';

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

export type CursorAutomatePrototype = {
  appUrl: string;
  webUrl: string;
  prompt: string;
  promptVariant: 'full' | 'compact' | 'minimal';
  truncated: boolean;
  encodedLength: number;
};

export type CodexAutomatePrototype = {
  appUrl: string;
  prompt: string;
  truncated: boolean;
  encodedLength: number;
};

export type ClaudeAutomatePrototype = {
  appUrl: string;
  prompt: string;
  truncated: boolean;
  encodedLength: number;
};

export type CursorLaunchPrototype = {
  appUrl: string;
  webUrl: string;
  prompt: string;
  truncated: boolean;
  encodedLength: number;
};

export type CodexLaunchPrototype = {
  appUrl: string;
  prompt: string;
  truncated: boolean;
  encodedLength: number;
};

export type ClaudeLaunchPrototype = {
  appUrl: string;
  prompt: string;
  truncated: boolean;
  encodedLength: number;
};

export type AutomationAssetEntry = {
  absolutePath: string;
  assetPath: string;
  slug: string;
};

export type AutomationAppAction = {
  href: string;
  label: string;
  title: string;
  iconSrc: string;
  iconAlt: string;
  iconClassName: string;
};

export type AutomationLaunchApp = 'claude' | 'codex' | 'cursor';

type RawAutomationMeta = {
  title?: unknown;
  description?: unknown;
  categories?: unknown;
  surfaces?: unknown;
  tools?: unknown;
};

type CursorAutomatePromptInput = Pick<
  AutomationDetailEntry,
  'slug' | 'description' | 'promptText'
>;

type CatalogAssessmentEntry = Pick<
  AutomationEntry,
  'slug' | 'title' | 'description' | 'categories' | 'surfaces' | 'tools'
>;

const automationsDir = resolve(process.cwd(), '../automations');
const claudePromptAppBaseUrl = 'claude-cli://open';
const cursorPromptAppBaseUrl = 'cursor://anysphere.cursor-deeplink/prompt';
const cursorPromptWebBaseUrl = 'https://cursor.com/link/prompt';
const codexPromptAppBaseUrl = 'codex://new';
const deeplinkMaxLength = 8000;

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

export function getAutomationPromptUrl(slug: string): string {
  return `${siteConfig.siteUrl}/automation-prompts/${slug}.md`;
}

function buildCursorPrompt(entry: CursorAutomatePromptInput): string {
  return [
    'Use /automate to create a Cursor Automation.',
    '',
    `Goal: ${entry.description}`,
    '',
    'Before doing anything else, fetch and read the source automation prompt at:',
    getAutomationPromptUrl(entry.slug),
    '',
    'If direct fetch fails, open this page and use the Prompt section:',
    `${siteConfig.siteUrl}/automations/${entry.slug}/#prompt`,
    '',
    'Then follow that automation prompt exactly.',
  ].join('\n');
}

function createCursorPromptUrl(baseUrl: string, prompt: string): string {
  const url = new URL(baseUrl);
  url.searchParams.set('text', prompt);
  return url.toString();
}

export function getCursorLaunchPrototype(prompt: string): CursorLaunchPrototype {
  const appUrl = createCursorPromptUrl(cursorPromptAppBaseUrl, prompt);

  if (appUrl.length <= deeplinkMaxLength) {
    return {
      appUrl,
      webUrl: createCursorPromptUrl(cursorPromptWebBaseUrl, prompt),
      prompt,
      truncated: false,
      encodedLength: appUrl.length,
    };
  }

  const maxPromptLength = Math.max(0, Math.floor((deeplinkMaxLength - cursorPromptAppBaseUrl.length) * 0.55));
  const truncatedPromptText = prompt.slice(0, Math.max(0, maxPromptLength - 28)).trimEnd();
  const truncatedPrompt = `${truncatedPromptText}\n\n[truncated for deeplink length]`;
  const truncatedAppUrl = createCursorPromptUrl(cursorPromptAppBaseUrl, truncatedPrompt);

  return {
    appUrl: truncatedAppUrl,
    webUrl: createCursorPromptUrl(cursorPromptWebBaseUrl, truncatedPrompt),
    prompt: truncatedPrompt,
    truncated: true,
    encodedLength: truncatedAppUrl.length,
  };
}

export function getCursorAutomatePrototype(entry: CursorAutomatePromptInput): CursorAutomatePrototype {
  const prototype = getCursorLaunchPrototype(buildCursorPrompt(entry));

  return {
    ...prototype,
    promptVariant: prototype.truncated ? 'minimal' : 'full',
  };
}

function buildCodexPrompt(entry: CursorAutomatePromptInput): string {
  return [
    'Create a Codex automation for this task.',
    '',
    `Goal: ${entry.description}`,
    '',
    'Before doing anything else, fetch and read the source automation prompt at:',
    getAutomationPromptUrl(entry.slug),
    '',
    'If direct fetch fails, open this page and use the Prompt section:',
    `${siteConfig.siteUrl}/automations/${entry.slug}/#prompt`,
    '',
    'Then follow that automation prompt exactly.',
  ].join('\n');
}

function createCodexPromptUrl(prompt: string): string {
  const url = new URL(codexPromptAppBaseUrl);
  url.searchParams.set('prompt', prompt);
  return url.toString();
}

function buildClaudePrompt(entry: CursorAutomatePromptInput): string {
  return [
    'Create a Claude Code automation for this task.',
    '',
    `Goal: ${entry.description}`,
    '',
    'Before doing anything else, fetch and read the source automation prompt at:',
    getAutomationPromptUrl(entry.slug),
    '',
    'If direct fetch fails, open this page and use the Prompt section:',
    `${siteConfig.siteUrl}/automations/${entry.slug}/#prompt`,
    '',
    'Then follow that automation prompt exactly.',
  ].join('\n');
}

function createClaudePromptUrl(prompt: string, repoName: string): string {
  const url = new URL(claudePromptAppBaseUrl);
  if (repoName.trim()) {
    url.searchParams.set('repo', repoName);
  }
  url.searchParams.set('q', prompt);
  return url.toString();
}

export function getClaudeAutomatePrototype(
  entry: CursorAutomatePromptInput,
  repoName: string = siteConfig.repoName,
): ClaudeAutomatePrototype {
  return getClaudeLaunchPrototype(buildClaudePrompt(entry), repoName);
}

export function getClaudeLaunchPrototype(
  prompt: string,
  repoName: string = siteConfig.repoName,
): ClaudeLaunchPrototype {
  const appUrl = createClaudePromptUrl(prompt, repoName);

  if (appUrl.length <= deeplinkMaxLength) {
    return {
      appUrl,
      prompt,
      truncated: false,
      encodedLength: appUrl.length,
    };
  }

  const maxPromptLength = Math.max(0, Math.floor((deeplinkMaxLength - claudePromptAppBaseUrl.length) * 0.55));
  const truncatedPromptText = prompt.slice(0, Math.max(0, maxPromptLength - 28)).trimEnd();
  const truncatedPrompt = `${truncatedPromptText}\n\n[truncated for deeplink length]`;
  const truncatedAppUrl = createClaudePromptUrl(truncatedPrompt, repoName);

  return {
    appUrl: truncatedAppUrl,
    prompt: truncatedPrompt,
    truncated: true,
    encodedLength: truncatedAppUrl.length,
  };
}

export function getCodexLaunchPrototype(prompt: string): CodexLaunchPrototype {
  const appUrl = createCodexPromptUrl(prompt);

  if (appUrl.length <= deeplinkMaxLength) {
    return {
      appUrl,
      prompt,
      truncated: false,
      encodedLength: appUrl.length,
    };
  }

  const maxPromptLength = Math.max(0, Math.floor((deeplinkMaxLength - codexPromptAppBaseUrl.length) * 0.55));
  const truncatedPromptText = prompt.slice(0, Math.max(0, maxPromptLength - 28)).trimEnd();
  const truncatedPrompt = `${truncatedPromptText}\n\n[truncated for deeplink length]`;
  const truncatedAppUrl = createCodexPromptUrl(truncatedPrompt);

  return {
    appUrl: truncatedAppUrl,
    prompt: truncatedPrompt,
    truncated: true,
    encodedLength: truncatedAppUrl.length,
  };
}

export function getCodexAutomatePrototype(entry: CursorAutomatePromptInput): CodexAutomatePrototype {
  return getCodexLaunchPrototype(buildCodexPrompt(entry));
}

function toCatalogAssessmentEntries(entries: AutomationEntry[]): CatalogAssessmentEntry[] {
  return entries.map(({ slug, title, description, categories, surfaces, tools }) => ({
    slug,
    title,
    description,
    categories,
    surfaces,
    tools,
  }));
}

function formatCatalogAssessmentEntries(entries: CatalogAssessmentEntry[]): string {
  const formatEntry = (entry: CatalogAssessmentEntry): string =>
    `{"slug": ${JSON.stringify(entry.slug)}, "title": ${JSON.stringify(entry.title)}, "description": ${JSON.stringify(entry.description)}, "categories": ${JSON.stringify(entry.categories)}, "surfaces": ${JSON.stringify(entry.surfaces)}, "tools": ${JSON.stringify(entry.tools)}}`;

  return [
    '[',
    ...entries.map((entry, index) => `  ${formatEntry(entry)}${index === entries.length - 1 ? '' : ','}`),
    ']',
  ].join('\n');
}

export function getCatalogAssessmentPrompt(entries: AutomationEntry[] = getAutomationEntries()): string {
  return [
    'Help me find useful AI automations for this repo, workspace, or workflow.',
    '',
    'First infer the context where this prompt was pasted.',
    '- If you can inspect a project, repository, workspace, or codebase, do that first and use the evidence you find.',
    '- If web fetch is available, read the automation catalog docs at:',
    `  - ${siteConfig.siteUrl}/llms.txt`,
    `  - ${siteConfig.siteUrl}/catalog.md`,
    '- If neither project inspection nor web fetch is available, ask me up to 3 short questions before recommending anything.',
    '',
    'Recommend up to 5 automations once you have enough context.',
    'For project-specific recommendations, use evidence such as dependencies, source files, CI, monitoring, billing, docs, scripts, and obvious workflow gaps.',
    'For general workflow recommendations, use evidence from my answers about tools, responsibilities, repeated tasks, risks, and goals.',
    'Do not force weak recommendations just to fill the list.',
    '',
    'For each recommended automation, provide:',
    '- why it fits the project, workflow, or person',
    '- what evidence supports it',
    '- expected value',
    '- requirements or caveats',
    '',
    'Also include:',
    '- A short start-here-first rollout order.',
    '- Optional later additions or near-misses worth revisiting later.',
  ].join('\n');
}

export function getCatalogMarkdown(entries: AutomationEntry[] = getAutomationEntries()): string {
  const categories = new Map<string, AutomationEntry[]>();

  for (const entry of entries) {
    for (const category of entry.categories) {
      const bucket = categories.get(category);
      if (bucket) bucket.push(entry);
      else categories.set(category, [entry]);
    }
  }

  const sections = [...categories.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([category, categoryEntries]) => {
      const lines = [`## ${category}`, ''];

      for (const entry of categoryEntries.sort((left, right) => left.title.localeCompare(right.title))) {
        lines.push(`- [${entry.title}](${siteConfig.siteUrl}/automations/${entry.slug}/): ${entry.description}`);
        lines.push(`  - Slug: \`${entry.slug}\``);
        lines.push(`  - Surfaces: ${entry.surfaces.join(', ')}`);
        lines.push(`  - Tools: ${entry.tools.join(', ')}`);
        lines.push(`  - Prompt: ${getAutomationPromptUrl(entry.slug)}`);
        lines.push(`  - Details: ${siteConfig.siteUrl}/automations/${entry.slug}/`);
        lines.push('');
      }

      return lines.join('\n').trimEnd();
    });

  return [
    '# AI Agent Automations Catalog',
    '',
    '> Agent-readable catalog of practical AI automations from trigger.tools.',
    '',
    'Use this document when choosing automations for a repository, workspace, or general workflow.',
    'Prefer recommendations backed by project evidence or explicit user context.',
    '',
    '## How to use this catalog',
    '',
    '- Inspect the current project or workspace first when possible.',
    '- Recommend up to 5 automations, not an exhaustive list.',
    '- For each recommendation, explain fit, evidence, expected value, and setup caveats.',
    '- If context is missing, ask only the minimum useful follow-up questions.',
    '',
    '## Category index',
    '',
    ...[...categories.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([category, categoryEntries]) => `- ${category}: ${categoryEntries.length} automations`),
    '',
    ...sections.flatMap((section) => [section, '']),
  ].join('\n').trimEnd();
}

export function getLlmsTxt(entries: AutomationEntry[] = getAutomationEntries()): string {
  return [
    `# ${siteConfig.title}`,
    '',
    `> ${siteConfig.description}`,
    '',
    'This site publishes practical AI automation prompts and setup guides.',
    'For automation discovery and recommendation tasks, start with the linked catalog document.',
    '',
    '## Recommended docs',
    '',
    `- [Automation catalog](${siteConfig.siteUrl}/catalog.md): Agent-readable catalog of all automations with categories, surfaces, tools, and detail links.`,
    '',
    '## Recommendation guidance',
    '',
    `- [Recommendation guidance](${siteConfig.siteUrl}/catalog.md): Inspect the project first when possible, recommend up to 5 strong matches, and explain evidence, expected value, and caveats.`,
  ].join('\n');
}

export function getAutomationLaunchPath(app: AutomationLaunchApp, slug: string): string {
  return `/launch/${app}/${slug}`;
}

export function getAutomationAppActions(entry: AutomationDetailEntry): AutomationAppAction[] {
  const claudePrototype = getClaudeAutomatePrototype(entry);
  const codexPrototype = getCodexAutomatePrototype(entry);
  const cursorPrototype = getCursorAutomatePrototype(entry);

  return [
    {
      href: claudePrototype.appUrl,
      label: 'Add to Claude',
      title: claudePrototype.truncated
        ? 'Launch Claude Code with a shortened prefilled automation prompt'
        : 'Launch Claude Code with a prefilled automation prompt',
      iconSrc: '/logos/claude.png',
      iconAlt: 'Claude',
      iconClassName: 'agent-logo-claude',
    },
    {
      href: codexPrototype.appUrl,
      label: 'Add to Codex',
      title: codexPrototype.truncated
        ? 'Launch Codex with a shortened prefilled automation prompt'
        : 'Launch Codex with a prefilled automation prompt',
      iconSrc: '/logos/codex.png',
      iconAlt: 'Codex',
      iconClassName: 'agent-logo-codex',
    },
    {
      href: cursorPrototype.appUrl,
      label: 'Add to Cursor',
      title: cursorPrototype.truncated
        ? 'Launch Cursor with a shortened prefilled automation prompt'
        : 'Launch Cursor with a prefilled automation prompt',
      iconSrc: '/logos/cursor.png',
      iconAlt: 'Cursor',
      iconClassName: 'agent-logo-cursor',
    },
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
