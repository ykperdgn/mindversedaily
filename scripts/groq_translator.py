#!/usr/bin/env python3
"""
Groq-based English to Turkish Article Translator
High-quality translation using Groq API with better prompts
"""

import os
import re
import glob
import datetime
import requests
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

def slugify_turkish(text: str) -> str:
    """Convert Turkish text to URL-friendly slug"""
    # Turkish character mapping
    tr_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }

    # Replace Turkish characters
    for tr_char, en_char in tr_map.items():
        text = text.replace(tr_char, en_char)

    # Convert to lowercase and replace spaces/special chars with hyphens
    text = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')

    # Limit length
    return text[:80]

def safe_groq_call(prompt: str, max_retries: int = 3) -> str:
    """Safe Groq API call with retry logic and rate limiting"""
    for attempt in range(max_retries):
        try:
            # Rate limiting: 15 seconds between calls for API safety
            time.sleep(15)

            result = generate_content(prompt)
            if result:
                return result.strip()
            else:
                print(f"   ⚠️ Empty response, attempt {attempt + 1}/{max_retries}")

        except Exception as e:
            print(f"   ❌ API error attempt {attempt + 1}/{max_retries}: {e}")            if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                wait_time = (attempt + 1) * 20  # Exponential backoff: 20, 40, 60 seconds
                print(f"   ⏳ Rate limit hit, waiting {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                time.sleep(3)

    print(f"   💀 Failed after {max_retries} attempts")
    return ""

def extract_frontmatter_and_content(markdown_content: str) -> Tuple[dict, str]:
    """Extract frontmatter and content from markdown file"""
    lines = markdown_content.strip().split('\n')

    if not lines[0].strip() == '---':
        raise ValueError("No frontmatter found")

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

def clean_groq_translation(text: str) -> str:
    """Clean up Groq translation output"""

    # Remove common artifacts
    artifacts = [
        r'^.*?(işte|burada|aşağıda).*?(çeviri|translation).*?:\s*',
        r'^.*?translation.*?:\s*',
        r'^.*?türkçe.*?:\s*',
        r'^\s*(çeviri|translation)\s*:\s*',
        r'^\s*türkçe\s*:\s*',
        r'^\s*here is.*?translation.*?:\s*'
    ]

    for pattern in artifacts:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()

def translate_with_groq(english_content: str) -> str:
    """Translate content using Groq API"""

    prompt = f"""Sen profesyonel bir çevirmensin. Bu İngilizce makaleyi mükemmel Türkçeye çevir.

KURALLAR:
- Doğal ve akıcı Türkçe kullan
- Teknik terimleri Türkçeleştir
- Orijinal anlamı ve tonu koru
- Sadece çeviriyi ver, açıklama yapma
- Başlıkları da çevir

Çevrilecek makale:
{english_content}

Türkçe çeviri:"""

    try:
        result = generate_content(prompt)
        if result:
            return clean_groq_translation(result)
        return ""
    except Exception as e:
        print(f"❌ Groq translation error: {e}")
        return ""

def translate_title_with_groq(english_title: str) -> str:
    """Translate title using Groq API"""

    prompt = f"""Bu İngilizce başlığı çekici ve kısa Türkçe başlığa çevir. 60 karakterden kısa olsun.

İngilizce başlık: {english_title}

Türkçe başlık:"""

    try:
        result = generate_content(prompt)
        if result:
            # Clean title
            turkish_title = clean_groq_translation(result)
            turkish_title = turkish_title.strip('"\'*').strip()

            # Remove any intro text
            if ':' in turkish_title:
                parts = turkish_title.split(':')
                if len(parts) > 1 and len(parts[1].strip()) > 10:
                    turkish_title = parts[1].strip()

            return turkish_title
        return ""
    except Exception as e:
        print(f"❌ Groq title translation error: {e}")
        return ""

def translate_description_with_groq(english_desc: str) -> str:
    """Translate description using Groq API"""

    prompt = f"""Bu İngilizce açıklamayı Türkçeye çevir. 150 karakterden kısa olsun.

İngilizce açıklama: {english_desc}

Türkçe açıklama:"""

    try:
        result = generate_content(prompt)
        if result:
            turkish_desc = clean_groq_translation(result)
            turkish_desc = turkish_desc.strip('"\'*').strip()

            # Limit length
            if len(turkish_desc) > 150:
                turkish_desc = turkish_desc[:147] + "..."

            return turkish_desc
        return ""
    except Exception as e:
        print(f"❌ Groq description translation error: {e}")
        return ""

def groq_translate_article(file_path: str) -> bool:
    """Translate single article using Groq API"""

    try:
        print(f"📝 Groq ile çevriliyor: {os.path.basename(file_path)}")

        # Read English file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, english_content = extract_frontmatter_and_content(content)
        english_title = frontmatter.get('title', '').strip('"')
        english_desc = frontmatter.get('description', '').strip('"')

        print(f"   📖 Başlık: {english_title[:50]}...")

        # Translate content
        print("   🤖 İçerik çevriliyor...")
        turkish_content = translate_with_groq(english_content)        if not turkish_content:
            print("   ❌ İçerik çevrilemedi")
            return False

        time.sleep(5)  # Rate limiting between translation steps

        # Translate title
        print("   📝 Başlık çevriliyor...")
        turkish_title = translate_title_with_groq(english_title)
        if not turkish_title:
            print("   ⚠️ Başlık çevrilemedi, varsayılan kullanılıyor")
            turkish_title = "Sağlık ve Yaşam Rehberi"

        time.sleep(5)  # Rate limiting between translation steps

        # Translate description
        print("   📄 Açıklama çevriliyor...")
        turkish_desc = translate_description_with_groq(english_desc)
        if not turkish_desc:
            turkish_desc = "MindVerse Daily'den sağlık ve yaşam konularında güncel bilgiler"

        # Create Turkish filename
        turkish_slug = slugify_turkish(turkish_title)
        date_prefix = os.path.basename(file_path)[:10]  # Extract date: 2025-07-03
        turkish_filename = f"{date_prefix}-{turkish_slug}.tr.md"

        # Create Turkish file path
        category_dir = os.path.dirname(file_path)
        turkish_file_path = os.path.join(category_dir, turkish_filename)

        # Create Turkish frontmatter
        turkish_frontmatter = frontmatter.copy()
        turkish_frontmatter['title'] = f'"{turkish_title}"'
        turkish_frontmatter['description'] = f'"{turkish_desc}"'

        # Write Turkish article
        with open(turkish_file_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            for key, value in turkish_frontmatter.items():
                f.write(f'{key}: {value}\n')
            f.write("---\n\n")
            f.write(turkish_content)

        print(f"   ✅ Çeviri tamamlandı: {turkish_title}")
        print(f"   💾 Dosya: {turkish_filename}")

        return True

    except Exception as e:
        print(f"   ❌ Çeviri hatası: {e}")
        return False

def get_recent_english_articles(days: int = 7) -> List[str]:
    """Get recent English articles that don't have Turkish versions"""
    today = datetime.datetime.now()
    recent_files = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*.en.md")
            en_files = glob.glob(pattern)

            for file_path in en_files:
                # Check if file is recent
                file_stat = os.stat(file_path)
                file_date = datetime.datetime.fromtimestamp(file_stat.st_mtime)

                if (today - file_date).days <= days:
                    # Check if Turkish version exists
                    tr_file_path = file_path.replace('.en.md', '.tr.md')
                    if not os.path.exists(tr_file_path):
                        recent_files.append(file_path)

    return recent_files

def is_already_translated(en_file_path: str) -> bool:
    """Check if English article is already translated"""
    tr_file_path = en_file_path.replace('.en.md', '.tr.md')
    return os.path.exists(tr_file_path)

def get_untranslated_articles(days: int = 7) -> List[str]:
    """Get English articles that need translation (smart detection)"""
    today = datetime.datetime.now()
    untranslated_files = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*.en.md")
            en_files = glob.glob(pattern)

            for file_path in en_files:
                # Check if file is recent enough
                file_stat = os.stat(file_path)
                file_date = datetime.datetime.fromtimestamp(file_stat.st_mtime)

                if (today - file_date).days <= days:
                    # Check if already translated
                    if not is_already_translated(file_path):
                        untranslated_files.append(file_path)
                        print(f"   🆕 Translation needed: {os.path.basename(file_path)}")

    return untranslated_files

def translate_recent_articles(days: int = 7):
    """Translate recent English articles to Turkish using Groq (with duplicate check)"""
    print(f"🌟 Groq ile son {days} günün İngilizce makalelerini Türkçeye çevirme başlıyor...")
    print("🔍 Duplicate kontrol yapılıyor...")

    # Get untranslated articles (with smart detection)
    untranslated_files = get_untranslated_articles(days)

    if not untranslated_files:
        print("✨ Çevrilecek yeni İngilizce makale bulunamadı!")
        print("💡 Tüm güncel makaleler zaten çevrilmiş görünüyor")
        return

    print(f"📚 {len(untranslated_files)} çevrilmemiş İngilizce makale bulundu")

    # Ask for confirmation if many files
    if len(untranslated_files) > 5:
        response = input(f"⚠️ {len(untranslated_files)} makale çevrilecek. Devam etmek istiyorum musunuz? (y/N): ")
        if response.lower() != 'y':
            print("❌ İptal edildi")
            return

    success_count = 0

    for i, file_path in enumerate(untranslated_files, 1):
        print(f"\n📖 {i}/{len(untranslated_files)} - Çeviriliyor...")

        # Double check - make sure it's not already translated
        if is_already_translated(file_path):
            print(f"   ⏭️ Zaten çevrilmiş: {os.path.basename(file_path)}")
            continue

        if groq_translate_article(file_path):
            success_count += 1        # Rate limiting between articles
        if i < len(untranslated_files):
            print("   ⏱️ API limitine saygı duyuyoruz (15 saniye bekleme)...")
            time.sleep(15)  # Generous wait time between articles

    print(f"\n🎉 Çeviri tamamlandı!")
    print(f"✅ Başarılı: {success_count}/{len(untranslated_files)} makale")
    print(f"📂 Türkçe makaleler: src/content/blog/ klasöründe .tr.md uzantılı")

    if success_count > 0:
        print(f"\n💡 Duplicate kontrol için çalıştırın:")
        print(f"   python scripts/smart_duplicate_detector.py --report-only")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Groq ile İngilizce makaleleri Türkçeye çevir")
    parser.add_argument("--days", type=int, default=7, help="Son kaç günün makalelerini çevir (varsayılan: 7)")

    args = parser.parse_args()

    translate_recent_articles(args.days)
