#!/usr/bin/env python3
"""
MindVerse Unified Content Generator
Supports both automatic (Groq English only) and manual (Groq English / Ollama Turkish) content generation
"""

import os
import sys
import json
import argparse
import datetime
import random
import time
import re
import requests
import subprocess
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

try:
    from image_fetcher import ImageFetcher
    from groq_client import generate_content
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure image_fetcher.py and groq_client.py are in the same directory")
    sys.exit(1)

class UnifiedContentGenerator:
    def __init__(self, mode: str = "auto", language: str = "en", categories: List[str] = None, count: int = 1):
        self.mode = mode  # "auto" or "manual"
        self.language = language  # "en" or "tr"
        self.categories = categories or ["health", "psychology", "history", "space", "quotes", "love"]
        self.count = count
        self.content_dir = Path("src/content/blog")
        self.image_fetcher = ImageFetcher()

        # API configurations
        self.ollama_url = "http://localhost:11434/api/generate"
        self.ollama_model = "llama3:latest"

        # Language-specific configurations
        self.config = self._get_language_config()

        # Existing titles tracking
        self.existing_titles = self._load_existing_titles()

        print(f"🚀 MindVerse Content Generator initialized:")
        print(f"   Mode: {mode}")
        print(f"   Language: {language}")
        print(f"   Categories: {categories}")
        print(f"   Count: {count}")

    def _get_language_config(self) -> Dict:
        """Get language-specific configuration"""
        if self.language == "en":
            return {
                "file_suffix": ".en.md",
                "api_type": "groq",
                "subtopics": {
                    "health": [
                        "mental wellness breakthroughs", "nutrition science discoveries", "exercise physiology",
                        "sleep optimization", "stress management techniques", "immune system boosting",
                        "healthy aging secrets", "preventive medicine", "brain health research",
                        "cardiovascular wellness", "digestive health science", "hormonal balance",
                        "mindful eating practices", "fitness innovation", "alternative medicine studies",
                        "medical breakthroughs", "longevity research findings", "disease prevention strategies"
                    ],
                    "psychology": [
                        "cognitive bias research", "emotional intelligence development", "child psychology",
                        "therapeutic approaches", "motivation science", "personality psychology",
                        "social dynamics", "memory enhancement", "behavioral psychology studies",
                        "social psychology research", "cognitive psychology", "positive psychology",
                        "neuroscience findings", "decision-making psychology", "habit formation science",
                        "mental resilience", "psychological disorders research", "therapy innovations"
                    ],
                    "history": [
                        "ancient civilizations mysteries", "world war revelations", "historical inventions impact",
                        "legendary leaders", "cultural revolution studies", "lost civilizations",
                        "heritage preservation", "archaeological breakthroughs", "medieval period insights",
                        "renaissance discoveries", "industrial revolution effects", "colonial history analysis"
                    ],
                    "space": [
                        "exoplanet discoveries", "black hole mysteries", "space missions", "Mars exploration",
                        "cosmic phenomena", "telescope innovations", "space technology", "astronaut experiences",
                        "galaxy formation", "dark matter research", "space colonization", "satellite technology"
                    ],
                    "quotes": [
                        "inspirational wisdom", "philosophical insights", "life lessons", "success principles",
                        "motivational thoughts", "leadership quotes", "personal development", "resilience wisdom",
                        "happiness philosophy", "career inspiration", "entrepreneurship quotes", "mindfulness sayings"
                    ],
                    "love": [
                        "relationship psychology", "attraction science", "emotional intimacy", "dating psychology",
                        "love languages", "relationship therapy", "marriage studies", "attachment theory",
                        "romantic psychology", "couples therapy", "relationship dynamics", "love neuroscience"
                    ]
                }
            }
        else:  # Turkish
            return {
                "file_suffix": ".tr.md",
                "api_type": "ollama",
                "subtopics": {
                    "health": [
                        "beslenme bilimi", "egzersiz fizyolojisi", "uyku optimizasyonu", "stres yönetimi",
                        "bağışıklık sistemi", "sağlıklı yaşlanma", "preventif tıp", "beyin sağlığı",
                        "kardiyovasküler sağlık", "sindirim sağlığı", "hormonal denge", "zihinsel beslenme",
                        "fitness yenilikleri", "alternatif tıp", "tıbbi atılımlar", "uzun yaşam araştırmaları"
                    ],
                    "psychology": [
                        "bilişsel önyargı araştırmaları", "duygusal zeka gelişimi", "çocuk psikolojisi",
                        "terapötik yaklaşımlar", "motivasyon bilimi", "kişilik psikolojisi", "sosyal dinamikler",
                        "hafıza geliştirme", "davranış psikolojisi", "sosyal psikoloji", "bilişsel psikoloji",
                        "pozitif psikoloji", "nörobilim bulguları", "karar verme psikolojisi"
                    ],
                    "history": [
                        "antik medeniyetler gizemleri", "dünya savaşları analizi", "tarihi icatların etkisi",
                        "efsanevi liderler", "kültürel devrim çalışmaları", "kayıp medeniyetler",
                        "miras koruma", "arkeolojik keşifler", "ortaçağ dönemi", "rönesans keşifleri"
                    ],
                    "space": [
                        "öte gezegen keşifleri", "kara delik gizemleri", "uzay misyonları", "Mars keşfi",
                        "kozmik fenomenler", "teleskop yenilikleri", "uzay teknolojisi", "astronot deneyimleri",
                        "galaksi oluşumu", "karanlık madde araştırması", "uzay kolonizasyonu", "uydu teknolojisi"
                    ],
                    "quotes": [
                        "ilham verici bilgelik", "felsefi içgörüler", "yaşam dersleri", "başarı ilkeleri",
                        "motivasyonel düşünceler", "liderlik bilgeliği", "kişisel gelişim", "dayanıklılık bilgeliği",
                        "mutluluk felsefesi", "kariyer ilhamı", "girişimcilik sözleri", "farkındalık özdeyişleri"
                    ],
                    "love": [
                        "ilişki psikolojisi", "çekim bilimi", "duygusal yakınlık", "flört psikolojisi",
                        "aşk dilleri", "ilişki terapisi", "evlilik çalışmaları", "bağlanma teorisi",
                        "romantik psikoloji", "çift terapisi", "ilişki dinamikleri", "aşk nörobilimi"
                    ]
                }
            }

    def _load_existing_titles(self) -> Set[str]:
        """Load existing article titles to prevent duplicates"""
        existing_titles = set()

        try:
            for category in self.categories:
                category_path = self.content_dir / category
                if category_path.exists():
                    for file_path in category_path.glob(f"*{self.config['file_suffix']}"):
                        # Extract title from filename
                        filename = file_path.stem
                        # Remove date prefix and language suffix
                        title_part = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
                        title_part = re.sub(r'\.(en|tr)$', '', title_part)
                        existing_titles.add(title_part.lower())
        except Exception as e:
            print(f"Warning: Could not load existing titles: {e}")        print(f"📚 Loaded {len(existing_titles)} existing titles for duplicate prevention")
        return existing_titles

    def _generate_title_and_content(self, category: str, subtopic: str) -> Tuple[str, str]:
        """Generate title and content using appropriate API"""
        if self.config["api_type"] == "groq":
            return self._generate_with_groq(category, subtopic)
        else:
            return self._generate_with_ollama(category, subtopic)

    def _generate_with_groq(self, category: str, subtopic: str) -> Tuple[str, str]:
        """Generate content using Groq API (English)"""
        prompt = f"""Write a professional blog article about {subtopic} in the {category} category.

STRICT FORMAT REQUIREMENTS:
- Start your response immediately with "TITLE: [Your Clean Title]"
- Do NOT include any introduction text before the title
- Do NOT include asterisks, quotes, or special formatting in the title
- Follow with "CONTENT: [Your article content]"

Content Requirements:
- Professional English writing
- 800-1200 words
- Include practical insights and recent research
- SEO-optimized content
- Engaging and informative tone
- Include relevant examples

Article Structure:
- Introduction (hook + overview)
- 3-4 main sections with subheadings
- Conclusion with actionable takeaways

Topic Focus: {subtopic}

RESPONSE FORMAT (follow exactly):
TITLE: [Clean professional title without asterisks or formatting]
CONTENT: [Full article content starting here...]"""

        try:
            result = generate_content(prompt)
            if not result:
                raise Exception("Empty response from Groq API")

            # Clean up the response and extract title/content
            result = result.strip()

            # Handle cases where AI includes introductory text
            # Look for the actual TITLE: marker
            title_start = result.find("TITLE:")
            if title_start == -1:
                # Fallback: try to find title in different formats
                lines = result.split('\n')
                for i, line in enumerate(lines):
                    if any(marker in line.lower() for marker in ['title:', '**', 'article:', 'blog:']):
                        title_start = result.find(line)
                        result = result[title_start:]
                        break
                else:
                    raise Exception("Could not find title marker in response")
            else:
                result = result[title_start:]

            if "TITLE:" in result and "CONTENT:" in result:
                # Split the response
                parts = result.split("CONTENT:", 1)
                if len(parts) != 2:
                    raise Exception("Could not split title and content properly")

                # Extract and clean title
                title_part = parts[0].replace("TITLE:", "").strip()

                # Advanced title cleaning
                # Remove introductory phrases
                title_part = re.sub(r'^(here is|this is|below is|following is).*?:\s*', '', title_part, flags=re.IGNORECASE)
                title_part = re.sub(r'^(a comprehensive|the|an?)?\s*(blog\s*)?(article\s*)?(on|about)?\s*', '', title_part, flags=re.IGNORECASE)

                # Remove formatting
                title_part = re.sub(r'\*+', '', title_part)  # Remove asterisks
                title_part = re.sub(r'^["\']|["\']$', '', title_part)  # Remove quotes
                title_part = re.sub(r'^\d+\.\s*', '', title_part)  # Remove numbering
                title_part = re.sub(r'^[-–—]\s*', '', title_part)  # Remove dashes
                title_part = re.sub(r'\s+', ' ', title_part)  # Normalize whitespace

                # Clean up newlines and extra formatting
                title_part = re.sub(r'\n.*$', '', title_part)  # Remove everything after first newline
                title_part = title_part.strip()

                # Extract and clean content
                content_part = parts[1].strip()
                # Remove any remaining title remnants from content
                content_part = re.sub(r'^\*+.*?\*+\s*', '', content_part, flags=re.MULTILINE)
                content_part = content_part.strip()

                # Validate title quality
                if len(title_part) < 10 or len(title_part) > 120:
                    raise Exception(f"Title length invalid: {len(title_part)} characters - '{title_part}'")

                if not title_part or not content_part:
                    raise Exception("Title or content is empty after cleaning")

                # Additional title validation
                invalid_chars = ['*', '\n', '\r', '\t']
                if any(char in title_part for char in invalid_chars):
                    # Try to clean further
                    for char in invalid_chars:
                        title_part = title_part.replace(char, ' ')
                    title_part = re.sub(r'\s+', ' ', title_part).strip()

                    if any(char in title_part for char in invalid_chars):
                        raise Exception(f"Title contains invalid characters after aggressive cleaning: '{title_part}'")

                # Ensure title doesn't end with colon or punctuation that would indicate incomplete parsing
                title_part = re.sub(r'[:\s]+$', '', title_part)

                print(f"   ✅ Generated clean title: {title_part}")
                return title_part, content_part
            else:
                raise Exception("Response missing TITLE: or CONTENT: markers")

        except Exception as e:
            print(f"❌ Groq generation error: {e}")
            print(f"   Raw response preview: {result[:300] if result else 'None'}...")
            return None, None

    def _generate_with_ollama(self, category: str, subtopic: str) -> Tuple[str, str]:
        """Generate content using Ollama API (Turkish)"""
        prompt = f"""{subtopic} konusunda {category} kategorisinde kapsamlı bir blog makalesi yazın.

Gereksinimler:
- Profesyonel Türkçe ile yazın
- Uzunluk: 800-1200 kelime
- Pratik içgörüler ve güncel araştırmalar dahil edin
- SEO-optimized içerik
- İlgi çekici ve bilgilendirici ton
- İlgili örnekler dahil edin

Yapı:
- Çekici başlık
- Giriş (dikkat çekici + genel bakış)
- Alt başlıklarla 3-4 ana bölüm
- Uygulanabilir çıkarımlarla sonuç

Odak: {subtopic}

Sadece şunları döndürün:
BAŞLIK: [makale başlığı]
İÇERİK: [tam makale içeriği]"""

        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }

        try:
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            content = result.get('response', '').strip()

            if "BAŞLIK:" in content and "İÇERİK:" in content:
                parts = content.split("İÇERİK:", 1)
                title = parts[0].replace("BAŞLIK:", "").strip()
                content = parts[1].strip()
                return title, content
            else:
                raise Exception("Invalid response format from Ollama API")
        except Exception as e:
            print(f"❌ Ollama generation error: {e}")
            return None, None

    def _create_filename(self, title: str) -> str:
        """Create a clean filename from title"""
        # Clean the title
        filename = re.sub(r'[^\w\s\-]', '', title.lower())
        filename = re.sub(r'[\s\-]+', '-', filename)
        filename = filename.strip('-')

        # Add date prefix
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')

        return f"{date_str}-{filename}"

    def _save_article(self, category: str, title: str, content: str) -> bool:
        """Save article to appropriate directory"""
        try:
            # Create category directory
            category_path = self.content_dir / category
            category_path.mkdir(parents=True, exist_ok=True)

            # Create filename
            filename = self._create_filename(title)
            file_path = category_path / f"{filename}{self.config['file_suffix']}"

            # Check if file already exists
            if file_path.exists():
                print(f"⚠️  File already exists: {file_path.name}")
                return False

            # Get image
            image_url = self.image_fetcher.get_image_for_category(category)

            # Create frontmatter
            frontmatter = f"""---
title: "{title}"
description: "{title[:150]}..."
category: "{category}"
pubDate: {datetime.datetime.now().strftime('%Y-%m-%d')}
heroImage: "{image_url}"
tags: ["{category}"]
---

"""

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)

            print(f"✅ Created: {file_path.name}")
            return True

        except Exception as e:
            print(f"❌ Save error: {e}")
            return False

    def generate_content(self) -> Dict[str, int]:
        """Generate content based on mode and configuration"""
        results = {"success": 0, "failed": 0, "skipped": 0}

        print(f"\n🎯 Starting content generation:")
        print(f"   Mode: {self.mode}")
        print(f"   Language: {self.language}")
        print(f"   API: {self.config['api_type']}")

        for category in self.categories:
            print(f"\n📂 Processing category: {category}")

            category_successes = 0
            for i in range(self.count):
                try:
                    # Select random subtopic
                    subtopics = self.config["subtopics"].get(category, [f"{category} research"])
                    subtopic = random.choice(subtopics)

                    print(f"   🔄 Generating article {i+1}/{self.count} - Topic: {subtopic}")

                    # Generate content
                    title, content = self._generate_title_and_content(category, subtopic)

                    if not title or not content:
                        print(f"   ❌ Generation failed for {subtopic}")
                        results["failed"] += 1
                        continue

                    # Check for duplicates
                    title_key = re.sub(r'[^\w\s]', '', title.lower())
                    if title_key in self.existing_titles:
                        print(f"   ⚠️  Duplicate title detected, skipping: {title}")
                        results["skipped"] += 1
                        continue

                    # Save article
                    if self._save_article(category, title, content):
                        self.existing_titles.add(title_key)
                        results["success"] += 1
                        category_successes += 1
                    else:
                        results["failed"] += 1

                    # Rate limiting
                    if self.config["api_type"] == "groq":
                        time.sleep(2)  # Groq rate limit
                    else:
                        time.sleep(5)  # Ollama processing time

                except Exception as e:
                    print(f"   ❌ Error generating content: {e}")
                    results["failed"] += 1

            print(f"   ✅ Category {category} completed: {category_successes} articles")

        return results

