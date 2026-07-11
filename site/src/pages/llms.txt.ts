import { getAutomationEntries, getLlmsTxt } from '../lib/automations';

export const prerender = true;

export function GET() {
  const entries = getAutomationEntries();
  const body = getLlmsTxt(entries);

  return new Response(body, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
    },
  });
}
