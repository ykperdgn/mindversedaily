# MindVerse Astro Blog

Modern, minimalist ve hızlı bir blog/news sitesi. Popsci.com tarzı küçük grid, SEO uyumlu, örnek içerikli ve Vercel deploy uyumlu.

## Özellikler
- Astro tabanlı, TypeScript desteği
- Kategoriler: science, health, business, world
- Modern grid/kart ve sade logo
- SEO dosyaları (robots.txt, sitemap.xml)
- İki dilli arama fonksiyonu (Türkçe/İngilizce)
- Gerçek zamanlı arama ve filtreleme
- Vercel ile kolay deploy

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
