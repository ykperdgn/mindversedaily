#!/usr/bin/env python3
"""
MindVerse Bulk Content Generator with Ollama
Generates 20 articles per category (120 total) using local Ollama
Ensures no duplicate titles in same language
"""

import os
import json
import datetime
import random
import time
import re
import requests
import subprocess
from typing import Dict, List, Set, Tuple
from image_fetcher import ImageFetcher

# Configuration
CATEGORIES = ["health", "psychology", "history", "space", "quotes", "love"]
ARTICLES_PER_CATEGORY = 20  # 20 articles per category for English site
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:latest"

# Enhanced subtopics with more variety to prevent duplicates
SUBTOPICS = {
    "health": [
        "mental wellness breakthroughs", "nutrition science discoveries", "exercise physiology", "sleep optimization",
        "stress management techniques", "immune system boosting", "healthy aging secrets", "preventive medicine",
        "brain health research", "cardiovascular wellness", "digestive health science", "hormonal balance",
        "mindful eating practices", "fitness innovation", "alternative medicine studies", "medical breakthroughs",
        "longevity research findings", "disease prevention strategies", "wellness habits", "health technology",
        "metabolic health", "cellular regeneration", "microbiome research", "chronic disease prevention",
        "mental health awareness", "functional medicine", "holistic wellness", "personalized nutrition",
        "exercise biochemistry", "sleep disorders treatment", "stress physiology", "anti-aging research"
    ],
    "psychology": [
        "cognitive bias research", "emotional intelligence development", "child psychology", "therapeutic approaches",
        "motivation science", "personality psychology", "social dynamics", "memory enhancement",
        "behavioral psychology studies", "social psychology research", "cognitive psychology", "positive psychology",
        "neuroscience findings", "decision-making psychology", "habit formation science", "mental resilience",
        "psychological disorders research", "therapy innovations", "human behavior analysis", "consciousness studies",
        "developmental psychology", "clinical psychology", "psychological assessment", "trauma psychology",
        "cognitive therapy", "mindfulness psychology", "personality development", "psychological wellness",
        "learning psychology", "attention research", "perception studies", "psychological healing"
    ],
    "history": [
        "ancient civilizations mysteries", "world war revelations", "historical inventions impact", "legendary leaders",
        "cultural revolution studies", "lost civilizations", "heritage preservation", "archaeological breakthroughs",
        "medieval period insights", "renaissance discoveries", "industrial revolution effects", "colonial history analysis",
        "ancient mysteries solved", "historical figures biography", "empire rise and fall", "pivotal historical events",
        "social movements history", "technological evolution", "military strategies", "historical artifacts",
        "forgotten empires", "historical turning points", "cultural exchanges", "ancient technologies",
        "historical documentaries", "timeline analysis", "historical research methods", "period studies",
        "civilization comparisons", "historical patterns", "legacy studies", "historical preservation"
    ],
    "space": [
        "exoplanet discoveries", "black hole mysteries", "space missions", "Mars exploration",
        "cosmic phenomena", "telescope innovations", "space technology", "astronaut experiences",
        "galaxy formation", "dark matter research", "space colonization", "satellite technology",
        "planetary science", "asteroid studies", "space weather", "cosmic radiation",
        "interstellar exploration", "space engineering", "astronomical discoveries", "universe mysteries",
        "space station research", "rocket technology", "space medicine", "extraterrestrial life",
        "cosmic evolution", "space debris", "lunar research", "solar system exploration",
        "space physics", "astrophysics discoveries", "space observations", "cosmic events"
    ],
    "quotes": [
        "inspirational wisdom", "philosophical insights", "life lessons", "success principles",
        "leadership wisdom", "historical quotes", "motivational thoughts", "personal growth quotes",
        "career inspiration", "overcoming adversity", "positive mindset", "achievement quotes",
        "resilience wisdom", "creativity inspiration", "entrepreneurship quotes", "happiness philosophy",
        "mindfulness quotes", "self-improvement wisdom", "wisdom literature", "timeless wisdom",
        "famous speeches", "literary quotes", "spiritual wisdom", "success stories",
        "life philosophy", "motivational speakers", "wisdom traditions", "inspirational stories",
        "personal development", "achievement mindset", "life transformation", "wisdom sharing"
    ],
    "love": [
        "relationship psychology", "attraction science", "love languages", "relationship advice",
        "romantic psychology", "long-distance relationships", "marriage studies", "dating psychology",
        "emotional intimacy", "relationship communication", "conflict resolution", "relationship phases",
        "attachment theory", "love neuroscience", "couples therapy", "modern dating",
        "relationship maintenance", "love psychology", "relationship hormones", "partnership dynamics",
        "romantic relationships", "love research", "relationship counseling", "emotional bonds",
        "love science", "relationship health", "romantic attachment", "partnership psychology",
        "love and commitment", "relationship success", "emotional connection", "love studies"
    ]
}

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower().replace(" ", "-")
    text = re.sub(r'[^a-z0-9\-]', '', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:60]  # Limit length

def clean_frontmatter_value(value: str) -> str:
    """Clean and sanitize frontmatter values"""
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

def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Call Ollama API to generate content"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.8,
            "top_p": 0.9,
            "top_k": 40,
            "num_predict": 2048
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=600)  # 10 minutes timeout
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        print(f"❌ Ollama API error: {e}")
        raise

