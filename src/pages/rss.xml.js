import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE_TITLE, SITE_DESCRIPTION, SITE_URL } from '../consts';

export async function GET(context) {
	const posts = await getCollection('blog');

	// Son 50 postu tarihe göre sırala ve geçerli olanları filtrele
	const validPosts = posts
		.filter(post => post.data.title && post.data.description && post.data.pubDate)
		.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf())
		.slice(0, 50);

	return rss({
		title: SITE_TITLE,
		description: SITE_DESCRIPTION,
		site: context.site || SITE_URL,
		items: validPosts.map((post) => ({
			title: post.data.title,
			description: post.data.description,
			pubDate: post.data.pubDate,
			link: `/blog/${post.id}/`,
		})),
	});
}
