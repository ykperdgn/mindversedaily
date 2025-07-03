#!/usr/bin/env python3
"""
MindVerse Groq English Content Generator
Generates high-quality English content using Groq API
"""

import os
import sys
import json
import datetime
import random
import time
import re
import requests
from typing import Dict, List, Set, Tuple
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

# Configuration
CATEGORIES = ["health", "psychology", "history", "space", "quotes", "love"]
ARTICLES_PER_RUN = 5  # Number of articles to generate per run

# English subtopics
ENGLISH_SUBTOPICS = {
    "health": [
        "nutrition science breakthroughs", "exercise physiology research", "sleep optimization studies",
        "stress management techniques", "immune system boosting", "healthy aging secrets",
        "preventive medicine advances", "brain health discoveries", "cardiovascular wellness",
        "digestive health science", "hormonal balance research", "mindful eating practices",
        "fitness innovation technology", "alternative medicine studies", "medical breakthroughs",
        "longevity research findings", "disease prevention strategies", "wellness habits formation",
        "metabolic health optimization", "cellular regeneration science", "microbiome research",
        "chronic disease prevention", "mental health awareness", "functional medicine approaches"
    ],
    "psychology": [
        "cognitive bias research", "emotional intelligence development", "child psychology studies",
        "therapeutic approaches innovation", "motivation science", "personality psychology",
        "social dynamics research", "memory enhancement techniques", "behavioral psychology",
        "social psychology findings", "cognitive psychology", "positive psychology",
        "neuroscience breakthroughs", "decision-making psychology", "habit formation science",
        "mental resilience building", "psychological wellness", "consciousness studies",
        "developmental psychology", "clinical psychology advances", "trauma psychology",
        "mindfulness psychology", "learning psychology", "attention research"
    ],
    "history": [
        "ancient civilizations mysteries", "world war revelations", "historical inventions impact",
        "legendary leaders analysis", "cultural revolution studies", "lost civilizations discoveries",
        "heritage preservation efforts", "archaeological breakthroughs", "medieval period insights",
        "renaissance discoveries", "industrial revolution effects", "colonial history analysis",
        "ancient mysteries solved", "historical figures biography", "empire rise and fall",
        "pivotal historical events", "social movements history", "technological evolution",
        "military strategies analysis", "historical artifacts studies", "forgotten empires"
    ],
    "space": [
        "exoplanet discoveries", "black hole mysteries", "space missions analysis",
        "Mars exploration updates", "cosmic phenomena research", "telescope innovations",
        "space technology advances", "astronaut experiences", "galaxy formation studies",
        "dark matter research", "space colonization plans", "satellite technology",
        "planetary science", "asteroid studies", "space weather patterns",
        "cosmic radiation effects", "interstellar exploration", "space engineering",
        "astronomical discoveries", "universe mysteries", "space station research"
    ],
    "quotes": [
        "inspirational wisdom collection", "philosophical insights", "life lessons wisdom",
        "success principles", "leadership wisdom", "historical quotes analysis",
        "motivational thoughts", "personal growth quotes", "career inspiration",
        "overcoming adversity", "positive mindset development", "achievement quotes",
        "resilience wisdom", "creativity inspiration", "entrepreneurship quotes",
        "happiness philosophy", "mindfulness quotes", "self-improvement wisdom"
    ],
    "love": [
        "relationship psychology research", "attraction science", "love languages study",
        "relationship advice", "romantic psychology", "long-distance relationships",
        "marriage studies", "dating psychology", "emotional intimacy",
        "relationship communication", "conflict resolution", "relationship phases",
        "attachment theory", "love neuroscience", "couples therapy",
        "modern dating trends", "relationship maintenance", "love psychology"
    ]
}

