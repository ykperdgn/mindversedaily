// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import react from '@astrojs/react';
import { fileURLToPath } from 'url';
import path from 'path';

// Normalize __dirname for ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// https://astro.build/config
export default defineConfig({
	site: 'https://mindversedaily.vercel.app',
	// Vite settings to resolve /assets to public/assets
	vite: {
		resolve: {
			alias: {
				'/assets': path.resolve(__dirname, 'public/assets')
			}
		}
	},
	integrations: [
		mdx(),
		sitemap({
			changefreq: 'daily',
			priority: 0.8,
			lastmod: new Date(),
			i18n: {
				defaultLocale: 'tr',
				locales: {
					tr: 'tr-TR',
					en: 'en-US'
				}
			}
		}),
		react(),
	],
	server: {
		host: '0.0.0.0',
		port: 4321,
	},
	build: {
		inlineStylesheets: 'auto'
	},
	compressHTML: true
});
