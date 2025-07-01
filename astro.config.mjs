// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
	site: 'https://mindversedaily.vercel.app',
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
		})
	],
	server: {
		host: '0.0.0.0',  // listen on all network interfaces
		port: 4321,       // dev server port
	},
});