class GroqEnglishGenerator:
    def __init__(self):
        self.content_dir = Path("src/content/blog")
        self.image_fetcher = ImageFetcher()
        self.existing_titles = self._load_existing_titles()

    def _load_existing_titles(self) -> Set[str]:
        """Load existing English article titles to prevent duplicates"""
        existing_titles = set()

        try:
            for category in CATEGORIES:
                category_path = self.content_dir / category
                if category_path.exists():
                    for file_path in category_path.glob("*.en.md"):
                        # Extract title from filename
                        filename = file_path.stem
                        # Remove date prefix and language suffix
                        title_part = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
                        title_part = re.sub(r'\.en$', '', title_part)
                        existing_titles.add(title_part.lower())
        except Exception as e:
            print(f"Warning: Could not load existing titles: {e}")

        print(f"📚 Loaded {len(existing_titles)} existing English titles for duplicate prevention")
        return existing_titles

    def slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower().replace(" ", "-")
        text = re.sub(r'[^a-z0-9\-]', '', text)
        text = re.sub(r'-+', '-', text).strip('-')
        return text[:60]  # Limit length

    def clean_frontmatter_value(self, value: str) -> str:
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

    def _generate_with_groq(self, category: str, subtopic: str) -> Tuple[str, str]:
        """Generate content using Groq API with improved title parsing"""
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
                title_part = re.sub(r'^(here is|this is|below is|following is).*?:\s*', '', title_part, flags=re.IGNORECASE)
                title_part = re.sub(r'^(a comprehensive|the|an?)?\s*(blog\s*)?(article\s*)?(on|about)?\s*', '', title_part, flags=re.IGNORECASE)
                title_part = re.sub(r'\*+', '', title_part)  # Remove asterisks
                title_part = re.sub(r'^["\']|["\']$', '', title_part)  # Remove quotes
                title_part = re.sub(r'^\d+\.\s*', '', title_part)  # Remove numbering
                title_part = re.sub(r'^[-–—]\s*', '', title_part)  # Remove dashes
                title_part = re.sub(r'\s+', ' ', title_part)  # Normalize whitespace
                title_part = re.sub(r'\n.*$', '', title_part)  # Remove everything after first newline
                title_part = re.sub(r'[:\s]+$', '', title_part)  # Remove trailing colons
                title_part = title_part.strip()

                # Extract and clean content
                content_part = parts[1].strip()
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
                    for char in invalid_chars:
                        title_part = title_part.replace(char, ' ')
                    title_part = re.sub(r'\s+', ' ', title_part).strip()

                print(f"   ✅ Generated clean title: {title_part}")
                return title_part, content_part
            else:
                raise Exception("Response missing TITLE: or CONTENT: markers")

        except Exception as e:
            print(f"❌ Groq generation error: {e}")
            print(f"   Raw response preview: {result[:300] if result else 'None'}...")
            return None, None

    def write_article(self, filepath: str, title: str, description: str, date: str, category: str, image: str, content: str):
        """Write article to file with frontmatter"""
        title_clean = self.clean_frontmatter_value(title)
        description_clean = self.clean_frontmatter_value(description)

        frontmatter = f"""---
title: "{title_clean}"
description: "{description_clean}"
category: "{category}"
pubDate: {date}
heroImage: "{image}"
tags: ["{category}"]
---

{content}"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)

        print(f"✅ Created: {os.path.basename(filepath)}")

    def generate_english_articles(self, categories: List[str] = None, count: int = ARTICLES_PER_RUN):
        """Generate English articles using Groq API"""
        print(f"🇺🇸 Starting English content generation with Groq API...")
        print(f"📊 Target: {count} articles per selected category")

        if categories is None:
            categories = CATEGORIES

        # Create content directory
        total_created = 0
        date = datetime.datetime.utcnow().strftime("%Y-%m-%d")

        for category in categories:
            print(f"\n📂 Processing category: {category.upper()}")
            category_dir = self.content_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)

            # Get subtopics for this category
            available_subtopics = ENGLISH_SUBTOPICS[category].copy()
            random.shuffle(available_subtopics)

            created_count = 0

            for i in range(count):
                max_attempts = 3
                article_created = False

                for attempt in range(max_attempts):
                    try:
                        # Select subtopic
                        subtopic = available_subtopics[i % len(available_subtopics)]

                        print(f"  📝 Creating English article {i+1}/{count}: {subtopic}")

                        # Generate content
                        title, content = self._generate_with_groq(category, subtopic)

                        if title and content:
                            # Check for duplicates
                            title_lower = title.lower()
                            if title_lower in self.existing_titles:
                                print(f"    ⚠️ Duplicate title detected, skipping...")
                                continue

                            # Add to existing titles
                            self.existing_titles.add(title_lower)

                            # Generate description from first paragraph of content
                            description = content.split('\n')[0][:150] + "..."

                            # Get image
                            try:
                                image = self.image_fetcher.get_relevant_image(category, title)
                            except:
                                image = "/assets/blog-placeholder-1.svg"

                            # Create filename
                            slug = self.slugify(title)
                            filepath = category_dir / f"{date}-{slug}.en.md"

                            # Write article
                            self.write_article(str(filepath), title, description, date, category, image, content)

                            created_count += 1
                            total_created += 1
                            article_created = True

                            print(f"    ✅ Created: {title[:60]}...")
                            break

                        time.sleep(2)  # Rate limiting

                    except Exception as e:
                        print(f"    ❌ Attempt {attempt + 1} failed: {e}")
                        continue

                if not article_created:
                    print(f"    ❌ Failed to create article for {subtopic}")

            print(f"  📊 Category {category}: {created_count} articles created")

        print(f"\n🎉 English content generation completed!")
        print(f"📊 Total articles created: {total_created}")
        return total_created

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate English content using Groq API")
    parser.add_argument("--categories", nargs="+", choices=CATEGORIES,
                       help="Categories to generate content for")
    parser.add_argument("--count", type=int, default=ARTICLES_PER_RUN,
                       help=f"Number of articles per category (default: {ARTICLES_PER_RUN})")

    args = parser.parse_args()

    generator = GroqEnglishGenerator()
    generator.generate_english_articles(
        categories=args.categories,
        count=args.count
    )

if __name__ == "__main__":
    main()
