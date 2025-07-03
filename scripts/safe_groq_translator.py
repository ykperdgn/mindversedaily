#!/usr/bin/env python3
"""
Rate-Limit Safe Groq Translator
Optimized for API limits with intelligent waiting and retry logic
"""

import os
import re
import glob
import datetime
import time
from typing import Tuple, List
from pathlib import Path

# Import Groq client
try:
    from groq_client import generate_content
except ImportError:
    print("❌ groq_client.py not found!")
    exit(1)

# Configuration
CONTENT_DIR = Path("src/content/blog")
API_DELAY = 8  # Seconds between API calls
MAX_RETRIES = 3

def safe_groq_translate(prompt: str, context: str = "") -> str:
    """Safe Groq call with rate limiting and retry logic"""

    for attempt in range(MAX_RETRIES):
        try:
            print(f"   🤖 {context} (attempt {attempt + 1})")

            # Rate limiting
            time.sleep(API_DELAY)

            result = generate_content(prompt)
            if result and result.strip():
                return result.strip()
            else:
                print(f"   ⚠️ Empty response")

        except Exception as e:
            error_msg = str(e).lower()
            print(f"   ❌ API error: {e}")

            if "rate limit" in error_msg or "too many requests" in error_msg:
                wait_time = (attempt + 1) * 15  # 15, 30, 45 seconds
                print(f"   ⏳ Rate limit! Waiting {wait_time}s...")
                time.sleep(wait_time)
            elif "503" in error_msg:
                wait_time = 30
                print(f"   🔄 Service unavailable! Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                time.sleep(5)

    print(f"   💀 Failed after {MAX_RETRIES} attempts")
    return ""

def clean_translation(text: str) -> str:
    """Clean up translation artifacts"""

    # Remove intro phrases
    patterns = [
        r'^.*?(işte|burada|aşağıda).*?(çeviri|translation).*?:\s*',
        r'^.*?translation.*?:\s*',
        r'^.*?türkçe.*?:\s*',
        r'^\s*(çeviri|translation)\s*:\s*'
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    # Clean whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()

def slugify_turkish(text: str) -> str:
    """Convert Turkish text to URL-friendly slug"""
    tr_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }

    for tr_char, en_char in tr_map.items():
        text = text.replace(tr_char, en_char)

    text = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')

    return text[:60]  # Shorter for safety

def extract_frontmatter(content: str) -> Tuple[dict, str]:
    """Extract frontmatter and content"""
    lines = content.strip().split('\n')

    if not lines[0].strip() == '---':
        raise ValueError("No frontmatter")

    frontmatter = {}
    content_start = 0

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            content_start = i + 1
            break
        elif ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"')

    content = '\n'.join(lines[content_start:]).strip()
    return frontmatter, content

def translate_article_safe(file_path: str) -> bool:
    """Translate article with API safety"""

    try:
        print(f"\n📝 Çevriliyor: {os.path.basename(file_path)}")

        # Read English file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, english_content = extract_frontmatter(content)
        english_title = frontmatter.get('title', '').strip('"')

        print(f"   📖 İngilizce: {english_title[:50]}...")

        # ONE BIG TRANSLATION CALL - save API usage
        big_prompt = f"""Sen profesyonel çevirmensin. Bu İngilizce blog makalesini Türkçeye çevir.

KURALL R:
- Doğal Türkçe kullan
- Başlığı ve içeriği çevir
- Sadece çeviriyi ver
- Format: BAŞLIK: [başlık] İÇERİK: [içerik]

İngilizce makale:
BAŞLIK: {english_title}
İÇERİK: {english_content}

Türkçe çeviri:"""

        # Single API call for everything
        translation = safe_groq_translate(big_prompt, "Tüm makale çevriliyor")

        if not translation:
            print("   ❌ Çeviri başarısız")
            return False

        # Parse the translation
        translation = clean_translation(translation)

        # Extract title and content
        if "BAŞLIK:" in translation and "İÇERİK:" in translation:
            parts = translation.split("İÇERİK:", 1)
            title_part = parts[0].replace("BAŞLIK:", "").strip()
            content_part = parts[1].strip()
        else:
            # Fallback: use first line as title
            lines = translation.split('\n')
            title_part = lines[0].strip('# ').strip()
            content_part = '\n'.join(lines[1:]).strip()

        # Clean title
        turkish_title = title_part.strip('"\'*').strip()
        if len(turkish_title) > 80:
            turkish_title = turkish_title[:77] + "..."

        # Generate description from content
        turkish_desc = content_part[:120] + "..." if len(content_part) > 120 else content_part
        turkish_desc = turkish_desc.replace('\n', ' ').strip()

        # Create Turkish filename
        turkish_slug = slugify_turkish(turkish_title)
        date_prefix = os.path.basename(file_path)[:10]
        turkish_filename = f"{date_prefix}-{turkish_slug}.tr.md"

        # File path
        category_dir = os.path.dirname(file_path)
        turkish_file_path = os.path.join(category_dir, turkish_filename)

        # Write Turkish file
        with open(turkish_file_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(f'title: "{turkish_title}"\n')
            f.write(f'description: "{turkish_desc}"\n')
            f.write(f'pubDate: {frontmatter.get("pubDate", "2025-07-03")}\n')
            f.write(f'category: {frontmatter.get("category", "health")}\n')
            f.write(f'tags: []\n')
            f.write(f'image: {frontmatter.get("image", "/assets/blog-placeholder-1.svg")}\n')
            f.write("---\n\n")
            f.write(content_part)

        print(f"   ✅ Başarılı: {turkish_title}")
        print(f"   💾 Dosya: {turkish_filename}")

        return True

    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return False

def translate_recent_safe(days: int = 7, max_articles: int = 5):
    """Translate recent articles with API safety"""

    print(f"🛡️  API-Safe Groq Çevirici")
    print(f"📅 Son {days} gün, maksimum {max_articles} makale")
    print(f"⏱️  API gecikme: {API_DELAY}s, retry: {MAX_RETRIES}")
    print("=" * 50)

    # Find recent English articles
    today = datetime.datetime.now()
    recent_files = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            for file_path in category_dir.glob("*.en.md"):
                # Check if recent
                file_stat = os.stat(file_path)
                file_date = datetime.datetime.fromtimestamp(file_stat.st_mtime)

                if (today - file_date).days <= days:
                    # Check if Turkish version exists
                    tr_file = str(file_path).replace('.en.md', '.tr.md')
                    if not os.path.exists(tr_file):
                        recent_files.append(str(file_path))

    if not recent_files:
        print("✨ Çevrilecek yeni makale yok!")
        return

    # Limit to max_articles to save API usage
    recent_files = recent_files[:max_articles]

    print(f"📚 {len(recent_files)} makale çevrilecek")

    success_count = 0

    for i, file_path in enumerate(recent_files, 1):
        print(f"\n🔄 {i}/{len(recent_files)}")

        if translate_article_safe(file_path):
            success_count += 1

        # Extra delay between articles
        if i < len(recent_files):
            print("   ⏳ API arası bekleme...")
            time.sleep(5)

    print(f"\n🎯 Sonuç: {success_count}/{len(recent_files)} başarılı")
    print("📂 Türkçe dosyalar: src/content/blog/*/*.tr.md")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API-Safe Groq Translator")
    parser.add_argument("--days", type=int, default=3, help="Son kaç gün (varsayılan: 3)")
    parser.add_argument("--max", type=int, default=3, help="Maksimum makale sayısı (varsayılan: 3)")

    args = parser.parse_args()

    translate_recent_safe(args.days, args.max)
