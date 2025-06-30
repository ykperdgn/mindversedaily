# MindVerse Astro Blog

Modern, minimalist ve hızlı bir blog/news sitesi. Popsci.com tarzı küçük grid, SEO uyumlu, örnek içerikli ve Vercel deploy uyumlu.

## Özellikler
- Astro tabanlı, TypeScript desteği
- Kategoriler: science, health, business, world
- Modern grid/kart ve sade logo
- SEO dosyaları (robots.txt, sitemap.xml)
- Vercel ile kolay deploy

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
