#!/usr/bin/env python3
"""
Otomatik deployment sistemi
"""

import os
import subprocess
import time
import schedule
from datetime import datetime
from ollama_content import OllamaContentGenerator
from groq_client import generate_content
import random

class AutoDeploymentSystem:
    def __init__(self):
        self.ollama_generator = OllamaContentGenerator()
        self.groq_available = True

    def run_command(self, command, description):
        """Terminal komutunu çalıştır"""
        print(f"🔄 {description}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} completed")
                return True
            else:
                print(f"❌ {description} failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ {description} error: {e}")
            return False    def create_daily_content(self):
        """Günlük içerik oluştur"""
        print(f"\n🌅 Daily content creation started at {datetime.now()}")

        # Groq ve Ollama arasında rastgele seç
        use_groq = random.choice([True, False]) and self.groq_available

        if use_groq:
            print("🤖 Using Groq API for content generation")
            try:
                from content_bot import create_articles_for_selected_categories
                # Her gün farklı kategoriler seç (2-3 kategori)
                categories = random.sample(self.ollama_generator.categories, random.randint(2, 3))
                print(f"📝 Creating content for categories: {categories}")

                # 15 saniye aralıklarla kategori başına içerik oluştur
                for i, category in enumerate(categories):
                    if i > 0:  # İlk kategori için bekleme yok
                        print(f"⏳ Waiting 15 seconds before next category...")
                        time.sleep(15)

                    print(f"📝 Creating content for category: {category}")
                    create_articles_for_selected_categories([category], auto_deploy_enabled=False)

                print("✅ Groq content creation completed")
            except Exception as e:
                print(f"❌ Groq failed, falling back to Ollama: {e}")
                use_groq = False

        if not use_groq:
            print("🦙 Using Ollama for content generation")
            # Her gün 2-3 kategori seç
            selected_categories = random.sample(self.ollama_generator.categories, random.randint(2, 3))
            print(f"📝 Creating content for categories: {selected_categories}")

            for category in selected_categories:
                print(f"📝 Creating English content for: {category}")
                self.ollama_generator.create_article(category, "en")
                time.sleep(15)

                print(f"📝 Creating Turkish content for: {category}")
                self.ollama_generator.create_article(category, "tr")
                time.sleep(15)

            print("✅ Ollama content creation completed")    def build_and_deploy(self):
        """Build ve deploy işlemi"""
        print("\n🏗️ Starting build and deployment process")

        # Git status check
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        if not result.stdout.strip():
            print("⚠️ No changes detected, skipping deployment")
            return True

        # Build first to ensure everything is working
        if not self.run_command("npm run build", "Building project"):
            return False

        # Git add
        if not self.run_command("git add .", "Adding new content to git"):
            return False

        # Git commit
        commit_msg = f"Auto-generated content - {datetime.now().strftime('%Y-%m-%d %H:%M')} [skip ci]"
        if not self.run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
            print("⚠️ No changes to commit")
            return True

        # Git push (Vercel otomatik production deploy yapacak)
        if not self.run_command("git push origin master", "Pushing to repository (triggers auto-deploy)"):
            return False

        print("🚀 Production deployment initiated automatically!")
        print("📱 Site will be live at: https://mindverse-new.vercel.app")
        return True

    def daily_automation(self):
        """Günlük tam otomasyonu"""
        print("=" * 60)
        print(f"🤖 DAILY AUTOMATION STARTED - {datetime.now()}")
        print("=" * 60)

        # 1. İçerik oluştur
        self.create_daily_content()

        # 2. Kısa bekleme
        time.sleep(30)

        # 3. Build ve deploy
        self.build_and_deploy()

        print("=" * 60)
        print(f"✅ DAILY AUTOMATION COMPLETED - {datetime.now()}")
        print("=" * 60)

    def start_scheduler(self):
        """Scheduler'ı başlat"""
        print("📅 Starting automated content scheduler...")

        # Her gün saat 09:00'da çalıştır
        schedule.every().day.at("09:00").do(self.daily_automation)

        # Alternatif: Her 6 saatte bir (daha sık içerik)
        # schedule.every(6).hours.do(self.daily_automation)

        print("⏰ Scheduler configured:")
        print("  - Daily content creation at 09:00")
        print("  - Automatic build and deployment")
        print("  - Push to Vercel for live updates")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et

def main():
    automation = AutoDeploymentSystem()

    import sys
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "run-once":
            # Tek seferlik çalıştır
            automation.daily_automation()
        elif mode == "schedule":
            # Scheduler'ı başlat
            automation.start_scheduler()
        elif mode == "content-only":
            # Sadece içerik oluştur
            automation.create_daily_content()
        elif mode == "deploy-only":
            # Sadece deploy et
            automation.build_and_deploy()
    else:
        print("Usage: python auto_deploy.py [run-once|schedule|content-only|deploy-only]")

if __name__ == "__main__":
    main()
