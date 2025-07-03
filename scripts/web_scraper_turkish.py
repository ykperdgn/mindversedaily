#!/usr/bin/env python3
"""
Turkish Content Web Scraper + Ollama Rewriter
Scrapes Turkish content from reliable sources and rewrites with Ollama
"""

import requests
import time
import re
from bs4 import BeautifulSoup
from typing import List, Dict
import feedparser

# Reliable Turkish sources
TURKISH_SOURCES = {
    "health": [
        "https://www.saglik.gov.tr/TR,11156/haberler.html",
        "https://sbu.saglik.gov.tr/",
        "https://hsgm.saglik.gov.tr/"
    ],
    "science": [
        "https://www.tubitak.gov.tr/tr/haber",
        "https://bilimteknik.tubitak.gov.tr/",
    ],
    "psychology": [
        "https://www.psikolog.org.tr/",
    ]
}

RSS_FEEDS = {
    "health": [
        "https://www.medicalnewstoday.com/rss",
        "https://feeds.webmd.com/rss/rss.aspx?RSSSource=RSS_PUBLIC",
    ],
    "science": [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://www.nature.com/nature.rss",
    ],
    "psychology": [
        "https://www.psychologytoday.com/us/blog/feed",
    ]
}

def fetch_turkish_articles(category: str, limit: int = 5) -> List[Dict]:
    """Fetch articles from Turkish sources"""
    articles = []

    if category in TURKISH_SOURCES:
        for url in TURKISH_SOURCES[category]:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract article links and titles
                # This would need customization per site
                links = soup.find_all('a', href=True)

                for link in links[:limit]:
                    if any(keyword in link.text.lower() for keyword in ['makale', 'haber', 'araştırma']):
                        articles.append({
                            'title': link.text.strip(),
                            'url': link['href'],
                            'source': url
                        })

            except Exception as e:
                print(f"Error fetching from {url}: {e}")
                continue

    return articles[:limit]

def fetch_rss_articles(category: str, limit: int = 3) -> List[Dict]:
    """Fetch articles from RSS feeds"""
    articles = []

    if category in RSS_FEEDS:
        for feed_url in RSS_FEEDS[category]:
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:limit]:
                    articles.append({
                        'title': entry.title,
                        'summary': getattr(entry, 'summary', ''),
                        'link': entry.link,
                        'published': getattr(entry, 'published', ''),
                        'source': feed_url
                    })

            except Exception as e:
                print(f"Error fetching RSS from {feed_url}: {e}")
                continue

    return articles[:limit]

def scrape_article_content(url: str) -> str:
    """Scrape full article content from URL"""
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Try to find main content
        content_selectors = [
            'article', '.content', '.post-content',
            '.entry-content', 'main', '.article-body'
        ]

        content = ""
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(strip=True)
                break

        if not content:
            # Fallback to all paragraphs
            paragraphs = soup.find_all('p')
            content = ' '.join([p.get_text(strip=True) for p in paragraphs])

        return content[:2000]  # Limit content length

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def rewrite_with_ollama(content: str, category: str, style: str = "blog") -> str:
    """Rewrite content using Ollama"""

    prompt = f"""Bu içeriği {category} kategorisinde Türkçe blog makalesi olarak yeniden yaz:

KAYNAK İÇERİK:
{content}

GÖREV:
- Kaynak içeriği anla ve ana fikirlerini al
- Türkçe blog makalesi formatında yeniden yaz
- 800-1200 kelime olsun
- Başlık + giriş + 3-4 ana bölüm + sonuç
- Sade ve anlaşılır Türkçe kullan
- Kaynak bilgiyi kopyalama, kendi ifadelerinle yaz

YAZMAYA BAŞLA:"""

    try:
        # Call Ollama API
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3:latest",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1500
            }
        }

        response = requests.post(ollama_url, json=payload, timeout=300)
        response.raise_for_status()

        return response.json()["response"]

    except Exception as e:
        print(f"Ollama error: {e}")
        return ""

def generate_hybrid_content(category: str, count: int = 2):
    """Generate Turkish content using web scraping + Ollama"""
    print(f"🌐 {category} kategorisinde hybrid Türkçe içerik oluşturuluyor...")

    # Fetch source articles
    print("📡 RSS feed'lerden makaleler alınıyor...")
    rss_articles = fetch_rss_articles(category, count)

    print("🔍 Türkçe kaynaklardan içerik aranıyor...")
    turkish_articles = fetch_turkish_articles(category, count)

    all_articles = rss_articles + turkish_articles

    if not all_articles:
        print("❌ Hiç makale bulunamadı")
        return

    print(f"📚 {len(all_articles)} makale bulundu")

    for i, article in enumerate(all_articles):
        print(f"\n📝 {i+1}/{len(all_articles)} işleniyor: {article['title'][:50]}...")

        # Get article content
        if 'summary' in article and article['summary']:
            content = article['summary']
        else:
            content = scrape_article_content(article.get('link', article.get('url', '')))

        if not content:
            print("   ❌ İçerik alınamadı")
            continue

        print(f"   ✅ {len(content)} karakter içerik alındı")

        # Rewrite with Ollama
        print("   🤖 Ollama ile yeniden yazılıyor...")
        rewritten = rewrite_with_ollama(content, category)

        if rewritten:
            print(f"   ✅ {len(rewritten)} karakter yeni içerik oluşturuldu")
            # Here you would save to markdown file
        else:
            print("   ❌ Ollama ile yazılamadı")

        time.sleep(2)  # Rate limiting

if __name__ == "__main__":
    import sys

    print("🇹🇷 Hybrid Türkçe İçerik Oluşturucu")
    print("=" * 40)

    if len(sys.argv) > 1:
        category = sys.argv[1].lower()
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    else:
        print("Mevcut kategoriler: health, science, psychology")
        category = input("Kategori seçin: ").strip().lower()

        if category not in ['health', 'science', 'psychology']:
            print("❌ Geçersiz kategori! health, science veya psychology seçin")
            exit(1)

        count = int(input("Kaç makale? (1-5): ") or 2)

    generate_hybrid_content(category, count)
