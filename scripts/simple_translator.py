#!/usr/bin/env python3
"""
Simple but Effective English to Turkish Translator
Uses very basic prompts and aggressive post-processing
"""

import os
import re
import glob
import datetime
import requests
import time
from typing import Tuple, List
from pathlib import Path

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:latest"
CONTENT_DIR = Path("src/content/blog")

def call_ollama(prompt: str) -> str:
    """Simple Ollama call"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 2000
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return ""

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

def aggressive_turkish_cleanup(text: str) -> str:
    """Aggressively clean up Turkish text"""

    # Remove any intro text
    intro_patterns = [
        r'^.*?(işte|burada|aşağıda).*?çevir.*?:\s*',
        r'^.*?translation.*?:\s*',
        r'^.*?türkçe.*?:\s*',
        r'^\s*çeviri\s*:\s*',
        r'^\s*türkçe\s*:\s*'
    ]

    for pattern in intro_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)        # English words that commonly slip through
        eng_to_tr = {
            # Common words
            r'\bwell-being\b': 'sağlıklı yaşam',
            r'\blifestyle\b': 'yaşam tarzı',
            r'\bprocessed foods?\b': 'işlenmiş gıdalar',
            r'\bresearch shows?\b': 'araştırmalar gösteriyor',
            r'\bparticipants?\b': 'katılımcılar',
            r'\bstudies?\b': 'çalışmalar',
            r'\bhealth\b': 'sağlık',
            r'\bnutrition\b': 'beslenme',
            r'\bexercise\b': 'egzersiz',
            r'\bstress\b': 'stres',
            r'\bsleep\b': 'uyku',
            r'\bdiet\b': 'diyet',
            r'\bfitness\b': 'kondisyon',
            r'\bwellness\b': 'sağlık',

            # Technical terms
            r'\bomega-3 fatty acids?\b': 'omega-3 yağ asitleri',
            r'\bcardiovascular\b': 'kardiyovasküler',
            r'\bimmune system\b': 'bağışıklık sistemi',
            r'\bblood pressure\b': 'kan basıncı',
            r'\bcholesterol\b': 'kolesterol',
            r'\bmental health\b': 'zihinsel sağlık',
            r'\bphysical activity\b': 'fiziksel aktivite',
            r'\bdigestive health\b': 'sindirim sağlığı',
            r'\bgut microbiom(e|u)\b': 'bağırsak mikrobiyomu',
            r'\binternal clock\b': 'iç saat',
            r'\bwhole grains?\b': 'tam tahıllar',
            r'\bomega-3 rich\b': 'omega-3 açısından zengin',

            # Common phrases with English
            r'\bcertain bacterial species, such as.*?,': 'belirli bakteri türleri',
            r'\bglucose tolerance and insulin sensitivity\b': 'glukoz toleransı ve insülin duyarlılığı',
            r'\bsuprachiasmatic nucleus \(SCN\)\b': 'suprakiazmatik çekirdek',
            r'\bcircadian rhythm\b': 'sirkadiyen ritim',
            r'\bdysbiosis\b': 'disbiyoz',
            r'\bFaecalibacterium\b': 'Faecalibacterium bakterisi',

            # Fix common translation errors
            r'\bçıkış trendleri\b': 'gelişen eğilimler',
            r'\bruh-sal bağıntı\b': 'zihin-beden bağlantısı',
            r'\bçağrışım\b': 'eylem çağrısı',
            r'\bdaha fazla:\b': 'bunun ötesinde:',
            r'\bsürüntü\b': 'kronik',
            r'\bmodifiable\b': 'değiştirilebilir',
            r'\belirteçlerini\b': 'belirleyicilerini',
            r'\badresleyerek\b': 'ele alarak',
            r'\bperspektif shifti\b': 'perspektif değişimi',
            r'\bshift\b': 'değişim',
            r'\bgut-friendly\b': 'bağırsak dostu',
            r'\bgut-\b': 'bağırsak ',
            r'\brich yiyecekler\b': 'zengin gıdalar',
            r'\bflaksed\b': 'keten tohumu',
            r'\bchia seeds\b': 'chia tohumu'
        }

    for eng_pattern, tr_replacement in eng_to_tr.items():
        text = re.sub(eng_pattern, tr_replacement, text, flags=re.IGNORECASE)

    # Clean up whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)

    return text.strip()

def extract_frontmatter_and_content(markdown_content: str) -> Tuple[dict, str]:
    """Extract frontmatter and content"""
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

def simple_translate_article(file_path: str) -> bool:
    """Simple translation approach"""

    try:
        print(f"📝 Çevriliyor: {os.path.basename(file_path)}")

        # Read English file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, english_content = extract_frontmatter_and_content(content)

        # VERY SIMPLE translation prompt
        simple_prompt = f"""Bu makaleyi Türkçeye çevir. Sadece çeviriyi ver:

{english_content}

