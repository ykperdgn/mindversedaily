// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
	site: 'https://mindversedaily.com',
	integrations: [mdx(), sitemap()],
	server: {
		host: '0.0.0.0',  // listen on all network interfaces
		port: 4321,       // dev server port
	},
});
