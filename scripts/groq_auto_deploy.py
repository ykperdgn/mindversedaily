#!/usr/bin/env python3
"""
Groq API ile otomatik içerik üretimi ve deployment
Server ortamında kullanılmak üzere tasarlandı
"""

import os
import sys
import time
import random
import subprocess
import schedule
from datetime import datetime
from content_bot import create_articles_for_selected_categories, auto_deploy

class GroqAutoDeployment:
    def __init__(self):
        self.categories = ["health", "psychology", "history", "space", "quotes", "love"]
        self.rate_limit_delay = 15  # 15 saniye API rate limit koruması

    def create_content_with_delay(self, categories_count=None):
        """Rate limit koruması ile içerik oluştur"""
        if categories_count is None:
            categories_count = random.randint(2, 4)  # 2-4 kategori arası

        selected_categories = random.sample(self.categories, categories_count)

        print(f"🎯 Selected categories for today: {selected_categories}")
        print(f"⏱️ Estimated time: {len(selected_categories) * self.rate_limit_delay * 2} seconds")

        for i, category in enumerate(selected_categories):
            if i > 0:
                print(f"⏳ Rate limit delay: {self.rate_limit_delay} seconds...")
                time.sleep(self.rate_limit_delay)

            print(f"\n📝 Creating content for category: {category} ({i+1}/{len(selected_categories)})")

            try:
                # Bu kategori için hem İngilizce hem Türkçe makale oluştur
                create_articles_for_selected_categories([category], auto_deploy_enabled=False)
                print(f"✅ Content created successfully for: {category}")

            except Exception as e:
                print(f"❌ Error creating content for {category}: {e}")
                continue

        print(f"\n🎉 Content creation completed for {len(selected_categories)} categories!")
        return len(selected_categories) > 0

    def deploy_changes(self):
        """Değişiklikleri deploy et"""
        print("\n🚀 Starting deployment process...")

        try:
            # auto_deploy fonksiyonunu kullan
            success = auto_deploy()

            if success:
                print("✅ Deployment completed successfully!")
                return True
            else:
                print("❌ Deployment failed!")
                return False

        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False

    def full_automation(self, categories_count=None):
        """Tam otomatik süreç: İçerik oluştur + Deploy et"""
        print("=" * 60)
        print(f"🤖 GROQ AUTO-DEPLOYMENT STARTED - {datetime.now()}")
        print("=" * 60)

        # 1. İçerik oluştur
        content_success = self.create_content_with_delay(categories_count)

        if not content_success:
            print("❌ No content was created, skipping deployment")
            return False

        # 2. Kısa bekleme
        print("\n⏳ Waiting 30 seconds before deployment...")
        time.sleep(30)

        # 3. Deploy et
        deploy_success = self.deploy_changes()

        print("=" * 60)
        print(f"{'✅ SUCCESS' if deploy_success else '❌ FAILED'} - GROQ AUTO-DEPLOYMENT COMPLETED - {datetime.now()}")
        print("=" * 60)

        return deploy_success

    def start_scheduler(self):
        """Günlük scheduler başlat"""
        print("📅 Starting Groq content automation scheduler...")
        print("⏰ Schedule: Every day at 09:00 AM")
        print("🎯 Will create 2-4 categories of content daily")
        print("🚀 Automatic deployment to Vercel")
        print("-" * 50)

        # Her gün saat 09:00'da çalıştır
        schedule.every().day.at("09:00").do(self.full_automation)

        # Test için: Her 2 saatte bir (geliştirme aşamasında)
        # schedule.every(2).hours.do(lambda: self.full_automation(2))

        print("✅ Scheduler started! Waiting for scheduled time...")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et

def main():
    groq_automation = GroqAutoDeployment()

    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "run-once":
            # Tek seferlik tam otomatik çalıştır
            categories_count = int(sys.argv[2]) if len(sys.argv) > 2 else None
            groq_automation.full_automation(categories_count)

        elif mode == "content-only":
            # Sadece içerik oluştur
            categories_count = int(sys.argv[2]) if len(sys.argv) > 2 else None
            groq_automation.create_content_with_delay(categories_count)

        elif mode == "deploy-only":
            # Sadece deploy et
            groq_automation.deploy_changes()

        elif mode == "schedule":
            # Scheduler'ı başlat
            groq_automation.start_scheduler()

        elif mode.startswith("category:"):
            # Belirli kategoriler için
            categories = mode.split(":")[1].split(",")
            categories = [c.strip() for c in categories if c.strip() in groq_automation.categories]
            if categories:
                print(f"🎯 Creating content for specific categories: {categories}")
                for i, category in enumerate(categories):
                    if i > 0:
                        time.sleep(15)
                    create_articles_for_selected_categories([category], auto_deploy_enabled=False)
                groq_automation.deploy_changes()
            else:
                print("❌ Invalid categories specified")
        else:
            print("❌ Invalid mode specified")
            print_usage()
    else:
        print_usage()

def print_usage():
    print("""
🤖 Groq Auto-Deployment Usage:

python groq_auto_deploy.py [MODE] [OPTIONS]

MODES:
  run-once [count]     - Run full automation once (optionally specify category count)
  content-only [count] - Only create content (optionally specify category count)
  deploy-only          - Only deploy existing changes
  schedule             - Start daily scheduler (runs at 09:00 AM)
  category:cat1,cat2   - Create content for specific categories

EXAMPLES:
  python groq_auto_deploy.py run-once 3
  python groq_auto_deploy.py content-only
  python groq_auto_deploy.py category:health,space
  python groq_auto_deploy.py schedule

CATEGORIES: health, psychology, history, space, quotes, love
""")

if __name__ == "__main__":
    main()