Türkçe çeviri:"""

        print("   🤖 Çevriliyor...")
        turkish_content = call_ollama(simple_prompt)

        if not turkish_content:
            print("   ❌ Çeviri başarısız")
            return False

        # Aggressive cleanup
        turkish_content = aggressive_turkish_cleanup(turkish_content)        # Create smart Turkish title from original
        english_title = frontmatter.get('title', '').strip('"')

        # Better title translation with context
        title_prompt = f"""Bu İngilizce başlığı çekici Türkçe başlığa çevir. 50 karakterden kısa olsun:

İngilizce: {english_title}

Türkçe başlık:"""

        turkish_title = call_ollama(title_prompt)
        turkish_title = aggressive_turkish_cleanup(turkish_title)

        # Clean up title formatting
        turkish_title = turkish_title.strip('"\'*').strip()

        # If title is still bad, extract key topic from content
        if len(turkish_title) > 70 or len(turkish_title) < 10 or not turkish_title:
            print("   ⚠️ Başlık kalitesiz, içerikten çıkarılıyor...")

            # Extract first heading or topic from content
            content_lines = turkish_content.split('\n')[:10]  # First 10 lines
            for line in content_lines:
                if line.startswith('**') and line.endswith('**'):
                    potential_title = line.strip('*').strip()
                    if 15 <= len(potential_title) <= 60:
                        turkish_title = potential_title
                        break

            # Still bad? Create topic-based title
            if not turkish_title or len(turkish_title) > 70:
                topic_words = ['metabolik', 'sağlık', 'beslenme', 'egzersiz', 'uyku', 'stres', 'zihinsel']
                found_topic = None
                for word in topic_words:
                    if word in turkish_content.lower():
                        found_topic = word.title()
                        break

                if found_topic:
                    turkish_title = f"{found_topic} Hakkında Bilmeniz Gerekenler"
                else:
                    category = frontmatter.get('category', 'genel')
                    category_names = {
                        'health': 'Sağlık',
                        'psychology': 'Psikoloji',
                        'history': 'Tarih',
                        'space': 'Uzay',
                        'quotes': 'Alıntılar',
                        'love': 'Aşk'
                    }
                    cat_tr = category_names.get(category, category.title())
                    turkish_title = f"{cat_tr} Dünyasından Yenilikler"

        time.sleep(2)

        # Simple description
        desc_prompt = f"Bu açıklamayı 50 kelimeye Türkçeye çevir: {frontmatter.get('description', '')}"
        turkish_description = call_ollama(desc_prompt)
        turkish_description = aggressive_turkish_cleanup(turkish_description)

        if len(turkish_description) > 150 or not turkish_description:
            turkish_description = f"{cat_tr} konusunda uzman görüşleri ve pratik öneriler"

        # Create Turkish filename
        date_part = os.path.basename(file_path)[:10]  # 2025-07-02
        title_slug = slugify_turkish(turkish_title)
        turkish_filename = f"{date_part}-{title_slug}.tr.md"

        # Create Turkish file path
        category_dir = os.path.dirname(file_path)
        turkish_file_path = os.path.join(category_dir, turkish_filename)

        # Create Turkish frontmatter
        turkish_frontmatter = {
            'title': f'"{turkish_title}"',
            'description': f'"{turkish_description}"',
            'pubDate': frontmatter.get('pubDate', '2025-07-03'),
            'category': frontmatter.get('category', 'health'),
            'tags': frontmatter.get('tags', '[]'),
            'image': frontmatter.get('image', '/assets/blog-placeholder-1.svg')
        }

        # Write Turkish file
        with open(turkish_file_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            for key, value in turkish_frontmatter.items():
                f.write(f'{key}: {value}\n')
            f.write("---\n\n")
            f.write(turkish_content)

        print(f"   ✅ Başarılı: {turkish_title[:50]}...")
        print(f"   📁 Dosya: {turkish_filename}")

        return True

    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return False

def get_recent_english_files(days: int = 7) -> List[str]:
    """Get recent English files"""
    recent_files = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*.en.md")
            en_files = glob.glob(pattern)

            for file_path in en_files:
                tr_file_path = file_path.replace('.en.md', '.tr.md')
                if not os.path.exists(tr_file_path):
                    recent_files.append(file_path)

    return recent_files[:10]  # Limit to 10 files

def main():
    print("🇹🇷 Basit Ama Etkili Çevirmen")
    print("=" * 40)

    # Check Ollama
    try:
        requests.get("http://localhost:11434/api/version", timeout=5)
        print("✅ Ollama çalışıyor")
    except:
        print("❌ Ollama çalışmıyor!")
        return

    # Get files to translate
    files = get_recent_english_files()

    if not files:
        print("❌ Çevrilecek İngilizce makale yok")
        return

    print(f"📚 {len(files)} makale bulundu")

    success = 0
    for i, file_path in enumerate(files, 1):
        print(f"\n{i}/{len(files)}")
        if simple_translate_article(file_path):
            success += 1
        time.sleep(3)  # Rate limiting

    print(f"\n🎉 Tamamlandı! {success}/{len(files)} başarılı")

if __name__ == "__main__":
    main()
