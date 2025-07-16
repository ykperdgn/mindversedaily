import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async ({ url }) => {
  try {
    const searchParams = new URLSearchParams(url.search);
    const lang = searchParams.get('lang') || 'tr';    // Get all blog posts
    const allPosts = await getCollection('blog');

    // Helper function to detect Turkish content
    const isTurkishContent = (text: string): boolean => {
      const turkishChars = /[öüşçğıİÖÜŞÇĞ]/;
      return turkishChars.test(text);
    };    // Filter posts by language using file ID endings (strict)
    const filteredPosts = allPosts.filter(post => {
      if (!post.id) return false;

      if (lang === 'en') {
        // English: ONLY files ending with 'en'
        return post.id.endsWith('en');
      } else {
        // Turkish: ONLY files ending with 'tr'
        return post.id.endsWith('tr');
      }
    });

    // Category translations
    const categoryTranslations: Record<string, string> = {
      'health': 'Sağlık',
      'psychology': 'Psikoloji',
      'history': 'Tarih',
      'space': 'Uzay',
      'quotes': 'Alıntılar',
      'love': 'Aşk',
      'business': 'İş Dünyası',
      'science': 'Bilim',
      'world': 'Dünya'
    };    // Transform posts for search API
    const searchablePosts = filteredPosts.map(post => {
      const id = post.id;
        // Create proper URL based on language and id structure
      let postUrl;
      if (lang === 'en') {
        // For English: /en/blog/id-without-en-suffix
        const baseId = id.replace(/en$/, '');
        postUrl = `/en/blog/${baseId}`;
      } else {
        // For Turkish: /blog/id-without-tr-suffix
        const baseId = id.replace(/tr$/, '');
        postUrl = `/blog/${baseId}`;
      }const category = post.data.category || '';

      return {
        title: post.data.title || '',
        description: post.data.description || '',
        category: category,
        categoryDisplayName: lang === 'tr' ? (categoryTranslations[category] || category) : category,
        date: post.data.pubDate?.toISOString() || '',
        url: postUrl,
        slug: id
      };
    });    return new Response(JSON.stringify({ posts: searchablePosts }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300' // 5 minutes cache
      }
    });
  } catch (error: any) {
    console.error('Error in posts API:', error);

    return new Response(JSON.stringify({ error: 'Failed to fetch posts', message: error?.message || 'Unknown error' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};
