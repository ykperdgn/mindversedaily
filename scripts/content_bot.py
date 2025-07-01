import os
import datetime
import random
import time
import re
from groq_client import generate_content

def slugify(text):
    # Sadece harf, rakam ve tire bırak, diğer her şeyi kaldır
    text = text.lower().replace(" ", "-")
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return text

def parse_article_fields(article_text):
    # Başlık, özet, görsel ve içerik ayıkla
    lines = article_text.splitlines()
    # Prompt artığı veya "Türkçeye çevir" gibi satırları atla
    lines = [l for l in lines if not l.lower().startswith("translate the following") and not l.lower().startswith("türkçeye çevir") and not l.lower().startswith("çevrilmiş hali:")]
    # Title ve summary satırlarını body'den de ayıkla
    title = next((l for l in lines if l.lower().startswith("title:") or l.lower().startswith("# ") or l.lower().startswith("**title:**")), None)
    description = next((l for l in lines if l.lower().startswith("summary:") or l.lower().startswith("description:") or l.lower().startswith("**summary:**")), None)
    # Hem frontmatter hem içerik body'deki image'ı yakala
    image = next((l for l in lines if l.lower().startswith("image:") or l.lower().startswith("img:") or l.lower().startswith("**image:**")), None)
    if image:
        image_url = image.split(":",1)[1].strip().strip('*').strip()
        if image_url.startswith('http'):
            image = image_url
        else:
            image = "https://mindversedaily.com/images/generated/default.jpg"
    else:
        image = "https://mindversedaily.com/images/generated/default.jpg"
    # Fallbacks
    if title:
        # **Title:** veya Title: veya # ...
        title = title.split(":",1)[1].strip() if ":" in title else title.strip("# *").strip()
    else:
        title = "Untitled"
    if description:
        description = description.split(":",1)[1].strip() if ":" in description else description.strip("# *").strip()
    else:
        description = "No summary."
    # İçerik kısmı (frontmatter ve başlık/özet/görsel satırlarını çıkar)
    content = "\n".join([
        l for l in lines if not any(l.lower().startswith(x) for x in [
            "title:", "summary:", "description:", "image:", "img:", "**image:**", "**title:**", "**summary:**"
        ])
    ]).strip()
    return title, description, image, content

categories = ["health", "psychology", "history", "space", "quotes", "love"]

subtopics = {
    "health": ["mental wellness", "nutrition tips", "exercise benefits", "sleep hygiene", "stress management", "immune system", "healthy aging"],
    "psychology": ["cognitive biases", "emotional intelligence", "child development", "therapy techniques", "motivation", "personality types", "group dynamics"],
    "history": ["ancient civilizations", "world wars", "historical inventions", "famous leaders", "revolutions", "lost cities", "cultural heritage"],
    "space": ["exoplanets", "black holes", "space exploration", "life on Mars", "cosmic phenomena", "telescopes", "space technology"],
    "quotes": ["inspirational quotes", "famous thinkers", "life lessons", "success and failure", "love and friendship", "wisdom from history"],
    "love": ["science of attraction", "relationship tips", "love languages", "psychology of love", "romantic gestures", "long-distance relationships"]
}

def create_articles_for_all_categories():
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    for category in categories:
        try:
            subtopic = random.choice(subtopics[category])
            prompt_en = (
                f"Write a long-form article (700+ words) in English in the category '{category}' focusing on '{subtopic}', including recent developments or scientific findings. "
                "Include a catchy title (start with 'Title:'), a short summary (start with 'Summary:'), and a suggested image URL (start with 'Image:'). Then write the full article."
            )
            english_article = generate_content(prompt_en)
            time.sleep(5)

            # Türkçe çeviri prompt'unu daha sade ve başlık/özet dahil olacak şekilde yap
            short_translation_prompt = (
                "Makalenin tamamını baştan sona Türkçeye çevir. Başlık ve özet dahil, başa tekrar Title: ve Summary: ekle. Sadece çeviriyi döndür:\n\n"
            ) + english_article[:12000]

            turkish_article = generate_content(short_translation_prompt)
            time.sleep(5)

            for lang, article in [("en", english_article), ("tr", turkish_article)]:
                title, description, image, content = parse_article_fields(article)
                slug = slugify(title)
                content_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog", category)
                os.makedirs(content_dir, exist_ok=True)
                filepath = os.path.join(content_dir, f"{date}-{slug}.{lang}.md")
                frontmatter = f"---\ntitle: \"{title}\"\ndescription: \"{description}\"\npubDate: {date}\ncategory: \"{category}\"\ntags: []\nimage: \"{image}\"\n---\n\n"
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(frontmatter)
                    f.write(content)
            print(f"✅ Successfully created articles for category '{category}' with subtopic '{subtopic}'.")
        except Exception as e:
            print(f"⚠️ Error while processing category '{category}': {e}")
            continue

def create_articles_for_selected_categories(selected_categories):
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    for category in selected_categories:
        try:
            subtopic = random.choice(subtopics[category])
            prompt_en = (
                f"Write a long-form article (700+ words) in English in the category '{category}' focusing on '{subtopic}', including recent developments or scientific findings. "
                "Include a catchy title (start with 'Title:'), a short summary (start with 'Summary:'), and a suggested image URL (start with 'Image:'). Then write the full article."
            )
            english_article = generate_content(prompt_en)
            time.sleep(5)

            short_translation_prompt = (
                "Makalenin tamamını baştan sona Türkçeye çevir. Başlık ve özet dahil, başa tekrar Title: ve Summary: ekle. Sadece çeviriyi döndür:\n\n"
            ) + english_article[:12000]

            turkish_article = generate_content(short_translation_prompt)
            time.sleep(5)

            for lang, article in [("en", english_article), ("tr", turkish_article)]:
                title, description, image, content = parse_article_fields(article)
                slug = slugify(title)
                content_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog", category)
                os.makedirs(content_dir, exist_ok=True)
                filepath = os.path.join(content_dir, f"{date}-{slug}.{lang}.md")
                frontmatter = f"---\ntitle: \"{title}\"\ndescription: \"{description}\"\npubDate: {date}\ncategory: \"{category}\"\ntags: []\nimage: \"{image}\"\n---\n\n"
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(frontmatter)
                    f.write(content)
            print(f"✅ Successfully created articles for category '{category}' with subtopic '{subtopic}'.")
        except Exception as e:
            print(f"⚠️ Error while processing category '{category}': {e}")
            continue

if __name__ == "__main__":
    # Sadece quotes kategorisi için çalıştır
    create_articles_for_selected_categories(["quotes"])
