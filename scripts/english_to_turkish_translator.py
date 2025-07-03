#!/usr/bin/env python3
"""
English to Turkish Article Translator using Ollama
Translates Groq-generated English articles to high-quality Turkish
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

def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Call Ollama API for translation"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,  # Lower temperature for more consistent translation
            "top_p": 0.9,
            "num_predict": 2048
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=600)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        print(f"❌ Ollama API error: {e}")
        raise

def extract_frontmatter_and_content(markdown_content: str) -> Tuple[dict, str]:
    """Extract frontmatter and content from markdown file"""
    lines = markdown_content.strip().split('\n')

    if not lines[0].strip() == '---':
        raise ValueError("Invalid markdown: no frontmatter start")

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

def clean_turkish_translation(text: str) -> str:
    """Clean and improve Turkish translation quality"""

    # Remove common translation artifacts
    artifacts = [
        r'Here is the.*?translation.*?:',
        r'İşte.*?çeviri.*?:',
        r'Burada.*?çevrilmiş.*?:',
        r'^(İşte|Burada|Aşağıda).*?:\s*',
        r'translation.*?follows.*?:',
        r'\*\*Translation.*?\*\*',
        r'---.*?Translation.*?---'
    ]

    for pattern in artifacts:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)

    # Fix common English words that slip through
    replacements = {
        r'\bwell-being\b': 'refah',
        r'\blifestyle\b': 'yaşam tarzı',
        r'\bprocessed foods?\b': 'işlenmiş gıdalar',
        r'\bwhole grain\b': 'tam tahıl',
        r'\bresearch shows?\b': 'araştırmalar gösteriyor',
        r'\bstudies? have found\b': 'çalışmalar buldu',
        r'\bparticipants?\b': 'katılımcılar',
        r'\bomega-3 fatty acids?\b': 'omega-3 yağ asitleri',
        r'\bdigestive health\b': 'sindirim sağlığı',
        r'\bcardiovascular\b': 'kardiyovasküler',
        r'\bimmune system\b': 'bağışıklık sistemi',
        r'\bblood pressure\b': 'kan basıncı',
        r'\bcholesterol\b': 'kolesterol',
        r'\bnutrition\b': 'beslenme',
        r'\bexercise\b': 'egzersiz',
        r'\bfitness\b': 'kondisyon',
        r'\bwellness\b': 'sağlık',
        r'\bhealthy\b': 'sağlıklı',
        r'\bdiet\b': 'diyet',
        r'\bstress\b': 'stres',
        r'\bsleep\b': 'uyku',
        r'\bmental health\b': 'zihinsel sağlık',
        r'\bphysical activity\b': 'fiziksel aktivite'
    }

    for eng_pattern, turkish_word in replacements.items():
        text = re.sub(eng_pattern, turkish_word, text, flags=re.IGNORECASE)

    # Clean up extra whitespace and formatting
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple newlines
    text = re.sub(r' +', ' ', text)  # Multiple spaces
    text = text.strip()

    return text

def translate_article_to_turkish(file_path: str) -> bool:
    """Translate a single English article to Turkish"""

    try:
        # Read English article
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract frontmatter and content
        frontmatter, english_content = extract_frontmatter_and_content(content)

        print(f"   📖 English article: {frontmatter.get('title', 'Unknown')[:50]}...")

        # Create high-quality Turkish translation prompt
        translation_prompt = f"""Sen profesyonel bir çevirmensin. Bu İngilizce makaleyi mükemmel Türkçeye çevir.

KATIK KURALLAR:
1. İngilizce hiçbir kelime kullanma - TEK KELİME BİLE
2. Doğal ve akıcı Türkçe cümleler kur
3. Teknik terimleri Türkçeleştir
4. Başlıkları da çevir
5. Orijinal anlamı koru ama Türk okuyucuya hitap et
6. Sadece çeviriyi ver, açıklama yapma

KELİME ÇEVİRİLERİ (ZORUNLU):
- well-being → refah/sağlıklı yaşam
- lifestyle → yaşam tarzı
- processed foods → işlenmiş gıdalar
- research shows → araştırmalar gösteriyor
- participants → katılımcılar
- omega-3 fatty acids → omega-3 yağ asitleri
- digestive health → sindirim sağlığı
- cardiovascular → kardiyovasküler
- immune system → bağışıklık sistemi
- nutrition → beslenme
- exercise → egzersiz
- wellness → sağlık
- stress → stres
- sleep → uyku
- mental health → zihinsel sağlık

