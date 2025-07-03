#!/usr/bin/env python3
"""
Smart Turkish Translator - Creates unique titles for each article
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
            "num_predict": 1500
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
    tr_map = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }

    for tr_char, en_char in tr_map.items():
        text = text.replace(tr_char, en_char)

    text = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')

    return text[:60]

def super_aggressive_cleanup(text: str) -> str:
    """Super aggressive English cleanup"""
    
    # Remove intro patterns
    intro_patterns = [
        r'^.*?(here is|this is|below is).*?translation.*?:?\s*',
        r'^.*?(işte|burada|aşağıda).*?(çeviri|translation).*?:?\s*',
        r'^\s*(translation|çeviri|türkçe)\s*:?\s*',
        r'^.*?follows.*?:?\s*'
    ]
    
    for pattern in intro_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # Dictionary of problematic English words
    english_words = {
        # Awareness and mental health terms that slip through
        r'\bawareness\b': 'farkındalık',
        r'\bstigma\b': 'damgalama',
        r'\bvulnerability\b': 'savunmasızlık',
        r'\bjudgment\b': 'yargı',
        r'\blistening\b': 'dinleme',
        r'\bself-compassion\b': 'öz-şefkat',
        r'\bmental load\b': 'zihinsel yük',
        r'\bmindfulness\b': 'bilinçli farkındalık',
        r'\breduction\b': 'azaltma',
        r'\bcomprehensive\b': 'kapsamlı',
        r'\beffective\b': 'etkili',
        
        # Health terms
        r'\bwell-being\b': 'refah',
        r'\blifestyle\b': 'yaşam tarzı',
        r'\bprocessed foods?\b': 'işlenmiş gıdalar',
        r'\bresearch shows?\b': 'araştırmalar gösteriyor',
        r'\bstudies show\b': 'çalışmalar gösteriyor',
        r'\bparticipants?\b': 'katılımcılar',
        r'\bomega-3 fatty acids?\b': 'omega-3 yağ asitleri',
        r'\bcardiovascular\b': 'kalp-damar',
        r'\bimmune system\b': 'bağışıklık sistemi',
        r'\bdigestive health\b': 'sindirim sağlığı',
        r'\bphysical activity\b': 'fiziksel aktivite',
        r'\bnutrition\b': 'beslenme',
        
        # Common words
        r'\bhealth\b': 'sağlık',
        r'\bexercise\b': 'egzersiz',
        r'\bfitness\b': 'kondisyon',
        r'\bwellness\b': 'sağlık',
        r'\bstress\b': 'stres',
        r'\bsleep\b': 'uyku',
        r'\bdiet\b': 'diyet',
        r'\bmental health\b': 'zihinsel sağlık',
        
        # Mixed language errors
        r'\bincidenceini\b': 'sıklığını',
        r'\bintervençileri\b': 'müdahaleleri',
        r'\btakeaways?\b': 'çıkarımlar',
        r'\bNCD\'?s?\b': 'KHH',
        r'\bNCD\'?lerin?\b': 'KHH\'ların',
        
        # Common phrases
        r'\bcombat\b': 'mücadele',
        r'\bapproach\b': 'yaklaşım',
        r'\bstrategies\b': 'stratejiler',
        r'\bprevention\b': 'önleme',
        r'\btreatment\b': 'tedavi',
        r'\bmanagement\b': 'yönetim'
    }
    
    for eng_pattern, tr_word in english_words.items():
        text = re.sub(eng_pattern, tr_word, text, flags=re.IGNORECASE)
    
    # Remove any remaining English sentences (containing common English words)
    english_sentence_patterns = [
        r'[^.!?]*\b(and|the|of|to|in|for|with|by|from|this|that|these|those|will|can|may|should|would)\b[^.!?]*[.!?]',
        r'[^.!?]*\b(mental health|well-being|research|studies|participants)\b[^.!?]*[.!?]'
    ]
    
    for pattern in english_sentence_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up formatting
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()
    
    return text

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

def create_unique_turkish_title(english_title: str, content_sample: str, category: str) -> str:
    """Create unique Turkish title based on content"""
    
    # Try simple translation first
    title_prompt = f"Bu başlığı çok kısa ve öz Türkçeye çevir: {english_title}"
    translated_title = call_ollama(title_prompt)
    translated_title = super_aggressive_cleanup(translated_title)
    
    # Clean up the translation
    translated_title = re.sub(r'^["\']|["\']$', '', translated_title)
    translated_title = translated_title.strip()
    
    # If translation is good, use it
    if 10 <= len(translated_title) <= 80 and not any(word in translated_title.lower() for word in ['title', 'başlık', 'here is', 'işte']):
        return translated_title
    
    # Otherwise create based on content keywords
    content_lower = content_sample.lower()
    
    # Category-specific title generation
    if category == 'health':
        if 'beslenme' in content_lower or 'diyet' in content_lower:
            return "Beslenme ve Sağlıklı Yaşam Rehberi"
        elif 'egzersiz' in content_lower or 'spor' in content_lower:
            return "Egzersiz ve Fitness ile Sağlıklı Yaşam"
        elif 'zihinsel' in content_lower or 'mental' in content_lower:
            return "Zihinsel Sağlık ve Farkındalık"
        elif 'kalp' in content_lower or 'kardiyovasküler' in content_lower:
            return "Kalp Sağlığı ve Koruma Yöntemleri"
        elif 'önleme' in content_lower or 'koruma' in content_lower:
            return "Hastalık Önleme ve Koruyucu Sağlık"
        else:
            return "Sağlık ve Yaşam Kalitesi Rehberi"
    
    elif category == 'psychology':
        if 'stres' in content_lower:
            return "Stres Yönetimi ve Zihinsel Sağlık"
        elif 'ilişki' in content_lower:
            return "İlişkiler ve Duygusal Sağlık"
        elif 'motivasyon' in content_lower:
            return "Motivasyon ve Kişisel Gelişim"
        else:
            return "Psikoloji ve İnsan Davranışları"
    
    elif category == 'space':
        return "Uzay Bilimleri ve Keşifler"
    elif category == 'history':
        return "Tarih ve Kültür Araştırmaları"
    elif category == 'love':
        return "Aşk ve İlişkiler Rehberi"
    elif category == 'quotes':
        return "İlham Verici Düşünceler ve Sözler"
    else:
        return f"{category.title()} Rehberi ve İpuçları"

def smart_translate_article(file_path: str) -> bool:
    """Smart translation with unique titles"""

    try:
        print(f"📝 Çevriliyor: {os.path.basename(file_path)}")

        # Read English file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, english_content = extract_frontmatter_and_content(content)

        # Simple translation
        translate_prompt = f"""Bu makaleyi Türkçeye çevir. Hiç İngilizce kelime kullanma:

