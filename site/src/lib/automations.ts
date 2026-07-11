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
  'description' | 'promptText'
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

function buildCursorPrompt(entry: CursorAutomatePromptInput): string {
  return [
    'Use /automate to create a Cursor Automation.',
    '',
    `Goal: ${entry.description}`,
    '',
    'Prompt:',
    entry.promptText,
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
    'Prompt:',
    entry.promptText,
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
    'Prompt:',
    entry.promptText,
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
    'Help me find useful AI automations from the catalog below.',
    '',
    'First infer the context where this prompt was pasted:',
    '- If you can inspect a project, repository, workspace, or codebase, use that evidence to identify relevant automations.',
    '- If this was pasted into a general chat without project context, interview me briefly before recommending automations.',
    '- If the context is ambiguous, ask whether I want project-specific recommendations or general workflow recommendations for my role, tools, company, or personal operations.',
    '',
    'When interviewing me, ask only the minimum useful questions. Prefer concise questions about my role, active tools, recurring workflows, business model, project stack, and pain points.',
    '',
    'Recommend up to 5 automations from the catalog once you have enough context.',
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
    '',
    'Automation catalog:',
    formatCatalogAssessmentEntries(toCatalogAssessmentEntries(entries)),
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
