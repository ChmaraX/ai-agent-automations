import { getAutomationDetailEntry, getAutomationEntries } from '../../lib/automations';

export const prerender = true;

export function getStaticPaths() {
  return getAutomationEntries().map((entry) => ({
    params: { slug: entry.slug },
  }));
}

export async function GET({ params }: { params: { slug?: string } }) {
  const slug = params.slug;
  if (!slug) {
    return new Response('Missing automation slug.', { status: 400 });
  }

  const entry = await getAutomationDetailEntry(slug);

  return new Response(`${entry.promptText}\n`, {
    headers: {
      'Content-Type': 'text/markdown; charset=utf-8',
    },
  });
}
