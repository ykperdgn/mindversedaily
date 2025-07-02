#!/usr/bin/env python3
"""
Turkish Content Generator with Groq API
Single category mode for API rate limiting
"""

import os
import json
import datetime
import random
import time
import re
import sys
from typing import Dict, List, Set, Tuple
from image_fetcher import ImageFetcher
from groq_client import generate_content

# Configuration
CATEGORIES = ["health", "psychology", "history", "space", "quotes", "love", "business", "science", "world"]
TARGET_ARTICLES = 1  # Generate 1 article at a time to respect API limits

# Turkish subtopics for better content variety
TURKISH_SUBTOPICS = {
    "health": [
        "beslenme bilimi", "egzersiz fizyolojisi", "uyku optimizasyonu", "stres yönetimi",
        "bağışıklık sistemi", "sağlıklı yaşlanma", "preventif tıp", "beyin sağlığı",
        "kardiyovasküler sağlık", "sindirim sağlığı", "hormonal denge", "zihinsel beslenme",
        "fitness yenilikleri", "alternatif tıp", "tıbbi atılımlar", "uzun yaşam araştırmaları",
        "hastalık önleme", "wellness alışkanlıkları", "sağlık teknolojisi", "metabolik sağlık"
    ],
    "psychology": [
        "bilişsel önyargı araştırmaları", "duygusal zeka gelişimi", "çocuk psikolojisi", "terapötik yaklaşımlar",
        "motivasyon bilimi", "kişilik psikolojisi", "sosyal dinamikler", "hafıza geliştirme",
        "davranış psikolojisi", "sosyal psikoloji", "bilişsel psikoloji", "pozitif psikoloji",
        "nörobilim bulguları", "karar verme psikolojisi", "alışkanlık oluşturma", "zihinsel dayanıklılık",
        "psikolojik bozukluklar", "terapi yenilikleri", "insan davranışı analizi", "bilinç çalışmaları"
    ],
    "history": [
        "antik medeniyetler gizemleri", "dünya savaşları analizi", "tarihi icatların etkisi", "efsanevi liderler",
        "kültürel devrim çalışmaları", "kayıp medeniyetler", "miras koruma", "arkeolojik keşifler",
        "ortaçağ dönemi", "rönesans keşifleri", "sanayi devrimi etkileri", "kolonyal tarih analizi",
        "antik gizemler", "tarihi şahsiyetler", "imparatorlukların yükseliş ve çöküşü", "dönüm noktası olaylar"
    ],
    "space": [
        "öte gezegen keşifleri", "kara delik gizemleri", "uzay misyonları", "Mars keşfi",
        "kozmik fenomenler", "teleskop yenilikleri", "uzay teknolojisi", "astronot deneyimleri",
        "galaksi oluşumu", "karanlık madde araştırması", "uzay kolonizasyonu", "uydu teknolojisi",
        "gezegen bilimi", "asteroid çalışmaları", "uzay hava durumu", "kozmik radyasyon"
    ],
    "quotes": [
        "ilham verici bilgelik", "felsefi içgörüler", "yaşam dersleri", "başarı ilkeleri",
        "liderlik bilgeliği", "tarihi sözler", "motivasyonel düşünceler", "kişisel gelişim sözleri",
        "kariyer ilhamı", "zorlukları aşma", "pozitif zihniyet", "başarı sözleri",
        "dayanıklılık bilgeliği", "yaratıcılık ilhamı", "girişimcilik sözleri", "mutluluk felsefesi"
    ],
    "love": [
        "ilişki psikolojisi", "çekim bilimi", "aşk dilleri", "ilişki tavsiyeleri",
        "romantik psikoloji", "uzak mesafe ilişkileri", "evlilik çalışmaları", "flört psikolojisi",
        "duygusal yakınlık", "ilişki iletişimi", "çatışma çözümü", "ilişki evreleri",
        "bağlanma teorisi", "aşk nörobilimi", "çift terapisi", "modern flört"
    ],
    "business": [
        "girişimcilik stratejileri", "liderlik gelişimi", "inovasyon yönetimi", "pazarlama trendleri",
        "dijital dönüşüm", "kurumsal kültür", "takım yönetimi", "performans optimizasyonu",
        "müşteri deneyimi", "veri analizi", "teknoloji trendleri", "sürdürülebilir iş"
    ],
    "science": [
        "bilimsel keşifler", "teknolojik atılımlar", "araştırma metodolojileri", "deneysel bulgular",
        "bilim tarihi", "gelecek teknolojileri", "bilimsel yenilikler", "araştırma trendleri",
        "bilim etiği", "interdisipliner çalışmalar", "bilimsel iletişim", "araştırma geliştirme"
    ],
    "world": [
        "küresel trendler", "uluslararası ilişkiler", "kültürlerarası iletişim", "sosyal değişim",
        "çevre sorunları", "ekonomik gelişmeler", "siyasi analizler", "toplumsal hareketler",
        "küreselleşme etkileri", "demografik değişimler", "şehirleşme", "teknoloji ve toplum"
    ]
}

