#!/usr/bin/env python3
"""
Clean Groq Translator - 15 second rate limiting
High-quality translation with API safety
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

def safe_groq_translate(prompt: str) -> str:
    """Safe Groq API call with 15-second rate limiting"""
    print("   ⏱️ API güvenliği için 15 saniye bekleniyor...")
    time.sleep(15)  # 15-second rate limiting

    try:
        result = generate_content(prompt)
        if result:
            # Clean the result
            result = result.strip()
            # Remove common artifacts
            if result.startswith(('İşte', 'Burada', 'Aşağıda')):
                lines = result.split('\n')
                if len(lines) > 1:
                    result = '\n'.join(lines[1:]).strip()

            return result
        return ""
    except Exception as e:
        print(f"   ❌ Groq API hatası: {e}")
        return ""

def translate_article_content(english_content: str) -> str:
    """Translate article content"""
    prompt = f"""Sen profesyonel çevirmensin. Bu İngilizce makaleyi doğal Türkçeye çevir.

KURALLAR:
- Akıcı ve doğal Türkçe kullan
- Teknik terimleri Türkçeleştir
- Başlıkları da çevir
- Sadece çeviriyi ver

Makale:
{english_content}

Türkçe çeviri:"""

    return safe_groq_translate(prompt)

def translate_title(english_title: str) -> str:
    """Translate article title"""
    prompt = f"""Bu başlığı çekici Türkçe başlığa çevir. 50 karakterden kısa olsun.

İngilizce: {english_title}

Türkçe başlık:"""

    result = safe_groq_translate(prompt)
    if result:
        # Clean title
        result = result.strip('"\'').strip()
        if ':' in result and len(result.split(':')[1].strip()) > 10:
            result = result.split(':')[1].strip()
        return result
    return "Sağlık ve Yaşam Rehberi"

def translate_description(english_desc: str) -> str:
    """Translate article description"""
    prompt = f"""Bu açıklamayı Türkçeye çevir. 100 karakterden kısa olsun.

İngilizce: {english_desc}

Türkçe açıklama:"""

    result = safe_groq_translate(prompt)
    if result:
        result = result.strip('"\'').strip()
        if len(result) > 100:
            result = result[:97] + "..."
        return result
    return "MindVerse Daily'den güncel bilgiler"

def translate_single_article(file_path: str) -> bool:
    """Translate a single English article to Turkish"""
    try:
        print(f"\n📝 Çevriliyor: {os.path.basename(file_path)}")

        # Check if already translated
        tr_file_path = file_path.replace('.en.md', '.tr.md')
        if os.path.exists(tr_file_path):
            print("   ⏭️ Zaten çevrilmiş, atlanıyor")
            return True

        # Read English file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, english_content = extract_frontmatter_and_content(content)
        english_title = frontmatter.get('title', '').strip('"')
        english_desc = frontmatter.get('description', '').strip('"')

        print(f"   📖 Başlık: {english_title[:40]}...")

        # Translate content (main translation - takes longest)
        print("   🤖 İçerik çevriliyor...")
        turkish_content = translate_article_content(english_content)
        if not turkish_content:
            print("   ❌ İçerik çevirme başarısız")
            return False

        # Translate title
        print("   📝 Başlık çevriliyor...")
        turkish_title = translate_title(english_title)

        # Translate description
        print("   📄 Açıklama çevriliyor...")
        turkish_desc = translate_description(english_desc)

        # Create Turkish filename
        turkish_slug = slugify_turkish(turkish_title)
        date_prefix = os.path.basename(file_path)[:10]  # Extract date
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

        print(f"   ✅ Başarılı: {turkish_title}")
        print(f"   💾 Dosya: {turkish_filename}")
        return True

    except Exception as e:
        print(f"   ❌ Çeviri hatası: {e}")
        return False

def get_recent_untranslated_articles(days: int = 5) -> List[str]:
    """Get recent English articles that need translation"""
    today = datetime.datetime.now()
    untranslated_files = []

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
                        untranslated_files.append(file_path)

    return untranslated_files

def main():
    """Main translation function"""
    import argparse

    parser = argparse.ArgumentParser(description="Groq ile güvenli çeviri (15s rate limit)")
    parser.add_argument("--days", type=int, default=5, help="Son kaç günün makalelerini çevir")
    args = parser.parse_args()

    print(f"🌟 Groq Güvenli Çevirici - Son {args.days} gün")
    print("⏱️ API güvenliği: Her çeviri arasında 15 saniye bekleme")
    print()

    # Get untranslated articles
    untranslated_files = get_recent_untranslated_articles(args.days)

    if not untranslated_files:
        print("✨ Çevrilecek yeni makale bulunamadı!")
        return

    print(f"📚 {len(untranslated_files)} çevrilmemiş makale bulundu:")
    for i, file_path in enumerate(untranslated_files, 1):
        print(f"   {i}. {os.path.basename(file_path)}")

    print()

    # Confirm if many files
    if len(untranslated_files) > 3:
        estimated_time = len(untranslated_files) * 1  # ~1 minute per article with 15s delays
        print(f"⚠️ Tahmini süre: {estimated_time} dakika (15s güvenli bekleme ile)")
        response = input("Devam etmek istiyor musunuz? (y/N): ")
        if response.lower() != 'y':
            print("❌ İptal edildi")
            return

    # Start translation
    success_count = 0
    total_time_start = time.time()

    for i, file_path in enumerate(untranslated_files, 1):
        print(f"\n{'='*60}")
        print(f"📖 {i}/{len(untranslated_files)} - Çeviri işlemi")

        if translate_single_article(file_path):
            success_count += 1

        # Show progress
        if i < len(untranslated_files):
            remaining = len(untranslated_files) - i
            print(f"   📊 Kalan: {remaining} makale")

    # Summary
    total_time = (time.time() - total_time_start) / 60
    print(f"\n{'='*60}")
    print(f"🎉 Çeviri süreci tamamlandı!")
    print(f"✅ Başarılı: {success_count}/{len(untranslated_files)} makale")
    print(f"⏱️ Toplam süre: {total_time:.1f} dakika")
    print(f"📂 Türkçe dosyalar: src/content/blog/ klasöründe .tr.md uzantılı")

if __name__ == "__main__":
    main()