def parse_turkish_article_fields(article_text: str, category: str, image_fetcher=None) -> Tuple[str, str, str, str]:
    """Parse title, description, image and content from generated Turkish article"""
    lines = article_text.strip().splitlines()

    # Remove empty lines and unwanted lines
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip unwanted patterns
        line_lower = line.lower()
        if any(pattern in line_lower for pattern in [
            "sen bir türk gazeteci", "görev:", "başla!", "konu:", "kategori:",
            "makale yapısı", "kalite kriterleri", "zorunlu format", "uyarı:",
            "yasak olan", "sadece türkçe", "son kontrol"
        ]):
            continue
        clean_lines.append(line)

    if not clean_lines:
        return f"Yeni {category.title()} Makalesi", f"MindVerse Daily'den {category} kategorisinde güncel makale", "/assets/blog-placeholder-1.svg", "Makale içeriği yüklenemedi."

    # Extract title from first line (usually after ##)
    title = None
    description = None
    content_start_idx = 0

    # Look for a proper title in first 3 lines
    for i, line in enumerate(clean_lines[:3]):
        # Remove markdown headers
        clean_line = line.strip('#').strip()

        # Skip if it's too short or too long for a title
        if len(clean_line) < 10 or len(clean_line) > 100:
            continue

        # Skip if it looks like a section header
        if any(header in clean_line.lower() for header in [
            'giriş', 'sonuç', 'tavsiye', 'öneri', 'başlık', 'açıklama'
        ]):
            continue

        # This looks like a good title
        if not title:
            title = clean_line
            content_start_idx = i + 1
            break

    # If no title found, use first meaningful line
    if not title and clean_lines:
        title = clean_lines[0].strip('#').strip()
        content_start_idx = 1

    # Extract description from content (first paragraph after title)
    for line in clean_lines[content_start_idx:content_start_idx+5]:
        if len(line) > 50 and not line.startswith('#') and not line.startswith('##'):
            description = line[:150] + "..." if len(line) > 150 else line
            break

    # Fallbacks for Turkish
    if not title:
        turkish_categories = {
            "health": "Sağlık",
            "psychology": "Psikoloji",
            "history": "Tarih",
            "space": "Uzay",
            "quotes": "Alıntılar",
            "love": "Aşk"
        }
        cat_turkish = turkish_categories.get(category, category.title())
        title = f"Yeni {cat_turkish} Makalesi"

    if not description:
        turkish_categories = {
            "health": "sağlık",
            "psychology": "psikoloji",
            "history": "tarih",
            "space": "uzay",
            "quotes": "alıntılar",
            "love": "aşk"
        }
        cat_turkish = turkish_categories.get(category, category)
        description = f"MindVerse Daily'den {cat_turkish} kategorisinde güncel araştırmalar ve uzman görüşleri"

    # Clean title and description
    title = clean_frontmatter_value(title)
    description = clean_frontmatter_value(description)

    # Get full content
    content = "\n\n".join(clean_lines).strip()
    if len(content) < 200:
        content = f"# {title}\n\n{description}\n\nDetaylı makale içeriği burada yer alacak."

    # Get image
    image = "/assets/blog-placeholder-1.svg"
    if image_fetcher:
        try:
            image = image_fetcher.get_relevant_image(category, title)
        except:
            pass

    return title, description, image, content

def parse_article_fields(article_text: str, category: str, image_fetcher=None) -> Tuple[str, str, str, str]:
    """Parse title, description, image and content from generated article"""
    # Clean the article text first
    lines = article_text.strip().splitlines()

    # Remove empty lines and common artifacts
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line_lower = line.lower()
        if any(x in line_lower for x in [
            "translate the following", "türkçeye çevir", "çevrilmiş hali:",
            "here is the", "burada", "write a comprehensive", "bu ingilizce makaleyi",
            "recent years have", "the power of", "another trend", "a study published",
            "individuals who", "compared to those", "in addition to"        ]):
            continue
        clean_lines.append(line)

    if not clean_lines:
        if category == "en" or "english" in str(category).lower():
            return f"New {category.title()} Article", f"Latest insights and research from MindVerse Daily in {category} category", "/assets/blog-placeholder-1.svg", "Article content could not be loaded."
        else:
            return f"Yeni {category.title()} Makalesi", f"MindVerse Daily'den {category} kategorisinde güncel makale", "/assets/blog-placeholder-1.svg", "Makale içeriği yüklenemedi."

    # Strategy: Use first substantial line as title, second as description if available
    title = None
    description = None
    content_start_idx = 0

    # Look for title in first few lines
    for i, line in enumerate(clean_lines[:3]):
        # Skip pattern labels
        if any(pattern in line.lower() for pattern in [
            "**başlık:**", "başlık:", "**title:**", "title:",
            "**özet:**", "özet:", "**summary:**", "summary:"
        ]):
            # Try to extract content after the pattern
            if ":" in line:
                extracted = line.split(":", 1)[1].strip().strip('"\'*').strip()
                if extracted and len(extracted) > 5:
                    if not title and len(extracted) < 150:
                        title = extracted
                    elif not description and len(extracted) > 20:
                        description = extracted
            continue

        # If this looks like a title (reasonable length, not too long)
        if not title and 10 <= len(line) <= 150 and not line.startswith(("*", "-", "1.", "2.", "•")):
            # Clean potential title
            potential_title = line.strip('"\'*#').strip()
            if len(potential_title) >= 10:
                title = potential_title
                content_start_idx = i + 1
                continue

        # If we have title but no description, this might be description
        if title and not description and 20 <= len(line) <= 300:
            description = line.strip('"\'*').strip()
            content_start_idx = i + 1
            continue

        # If we have both, start content from here
        if title and description:
            content_start_idx = i
            break

    # If we still don't have title, use first meaningful line
    if not title and clean_lines:
        title = clean_lines[0].strip('"\'*#').strip()
        content_start_idx = 1

    # If we still don't have description, try to extract from content
    if not description and len(clean_lines) > content_start_idx:
        for line in clean_lines[content_start_idx:content_start_idx+3]:
            if 20 <= len(line) <= 300 and not line.startswith("#"):
                description = line[:150] + "..." if len(line) > 150 else line
                break    # Fallbacks - improve for English content
    if not title:
        title = f"Latest {category.title()} Insights"
    if not description:
        description = f"Discover cutting-edge research and insights from MindVerse Daily in the {category} category"

    # Clean title and description
    title = clean_frontmatter_value(title)
    description = clean_frontmatter_value(description)

    # Extract content (everything after title and description)
    content_lines = clean_lines[content_start_idx:]

    # Remove any remaining pattern lines from content
    filtered_content = []
    for line in content_lines:
        if not any(pattern in line.lower() for pattern in [
            "**başlık:**", "başlık:", "**title:**", "title:",
            "**özet:**", "özet:", "**summary:**", "summary:"
        ]):
            filtered_content.append(line)

    # Join content
    if filtered_content:
        content = "\n\n".join(filtered_content).strip()
    else:
        content = f"# {title}\n\n{description}\n\nDetaylı makale içeriği burada yer alacak."

    # Ensure content has reasonable length
    if len(content) < 100:
        content = f"# {title}\n\n{description}\n\n" + "\n\n".join(clean_lines)

    # Get image
    image = "/assets/blog-placeholder-1.svg"  # Default
    if image_fetcher:
        try:
            image = image_fetcher.get_relevant_image(category, title)
        except:
            pass

    return title, description, image, content

