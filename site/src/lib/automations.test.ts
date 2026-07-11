import test from 'node:test';
import assert from 'node:assert/strict';

import {
  getAutomationAppActions,
  getCatalogAssessmentPrompt,
  getAutomationPromptUrl,
  getCatalogMarkdown,
  getClaudeAutomatePrototype,
  getAutomationDetailEntry,
  getAutomationLaunchPath,
  getCodexAutomatePrototype,
  getCursorAutomatePrototype,
  getLlmsTxt,
} from './automations.ts';

test('getAutomationDetailEntry returns README content and validated metadata for a known automation', async () => {
  const entry = await getAutomationDetailEntry('github-pr-review-router');

  assert.equal(entry.slug, 'github-pr-review-router');
  assert.equal(entry.title, 'GitHub PR Review Router');
  assert.ok(entry.readmeHtml.includes('<h2 id="overview">Overview</h2>'));
  assert.deepEqual(entry.metadataGroups, [
    { label: 'Categories', values: ['Developer Workflow'] },
    { label: 'Surfaces', values: ['GitHub'] },
    { label: 'Tools', values: ['GitHub MCP'] },
  ]);
  assert.equal(entry.promptFileName, 'github-pr-review-router.md');
  assert.ok(entry.promptText.includes('You are a GitHub pull request review router.'));
  assert.ok(entry.headings.some((heading) => heading.slug === 'overview'));
});

test('getAutomationDetailEntry returns README content and validated metadata for backlink-opportunity-finder', async () => {
  const entry = await getAutomationDetailEntry('backlink-opportunity-finder');

  assert.equal(entry.slug, 'backlink-opportunity-finder');
  assert.equal(entry.title, 'Backlink Opportunity Finder');
  assert.ok(entry.readmeHtml.includes('<h2 id="overview">Overview</h2>'));
  assert.deepEqual(entry.metadataGroups, [
    { label: 'Categories', values: ['Marketing'] },
    { label: 'Surfaces', values: ['Public Web', 'Gmail'] },
    { label: 'Tools', values: ['Firecrawl', 'Gmail MCP', 'public web fetch'] },
  ]);
  assert.equal(entry.promptFileName, 'backlink-opportunity-finder.md');
  assert.ok(entry.promptText.includes('You are a backlink opportunity and outreach draft automation.'));
  assert.ok(entry.headings.some((heading) => heading.slug === 'overview'));
});

test('getCursorAutomatePrototype returns a direct Cursor prompt deeplink for sentry-triage-and-fix', async () => {
  const entry = await getAutomationDetailEntry('sentry-triage-and-fix');
  const prototype = getCursorAutomatePrototype(entry);

  assert.ok(prototype.appUrl.startsWith('cursor://anysphere.cursor-deeplink/prompt?text='));
  assert.ok(prototype.webUrl.startsWith('https://cursor.com/link/prompt?text='));
  assert.ok(prototype.prompt.includes('Use /automate to create a Cursor Automation.'));
  assert.ok(prototype.prompt.includes(`Goal: ${entry.description}`));
  assert.ok(prototype.prompt.includes(getAutomationPromptUrl(entry.slug)));
  assert.ok(prototype.prompt.includes(`https://trigger.tools/automations/${entry.slug}/#prompt`));
  assert.ok(!prototype.prompt.includes(entry.promptText));
  assert.equal(prototype.truncated, false);
  assert.ok(prototype.encodedLength <= 8000);
});

test('getCodexAutomatePrototype returns a direct Codex prompt deeplink for sentry-triage-and-fix', async () => {
  const entry = await getAutomationDetailEntry('sentry-triage-and-fix');
  const prototype = getCodexAutomatePrototype(entry);

  assert.ok(prototype.appUrl.startsWith('codex://new?prompt='));
  assert.ok(prototype.prompt.includes('Create a Codex automation for this task.'));
  assert.ok(prototype.prompt.includes(`Goal: ${entry.description}`));
  assert.ok(prototype.prompt.includes(getAutomationPromptUrl(entry.slug)));
  assert.ok(prototype.prompt.includes(`https://trigger.tools/automations/${entry.slug}/#prompt`));
  assert.ok(!prototype.prompt.includes(entry.promptText));
  assert.equal(prototype.truncated, false);
  assert.ok(prototype.encodedLength <= 8000);
});

test('getClaudeAutomatePrototype returns a direct Claude Code deeplink for sentry-triage-and-fix', async () => {
  const entry = await getAutomationDetailEntry('sentry-triage-and-fix');
  const prototype = getClaudeAutomatePrototype(entry);

  assert.ok(prototype.appUrl.startsWith('claude-cli://open?'));
  assert.ok(prototype.appUrl.includes('repo=ChmaraX%2Fai-agent-automations'));
  assert.ok(prototype.appUrl.includes('q='));
  assert.ok(prototype.prompt.includes('Create a Claude Code automation for this task.'));
  assert.ok(prototype.prompt.includes(`Goal: ${entry.description}`));
  assert.ok(prototype.prompt.includes(getAutomationPromptUrl(entry.slug)));
  assert.ok(prototype.prompt.includes(`https://trigger.tools/automations/${entry.slug}/#prompt`));
  assert.ok(!prototype.prompt.includes(entry.promptText));
  assert.equal(prototype.truncated, false);
  assert.ok(prototype.encodedLength <= 8000);
});

