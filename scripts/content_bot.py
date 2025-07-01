import os
import datetime
import random
import time
import re
import subprocess
from groq_client import generate_content
from image_fetcher import ImageFetcher

def slugify(text):
    # Sadece harf, rakam ve tire bırak, diğer her şeyi kaldır
    text = text.lower().replace(" ", "-")
    text = re.sub(r'[^a-z0-9\-]', '', text)
    return text

def parse_article_fields(article_text, category=None, image_fetcher=None):
    # Başlık, özet, görsel ve içerik ayıkla
    lines = article_text.splitlines()
    # Prompt artığı veya "Türkçeye çevir" gibi satırları atla
    lines = [l for l in lines if not l.lower().startswith("translate the following") and not l.lower().startswith("türkçeye çevir") and not l.lower().startswith("çevrilmiş hali:")]
    # Title ve summary satırlarını body'den de ayıkla
    title = next((l for l in lines if l.lower().startswith("title:") or l.lower().startswith("# ") or l.lower().startswith("**title:**")), None)
    description = next((l for l in lines if l.lower().startswith("summary:") or l.lower().startswith("description:") or l.lower().startswith("**summary:**")), None)    # Fallbacks
    if title:
        # **Title:** veya Title: veya # ...
        title = title.split(":",1)[1].strip() if ":" in title else title.strip("# *").strip()
        # Ekstra karakterleri temizle
        title = title.strip('*"').strip()
    else:
        title = "Untitled"

    # Untitled kontrolü - eğer başlık Untitled veya boşsa, içerikten çıkar
    if not title or title.lower() in ["untitled", "başlıksız", ""]:
        # İçerikten ilk anlamlı cümleyi başlık yap
        content_lines = [l for l in lines if l.strip() and len(l.strip()) > 20 and not any(l.lower().startswith(x) for x in [
            "title:", "summary:", "description:", "image:", "img:", "**image:**", "**title:**", "**summary:**", "başlık:", "özet:"
        ])]
        if content_lines:
            title = content_lines[0].strip().strip('"*').strip()[:80]  # İlk 80 karakter
            if title.endswith(":"):
                title = title[:-1]
        else:
            title = f"Article about {category}" if category else "New Article"

    if description:
        description = description.split(":",1)[1].strip() if ":" in description else description.strip("# *").strip()
        # Ekstra karakterleri temizle
        description = description.strip('*"').strip()
    else:
        description = "No summary."

    # Description kontrolü
    if not description or description.lower() in ["no summary.", "özet yok.", ""]:
        # İçerikten ilk paragrafı özet yap
        content_lines = [l for l in lines if len(l.strip()) > 50 and not any(l.lower().startswith(x) for x in [
            "title:", "summary:", "description:", "image:", "img:", "**image:**", "**title:**", "**summary:**", "başlık:", "özet:"
        ])]
        if content_lines:
            description = content_lines[0].strip().strip('"*').strip()[:150] + "..."  # İlk 150 karakter
        else:
            description = f"An article about {category}" if category else "A new article"

    # API'den görsel çek
    if image_fetcher and title and category:
        image = image_fetcher.get_image_for_content(title, category, description)
        print(f"🖼️ Image fetched for '{title}': {image}")
    else:
        image = "/assets/blog-placeholder-1.svg"

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

def create_articles_for_all_categories(auto_deploy_enabled=False):
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    image_fetcher = ImageFetcher()  # Image fetcher instance'ı oluştur

    for category in categories:
        try:
            subtopic = random.choice(subtopics[category])
            prompt_en = (
                f"Write a long-form article (700+ words) in English in the category '{category}' focusing on '{subtopic}', including recent developments or scientific findings. "
                "Include a catchy title (start with 'Title:') and a short summary (start with 'Summary:'). Then write the full article."
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
                title, description, image, content = parse_article_fields(article, category, image_fetcher)
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

    # Otomatik deploy
    if auto_deploy_enabled:
        time.sleep(10)  # Content creation tamamlansin
        auto_deploy()

def create_articles_for_selected_categories(selected_categories, auto_deploy_enabled=False):
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    image_fetcher = ImageFetcher()  # Image fetcher instance'ı oluştur

    for category in selected_categories:
        try:
            subtopic = random.choice(subtopics[category])
            prompt_en = (
                f"Write a long-form article (700+ words) in English in the category '{category}' focusing on '{subtopic}', including recent developments or scientific findings. "
                "Include a catchy title (start with 'Title:') and a short summary (start with 'Summary:'). Then write the full article."
            )
            english_article = generate_content(prompt_en)
            time.sleep(5)

            short_translation_prompt = (
                "Makalenin tamamını baştan sona Türkçeye çevir. Başlık ve özet dahil, başa tekrar Title: ve Summary: ekle. Sadece çeviriyi döndür:\n\n"
            ) + english_article[:12000]

            turkish_article = generate_content(short_translation_prompt)
            time.sleep(5)

            for lang, article in [("en", english_article), ("tr", turkish_article)]:
                title, description, image, content = parse_article_fields(article, category, image_fetcher)
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

    # Otomatik deploy
    if auto_deploy_enabled:
        time.sleep(10)  # Content creation tamamlansin
        auto_deploy()

def auto_deploy():
    """Otomatik build ve deploy işlemi"""
    try:
        print("\n🚀 Starting automatic deployment...")
        base_dir = os.path.dirname(os.path.dirname(__file__))  # scripts/../

        # Git add
        result = subprocess.run(["git", "add", "."], cwd=base_dir, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"❌ Git add failed: {result.stderr}")
            return False

        # Git commit
        commit_msg = f"Auto-generated content - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(["git", "commit", "-m", commit_msg], cwd=base_dir, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print("⚠️ No changes to commit or commit failed")

        # Build
        print("🏗️ Building project...")
        result = subprocess.run(["npm", "run", "build"], cwd=base_dir, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False

        # Git push (Vercel otomatik deploy yapacak)
        result = subprocess.run(["git", "push", "origin", "main"], cwd=base_dir, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False

        print("✅ Automatic deployment completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

if __name__ == "__main__":
    import sys

    # Komut satırı argümanlarını kontrol et
    auto_deploy_enabled = "--deploy" in sys.argv

    if len(sys.argv) > 1 and sys.argv[1] not in ["--deploy"]:
        # Belirli kategoriler
        categories_to_create = [arg for arg in sys.argv[1:] if arg != "--deploy"]
        create_articles_for_selected_categories(categories_to_create, auto_deploy_enabled)
    else:
        # Tek kategori test için
        create_articles_for_selected_categories(["health"], auto_deploy_enabled)
