# MindVerse Astro Blog

Modern, minimalist ve hızlı bir blog/news sitesi. Popsci.com tarzı küçük grid, SEO uyumlu, örnek içerikli ve Vercel deploy uyumlu.

## Özellikler
- Astro tabanlı, TypeScript desteği
- Kategoriler: science, health, business, world
- Modern grid/kart ve sade logo
- SEO dosyaları (robots.txt, sitemap.xml)
- Twitter Bot entegrasyonu (otomatik paylaşım)
- Vercel ile kolay deploy

## Twitter Bot 🐦

Site otomatik olarak yeni blog yazılarını Twitter'da paylaşır.

### Kurulum
1. `.env.example` dosyasını kopyalayarak `.env` oluşturun
2. [Twitter Developer Portal](https://developer.twitter.com/)'dan API anahtarlarınızı alın
3. API anahtarlarını `.env` dosyasına ekleyin

### Manuel Çalıştırma
```bash
# Test modu (gerçek tweet atmaz)
TWITTER_TEST_MODE=true python scripts/twitter_bot.py

# Production modu (gerçek tweet atar)
python scripts/twitter_bot.py

# Windows için hazır script
run_twitter_bot.bat
```

### Otomatik Çalışma
GitHub Actions ile her gün 2 kez otomatik çalışır:
- 09:00 UTC (12:00 TR)
- 15:00 UTC (18:00 TR)

### Tweet Formatı
Bot şu formatta tweet'ler oluşturur:
- Kategori emojisi + başlık
- Kısa açıklama
- Link
- Hashtag'ler (#MindVerseDaily, #kategori)

## Geliştirme
```sh
npm run dev
```

## Build
```sh
npm run build
```

## Deploy
Vercel ile tek tık deploy veya `vercel --prod` komutu ile canlıya alın.

## Vercel & GitHub Entegrasyonu
1. Vercel panelinde “Add New Project” diyerek [ykperdgn/mindversedaily](https://github.com/ykperdgn/mindversedaily) reposunu seçin.
2. Proje kök dizinini `public/mindverse_new` olarak ayarlayın.
3. Build komutu: `npm run build`, output directory: `dist`.
4. Ortam değişkeni olarak `GNEWS_API_KEY` ekleyin.
5. Her push’ta otomatik deploy gerçekleşir.
6. Otomasyon veya içerik botu ile deploy tetiklemek için yeni webhook URL’niz:
   https://api.vercel.com/v1/integrations/deploy/prj_AGaMnVDNwQRriAJoIR6DbhRDgLnA/EClzUbpcNT
