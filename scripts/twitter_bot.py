"""
MindVerse Daily Twitter Bot
Yeni blog yazıları otomatik olarak Twitter'da paylaşılır.
Son blog yazısını okur ve tweet atar.
"""

import tweepy
import json
import os
import time
from datetime import datetime, timedelta
import re
import random
from pathlib import Path

class TwitterBot:
    def __init__(self, test_mode=False):
        # Test mode - gerçek tweet atmadan test için
        self.test_mode = test_mode

        # Twitter API v2 credentials
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        # Twitter client initialization
        if not self.test_mode:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )

        # Shared posts tracking
        self.shared_posts_file = "scripts/data/shared_tweets.json"
        self.load_shared_posts()

    def load_shared_posts(self):
        """Daha önce paylaşılan postları yükle"""
        try:
            with open(self.shared_posts_file, 'r', encoding='utf-8') as f:
                self.shared_posts = json.load(f)
        except FileNotFoundError:
            self.shared_posts = []

    def save_shared_posts(self):
        """Paylaşılan postları kaydet"""
        os.makedirs(os.path.dirname(self.shared_posts_file), exist_ok=True)
        with open(self.shared_posts_file, 'w', encoding='utf-8') as f:
            json.dump(self.shared_posts, f, indent=2, ensure_ascii=False)

    def get_category_emoji(self, category):
        """Kategori için emoji döndür"""
        category_emojis = {
            "health": "🧬",
            "psychology": "🧠",
            "history": "📜",
            "space": "🚀",
            "quotes": "💬",
            "love": "❤️",
            "horoscope": "🔮",
            "science": "🔬",
            "technology": "💻",
            "nature": "🌿"
        }
        return category_emojis.get(category.lower(), "📝")

    def get_latest_blog_posts(self, days_back=1):
        """Son günlerde oluşturulan blog yazılarını getir"""
        content_dir = Path("src/content/blog")
        posts = []

        if not content_dir.exists():
            print(f"❌ Blog içerik klasörü bulunamadı: {content_dir}")
            return posts

        # Son X gün içinde oluşturulan dosyaları bul
        cutoff_date = datetime.now() - timedelta(days=days_back)

        for category_dir in content_dir.iterdir():
            if category_dir.is_dir():
                for post_file in category_dir.glob("*.md"):
                    # Dosya oluşturma tarihi kontrol et
                    file_mtime = datetime.fromtimestamp(post_file.stat().st_mtime)

                    if file_mtime > cutoff_date:
                        post_data = self.parse_blog_post(post_file)
                        if post_data:
                            posts.append(post_data)

        # Tarihe göre sırala (en yeni önce)
        posts.sort(key=lambda x: x['date'], reverse=True)
        return posts

    def parse_blog_post(self, file_path):
        """Blog yazısını parse et"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Frontmatter'ı parse et
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2].strip()

                    # Title'ı çıkar
                    title_match = re.search(r'title:\s*["\']([^"\']+)["\']', frontmatter)
                    title = title_match.group(1) if title_match else file_path.stem

                    # Description'ı çıkar
                    desc_match = re.search(r'description:\s*["\']([^"\']+)["\']', frontmatter)
                    description = desc_match.group(1) if desc_match else ""

                    # Category'yi çıkar
                    cat_match = re.search(r'category:\s*["\']([^"\']+)["\']', frontmatter)
                    category = cat_match.group(1) if cat_match else file_path.parent.name

                    # Dosya adından slug oluştur
                    filename = file_path.stem
                    # Language suffix'i kaldır (.tr veya .en)
                    slug = re.sub(r'\.(tr|en)$', '', filename)

                    # URL oluştur - blog olmadan direkt kategori/slug
                    url = f"https://mindversedaily.com/{category}/{slug}"

                    return {
                        'id': filename,
                        'title': title,
                        'description': description,
                        'category': category,
                        'url': url,
                        'slug': slug,
                        'file_path': str(file_path),                        'date': datetime.fromtimestamp(file_path.stat().st_mtime)
                    }
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None

    def create_tweet_content(self, post_data):
        """Tweet içeriği oluştur"""
        title = post_data.get('title', 'Yeni Yazı')
        category = post_data.get('category', 'blog')
        url = post_data.get('url', '')
        description = post_data.get('description', '')

        emoji = self.get_category_emoji(category)

        # Title'ı kısalt (80 karakter max)
        short_title = title[:80] + "..." if len(title) > 80 else title

        # Description'ı kısalt (100 karakter max)
        short_desc = description[:100] + "..." if len(description) > 100 else description

        # Tweet template'leri - daha kısa ve etkili
        tweet_templates = [
            f"{emoji} {short_title}\n\n💡 {short_desc}\n\n🔗 {url}\n\n#MindVerseDaily #{category.title()}",
            f"{emoji} {short_title}\n\n📖 {short_desc}\n\n👉 {url}\n\n#MindVerse #{category}",
            f"🌟 {short_title}\n\n{emoji} {short_desc}\n\n📚 {url}\n\n#MindVerseDaily #Bilim",
        ]

        # En uygun template'i seç (280 karakter limiti)
        for template in tweet_templates:
            if len(template) <= 280:
                return template

        # Hiçbiri uygun değilse en basit formatı kullan
        base_tweet = f"{emoji} {short_title}\n\n🔗 {url}\n\n#MindVerseDaily"
        return self.truncate_text(base_tweet, 280)

    def truncate_text(self, text, max_length=280):
        """Metni Twitter limiti için kısalt"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    def post_tweet(self, content):
        """Tweet gönder"""
        if self.test_mode:
            print(f"🧪 TEST MODE - Tweet içeriği:")
            print(f"📝 Karakter sayısı: {len(content)}")
            print(f"📄 İçerik:\n{content}")
            print("-" * 50)
            return "test_tweet_id_123"

        try:
            response = self.client.create_tweet(text=content)
            if response.data:
                print(f"✅ Tweet başarıyla gönderildi: {response.data['id']}")
                return response.data['id']
            else:
                print("❌ Tweet gönderilemedi")
                return None
        except Exception as e:
            print(f"❌ Twitter API hatası: {str(e)}")
            return None

    def share_latest_posts(self, max_posts=3):
        """Son blog yazılarını paylaş"""
        posts = self.get_latest_blog_posts(days_back=2)

        if not posts:
            print("🔍 Son 2 günde yeni post bulunamadı")
            return False

        shared_count = 0

        for post in posts[:max_posts]:
            post_id = post.get('id', '')

            # Daha önce paylaşılmış mı kontrol et
            if any(shared['post_id'] == post_id for shared in self.shared_posts):
                print(f"🔄 Post zaten paylaşılmış: {post['title'][:50]}...")
                continue

            # Tweet içeriği oluştur ve gönder
            tweet_content = self.create_tweet_content(post)
            tweet_id = self.post_tweet(tweet_content)

            if tweet_id:
                # Paylaşılan postlara ekle
                self.shared_posts.append({
                    'post_id': post_id,
                    'tweet_id': tweet_id,
                    'shared_at': datetime.now().isoformat(),
                    'title': post['title'],
                    'category': post['category'],
                    'url': post['url']
                })
                self.save_shared_posts()
                shared_count += 1
                print(f"📤 Paylaşıldı: {post['title'][:50]}...")

                # Rate limit koruması
                if not self.test_mode:
                    time.sleep(10)
            else:
                print(f"❌ Paylaşılamadı: {post['title'][:50]}...")

        print(f"🎉 Toplam {shared_count} post paylaşıldı")
        return shared_count > 0

    def share_daily_summary(self):
        """Günlük özet tweet'i"""
        today = datetime.now().strftime("%d %B %Y")

        summary_tweets = [
            f"""🌌 MindVerse Daily - {today}

📚 Bugünkü konularımız:
🧬 Sağlık ve yaşam
🧠 Psikoloji araştırmaları
📜 Tarih ve kültür
🚀 Uzay keşifleri
💬 İlham verici içerikler

👉 mindversedaily.com

#MindVerseDaily #Bilim #Sağlık""",

            f"""🌟 {today} - Yeni Gün, Yeni Keşifler!

🔬 Bilim dünyasından güncel haberler
💡 Zihin açan psikoloji yazıları
🌍 Geçmişten geleceğe yolculuk
❤️ İnsan ilişkileri üzerine rehberler

📖 mindversedaily.com'da sizleri bekliyor!

#MindVerse #Güncel""",

            f"""☀️ Günaydın! {today}

🧬 Sağlık • 🧠 Psikoloji • 📜 Tarih • 🚀 Uzay • 💬 Motivasyon

Her gün yeni bilgiler, keşifler ve ilham verici içeriklerle dolu!

🌐 mindversedaily.com

#MindVerseDaily #BilgiDolu"""
        ]

        # Rastgele bir özet tweet seç
        tweet_content = random.choice(summary_tweets)
        return self.post_tweet(tweet_content)

def main():
    """Ana fonksiyon"""
    # Test mode için environment variable kontrol et
    test_mode = os.getenv('TWITTER_TEST_MODE', 'false').lower() == 'true'

    bot = TwitterBot(test_mode=test_mode)

    print("🐦 MindVerse Daily Twitter Bot başlatılıyor...")
    if test_mode:
        print("🧪 TEST MODE - Gerçek tweet atılmayacak")

    # Önce son postları paylaş
    shared = bot.share_latest_posts(max_posts=2)

    # Eğer yeni post yoksa günlük özet paylaş
    if not shared:
        print("📰 Yeni post bulunamadı, günlük özet paylaşılıyor...")
        bot.share_daily_summary()

    print("✨ Twitter bot işlemi tamamlandı!")

if __name__ == "__main__":
    main()
