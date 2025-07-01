// Place any global data in this file.
// You can import this data from anywhere in your site by using the `import` keyword.

export const SITE_TITLE = 'MindVerse Daily - Bilim, Sağlık ve Teknoloji Haberleri';
export const SITE_DESCRIPTION = 'MindVerse Daily: Bilim, sağlık, psikoloji, tarih, uzay ve teknoloji alanlarında güncel haberler, araştırmalar ve derinlemesine analizler. Her gün yeni içeriklerle bilgiye açılan kapınız.';
export const SITE_URL = 'https://mindversedaily.vercel.app';
export const SITE_AUTHOR = 'MindVerse Editorial Team';
export const SITE_KEYWORDS = 'bilim haberleri, sağlık, psikoloji, teknoloji, uzay, tarih, araştırma, güncel haberler, akademik çalışmalar, bilimsel keşifler, mental sağlık, beslenme, egzersiz, motivasyon, aşk rehberi';
export const SITE_LANG = 'tr-TR';
export const SITE_LOCALE = 'tr_TR';

// Enhanced SEO Configuration
export const SITE_TWITTER = '@mindversedaily';
export const SITE_FACEBOOK = 'mindversedaily';
export const SITE_INSTAGRAM = 'mindversedaily';

// Analytics and Monetization
export const GOOGLE_ANALYTICS_ID = 'G-B91B93QXHJ';
export const GOOGLE_ADSENSE_ID = 'ca-pub-3096725438789562';
export const GOOGLE_SITE_VERIFICATION = 'MindVerse-Daily-Blog-Verification-2025';

// Content Configuration
export const POSTS_PER_PAGE = 12;
export const FEATURED_POSTS_COUNT = 6;

// Category Configuration with SEO
export const CATEGORIES = {
  health: {
    name: 'Sağlık',
    description: 'Sağlık haberleri, tıp, mental sağlık, beslenme ve egzersiz rehberleri',
    keywords: 'sağlık haberleri, tıp, wellness, mental sağlık, beslenme, egzersiz, doktor tavsiyeleri',
    color: '#10b981'
  },
  psychology: {
    name: 'Psikoloji',
    description: 'Psikoloji, davranış bilimi, zihin sağlığı ve kişilik gelişimi',
    keywords: 'psikoloji, davranış bilimi, zihin sağlığı, kişilik, terapi, bilişsel psikoloji',
    color: '#8b5cf6'
  },
  history: {
    name: 'Tarih',
    description: 'Tarih haberleri, antik medeniyetler, kültür ve arkeoloji',
    keywords: 'tarih haberleri, geçmiş, medeniyet, kültür, arkeoloji, antik çağ, tarihsel olaylar',
    color: '#f59e0b'
  },
  space: {
    name: 'Uzay',
    description: 'Uzay haberleri, astronomi, gezegen keşfi ve uzay teknolojisi',
    keywords: 'uzay haberleri, astronomi, gezegen keşfi, galaksi, NASA, astronot, uzay teknolojisi',
    color: '#3b82f6'
  },
  quotes: {
    name: 'Alıntılar',
    description: 'İlham verici sözler, motivasyon ve başarı rehberleri',
    keywords: 'ilham verici sözler, alıntılar, hikmet, felsefe, motivasyon, başarı sözleri',
    color: '#ef4444'
  },
  love: {
    name: 'Aşk',
    description: 'Aşk rehberi, ilişki tavsiyeleri ve duygusal gelişim',
    keywords: 'aşk rehberi, ilişki tavsiyeleri, duygular, romantizm, sevgi, çift terapisi',
    color: '#ec4899'
  }
};

// Performance Configuration
export const IMAGE_SIZES = [320, 640, 768, 1024, 1200];
export const IMAGE_QUALITY = 85;

// Internationalization
export const SUPPORTED_LANGUAGES = ['tr', 'en'];
export const DEFAULT_LANGUAGE = 'tr';
