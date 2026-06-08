import { readFileSync } from 'node:fs';
import { extname } from 'node:path';

import { getAutomationAssetEntries } from '../../../lib/automations';

export const prerender = true;

const contentTypes = new Map<string, string>([
  ['.gif', 'image/gif'],
  ['.html', 'text/html; charset=utf-8'],
  ['.jpeg', 'image/jpeg'],
  ['.jpg', 'image/jpeg'],
  ['.png', 'image/png'],
  ['.svg', 'image/svg+xml'],
  ['.webm', 'video/webm'],
  ['.webp', 'image/webp'],
]);

export function getStaticPaths() {
  return getAutomationAssetEntries().map((asset) => ({
    params: {
      slug: asset.slug,
      assetPath: asset.assetPath,
    },
    props: asset,
  }));
}

export function GET({ props }: { props: { absolutePath: string } }) {
  const contentType = contentTypes.get(extname(props.absolutePath).toLowerCase()) ?? 'application/octet-stream';

  return new Response(readFileSync(props.absolutePath), {
    headers: {
      'Content-Type': contentType,
    },
  });
}