def clean_turkish_translation(text: str) -> str:
    """ULTRA AGGRESSİVE İngilizce temizleyici - Hiç İngilizce kelime bırakmaz!"""

    # ULTRA AGGRESSIVE İngilizce temizleme
    replacements = {
        # En yaygın İngilizce kelimeler - tamamen temizle
        r'\bhealth\b': 'sağlık',
        r'\bscience\b': 'bilim',
        r'\bresearch\b': 'araştırma',
        r'\bstudies\b': 'çalışmalar',
        r'\blifestyle\b': 'yaşam tarzı',
        r'\bwell-being\b': 'refah',
        r'\bprocessed\b': 'işlenmiş',
        r'\bwhole grain\b': 'tam tahıl',
        r'\bparticipants\b': 'katılımcılar',
        r'\bdigestive\b': 'sindirim',
        r'\bomega-3\s+fatty\s+acids\b': 'omega-3 yağ asitleri',
        r'\bGI\s+health\b': 'sindirim sağlığı',
        r'\bdigestive\s+health\s+science\b': 'sindirim sağlığı bilimi',

        # İngilizce bağlaçlar ve artikeller
        r'\blike\b': 'gibi',
        r'\band\b': 've',
        r'\bthe\b': '',
        r'\bof\b': '',
        r'\bto\b': '',
        r'\bin\b': '',
        r'\bfor\b': 'için',
        r'\bwith\b': 'ile',
        r'\bby\b': 'tarafından',
        r'\bfrom\b': 'den',

        # İngilizce zamir ve sıfatlar
        r'\btheir\b': 'onların',
        r'\bwho\b': 'olan',
        r'\bwhen\b': 'zaman',
        r'\bwhich\b': 'hangi',
        r'\bthat\b': 'o',
        r'\bthis\b': 'bu',
        r'\bthese\b': 'bunlar',
        r'\bthose\b': 'şunlar',

        # İngilizce cümle kalıpları - tamamen Türkçeleştir
        r'\bresearch\s+shows\b': 'araştırmalar gösteriyor',
        r'\bstudies\s+have\s+found\b': 'çalışmalar bulmuştur',
        r'\bparticipants\s+who\s+consumed\b': 'katılımcıların',
        r'\bcompared\s+to\b': 'ile karşılaştırıldığında',
        r'\brecent\s+years\b': 'son yıllarda',
        r'\bindividuals\s+who\b': 'kişiler',
        r'\banother\s+trend\b': 'başka bir eğilim',
        r'\ba\s+study\s+published\b': 'yayınlanan bir çalışma',
        r'\bJournal\s+of\b': 'Dergisi',
        r'\bshowed\s+significant\s+improvements\b': 'önemli iyileşmeler gösterdi',
        r'\bimprovements\s+their\b': 'iyileştirmeler',

        # Teknik terimler - Türkçeleştir
        r'\bholistik\s+refah\b': 'bütüncül sağlık',
        r'\bwellness\b': 'esenlik',
        r'\bholistic\b': 'bütüncül',
        r'\bomega-3\s+esterleri\b': 'omega-3 yağ asitleri',
        r'\besterleri\b': 'yağ asitleri',

        # Journal isimleri - Türkçeleştir
        r'Journal\s+of\s+Clinical\s+Endocrinology\s+and\s+Metabolism': 'Klinik Endokrinoloji ve Metabolizma Dergisi',
        r'Journal\s+of\s+Nutrition': 'Beslenme Dergisi',
        r'Journal\s+of\s+Women\'s\s+Health': 'Kadın Sağlığı Dergisi',
        r'National\s+Sleep\s+Foundation': 'Ulusal Uyku Vakfı',

        # Cümle başları - Türkçeleştir
        r'^In\s+recent\s+years,': 'Son yıllarda,',
        r'^Research\s+shows': 'Araştırmalar gösteriyor',
        r'^Studies\s+have\s+found': 'Çalışmalar bulmuştur',
        r'^Furthermore,': 'Ayrıca,',
        r'^However,': 'Ancak,',
        r'^Moreover,': 'Dahası,',
        r'^Additionally,': 'Ek olarak,',
        r'^In\s+addition,': 'Bunun yanında,',

        # Karma İngilizce-Türkçe ifadeler temizle
        r'\ba\s+diet\s+rich\s+fiber\b': 'lif açısından zengin bir diyet',
        r'\brich\s+in\b': 'açısından zengin',
        r'\bhigh\s+in\b': 'yüksek miktarda',
        r'\blow\s+in\b': 'düşük miktarda',

        # Son temizlik - kalan İngilizce kelimeler için
        r'\benergy\b': 'enerji',
        r'\bprotein\b': 'protein',
        r'\bvitamin\b': 'vitamin',
        r'\bmineral\b': 'mineral',
        r'\bfiber\b': 'lif',
        r'\bcarbohydrate\b': 'karbonhidrat',
        r'\bfat\b': 'yağ',
        r'\bsugar\b': 'şeker',
        r'\bsalt\b': 'tuz',
        r'\bwater\b': 'su',
        r'\bexercise\b': 'egzersiz',
        r'\bfitness\b': 'fitness',
        r'\btraining\b': 'antrenman',
        r'\bworkout\b': 'egzersiz',
        r'\bstress\b': 'stres',
        r'\bsleep\b': 'uyku',
        r'\bdiet\b': 'diyet',
        r'\bnutrition\b': 'beslenme',
        r'\bfood\b': 'gıda',
        r'\bmeal\b': 'öğün',
        r'\bbreakfast\b': 'kahvaltı',
        r'\blunch\b': 'öğle yemeği',
        r'\bdinner\b': 'akşam yemeği',
        r'\bsnack\b': 'atıştırmalık',

        # Noktalama ve boşluk düzeltmeleri
        r'\s+': ' ',  # Çoklu boşlukları tek boşluğa çevir
        r'\s+,': ',',  # Virgül öncesi boşluk kaldır
        r'\s+\.': '.',  # Nokta öncesi boşluk kaldır
        r'\s+;': ';',  # Noktalı virgül öncesi boşluk kaldır
        r'\s+:': ':',  # İki nokta öncesi boşluk kaldır
    }

    # Tüm değişiklikleri uygula
    import re
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Ek temizlik - başta/sonda boşluk kaldır
    text = text.strip()

    # Çift boşlukları tek boşluğa çevir (son kontrol)
    text = re.sub(r'\s+', ' ', text)

    return text