def slugify(text: str) -> str:
    """Convert Turkish text to URL-friendly slug"""
    # Turkish character replacements
    tr_replacements = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }

    for tr_char, en_char in tr_replacements.items():
        text = text.replace(tr_char, en_char)

    text = text.lower().replace(" ", "-")
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:60]

def clean_frontmatter_value(value: str) -> str:
    """Clean and sanitize frontmatter values for Turkish content"""
    if not value:
        return ""

    value = str(value).strip()

    # Remove dangerous YAML characters
    dangerous_chars = ['"', "'", ":", "|", ">", "[", "]", "{", "}", "&", "*", "#", "@", "`", "\\"]
    for char in dangerous_chars:
        if char in ['"', "'"]:
            value = value.replace(char, "")
        else:
            value = value.replace(char, " ")

    # Clean multiple spaces
    value = re.sub(r'\s+', ' ', value).strip()

    # Limit length
    if len(value) > 200:
        value = value[:197] + "..."

    return value

def generate_turkish_article(category: str, subtopic: str) -> str:
    """Generate Turkish article using Groq API"""

    prompt = f"""Sen profesyonel bir Türkçe içerik yazarısın. {category} kategorisi için "{subtopic}" konusunda tamamen Türkçe bir makale yaz.

MUTLAKA TÜRKÇE YAZ! İngilizce kelime kullanma.

Gereksinimler:
- Başlık tamamen Türkçe olsun
- 150-200 kelimelik Türkçe özet
- En az 800 kelime uzunluğunda Türkçe içerik
- Bilimsel ve güncel bilgiler
- Okuyucu dostu Türkçe dil
- Türkçe alt başlıklar
- Pratik Türkçe öneriler

Şu formatta yaz:
BAŞLIK: [Türkçe makale başlığı]
ÖZET: [Türkçe makale özeti]
İÇERİK: [Türkçe makale içeriği]

Konu: {subtopic}
Kategori: {category}

SADECE TÜRKÇE YAZ!"""

    try:
        print(f"🤖 Groq API'den {category} kategorisi için Türkçe makale isteniyor...")
        response = generate_content(prompt)
        print("✅ Groq API'den yanıt alındı")
        return response
    except Exception as e:
        print(f"❌ Groq API hatası: {e}")
        raise

def parse_turkish_article(article_text: str, category: str) -> Tuple[str, str, str]:
    """Parse title, description and content from Turkish article"""
    lines = article_text.strip().splitlines()

    title = None
    description = None
    content_lines = []

    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for section headers
        if line.startswith("BAŞLIK:") or line.startswith("Başlık:"):
            title = line.split(":", 1)[1].strip()
            current_section = "title"
            continue
        elif line.startswith("ÖZET:") or line.startswith("Özet:"):
            description = line.split(":", 1)[1].strip()
            current_section = "description"
            continue
        elif line.startswith("İÇERİK:") or line.startswith("İçerik:"):
            current_section = "content"
            continue

        # Add content to appropriate section
        if current_section == "title" and not title:
            title = line
        elif current_section == "description" and not description:
            description = line
        elif current_section == "content":
            content_lines.append(line)
        elif not title:  # First line as title if no explicit section
            title = line
            current_section = "content"
        elif not description and len(line) > 50:  # Second substantial line as description
            description = line
            current_section = "content"
        else:
            content_lines.append(line)

    # Fallbacks
    if not title:
        title = f"{category.title()} Alanında Yeni Gelişmeler"

    if not description:
        description = f"{category} kategorisinde güncel araştırmalar ve uzman görüşleri ile detaylı analiz."

    # Clean values
    title = clean_frontmatter_value(title)
    description = clean_frontmatter_value(description)

    # Join content
    content = "\n\n".join(content_lines) if content_lines else f"# {title}\n\n{description}\n\nDetaylı makale içeriği burada yer alacak."

    return title, description, content

