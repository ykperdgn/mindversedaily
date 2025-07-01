"""
Twitter Bot Performance Monitor
Bot'un performansını izler ve raporlar oluşturur.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

class TwitterBotMonitor:
    def __init__(self):
        # Yolları düzelt
        script_dir = Path(__file__).parent
        self.shared_tweets_file = script_dir / "data" / "shared_tweets.json"
        self.logs_dir = script_dir / "logs"
        self.reports_dir = script_dir / "reports"

        # Klasörleri oluştur
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def load_shared_tweets(self):
        """Paylaşılan tweet'leri yükle"""
        try:
            with open(self.shared_tweets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def generate_performance_report(self):
        """Performans raporu oluştur"""
        tweets = self.load_shared_tweets()

        if not tweets:
            print("❌ Henüz paylaşılmış tweet bulunamadı")
            return

        # Tweet verilerini analiz et
        total_tweets = len(tweets)
        today = datetime.now().date()

        # Son 7 günün verileri
        recent_tweets = []
        for tweet in tweets:
            tweet_date = datetime.fromisoformat(tweet['shared_at']).date()
            if (today - tweet_date).days <= 7:
                recent_tweets.append(tweet)

        # Kategori dağılımı
        categories = {}
        for tweet in tweets:
            category = tweet.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        # Rapor oluştur
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_tweets': total_tweets,
            'recent_tweets_7_days': len(recent_tweets),
            'average_per_day': len(recent_tweets) / 7 if recent_tweets else 0,
            'category_distribution': categories,
            'last_tweet': tweets[-1] if tweets else None,
            'performance_metrics': self.calculate_metrics(tweets)
        }

        # Raporu kaydet
        report_file = self.reports_dir / f"twitter_bot_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("📊 Twitter Bot Performans Raporu")
        print("=" * 40)
        print(f"📈 Toplam Tweet: {total_tweets}")
        print(f"📅 Son 7 gün: {len(recent_tweets)} tweet")
        print(f"⚡ Günlük ortalama: {len(recent_tweets) / 7:.1f}")
        print(f"🏷️ En aktif kategori: {max(categories.items(), key=lambda x: x[1])[0] if categories else 'N/A'}")

        if tweets:
            last_tweet_time = datetime.fromisoformat(tweets[-1]['shared_at'])
            print(f"🕐 Son tweet: {last_tweet_time.strftime('%d/%m/%Y %H:%M')}")

        print(f"📄 Rapor kaydedildi: {report_file}")

        return report

    def calculate_metrics(self, tweets):
        """Performans metriklerini hesapla"""
        if not tweets:
            return {}

        # Zaman bazlı analiz
        tweet_times = [datetime.fromisoformat(tweet['shared_at']) for tweet in tweets]

        # Son 24 saat
        last_24h = [t for t in tweet_times if (datetime.now() - t).total_seconds() < 86400]

        # Son 7 gün
        last_7d = [t for t in tweet_times if (datetime.now() - t).days < 7]

        return {
            'tweets_last_24h': len(last_24h),
            'tweets_last_7d': len(last_7d),
            'success_rate': 100.0,  # Başarı oranı (şimdilik %100)
            'avg_tweet_length': self.calculate_avg_tweet_length(tweets),
            'most_active_hour': self.find_most_active_hour(tweet_times)
        }

    def calculate_avg_tweet_length(self, tweets):
        """Ortalama tweet uzunluğunu hesapla"""
        if not tweets:
            return 0

        # Tweet içeriklerini tahmin et (title + description + link + hashtags)
        total_length = 0
        for tweet in tweets:
            title = tweet.get('title', '')
            # Tahmini tweet uzunluğu
            estimated_length = len(title[:80]) + 100  # URL + hashtag + açıklama
            total_length += estimated_length

        return total_length / len(tweets)

    def find_most_active_hour(self, tweet_times):
        """En aktif saati bul"""
        if not tweet_times:
            return 0

        hours = [t.hour for t in tweet_times]
        hour_counts = {}
        for hour in hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        if hour_counts:
            return max(hour_counts.items(), key=lambda x: x[1])[0]
        return 0

    def create_visual_report(self):
        """Görsel rapor oluştur"""
        tweets = self.load_shared_tweets()

        if not tweets:
            print("❌ Görsel rapor için yeterli veri yok")
            return

        # Kategori dağılımı grafiği
        categories = {}
        for tweet in tweets:
            category = tweet.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        if categories:
            plt.figure(figsize=(10, 6))
            plt.bar(categories.keys(), categories.values())
            plt.title('Tweet Kategori Dağılımı')
            plt.xlabel('Kategori')
            plt.ylabel('Tweet Sayısı')
            plt.xticks(rotation=45)
            plt.tight_layout()

            chart_file = self.reports_dir / f"category_distribution_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(chart_file)
            plt.close()

            print(f"📊 Görsel rapor oluşturuldu: {chart_file}")

    def check_bot_health(self):
        """Bot sağlığını kontrol et"""
        tweets = self.load_shared_tweets()

        health_status = {
            'status': 'healthy',
            'last_check': datetime.now().isoformat(),
            'issues': []
        }

        # Son 24 saatte tweet var mı?
        if tweets:
            last_tweet = datetime.fromisoformat(tweets[-1]['shared_at'])
            hours_since_last = (datetime.now() - last_tweet).total_seconds() / 3600

            if hours_since_last > 48:  # 2 günden fazla
                health_status['status'] = 'warning'
                health_status['issues'].append(f"Son tweet {hours_since_last:.1f} saat önce")
        else:
            health_status['status'] = 'error'
            health_status['issues'].append("Hiç tweet paylaşılmamış")

        # Sağlık durumunu kaydet
        health_file = self.logs_dir / "bot_health.json"
        with open(health_file, 'w', encoding='utf-8') as f:
            json.dump(health_status, f, indent=2, ensure_ascii=False)

        # Sonucu göster
        status_emoji = {"healthy": "✅", "warning": "⚠️", "error": "❌"}
        print(f"{status_emoji[health_status['status']]} Bot Durumu: {health_status['status'].upper()}")

        if health_status['issues']:
            print("🔍 Tespit edilen sorunlar:")
            for issue in health_status['issues']:
                print(f"  - {issue}")

        return health_status

def main():
    """Ana fonksiyon"""
    monitor = TwitterBotMonitor()

    print("🔍 Twitter Bot İzleme Sistemi")
    print("=" * 40)

    # Performans raporu
    report = monitor.generate_performance_report()
    print()

    # Sağlık kontrolü
    health = monitor.check_bot_health()
    print()

    # Görsel rapor (opsiyonel)
    try:
        monitor.create_visual_report()
    except ImportError:
        print("📊 Görsel rapor için matplotlib kurulu değil")
    except Exception as e:
        print(f"📊 Görsel rapor oluşturulamadı: {e}")

if __name__ == "__main__":
    main()
