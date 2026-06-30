import test from 'node:test';
import assert from 'node:assert/strict';

import {
  getAutomationAppActions,
  getAutomationDetailEntry,
  getCodexAutomatePrototype,
  getCursorAutomatePrototype,
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

test('getCursorAutomatePrototype returns a direct Cursor prompt deeplink for sentry-triage-and-fix', async () => {
  const entry = await getAutomationDetailEntry('sentry-triage-and-fix');
  const prototype = getCursorAutomatePrototype(entry);

  assert.ok(prototype.appUrl.startsWith('cursor://anysphere.cursor-deeplink/prompt?text='));
  assert.ok(prototype.webUrl.startsWith('https://cursor.com/link/prompt?text='));
  assert.ok(prototype.prompt.includes('Use /automate to create a Cursor Automation.'));
  assert.ok(prototype.prompt.includes(`Goal: ${entry.description}`));
  assert.ok(prototype.prompt.includes('Prompt:'));
  assert.ok(prototype.prompt.includes('You are a conservative Sentry triage-and-fix automation.'));
  assert.equal(prototype.truncated, false);
  assert.ok(prototype.encodedLength <= 8000);
});

test('getCodexAutomatePrototype returns a direct Codex prompt deeplink for sentry-triage-and-fix', async () => {
  const entry = await getAutomationDetailEntry('sentry-triage-and-fix');
  const prototype = getCodexAutomatePrototype(entry);

  assert.ok(prototype.appUrl.startsWith('codex://new?prompt='));
  assert.ok(prototype.prompt.includes('Create a Codex automation for this task.'));
  assert.ok(prototype.prompt.includes(`Goal: ${entry.description}`));
  assert.ok(prototype.prompt.includes('Prompt:'));
  assert.ok(prototype.prompt.includes('You are a conservative Sentry triage-and-fix automation.'));
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
  assert.ok(actions[0]?.href.startsWith('codex://new?prompt='));
  assert.ok(actions[1]?.href.startsWith('cursor://anysphere.cursor-deeplink/prompt?text='));
});

test('getAutomationAppActions returns connected app CTA metadata for github-pr-review-router', async () => {
  const entry = await getAutomationDetailEntry('github-pr-review-router');
  const actions = getAutomationAppActions(entry);
  const codexPrompt = new URL(actions[0]?.href ?? 'codex://new').searchParams.get('prompt') ?? '';

  assert.equal(actions.length, 2);
  assert.deepEqual(
    actions.map((action) => action.label),
    ['Add to Codex', 'Add to Cursor'],
  );
  assert.ok(actions[0]?.href.startsWith('codex://new?prompt='));
  assert.ok(actions[1]?.href.startsWith('cursor://anysphere.cursor-deeplink/prompt?text='));
  assert.ok(codexPrompt.includes(`Goal: ${entry.description}`));
});