def load_existing_turkish_titles(category: str) -> Set[str]:
    """Load existing Turkish titles for the category"""
    existing_titles = set()

    content_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog", category)

    if os.path.exists(content_dir):
        for filename in os.listdir(content_dir):
            if filename.endswith(".tr.md"):
                try:
                    with open(os.path.join(content_dir, filename), 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'title:' in content:
                            title_line = [line for line in content.split('\n') if line.strip().startswith('title:')]
                            if title_line:
                                title = title_line[0].split('title:', 1)[1].strip().strip('"\'')
                                existing_titles.add(title.lower())
                except:
                    continue

    return existing_titles

def create_turkish_article_file(category: str, title: str, description: str, content: str, image_url: str):
    """Create Turkish article markdown file"""

    # Create date and slug
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)

    # Create filename
    filename = f"{date_str}-{slug}.tr.md"

    # Create directory if it doesn't exist
    category_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog", category)
    os.makedirs(category_dir, exist_ok=True)

    # Create file path
    file_path = os.path.join(category_dir, filename)

    # Create frontmatter
    frontmatter = f'''---
title: "{title}"
description: "{description}"
pubDate: {date_str}
category: "{category}"
tags: []
image: "{image_url}"
---

{content}'''

    # Write file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"✅ Türkçe makale oluşturuldu: {filename}")
    return filename

def generate_single_turkish_article(category: str):
    """Generate a single Turkish article for the specified category"""

    if category not in CATEGORIES:
        print(f"❌ Geçersiz kategori: {category}")
        return

    if category not in TURKISH_SUBTOPICS:
        print(f"❌ {category} için Türkçe alt konular tanımlanmamış")
        return

    print(f"\n🚀 {category.upper()} kategorisi için Türkçe makale üretimi başlıyor...")

    # Load existing titles
    existing_titles = load_existing_turkish_titles(category)
    print(f"📊 Mevcut {len(existing_titles)} Türkçe makale bulundu")

    # Initialize image fetcher
    try:
        image_fetcher = ImageFetcher()
    except:
        image_fetcher = None
        print("⚠️  Image fetcher başlatılamadı, varsayılan resim kullanılacak")

    # Select random subtopic
    subtopic = random.choice(TURKISH_SUBTOPICS[category])
    print(f"📝 Seçilen konu: {subtopic}")

    try:
        # Generate article with Groq
        article_text = generate_turkish_article(category, subtopic)

        # Parse article
        title, description, content = parse_turkish_article(article_text, category)

        # Check if title already exists
        if title.lower() in existing_titles:
            print(f"⚠️  Başlık zaten mevcut, farklı bir başlık oluşturuluyor...")
            title = f"{title} - Güncel Araştırmalar"

        # Get image
        if image_fetcher:
            try:
                image_url = image_fetcher.get_random_image()
                print(f"🖼️  Resim bulundu: {image_url}")
            except:
                image_url = "/assets/blog-placeholder-1.svg"
                print("⚠️  Resim bulunamadı, varsayılan resim kullanılıyor")
        else:
            image_url = "/assets/blog-placeholder-1.svg"

        # Create article file
        filename = create_turkish_article_file(category, title, description, content, image_url)

        print(f"🎉 {category} kategorisi için Türkçe makale başarıyla oluşturuldu!")
        print(f"📄 Dosya: {filename}")
        print(f"📖 Başlık: {title}")

        # Add delay to respect API limits
        print("⏱️  API limitleri için 3 saniye bekleniyor...")
        time.sleep(3)

    except Exception as e:
        print(f"❌ Makale oluşturulurken hata: {e}")
        raise

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Kullanım: python turkish_content_generator.py <kategori>")
        print(f"Kategoriler: {', '.join(CATEGORIES)}")
        return

    category = sys.argv[1].lower()

    if category not in CATEGORIES:
        print(f"❌ Geçersiz kategori: {category}")
        print(f"Geçerli kategoriler: {', '.join(CATEGORIES)}")
        return

    try:
        generate_single_turkish_article(category)
    except KeyboardInterrupt:
        print("\n⚠️  İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")

if __name__ == "__main__":
    main()
