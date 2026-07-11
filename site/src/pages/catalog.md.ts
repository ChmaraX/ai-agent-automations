import { getAutomationEntries, getCatalogMarkdown } from '../lib/automations';

export const prerender = true;

export function GET() {
  const entries = getAutomationEntries();
  const body = getCatalogMarkdown(entries);

  return new Response(body, {
    headers: {
      'Content-Type': 'text/markdown; charset=utf-8',
    },
  });
}
