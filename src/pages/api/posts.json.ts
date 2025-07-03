import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async ({ url }) => {
  try {
    const searchParams = new URLSearchParams(url.search);
    const lang = searchParams.get('lang') || 'tr';

    // Get all blog posts
    const allPosts = await getCollection('blog');

    // Filter posts by language
    const filteredPosts = allPosts.filter(post => {
      if (!post.slug) return false;

      if (lang === 'en') {
        return post.slug.endsWith('.en');
      } else {
        // Turkish posts: either .tr ending or no language suffix
        return post.slug.endsWith('.tr') || (!post.slug.endsWith('.en') && !post.slug.endsWith('.tr'));
      }
    });

    // Transform posts for search API
    const searchablePosts = filteredPosts.map(post => {
      const slug = post.slug || post.id;
      const baseSlug = slug.replace(/\.(tr|en)$/, '');

      // Create proper URL based on language
      let postUrl;
      if (lang === 'en') {
        postUrl = `/${baseSlug}en`;
      } else {
        postUrl = `/${slug}`;
      }

      return {
        title: post.data.title || '',
        description: post.data.description || '',
        category: post.data.category || '',
        date: post.data.pubDate?.toISOString() || '',
        url: postUrl,
        slug: slug
      };
    });

    return new Response(JSON.stringify(searchablePosts), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300' // 5 minutes cache
      }
    });

  } catch (error) {
    console.error('Error in posts API:', error);

    return new Response(JSON.stringify({ error: 'Failed to fetch posts' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};
