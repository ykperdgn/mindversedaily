// @ts-check
import { defineConfig } from 'astro/config';
import { fileURLToPath } from 'url';
import path from 'path';

// Normalize __dirname for ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// https://astro.build/config
// To enable indexing set PUBLIC_INDEXING=true in environment (Vercel env var)
// Optionally disable sitemap plugin during rebuild phase if needed.
export default defineConfig({
	site: 'https://www.mindversedaily.com',
	// Vite settings to resolve /assets to public/assets
	vite: {
		resolve: {
			alias: {
				'/assets': path.resolve(__dirname, 'public/assets')
			}
		},
		define: {
			'__MV_REDESIGN__': 'true'
		}
	},
	integrations: [],
	server: {
		host: '0.0.0.0',
		port: 4321,
	},
	build: {
		inlineStylesheets: 'auto'
	},
	compressHTML: true
});
