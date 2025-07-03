# MindVerse Astro Blog

Modern, minimalist ve hızlı bir blog/news sitesi. Popsci.com tarzı küçük grid, SEO uyumlu, örnek içerikli ve Vercel deploy uyumlu.

## Özellikler
- Astro tabanlı, TypeScript desteği
- Kategoriler: science, health, business, world
- Modern grid/kart ve sade logo
- SEO dosyaları (robots.txt, sitemap.xml)
- Twitter Bot entegrasyonu (otomatik paylaşım)
- İki dilli arama fonksiyonu (Türkçe/İngilizce)
- Gerçek zamanlı arama ve filtreleme
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

## Arama Fonksiyonu 🔍

Site, dil özelinde güçlü bir arama sistemi içerir:

### Özellikler
- **Dil bazlı arama**: Türkçe sayfada Türkçe içerik, İngilizce sayfada İngilizce içerik arar
- **Gerçek zamanlı filtreleme**: 300ms gecikme ile hızlı sonuçlar
- **Çoklu alan arama**: Başlık, açıklama ve kategori alanlarında arar
- **Arama terimi vurgulama**: Bulunan terimleri renkli gösterir
- **Mobil uyumlu**: Responsive tasarım
- **API entegrasyonu**: `/api/posts.json` endpoint'i ile dinamik veri

### Kullanım
- Ana sayfadaki arama kutusuna yazmaya başlayın
- Sonuçlar otomatik olarak filtrelenir
- "Temizle" butonu ile aramayı sıfırlayın
- Her dilde kendi içeriğini arar

## İletişim
📧 mindversedaily@gmail.com

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
1. Vercel panelinde "Add New Project" diyerek [ykperdgn/mindversedaily](https://github.com/ykperdgn/mindversedaily) reposunu seçin.
2. Proje kök dizinini `public/mindverse_new` olarak ayarlayın.
3. Build komutu: `npm run build`, output directory: `dist`.
4. Her push'ta otomatik deploy gerçekleşir.
5. Otomasyon veya içerik botu ile deploy tetiklemek için yeni webhook URL'niz:
   https://api.vercel.com/v1/integrations/deploy/prj_AGaMnVDNwQRriAJoIR6DbhRDgLnA/EClzUbpcNT
