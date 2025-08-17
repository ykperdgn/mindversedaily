# MindVerse Minimal E‑Book Hub

Focused Astro site hosting previews & metadata for MindVerse authored Kindle e‑books. Previously a multi‑category bilingual blog; now intentionally reduced while rebuilding. No affiliate links; only direct Amazon product pages for our titles.

## Current Status (Rebuild Phase)
- Indexing disabled by default (`PUBLIC_INDEXING=false`) – dynamic `robots.txt` & `sitemap.xml` endpoints adapt when toggled.
- Legacy blog, astrology widgets, automation & unused components fully removed.
- Three initial ebook entries with on‑site preview extraction.
- Google AdSense script integrated (non‑personalized until launch) to satisfy future monetization placement.
- Privacy Policy & Terms pages implemented for AdSense compliance.
- Book JSON‑LD structured data injected on each e‑book detail page.

## Tech Stack
- Astro ^5
- TypeScript capable (minimal usage)
- No React / MDX / Tailwind (purged) for minimal footprint
- `sharp` for future image optimization

## Content Model (`src/content/config.ts`)
Collection `ebooks` fields:
- title, author, language (default en)
- amazonAsin, amazonUrl
- cover (path under `/public`)
- description (<=500 chars)
- categories (string[])
- publishDate (Date)
- preview: optional { type: words | break | percent, value?: number }

Preview extraction supports:
- words: first N words
- break: explicit `<!-- preview-start -->` to `<!-- preview-end -->`
- percent: first N percent of words

## Dynamic Indexing Control
- `src/pages/robots.txt.js` emits Allow/Disallow based on `PUBLIC_INDEXING`.
- `src/pages/sitemap.xml.js` returns empty set when indexing disabled; full minimal sitemap when enabled.
- `BaseLayout.astro` automatically toggles robots meta and canonical.

## Planned Next Steps
1. Replace placeholder cover images with real assets (`/public/assets/covers/*.jpg`).
2. Add optional author/about page for credibility.
3. Optional email subscription endpoint + form.
4. Accessibility & performance pass (alt text completeness, image optimization pipeline via `sharp`).
5. Light privacy‑friendly analytics.

## Environment Variables
- `PUBLIC_INDEXING` = `true` to allow indexing (removes noindex meta, robots Disallow & exposes populated sitemap).
- Optionally set `SITE_URL` for accurate absolute URLs in sitemap & JSON‑LD.

## Development
```
npm install
npm run dev
```
Build:
```
npm run build
```
Output: `dist/` (deploy via Vercel).

## Deployment
Set `PUBLIC_INDEXING=false` until launch; then switch to true + redeploy when baseline content & policies ready. Provide real contact addresses in Privacy & Terms before enabling.

## Policies
Privacy Policy (`/privacy-policy`) and Terms (`/terms`) active. Update contact emails before production indexing.

## License
All original content © MindVerse. Codebase internal use; no explicit open‑source license at this time.