{english_content}

Türkçe:"""

        print("   🤖 İçerik çevriliyor...")
        turkish_content = call_ollama(translate_prompt)

        if not turkish_content:
            print("   ❌ Çeviri başarısız")
            return False

        # Super aggressive cleanup
        turkish_content = super_aggressive_cleanup(turkish_content)

        time.sleep(2)

        # Create unique title
        english_title = frontmatter.get('title', '').strip('"')
        category = frontmatter.get('category', 'health')
        
        print("   📝 Benzersiz başlık oluşturuluyor...")
        turkish_title = create_unique_turkish_title(english_title, turkish_content[:300], category)

        time.sleep(2)

        # Simple description
        english_desc = frontmatter.get('description', '')
        desc_prompt = f"Bu açıklamayı 50 kelimeye çevir: {english_desc}"
        turkish_description = call_ollama(desc_prompt)
        turkish_description = super_aggressive_cleanup(turkish_description)

        if len(turkish_description) > 150 or len(turkish_description) < 10:
            category_names = {
                'health': 'sağlık',
                'psychology': 'psikoloji',
                'history': 'tarih',
                'space': 'uzay',
                'quotes': 'ilham',
                'love': 'aşk'
            }
            cat_tr = category_names.get(category, category)
            turkish_description = f"{cat_tr.title()} konusunda uzman görüşleri ve pratik öneriler"

        # Create Turkish filename
        date_part = os.path.basename(file_path)[:10]
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

        print(f"   ✅ Başarılı: {turkish_title}")
        print(f"   📁 Dosya: {turkish_filename}")

        return True

    except Exception as e:
        print(f"   ❌ Hata: {e}")
        return False

def get_recent_english_files(days: int = 7) -> List[str]:
    """Get recent English files without Turkish versions"""
    recent_files = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*.en.md")
            en_files = glob.glob(pattern)

            for file_path in en_files:
                tr_file_path = file_path.replace('.en.md', '.tr.md')
                if not os.path.exists(tr_file_path):
                    recent_files.append(file_path)

    return recent_files

def main():
    print("🧠 Akıllı Türkçe Çevirmen")
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
        if smart_translate_article(file_path):
            success += 1
        time.sleep(4)  # Rate limiting

    print(f"\n🎉 Tamamlandı! {success}/{len(files)} başarılı")

if __name__ == "__main__":
    main()
