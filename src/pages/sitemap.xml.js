import { getCollection } from 'astro:content';

export async function GET() {
  const indexingEnabled = import.meta.env.PUBLIC_INDEXING === 'true';
  if (!indexingEnabled) {
    return new Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>', { headers: { 'Content-Type': 'application/xml' } });
  }
  const ebooks = await getCollection('ebooks');
  const origin = import.meta.env.SITE_URL || 'https://mindversedaily.vercel.app';
  const urls = [ '/', '/ebooks', '/privacy-policy', '/terms', ...ebooks.map(e => `/ebooks/${e.slug ?? e.id.replace(/\.md$/, '')}`) ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map(u => `  <url><loc>${origin}${u}</loc></url>`).join('\n')}\n</urlset>`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml' } });
}
