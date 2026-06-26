import test from 'node:test';
import assert from 'node:assert/strict';

import { getAutomationDetailEntry } from './automations.ts';

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
