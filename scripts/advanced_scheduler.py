#!/usr/bin/env python3
"""
Gelişmiş Otomatik İçerik ve Deployment Sistemi
- Her kategori için 15 saniye arayla içerik üretir
- Günde 2 kez çalışır: 09:00 ve 21:00
- Her 6 saatte bir alternatif olarak çalışabilir
- Frontmatter hatalarını önler
- Otomatik deployment
"""

import os
import sys
import time
import random
import schedule
import threading
from datetime import datetime
from content_bot import create_articles_for_selected_categories, auto_deploy

class AdvancedContentScheduler:
    def __init__(self):
        # Sabit kategori sırası - her zaman bu sırayla işlenecek
        self.categories = ["health", "psychology", "history", "space", "quotes", "love"]
        self.rate_limit_delay = 15  # 15 saniye kategori arası bekleme
        self.is_running = False

    def create_content_with_staggered_timing(self, categories_count=None):
        """Kategori bazlı aralıklı içerik üretimi"""
        if self.is_running:
            print("⚠️ Content creation already in progress, skipping...")
            return False

        self.is_running = True

        try:
            if categories_count is None:
                categories_count = random.randint(2, 4)  # 2-4 kategori arası

            selected_categories = random.sample(self.categories, categories_count)

            print(f"\n🎯 Daily Content Schedule Started")
            print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🏷️ Selected categories: {selected_categories}")
            print(f"⏱️ Estimated time: {len(selected_categories) * self.rate_limit_delay * 2} seconds")
            print(f"🔄 Rate limit: {self.rate_limit_delay}s between categories")
            print("-" * 50)

            successful_categories = []
            failed_categories = []
            total_duration = 0

            for i, category in enumerate(selected_categories):
                # Kategori arası bekleme (ilk kategori hariç)
                if i > 0:
                    print(f"\n⏳ Inter-category delay: {self.rate_limit_delay} seconds...")
                    print(f"   🎯 Next up: {category} ({i+1}/{len(selected_categories)})")
                    print(f"   📈 Progress so far: {len(successful_categories)} successful, {len(failed_categories)} failed")

                    # Geri sayım (15 saniye)
                    for remaining in range(self.rate_limit_delay, 0, -5):
                        if remaining <= self.rate_limit_delay:
                            print(f"   ⏰ {remaining}s remaining...")
                            time.sleep(5)

                    print(f"   🚀 Starting {category} now!")

                # Kategori işleme
                success, duration = self.create_single_category_content(category, i, len(selected_categories))
                total_duration += duration

                if success:
                    successful_categories.append(category)
                    print(f"   🎉 {category} completed successfully!")
                else:
                    failed_categories.append(category)
                    print(f"   💥 {category} failed!")

                # Progress özeti
                print(f"\n📊 Current Progress:")
                print(f"   ✅ Successful: {len(successful_categories)}/{len(selected_categories)} - {successful_categories}")
                print(f"   ❌ Failed: {len(failed_categories)}/{len(selected_categories)} - {failed_categories}")
                print(f"   ⏱️ Total time elapsed: {total_duration // 60:.0f}m {total_duration % 60:.0f}s")

                if i < len(selected_categories) - 1:  # Son kategori değilse
                    remaining_cats = selected_categories[i+1:]
                    print(f"   📋 Remaining: {' → '.join(remaining_cats)}")

            # Final özet
            print(f"\n🎉 Sequential Content Creation Completed!")
            print(f"=" * 60)
            print(f"📋 Processing order: {' → '.join(selected_categories)}")
            print(f"✅ Successful categories ({len(successful_categories)}): {successful_categories}")
            if failed_categories:
                print(f"❌ Failed categories ({len(failed_categories)}): {failed_categories}")
            print(f"⏱️ Total session duration: {total_duration // 60:.0f}m {total_duration % 60:.0f}s")
            print(f"📊 Success rate: {len(successful_categories)}/{len(selected_categories)} ({len(successful_categories)/len(selected_categories)*100:.1f}%)")

            return len(successful_categories) > 0

        finally:
            self.is_running = False

    def create_single_category_content(self, category, category_index, total_categories):
        """Tek kategori için içerik oluştur ve detaylı takip et"""
        category_start_time = datetime.now()
        print(f"\n📝 Starting content creation for: {category}")
        print(f"   📊 Progress: {category_index + 1}/{total_categories} categories")
        print(f"   ⏰ Started at: {category_start_time.strftime('%H:%M:%S')}")
        print(f"   🔄 Expected duration: ~40-60 seconds (EN + TR articles)")

        try:
            # Bu kategori için hem İngilizce hem Türkçe makale oluştur
            print(f"   🇬🇧 Creating English article for {category}...")
            create_articles_for_selected_categories([category], auto_deploy_enabled=False)

            category_end_time = datetime.now()
            duration = (category_end_time - category_start_time).total_seconds()

            print(f"   ✅ Content creation completed for: {category}")
            print(f"   ⏱️ Duration: {duration:.1f} seconds")
            print(f"   🏁 Finished at: {category_end_time.strftime('%H:%M:%S')}")

            return True, duration

        except Exception as e:
            category_end_time = datetime.now()
            duration = (category_end_time - category_start_time).total_seconds()

            print(f"   ❌ Error creating content for {category}: {e}")
            print(f"   ⏱️ Failed after: {duration:.1f} seconds")

            return False, duration

    def create_content_with_staggered_timing(self, categories_count=None):
        """Kategori bazlı sıralı içerik üretimi - Belirli sırayla"""
        if self.is_running:
            print("⚠️ Content creation already in progress, skipping...")
            return False

        self.is_running = True

        try:
            if categories_count is None:
                categories_count = random.randint(2, 4)  # 2-4 kategori arası

            # Kategorileri sabit sıraya göre seç (health → psychology → history → space → quotes → love)
            selected_categories = self.categories[:categories_count]
            total_estimated_time = len(selected_categories) * (60 + self.rate_limit_delay)  # 60s per category + delay

            print(f"\n🎯 Sequential Content Schedule Started")
            print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🏷️ Categories in order: {' → '.join(selected_categories)}")
            print(f"⏱️ Estimated total time: {total_estimated_time // 60}m {total_estimated_time % 60}s")
            print(f"🔄 Inter-category delay: {self.rate_limit_delay}s")
            print(f"📊 Total categories to process: {len(selected_categories)}")
            print("=" * 60)

            successful_categories = []
            failed_categories = []
            total_duration = 0

            for i, category in enumerate(selected_categories):
                # Kategori arası bekleme (ilk kategori hariç)
                if i > 0:
                    print(f"\n⏳ Inter-category delay: {self.rate_limit_delay} seconds...")
                    print(f"   🎯 Next up: {category} ({i+1}/{len(selected_categories)})")
                    print(f"   📈 Progress so far: {len(successful_categories)} successful, {len(failed_categories)} failed")
                    print(f"   📋 Sequence: {' → '.join(selected_categories[:i])} ✅ → [{category}] → {' → '.join(selected_categories[i+1:])}")

                    # Geri sayım (15 saniye)
                    for remaining in range(self.rate_limit_delay, 0, -5):
                        if remaining <= self.rate_limit_delay:
                            print(f"   ⏰ {remaining}s remaining...")
                            time.sleep(5)

                    print(f"   🚀 Starting {category} now!")

                # Kategori işleme
                success, duration = self.create_single_category_content(category, i, len(selected_categories))
                total_duration += duration

                if success:
                    successful_categories.append(category)
                    print(f"   🎉 {category} completed successfully!")
                else:
                    failed_categories.append(category)
                    print(f"   💥 {category} failed!")

                # Progress özeti
                print(f"\n📊 Current Progress:")
                print(f"   ✅ Successful: {len(successful_categories)}/{len(selected_categories)} - {successful_categories}")
                print(f"   ❌ Failed: {len(failed_categories)}/{len(selected_categories)} - {failed_categories}")
                print(f"   ⏱️ Total time elapsed: {total_duration // 60:.0f}m {total_duration % 60:.0f}s")

                if i < len(selected_categories) - 1:  # Son kategori değilse
                    remaining_cats = selected_categories[i+1:]
                    print(f"   📋 Remaining: {' → '.join(remaining_cats)}")

            # Final özet
            print(f"\n🎉 Sequential Content Creation Completed!")
            print(f"=" * 60)
            print(f"📋 Processing order: {' → '.join(selected_categories)}")
            print(f"✅ Successful categories ({len(successful_categories)}): {successful_categories}")
            if failed_categories:
                print(f"❌ Failed categories ({len(failed_categories)}): {failed_categories}")
            print(f"⏱️ Total session duration: {total_duration // 60:.0f}m {total_duration % 60:.0f}s")
            print(f"📊 Success rate: {len(successful_categories)}/{len(selected_categories)} ({len(successful_categories)/len(selected_categories)*100:.1f}%)")

            return len(successful_categories) > 0

        finally:
            self.is_running = False

    def deploy_changes(self):
        """Değişiklikleri deploy et"""
        print(f"\n🚀 Starting deployment process at {datetime.now().strftime('%H:%M:%S')}")

        try:
            success = auto_deploy()

            if success:
                print("✅ Deployment completed successfully!")
                print(f"🌐 Site will be updated on Vercel automatically")
                return True
            else:
                print("❌ Deployment failed!")
                return False

        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False

    def full_daily_cycle(self, categories_count=None):
        """Tam günlük döngü: İçerik oluştur + Deploy et"""
        cycle_start = datetime.now()

        print("=" * 60)
        print(f"🤖 DAILY CONTENT CYCLE STARTED")
        print(f"⏰ Time: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. İçerik oluştur (kategori bazlı aralıklı)
        content_success = self.create_content_with_staggered_timing(categories_count)

        if not content_success:
            print("❌ No content was created, skipping deployment")
            return False

        # 2. Kısa bekleme
        print(f"\n⏳ Waiting 30 seconds before deployment...")
        time.sleep(30)

        # 3. Deploy et
        deploy_success = self.deploy_changes()

        cycle_end = datetime.now()
        duration = cycle_end - cycle_start

        print("=" * 60)
        print(f"{'✅ SUCCESS' if deploy_success else '❌ FAILED'} - DAILY CYCLE COMPLETED")
        print(f"⏱️ Duration: {duration.total_seconds():.0f} seconds")
        print(f"🏁 Finished: {cycle_end.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        return deploy_success

    def start_daily_scheduler(self):
        """Günlük 2 kez scheduler (09:00 ve 21:00)"""
        print("📅 Starting Advanced Sequential Content Scheduler...")
        print("⏰ Schedule Configuration:")
        print("  - 09:00 AM: Morning content creation (3-4 categories)")
        print("  - 09:00 PM: Evening content creation (2-3 categories)")
        print("  - Sequential order: health → psychology → history → space → quotes → love")
        print("  - 15s delay between each completed category")
        print("  - Automatic deployment after all content creation")
        print("  - Frontmatter error protection")
        print("-" * 50)

        # Sabah 09:00 - Daha fazla kategori
        schedule.every().day.at("09:00").do(lambda: self.full_daily_cycle(random.randint(3, 4)))

        # Akşam 21:00 (9 PM) - Daha az kategori
        schedule.every().day.at("21:00").do(lambda: self.full_daily_cycle(random.randint(2, 3)))

        print("✅ Sequential scheduler configured and started!")
        print("📋 Category processing order: health → psychology → history → space → quotes → love")
        print("💤 Waiting for scheduled times...")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et

    def start_frequent_scheduler(self):
        """Her 6 saatte bir scheduler"""
        print("📅 Starting Frequent Content Scheduler...")
        print("⏰ Schedule Configuration:")
        print("  - Every 6 hours: Content creation (2-3 categories)")
        print("  - 15s delay between categories")
        print("  - Automatic deployment")
        print("-" * 50)

        # Her 6 saatte bir
        schedule.every(6).hours.do(lambda: self.full_daily_cycle(random.randint(2, 3)))

        print("✅ Frequent scheduler started!")
        print("💤 Next run in 6 hours...")

        while True:
            schedule.run_pending()
            time.sleep(300)  # Her 5 dakika kontrol et

    def test_single_category(self, category):
        """Tek kategori test"""
        if category not in self.categories:
            print(f"❌ Invalid category: {category}")
            print(f"✅ Valid categories: {', '.join(self.categories)}")
            return False

        print(f"🧪 Testing single category: {category}")

        try:
            create_articles_for_selected_categories([category], auto_deploy_enabled=False)
            print(f"✅ Test successful for category: {category}")
            return True
        except Exception as e:
            print(f"❌ Test failed for category {category}: {e}")
            return False

def main():
    scheduler = AdvancedContentScheduler()

    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "daily":
            # Günlük scheduler (09:00 ve 21:00)
            scheduler.start_daily_scheduler()

        elif mode == "frequent":
            # Her 6 saatte bir
            scheduler.start_frequent_scheduler()

        elif mode == "run-once":
            # Tek seferlik tam döngü
            categories_count = int(sys.argv[2]) if len(sys.argv) > 2 else None
            scheduler.full_daily_cycle(categories_count)

        elif mode == "content-only":
            # Sadece içerik oluştur
            categories_count = int(sys.argv[2]) if len(sys.argv) > 2 else None
            scheduler.create_content_with_staggered_timing(categories_count)

        elif mode == "deploy-only":
            # Sadece deploy et
            scheduler.deploy_changes()

        elif mode.startswith("test:"):
            # Tek kategori test
            category = mode.split(":")[1]
            scheduler.test_single_category(category)

        elif mode.startswith("categories:"):
            # Belirli kategoriler için
            categories = mode.split(":")[1].split(",")
            categories = [c.strip() for c in categories if c.strip() in scheduler.categories]
            if categories:
                print(f"🎯 Creating content for specific categories: {categories}")
                for i, category in enumerate(categories):
                    if i > 0:
                        print(f"⏳ Waiting {scheduler.rate_limit_delay} seconds...")
                        time.sleep(scheduler.rate_limit_delay)
                    create_articles_for_selected_categories([category], auto_deploy_enabled=False)
                scheduler.deploy_changes()
            else:
                print("❌ Invalid categories specified")
        else:
            print("❌ Invalid mode specified")
            print_usage()
    else:
        print_usage()

def print_usage():
    print("""
🤖 Advanced Content Scheduler Usage:

python advanced_scheduler.py [MODE] [OPTIONS]

SCHEDULING MODES:
  daily              - Start daily scheduler (09:00 AM & 09:00 PM)
  frequent           - Start frequent scheduler (every 6 hours)

SINGLE RUN MODES:
  run-once [count]   - Run full cycle once (optional category count)
  content-only [count] - Only create content (optional category count)
  deploy-only        - Only deploy existing changes

TESTING MODES:
  test:category      - Test single category (e.g., test:health)
  categories:cat1,cat2 - Create content for specific categories

EXAMPLES:
  python advanced_scheduler.py daily
  python advanced_scheduler.py frequent
  python advanced_scheduler.py run-once 3
  python advanced_scheduler.py content-only 2
  python advanced_scheduler.py test:space
  python advanced_scheduler.py categories:health,psychology

FEATURES:
  ✅ 15s delay between categories
  ✅ Frontmatter error protection
  ✅ Automatic deployment
  ✅ Multiple scheduling options
  ✅ Progress tracking
  ✅ Error handling

CATEGORIES: health, psychology, history, space, quotes, love
""")

if __name__ == "__main__":
    main()