def load_existing_titles() -> Dict[str, Set[str]]:
    """Load existing article titles to avoid duplicates"""
    existing_titles = {"en": set(), "tr": set()}

    content_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")

    for category in CATEGORIES:
        category_dir = os.path.join(content_dir, category)
        if os.path.exists(category_dir):
            for filename in os.listdir(category_dir):
                if filename.endswith(".md"):
                    # Extract language from filename
                    if filename.endswith(".en.md"):
                        lang = "en"
                    elif filename.endswith(".tr.md"):
                        lang = "tr"
                    else:
                        continue

                    # Read title from file
                    try:
                        with open(os.path.join(category_dir, filename), 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract title from frontmatter
                            if 'title:' in content:
                                title_line = [line for line in content.split('\n') if line.strip().startswith('title:')]
                                if title_line:
                                    title = title_line[0].split('title:', 1)[1].strip().strip('"\'')
                                    existing_titles[lang].add(title.lower())
                    except:
                        continue

    return existing_titles

def generate_unique_title(category: str, subtopic: str, lang: str, existing_titles: Set[str], attempt: int = 1) -> str:
    """Generate a unique title that doesn't exist yet with strong variation"""

    # Title style variations for English
    title_styles = [
        "The Science Behind {topic}",
        "Understanding {topic}: A Comprehensive Guide",
        "Exploring {topic}: Latest Research and Insights",
        "The Power of {topic} in Modern Life",
        "Mastering {topic}: Expert Strategies and Tips",
        "The Hidden Truth About {topic}",
        "Revolutionary Insights into {topic}",
        "The Complete Guide to {topic}",
        "Breakthrough Research on {topic}",
        "The Future of {topic}: Trends and Predictions",
        "Unlocking the Secrets of {topic}",
        "Advanced {topic}: What You Need to Know",
        "The Essential Guide to {topic}",
        "{topic}: Latest Discoveries and Applications",
        "Transforming Lives Through {topic}",
        "The Art and Science of {topic}",
        "Modern Approaches to {topic}",
        "Evidence-Based {topic}: What Research Shows",
        "The Psychology Behind {topic}",
        "Innovative Strategies for {topic}"
    ]

    # Select different style based on attempt
    style = title_styles[(attempt - 1) % len(title_styles)]
    formatted_topic = subtopic.title()

    # Create sophisticated prompts
    if lang == "en":
        prompt = (
            f"Create a unique, engaging article title using this format: '{style.format(topic='{TOPIC}')}'\n"
            f"Topic: {subtopic}\n"
            f"Category: {category}\n"
            f"Requirements:\n"
            f"- Replace {{TOPIC}} with appropriate terms related to '{subtopic}'\n"
            f"- Make it SEO-friendly and compelling\n"
            f"- Ensure it's different from common titles\n"
            f"- Keep it under 80 characters\n"
            f"- Make it specific and informative\n"
            f"- Only return the final title, nothing else\n"
            f"Attempt #{attempt}"
        )
    else:  # Turkish
        tr_styles = [
            "{topic} Biliminin Sırları",
            "{topic} Rehberi: Kapsamlı Analiz",
            "{topic} Keşfi: Son Araştırmalar",
            "Modern Yaşamda {topic} Gücü",
            "{topic} Ustalığı: Uzman Stratejileri",
            "{topic} Hakkında Gizli Gerçekler",
            "{topic} Devrimsel Yaklaşımları",
            "{topic} Tam Rehberi",
            "{topic} Üzerine Çığır Açan Araştırmalar",
            "{topic} Geleceği: Eğilimler ve Öngörüler"
        ]
        tr_style = tr_styles[(attempt - 1) % len(tr_styles)]
        prompt = (
            f"Bu formatı kullanarak benzersiz bir makale başlığı oluştur: '{tr_style.format(topic='{KONU}')}'\n"
            f"Konu: {subtopic}\n"
            f"Kategori: {category}\n"
            f"Gereksinimler:\n"
            f"- {{KONU}} yerine '{subtopic}' ile ilgili uygun terimleri kullan\n"
            f"- SEO dostu ve çekici olsun\n"
            f"- Yaygın başlıklardan farklı olsun\n"
            f"- 80 karakterden kısa olsun\n"
            f"- Spesifik ve bilgilendirici olsun\n"
            f"- Sadece son başlığı döndür\n"
            f"Deneme #{attempt}"
        )

    title = call_ollama(prompt).strip().strip('"\'')
    title = clean_frontmatter_value(title)

    # Additional uniqueness check - if still duplicate, add variation
    if title.lower() in existing_titles:
        variations = [
            f"{title}: New Perspectives",
            f"{title} - Updated Research",
            f"{title}: Modern Insights",
            f"{title} and Beyond",
            f"Rethinking {title}"
        ]
        title = variations[attempt % len(variations)]

    return title

def write_article(filepath: str, title: str, description: str, date: str, category: str, image: str, content: str):
    """Write article to file with frontmatter"""
    tags = []  # Can be enhanced later

    frontmatter = f"""---
title: "{title}"
description: "{description}"
pubDate: {date}
category: "{category}"
tags: {tags}
image: "{image}"
---

{content}"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"✅ Created: {os.path.basename(filepath)}")

def generate_english_content_only():
    """Generate ONLY English content - optimized for international audience"""
    print(f"🇺🇸 Starting ENGLISH-ONLY content generation for international audience...")
    print(f"📊 Target: {ARTICLES_PER_CATEGORY} unique articles per category ({len(CATEGORIES)} categories)")
    print(f"📝 Total English articles to generate: {ARTICLES_PER_CATEGORY * len(CATEGORIES)}")

    # Load existing titles to ensure uniqueness
    existing_titles = load_existing_titles()
    print(f"📚 Loaded {len(existing_titles['en'])} existing EN titles to avoid duplicates")

    # Initialize image fetcher
    image_fetcher = ImageFetcher()

    # Create content directory
    content_base_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")

    total_created = 0
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    # Track used subtopics to ensure maximum variety
    used_subtopics = set()

    for category in CATEGORIES:
        print(f"\n📂 Processing category: {category.upper()}")
        category_dir = os.path.join(content_base_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        # Get ALL available subtopics for this category
        available_subtopics = SUBTOPICS[category].copy()
        random.shuffle(available_subtopics)

        created_count = 0
        category_titles = set()  # Track titles within this category

        for i in range(ARTICLES_PER_CATEGORY):
            max_attempts = 5
            article_created = False

            for attempt in range(max_attempts):
                try:
                    # Select a unique subtopic
                    subtopic = available_subtopics[i % len(available_subtopics)]

                    # Add variation if we've used this subtopic before
                    if subtopic in used_subtopics:
                        subtopic_variations = [
                            f"{subtopic} research",
                            f"{subtopic} innovations",
                            f"{subtopic} breakthroughs",
                            f"{subtopic} science",
                            f"{subtopic} studies"
                        ]
                        subtopic = subtopic_variations[attempt % len(subtopic_variations)]

                    used_subtopics.add(subtopic)

                    print(f"  📝 Creating English article {i+1}/{ARTICLES_PER_CATEGORY}: {subtopic}")

                    # Super enhanced English prompt for maximum uniqueness
                    en_prompt = (
                        f"Write an exceptional, unique article about '{subtopic}' for the '{category}' category.\n\n"
                        f"ARTICLE SPECIFICATIONS:\n"
                        f"- 900-1200 words of original, high-value content\n"
                        f"- Include cutting-edge research from 2023-2025\n"
                        f"- Expert-level insights and analysis\n"
                        f"- International perspective for global audience\n"
                        f"- Use compelling section headings (## format)\n"
                        f"- Include actionable takeaways and practical advice\n"
                        f"- Reference recent studies and expert opinions\n"
                        f"- Professional yet engaging writing style\n\n"
                        f"UNIQUENESS MANDATE:\n"
                        f"- Take a fresh, innovative angle on '{subtopic}'\n"
                        f"- Avoid common clichés and overused phrases\n"
                        f"- Present unique insights and perspectives\n"
                        f"- Focus on latest developments and emerging trends\n"
                        f"- Make it valuable for educated international readers\n\n"
                        f"CONTENT STRUCTURE:\n"
                        f"- Compelling opening that hooks the reader\n"
                        f"- 3-5 well-structured sections with clear headings\n"
                        f"- Include relevant examples and case studies\n"
                        f"- Strong conclusion with key takeaways\n"
                        f"- Write ONLY in perfect English\n\n"
                        f"Focus Topic: {subtopic}\n"
                        f"Category Context: {category}\n"
                        f"Attempt: {attempt + 1}/{max_attempts}"
                    )

                    english_article = call_ollama(en_prompt)
                    time.sleep(3)  # Longer rate limiting for better quality

                    # Parse English article
                    en_title, en_description, en_image, en_content = parse_article_fields(
                        english_article, category, image_fetcher
                    )

                    # Strict uniqueness check
                    title_lower = en_title.lower()
                    if title_lower in existing_titles["en"] or title_lower in category_titles:
                        print(f"    ⚠️ Duplicate title detected: '{en_title}' - generating new one (attempt {attempt + 1})")
                        en_title = generate_unique_title(category, subtopic, "en", existing_titles["en"], attempt + 1)
                        title_lower = en_title.lower()

                    # Final uniqueness verification
                    if title_lower not in existing_titles["en"] and title_lower not in category_titles:
                        existing_titles["en"].add(title_lower)
                        category_titles.add(title_lower)

                        # Create file names
                        en_slug = slugify(en_title)
                        en_filepath = os.path.join(category_dir, f"{date}-{en_slug}.en.md")

                        # Write English article
                        write_article(en_filepath, en_title, en_description, date, category, en_image, en_content)

                        created_count += 1
                        total_created += 1
                        article_created = True

                        print(f"    ✅ Created: {en_title[:60]}...")
                        break
                    else:
                        print(f"    ⚠️ Still duplicate after generation, trying again...")

                except Exception as e:
                    print(f"    ❌ Attempt {attempt + 1} failed for {subtopic}: {e}")
                    continue

            if not article_created:
                print(f"    ❌ Failed to create unique article for {subtopic} after {max_attempts} attempts")

        print(f"  📊 Category {category}: {created_count} unique English articles created")

    print(f"\n🎉 ENGLISH-ONLY content generation completed!")
    print(f"📊 Total unique English articles created: {total_created}")
    print(f"📂 Articles saved for international audience in: {content_base_dir}")
    print(f"🌍 Ready for English site visitors!")
    return total_created

def translate_to_turkish():
    """Translate all English articles to Turkish"""
    print(f"\n🔄 Starting Turkish translation process...")

    # Load existing titles
    existing_titles = load_existing_titles()

    # Initialize image fetcher
    image_fetcher = ImageFetcher()    # Create content directory
    content_base_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")

    total_translated = 0
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    for category in CATEGORIES:
        print(f"\n📂 Translating {category.upper()} articles...")
        category_dir = os.path.join(content_base_dir, category)

        if not os.path.exists(category_dir):
            continue

        # Find all English articles in this category from recent days (last 3 days)
        import datetime as dt
        today = dt.datetime.utcnow()
        recent_dates = [(today - dt.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(3)]

        english_files = []
        for f in os.listdir(category_dir):
            if f.endswith('.en.md'):
                # Check if file starts with any recent date
                for recent_date in recent_dates:
                    if f.startswith(recent_date):
                        # Check if Turkish version doesn't exist
                        tr_equivalent = f.replace('.en.md', '.tr.md')
                        if not os.path.exists(os.path.join(category_dir, tr_equivalent)):
                            english_files.append(f)
                        break

        if not english_files:
            print(f"    ℹ️ No untranslated English articles found for {category}")
            continue

        for en_file in english_files:
            try:
                en_filepath = os.path.join(category_dir, en_file)

                # Read English article
                with open(en_filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract content after frontmatter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    english_content = parts[2].strip()
                else:
                    continue

                print(f"  🔄 Translating: {en_file}")                # Create MUCH better Turkish translation prompt
                tr_prompt = (
                    f"GÖREV: Bu İngilizce makaleyi TAMAMEN ve SADECE Türkçeye çevir.\n\n"
                    f"KATIK KURALLAR:\n"
                    f"1. Hiçbir İngilizce kelime kullanma - hiçbiri!\n"
                    f"2. Şu kelimeleri asla kullanma: 'like', 'and', 'the', 'of', 'to', 'in', 'for', 'with', 'by', 'from', 'well-being', 'processed'\n"
                    f"3. Teknik terimleri Türkçeleştir:\n"
                    f"   - 'well-being' → 'refah' veya 'sağlıklı yaşam'\n"
                    f"   - 'processed foods' → 'işlenmiş gıdalar'\n"
                    f"   - 'whole grain' → 'tam tahıl'\n"
                    f"   - 'lifestyle' → 'yaşam tarzı'\n"
                    f"   - 'research shows' → 'araştırmalar gösteriyor'\n"
                    f"   - 'studies have found' → 'çalışmalar buldu'\n"
                    f"4. Dergi isimlerini Türkçe açıkla: 'Journal of...' → '... Dergisi'\n"
                    f"5. Alıntıları da Türkçeye çevir\n"
                    f"6. Tamamen doğal Türkçe cümleler kur\n"
                    f"7. İngilizce yapı kalıplarını kullanma, Türkçe cümle yapısı kullan\n\n"                    f"UYARI: Tek bir İngilizce kelime görürsem çeviri başarısız sayılacak!\n\n"
                    f"Çevrilecek makale:\n{english_content}"
                )

                turkish_article = call_ollama(tr_prompt)
                time.sleep(2)  # Rate limiting

                # Clean up the Turkish translation
                turkish_article = clean_turkish_translation(turkish_article)

                # Parse Turkish article
                tr_title, tr_description, tr_image, tr_content = parse_article_fields(
                    turkish_article, category, image_fetcher
                )

                # Clean Turkish translation
                tr_content = clean_turkish_translation(tr_content)

                # Ensure Turkish title is unique
                attempt = 1
                while tr_title.lower() in existing_titles["tr"] and attempt <= 3:
                    print(f"    ⚠️ Duplicate TR title detected, generating new one (attempt {attempt})")
                    tr_title = generate_unique_title(category, tr_title, "tr", existing_titles["tr"], attempt)
                    attempt += 1

                existing_titles["tr"].add(tr_title.lower())

                # Create Turkish file
                tr_slug = slugify(tr_title)
                tr_filepath = os.path.join(category_dir, f"{date}-{tr_slug}.tr.md")

                # Write Turkish article
                write_article(tr_filepath, tr_title, tr_description, date, category, tr_image, tr_content)

                total_translated += 1
                print(f"    ✅ Translated: {tr_title[:60]}...")

            except Exception as e:
                print(f"    ❌ Error translating {en_file}: {e}")
                continue

    print(f"\n🎉 Turkish translation completed!")
    print(f"📊 Total articles translated: {total_translated}")
    return total_translated

def comprehensive_content_generation():
    """Generate comprehensive content: First English, then Turkish translations"""
    print(f"🚀 Starting comprehensive content generation...")

    # Step 1: Generate English content
    english_count = generate_english_content_only()

    # Step 2: Translate to Turkish
    turkish_count = translate_to_turkish()

    total_articles = english_count + turkish_count
    print(f"\n🎉 Complete content generation finished!")
    print(f"📊 Total articles created: {total_articles}")
    print(f"📝 English articles: {english_count}")
    print(f"📝 Turkish articles: {turkish_count}")

    return total_articles

def generate_turkish_content_only():
    """Generate ONLY Turkish content directly using Ollama"""
    print(f"🇹🇷 Direkt Türkçe içerik oluşturuluyor...")
    print(f"📊 Hedef: {ARTICLES_PER_CATEGORY} benzersiz makale/kategori ({len(CATEGORIES)} kategori)")
    print(f"📝 Toplam Türkçe makale: {ARTICLES_PER_CATEGORY * len(CATEGORIES)}")

    # Load existing titles to ensure uniqueness
    existing_titles = load_existing_titles()
    print(f"📚 Yüklendi: {len(existing_titles['tr'])} mevcut TR başlık")

    # Initialize image fetcher
    image_fetcher = ImageFetcher()

    # Create content directory
    content_base_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")

    total_created = 0
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    # Track used subtopics to ensure maximum variety
    used_subtopics = set()

    for category in CATEGORIES:
        print(f"\n📂 Kategori işleniyor: {category.upper()}")
        category_dir = os.path.join(content_base_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        # Get ALL available subtopics for this category
        available_subtopics = SUBTOPICS[category].copy()
        random.shuffle(available_subtopics)

        created_count = 0
        category_titles = set()  # Track titles within this category

        for i in range(ARTICLES_PER_CATEGORY):
            max_attempts = 5
            article_created = False

            for attempt in range(max_attempts):
                try:
                    # Select a unique subtopic
                    subtopic = available_subtopics[i % len(available_subtopics)]

                    # Add variation if we've used this subtopic before
                    if subtopic in used_subtopics:
                        subtopic_variations = [
                            f"{subtopic} araştırmaları",
                            f"{subtopic} yenilikleri",
                            f"{subtopic} buluşları",
                            f"{subtopic} bilimi",
                            f"{subtopic} çalışmaları"
                        ]
                        subtopic = subtopic_variations[attempt % len(subtopic_variations)]

                    used_subtopics.add(subtopic)

                    print(f"  📝 Türkçe makale oluşturuluyor {i+1}/{ARTICLES_PER_CATEGORY}: {subtopic}")                    # Türkçe içerik için ULTRA GÜÇLÜ prompt - Kaliteli uzun makale
                    tr_prompt = f"""SEN BİR TÜRK GAZETECİ VE UZMAN YAZARSIN!

GÖREV: '{subtopic}' konusunda '{category}' kategorisinde 1200-1500 kelimelik profesyonel Türkçe makale yaz.

🚫 KESİN YASAK OLAN İNGİLİZCE KELİMELER:
- health, science, research, studies, lifestyle, well-being, processed
- participants, omega-3, fatty acids, digestive, GI health
- like, and, the, of, to, in, for, with, by, from
- TAMAMEN TÜRKÇE YAZ! TEK İNGİLİZCE KELİME YOKTUR!

✅ SADECE TÜRKÇE KULLAN:
- "sağlık" (health), "bilim" (science), "araştırma" (research)
- "çalışmalar" (studies), "yaşam tarzı" (lifestyle)
- "katılımcılar" (participants), "sindirim sistemi" (digestive system)
- "omega-3 yağ asitleri" (omega-3 fatty acids)

📝 MAKALE YAPISI (ZORUNLU FORMAT):

## Giriş (150-200 kelime)
- Konuya çekici başlangıç
- Problemin önemini vurgula
- Makalenin içeriğini özetle

## [Ana Başlık 1] (250-300 kelime)
- Konunun temel bilgileri
- Güncel Türkiye araştırmaları
- Türk uzmanların görüşleri

## [Ana Başlık 2] (250-300 kelime)
- Derinlemesine analiz
- Uygulama örnekleri
- Pratik bilgiler

## [Ana Başlık 3] (250-300 kelime)
- Son gelişmeler
- Gelecek eğilimleri
- Uzman tavsiyeleri

## Uygulanabilir Tavsiyeler (200-250 kelime)
- 5-7 somut önerı
- Günlük yaşama adapte edilebilir
- Türk kültürüne uygun

## Sonuç (150-200 kelime)
- Ana noktaları özetle
- Okuyucuya motivasyon ver
- Eylem çağrısı

🎯 KALİTE KRİTERLERİ:
- Her paragraf en az 3-4 cümle
- Akıcı ve doğal Türkçe
- Bilimsel ama anlaşılır dil
- Somut örnekler ver
- Türkiye'den referanslar kullan

⚠️ SON KONTROL:
- Hiç İngilizce kelime var mı? ❌
- 1200+ kelime var mı? ✅
- Başlıklar net mi? ✅
- Akıcı Türkçe mi? ✅

Konu: {subtopic}
Kategori: {category}

BAŞLA! (Sadece makale içeriğini yaz, başka açıklama yapma)"""

                    turkish_article = call_ollama(tr_prompt)
                    time.sleep(3)  # Rate limiting for better quality

                    # Parse Turkish article with specialized function
                    tr_title, tr_description, tr_image, tr_content = parse_turkish_article_fields(
                        turkish_article, category, image_fetcher
                    )

                    # Clean Turkish content
                    tr_content = clean_turkish_translation(tr_content)

                    # Strict uniqueness check
                    title_lower = tr_title.lower()
                    if title_lower in existing_titles["tr"] or title_lower in category_titles:
                        print(f"    ⚠️ Duplicate title detected: '{tr_title}' - generating new one (attempt {attempt + 1})")
                        tr_title = generate_unique_title(category, subtopic, "tr", existing_titles["tr"], attempt + 1)
                        title_lower = tr_title.lower()

                    # Final uniqueness verification
                    if title_lower not in existing_titles["tr"] and title_lower not in category_titles:
                        existing_titles["tr"].add(title_lower)
                        category_titles.add(title_lower)

                        # Create file names
                        tr_slug = slugify(tr_title)
                        tr_filepath = os.path.join(category_dir, f"{date}-{tr_slug}.tr.md")

                        # Write Turkish article
                        write_article(tr_filepath, tr_title, tr_description, date, category, tr_image, tr_content)

                        created_count += 1
                        total_created += 1
                        article_created = True

                        print(f"    ✅ Oluşturuldu: {tr_title[:60]}...")
                        break
                    else:
                        print(f"    ⚠️ Hala aynı başlık, tekrar deneniyor...")

                except Exception as e:
                    print(f"    ❌ Deneme {attempt + 1} başarısız {subtopic}: {e}")
                    continue

            if not article_created:
                print(f"    ❌ {subtopic} için {max_attempts} denemeden sonra makale oluşturulamadı")

        print(f"  📊 Kategori {category}: {created_count} benzersiz Türkçe makale oluşturuldu")

    print(f"\n🎉 TÜRKÇE içerik oluşturma tamamlandı!")
    print(f"📊 Toplam benzersiz Türkçe makale: {total_created}")
    print(f"📂 Makaleler kaydedildi: {content_base_dir}")
    print(f"🇹🇷 Türk ziyaretçiler için hazır!")
    return total_created

def auto_deploy():
    """Deploy the site automatically"""
    try:
        print("\n🚀 Starting auto-deployment...")

        # Build the site
        print("📦 Building site...")
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=os.path.join(os.path.dirname(__file__), ".."),
            capture_output=True,
            text=True
        )

        if build_result.returncode != 0:
            print(f"❌ Build failed: {build_result.stderr}")
            return False

        print("✅ Build successful")

        # Deploy to Vercel
        print("🌐 Deploying to Vercel...")
        deploy_result = subprocess.run(
            ["vercel", "--prod"],
            cwd=os.path.join(os.path.dirname(__file__), ".."),
            capture_output=True,
            text=True
        )

        if deploy_result.returncode != 0:
            print(f"❌ Deploy failed: {deploy_result.stderr}")
            return False

        print("✅ Deployment successful")
        print(f"🌐 Site URL: https://mindversedaily.vercel.app")
        return True

    except Exception as e:
        print(f"❌ Auto-deployment error: {e}")
        return False

if __name__ == "__main__":
    print("🌌 MindVerse Bulk Content Generator")
    print("=" * 50)

    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        print("✅ Ollama is running")
    except:
        print("❌ Ollama is not running. Please start Ollama first!")
        exit(1)    # User choice menu
    print("\nSeçenekler:")
    print("1. 🇺🇸 SADECE İngilizce içerik oluştur (20 makale/kategori)")
    print("2. 🔄 Mevcut İngilizce içerikleri Türkçeye çevir")
    print("3. 🌐 Kapsamlı oluşturma (İngilizce + Türkçe çeviri)")
    print("4. 🇹🇷 SADECE Türkçe içerik oluştur (Direkt Ollama ile)")

    choice = input("\nSeçiminizi yapın (1-4): ").strip()

    if choice == "1":
        print("\n🇺🇸 SADECE İngilizce içerik oluşturuluyor - Uluslararası ziyaretçiler için optimize edildi...")
        generate_english_content_only()
    elif choice == "2":
        print("\n🇹🇷 İngilizce içerikler Türkçeye çevriliyor...")
        translate_to_turkish()
    elif choice == "3":
        print("\n🌐 Kapsamlı içerik oluşturma başlıyor...")
        comprehensive_content_generation()
    elif choice == "4":
        print("\n🇹🇷 SADECE Türkçe içerik oluşturuluyor...")
        generate_turkish_content_only()
    else:
        print("❌ Geçersiz seçim!")
        exit(1)

    # Ask for auto-deployment
    deploy_choice = input("\n🚀 Production'a otomatik deploy edilsin mi? (y/n): ").lower().strip()
    if deploy_choice in ['y', 'yes', 'evet', 'e']:
        auto_deploy()
    else:
        print("📝 İçerik oluşturuldu ama deploy edilmedi. Manuel deploy için: 'npm run build && vercel --prod'")

    print("\n🎉 Tamamlandı! İyi blog yazıları! 🌌")
