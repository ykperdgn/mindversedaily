export function GET() {
  const indexingEnabled = import.meta.env.PUBLIC_INDEXING === 'true';
  const site = import.meta.env.SITE_URL || 'https://mindversedaily.vercel.app';
  let body;
  if (indexingEnabled) {
    body = `User-agent: *\nAllow: /\n\nSitemap: ${site}/sitemap.xml`;
  } else {
    body = `User-agent: *\nDisallow: /\n\nUser-agent: AdsBot-Google\nAllow: /\n\n# Rebuild phase: blocked for general crawlers`;
  }
  return new Response(body, { headers: { 'Content-Type': 'text/plain' } });
}
