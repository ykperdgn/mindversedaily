import fs from 'fs';
import path from 'path';
import axios from 'axios';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../.env') });

const API_KEY = process.env.GNEWS_API_KEY;
const BASE_URL = 'https://gnews.io/api/v4/top-headlines';
const CATEGORIES = ['science', 'health', 'business', 'world'];
const MAX_ARTICLES = 10;

async function fetchArticles(category: string) {
  const url = `${BASE_URL}?token=${API_KEY}&q=${category}&lang=en&max=${MAX_ARTICLES}`;
  const res = await axios.get(url);
  return res.data.articles || [];
}

function slugify(text: string) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60);
}

function ensureDir(dir: string) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

async function main() {
  for (const category of CATEGORIES) {
    const articles = await fetchArticles(category);
    const dir = path.join(__dirname, '../src/content/blog/', category);
    ensureDir(dir);
    for (const article of articles) {
      const slug = slugify(article.title);
      const file = path.join(dir, `${slug}.md`);
      if (fs.existsSync(file)) continue;
      const md = `---\ntitle: "${article.title.replace(/"/g, '')}"\ndate: "${new Date(article.publishedAt).toISOString()}"\ncategory: "${category}"\nimage: "${article.image || ''}"\n---\n\n${article.description || article.content || ''}\n`;
      fs.writeFileSync(file, md, 'utf-8');
      console.log(`[✔] ${category}: ${article.title}`);
    }
  }
}

main();