def main():
    parser = argparse.ArgumentParser(description='MindVerse Unified Content Generator')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='auto',
                       help='Generation mode (default: auto)')
    parser.add_argument('--language', choices=['en', 'tr'], default='en',
                       help='Content language (default: en)')
    parser.add_argument('--categories', nargs='+',
                       default=['health', 'psychology', 'history', 'space', 'quotes', 'love'],
                       help='Categories to generate content for')
    parser.add_argument('--count', type=int, default=1,
                       help='Number of articles per category (default: 1)')

    args = parser.parse_args()

    # Validate mode and language combination
    if args.mode == 'auto' and args.language == 'tr':
        print("❌ Auto mode only supports English (--language en)")
        print("   Use --mode manual for Turkish content generation")
        sys.exit(1)

    # Initialize generator
    generator = UnifiedContentGenerator(
        mode=args.mode,
        language=args.language,
        categories=args.categories,
        count=args.count
    )

    # Generate content
    start_time = time.time()
    results = generator.generate_content()
    elapsed_time = time.time() - start_time

    # Print summary
    print(f"\n📊 Generation Summary:")
    print(f"   ✅ Success: {results['success']}")
    print(f"   ❌ Failed: {results['failed']}")
    print(f"   ⚠️  Skipped: {results['skipped']}")
    print(f"   ⏱️  Time: {elapsed_time:.1f}s")
    print(f"   🎯 Mode: {args.mode} ({args.language.upper()})")

if __name__ == "__main__":
    main()