ÇEVİRİLECEK MAKALE:
{english_content}

TÜRKÇE ÇEVİRİ:"""

        # Get translation from Ollama
        print("   🤖 Ollama ile çevriliyor...")
        turkish_translation = call_ollama(translation_prompt)

        if not turkish_translation:
            print("   ❌ Çeviri alınamadı")
            return False

        # Clean the translation
        turkish_translation = clean_turkish_translation(turkish_translation)

        # Translate title and description
        title_prompt = f"""Bu İngilizce başlığı Türkçeye çevir. Sadece çeviriyi ver, açıklama yapma:

İngilizce: {frontmatter.get('title', '')}

Türkçe:"""

        turkish_title = call_ollama(title_prompt).strip()
        turkish_title = clean_turkish_translation(turkish_title)

        time.sleep(2)  # Rate limiting

        desc_prompt = f"""Bu İngilizce açıklamayı Türkçeye çevir. Sadece çeviriyi ver, açıklama yapma:

İngilizce: {frontmatter.get('description', '')}

Türkçe:"""

        turkish_description = call_ollama(desc_prompt).strip()
        turkish_description = clean_turkish_translation(turkish_description)

        # Create Turkish file path
        turkish_file_path = file_path.replace('.en.md', '.tr.md')

        # Create Turkish frontmatter
        turkish_frontmatter = frontmatter.copy()
        turkish_frontmatter['title'] = f'"{turkish_title}"'
        turkish_frontmatter['description'] = f'"{turkish_description[:150]}..."'

        # Write Turkish article
        with open(turkish_file_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            for key, value in turkish_frontmatter.items():
                f.write(f'{key}: {value}\n')
            f.write("---\n\n")
            f.write(turkish_translation)

        print(f"   ✅ Türkçe makale oluşturuldu: {turkish_title[:50]}...")
        return True

    except Exception as e:
        print(f"   ❌ Çeviri hatası: {e}")
        return False

def get_recent_english_articles(days: int = 1) -> List[str]:
    """Get recently created English articles"""
    today = datetime.datetime.now()
    recent_files = []

    # Check each category
    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*.en.md")
            en_files = glob.glob(pattern)

            for file_path in en_files:
                # Check if Turkish version doesn't exist
                tr_file_path = file_path.replace('.en.md', '.tr.md')
                if not os.path.exists(tr_file_path):
                    # Check if file is recent
                    file_date = os.path.getctime(file_path)
                    file_datetime = datetime.datetime.fromtimestamp(file_date)

                    if (today - file_datetime).days <= days:
                        recent_files.append(file_path)

    return recent_files

def translate_recent_articles(days: int = 1):
    """Translate recent English articles to Turkish"""
    print("🔍 Son İngilizce makaleler aranıyor...")

    recent_files = get_recent_english_articles(days)

    if not recent_files:
        print("❌ Çevrilecek yeni İngilizce makale bulunamadı")
        return

    print(f"📚 {len(recent_files)} İngilizce makale bulundu")

    success_count = 0
    total_count = len(recent_files)

    for i, file_path in enumerate(recent_files, 1):
        print(f"\n📝 {i}/{total_count} çevriliyor...")

        if translate_article_to_turkish(file_path):
            success_count += 1

        # Rate limiting between translations
        time.sleep(3)

    print(f"\n🎉 Çeviri tamamlandı!")
    print(f"✅ Başarılı: {success_count}/{total_count}")
    print(f"📂 Türkçe makaleler: src/content/blog/*/yyyymmdd-*.tr.md")

if __name__ == "__main__":
    print("🇹🇷 İngilizce → Türkçe Makale Çevirmeni")
    print("=" * 50)

    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        print("✅ Ollama çalışıyor")
    except:
        print("❌ Ollama çalışmıyor! Lütfen 'ollama serve' komutunu çalıştırın")
        exit(1)

    days = int(input("Son kaç günün makalelerini çevirmek istiyorsunuz? (1-7): ") or 1)
    translate_recent_articles(days)
