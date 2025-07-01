#!/usr/bin/env python3
"""
Ollama ile içerik üretimi ve otomatik deployment sistemi
"""

import os
import datetime
import random
import time
import re
import requests
import json
from image_fetcher import ImageFetcher

class OllamaContentGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.1:8b"  # Veya kullandığınız model
        self.image_fetcher = ImageFetcher()

        self.categories = ["health", "psychology", "history", "space", "quotes", "love"]

        self.subtopics = {
            "health": [
                "mental wellness", "nutrition tips", "exercise benefits", "sleep hygiene",
                "stress management", "immune system", "healthy aging", "preventive medicine",
                "fitness routines", "meditation benefits", "diet trends", "healthcare technology"
            ],
            "psychology": [
                "cognitive biases", "emotional intelligence", "child development", "therapy techniques",
                "motivation", "personality types", "group dynamics", "behavioral psychology",
                "neuroscience insights", "mental health awareness", "learning psychology", "social psychology"
            ],
            "history": [
                "ancient civilizations", "world wars", "historical inventions", "famous leaders",
                "revolutions", "lost cities", "cultural heritage", "archaeological discoveries",
                "medieval times", "renaissance period", "industrial revolution", "modern history"
            ],
            "space": [
                "exoplanets", "black holes", "space exploration", "life on Mars",
                "cosmic phenomena", "telescopes", "space technology", "astronauts",
                "solar system", "galaxies", "space missions", "astronomy discoveries"
            ],
            "quotes": [
                "inspirational quotes", "famous thinkers", "life lessons", "success philosophy",
                "motivational wisdom", "philosophical insights", "leadership quotes", "creativity quotes",
                "happiness quotes", "wisdom from literature", "historical quotes", "modern thinkers"
            ],
            "love": [
                "science of attraction", "relationship tips", "love languages", "psychology of love",
                "romantic gestures", "long-distance relationships", "marriage advice", "dating psychology",
                "emotional connections", "relationship communication", "love science", "couple dynamics"
            ]
        }

    def generate_with_ollama(self, prompt):
        """Ollama ile içerik üret"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            }

            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Ollama connection error: {e}")
            return None

    def slugify(self, text):
        """URL-friendly slug oluştur"""
        text = text.lower().replace(" ", "-")
        text = re.sub(r'[^a-z0-9\-]', '', text)
        return text[:80]  # Max 80 karakter

    def parse_article_fields(self, article_text, category):
        """Makale alanlarını ayıkla"""
        lines = article_text.splitlines()

        # Başlık bul
        title = None
        for line in lines:
            if line.lower().startswith("title:") or line.lower().startswith("# "):
                title = line.split(":", 1)[1].strip() if ":" in line else line.strip("# ").strip()
                title = title.strip('*"').strip()
                break

        # Özet bul
        description = None
        for line in lines:
            if line.lower().startswith("summary:") or line.lower().startswith("description:"):
                description = line.split(":", 1)[1].strip()
                description = description.strip('*"').strip()
                break

        # Fallbacks
        if not title or title.lower() in ["untitled", "başlıksız"]:
            content_lines = [l for l in lines if l.strip() and len(l.strip()) > 20]
            if content_lines:
                title = content_lines[0].strip().strip('"*')[:80]
                if title.endswith(":"):
                    title = title[:-1]
            else:
                title = f"Article about {category}"

        if not description:
            description = f"An informative article about {category}"

        # İçerik temizle
        content = "\n".join([
            l for l in lines if not any(l.lower().startswith(x) for x in [
                "title:", "summary:", "description:", "image:", "başlık:", "özet:"
            ])
        ]).strip()

        # Görsel al
        image = self.image_fetcher.get_image_for_content(title, category, description)

        return title, description, image, content

    def create_article(self, category, language="en"):
        """Tek makale oluştur"""
        subtopic = random.choice(self.subtopics[category])

        if language == "en":
            prompt = f"""Write a comprehensive, engaging article (800+ words) about '{subtopic}' in the '{category}' category.

Start with:
Title: [Catchy, SEO-friendly title]
Summary: [2-3 sentence summary]

Then write the full article with:
- Engaging introduction
- Multiple detailed sections with subheadings
- Recent scientific findings or developments
- Practical tips or insights
- Strong conclusion
- Professional, informative tone

Make it factual, well-researched, and valuable for readers."""

        else:  # Turkish
            prompt = f"""'{subtopic}' konusunda '{category}' kategorisinde kapsamlı, ilgi çekici bir makale (800+ kelime) yaz.

Şununla başla:
Title: [Çekici, SEO dostu başlık]
Summary: [2-3 cümlelik özet]

Sonra tam makaleyi şunlarla yaz:
- İlgi çekici giriş
- Alt başlıklarla detaylı bölümler
- Son bilimsel bulgular veya gelişmeler
- Pratik ipuçları veya öngörüler
- Güçlü sonuç
- Profesyonel, bilgilendirici ton

Gerçeklere dayalı, iyi araştırılmış ve okuyucular için değerli olsun."""

        print(f"🤖 Generating {language} article for {category} - {subtopic}")
        article = self.generate_with_ollama(prompt)

        if not article:
            print(f"❌ Failed to generate article for {category}")
            return False

        title, description, image, content = self.parse_article_fields(article, category)
        slug = self.slugify(title)

        # Dosya yolu
        date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        content_dir = os.path.join("src", "content", "blog", category)
        os.makedirs(content_dir, exist_ok=True)
        filepath = os.path.join(content_dir, f"{date}-{slug}.{language}.md")

        # Frontmatter ve içerik
        frontmatter = f'''---
title: "{title}"
description: "{description}"
pubDate: {date}
category: "{category}"
tags: []
image: "{image}"
---

'''

        # Dosyayı yaz
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter + content)

        print(f"✅ Created: {filepath}")
        print(f"🖼️ Image: {image}")
        return True

    def bulk_create_articles(self, articles_per_category=5):
        """Her kategori için toplu makale üret"""
        total_created = 0

        for category in self.categories:
            print(f"\n📝 Creating articles for {category}...")

            for i in range(articles_per_category):
                # İngilizce makale
                if self.create_article(category, "en"):
                    total_created += 1

                # 15 saniye bekle (API limit)
                time.sleep(15)

                # Türkçe makale
                if self.create_article(category, "tr"):
                    total_created += 1

                # 15 saniye bekle
                time.sleep(15)

                print(f"⏳ Completed {i+1}/{articles_per_category} for {category}")

        print(f"\n🎉 Total articles created: {total_created}")
        return total_created

    def daily_content_creation(self):
        """Günlük otomatik içerik üretimi"""
        print("🌅 Starting daily content creation...")

        # Her kategoriden 1 makale
        for category in self.categories:
            # İngilizce
            self.create_article(category, "en")
            time.sleep(15)

            # Türkçe
            self.create_article(category, "tr")
            time.sleep(15)

        print("✅ Daily content creation completed!")

def main():
    generator = OllamaContentGenerator()

    import sys
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "bulk":
            # Toplu üretim - her kategoriden 5 makale
            generator.bulk_create_articles(5)
        elif mode == "daily":
            # Günlük üretim - her kategoriden 1 makale
            generator.daily_content_creation()
        elif mode == "test":
            # Test - sadece 1 kategori
            generator.create_article("quotes", "en")
    else:
        print("Usage: python ollama_content.py [bulk|daily|test]")

if __name__ == "__main__":
    main()