test('getAutomationAppActions returns connected app CTA metadata for sentry-triage-and-fix', async () => {
  const entry = await getAutomationDetailEntry('sentry-triage-and-fix');
  const actions = getAutomationAppActions(entry);

  assert.deepEqual(
    actions.map((action) => ({
      label: action.label,
      iconAlt: action.iconAlt,
      iconClassName: action.iconClassName,
    })),
    [
      {
        label: 'Add to Claude',
        iconAlt: 'Claude',
        iconClassName: 'agent-logo-claude',
      },
      {
        label: 'Add to Codex',
        iconAlt: 'Codex',
        iconClassName: 'agent-logo-codex',
      },
      {
        label: 'Add to Cursor',
        iconAlt: 'Cursor',
        iconClassName: 'agent-logo-cursor',
      },
    ],
  );
  assert.ok(actions[0]?.href.startsWith('claude-cli://open?'));
  assert.ok(actions[1]?.href.startsWith('codex://new?prompt='));
  assert.ok(actions[2]?.href.startsWith('cursor://anysphere.cursor-deeplink/prompt?text='));
});

test('getAutomationAppActions returns connected app CTA metadata for github-pr-review-router', async () => {
  const entry = await getAutomationDetailEntry('github-pr-review-router');
  const actions = getAutomationAppActions(entry);

  assert.equal(actions.length, 3);
  assert.deepEqual(
    actions.map((action) => action.label),
    ['Add to Claude', 'Add to Codex', 'Add to Cursor'],
  );
  assert.ok(actions[0]?.href.startsWith('claude-cli://open?'));
  assert.ok(actions[1]?.href.startsWith('codex://new?prompt='));
  assert.ok(actions[2]?.href.startsWith('cursor://anysphere.cursor-deeplink/prompt?text='));
});

test('getAutomationLaunchPath returns stable site launcher routes', () => {
  assert.equal(getAutomationLaunchPath('claude', 'github-pr-review-router'), '/launch/claude/github-pr-review-router');
  assert.equal(getAutomationLaunchPath('codex', 'github-pr-review-router'), '/launch/codex/github-pr-review-router');
  assert.equal(getAutomationLaunchPath('cursor', 'github-pr-review-router'), '/launch/cursor/github-pr-review-router');
});

test('getAutomationPromptUrl returns stable hosted prompt URLs', () => {
  assert.equal(getAutomationPromptUrl('github-pr-review-router'), 'https://trigger.tools/automation-prompts/github-pr-review-router.md');
});

test('getCatalogAssessmentPrompt returns a catalog-wide recommendation prompt', () => {
  const prompt = getCatalogAssessmentPrompt();

  assert.ok(prompt.includes('If web fetch is available, read the automation catalog docs at:'));
  assert.ok(prompt.includes('https://trigger.tools/llms.txt'));
  assert.ok(prompt.includes('https://trigger.tools/catalog.md'));
  assert.ok(prompt.includes('If neither project inspection nor web fetch is available, ask me up to 3 short questions before recommending anything.'));
  assert.ok(prompt.includes('For each recommended automation, provide:'));
  assert.ok(prompt.includes('A short start-here-first rollout order.'));
  assert.ok(!prompt.includes('"slug": "github-pr-review-router"'));
});

test('getCatalogMarkdown returns an agent-readable markdown catalog', () => {
  const markdown = getCatalogMarkdown();

  assert.ok(markdown.startsWith('# AI Agent Automations Catalog'));
  assert.ok(markdown.includes('## Developer Workflow'));
  assert.ok(markdown.includes('- [GitHub PR Review Router](https://trigger.tools/automations/github-pr-review-router/):'));
  assert.ok(markdown.includes('  - Slug: `github-pr-review-router`'));
  assert.ok(markdown.includes('  - Prompt: https://trigger.tools/automation-prompts/github-pr-review-router.md'));
  assert.ok(markdown.includes('  - Details: https://trigger.tools/automations/github-pr-review-router/'));
  assert.ok(markdown.includes('## Category index'));
});

test('getLlmsTxt returns a short index that points agents at the catalog', () => {
  const llms = getLlmsTxt();

  assert.ok(llms.startsWith('# AI Agent Automations'));
  assert.ok(llms.includes('[Automation catalog](https://trigger.tools/catalog.md)'));
  assert.ok(llms.includes('## Recommendation guidance'));
  assert.ok(llms.includes('[Recommendation guidance](https://trigger.tools/catalog.md):'));
  assert.ok(!llms.includes('## Category coverage'));
});
