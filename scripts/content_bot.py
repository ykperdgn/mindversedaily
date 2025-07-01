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
                "Include a catchy title, a short summary, 3 shareable sentences, and a CTA at the end."
            )
            english_article = generate_content(prompt_en)
            time.sleep(5)

            short_translation_prompt = (
                "Translate the following English article into Turkish. Keep all formatting, structure, and headlines the same:\n\n"
            ) + english_article[:12000]

            turkish_article = generate_content(short_translation_prompt)
            time.sleep(5)

            title_line = english_article.splitlines()[0]
            title = title_line.strip("# ")
            slug = slugify(title)

            content_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog", category)
            os.makedirs(content_dir, exist_ok=True)

            for lang, content in [("en", english_article), ("tr", turkish_article)]:
                filepath = os.path.join(content_dir, f"{date}-{slug}.{lang}.md")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
            print(f"✅ Successfully created articles for category '{category}' with subtopic '{subtopic}'.")
        except Exception as e:
            print(f"⚠️ Error while processing category '{category}': {e}")
            continue

if __name__ == "__main__":
    create_articles_for_all_categories()
