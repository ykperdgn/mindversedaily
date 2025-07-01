# 🔐 GitHub Secrets Kurulum Rehberi

## 1. GitHub Repository Settings'e Git
https://github.com/ykperdgn/mindversedaily/settings/secrets/actions

## 2. Şu Secrets'ları Ekle:

### Twitter API Anahtarları
- **Name:** `TWITTER_API_KEY`
  **Value:** [Twitter Developer Portal'dan alınan API Key]

- **Name:** `TWITTER_API_SECRET`
  **Value:** [Twitter Developer Portal'dan alınan API Key Secret]

- **Name:** `TWITTER_ACCESS_TOKEN`
  **Value:** [Twitter Developer Portal'dan alınan Access Token]

- **Name:** `TWITTER_ACCESS_TOKEN_SECRET`
  **Value:** [Twitter Developer Portal'dan alınan Access Token Secret]

- **Name:** `TWITTER_BEARER_TOKEN`
  **Value:** [Twitter Developer Portal'dan alınan Bearer Token]

## 3. Test Mode Kapatma (Opsiyonel)
Production'da test mode'u kapatmak için:
- **Name:** `TWITTER_TEST_MODE`
  **Value:** `false`

## 4. Workflow'u Test Et
1. Actions sekmesine git: https://github.com/ykperdgn/mindversedaily/actions
2. "🐦 Daily Twitter Bot" workflow'unu seç
3. "Run workflow" butonuna bas
4. Test çalıştırmasını izle

## 5. Otomatik Çalışma Saatleri
Bot şu saatlerde otomatik çalışacak:
- **09:00 UTC** (12:00 Türkiye saati) - Sabah paylaşımı
- **15:00 UTC** (18:00 Türkiye saati) - Öğleden sonra paylaşımı

## 📊 Monitoring
Bot çalıştıktan sonra logs'u kontrol etmek için:
1. Actions sekmesinde çalıştırma detayına tıkla
2. "🐦 Run Twitter Bot" adımının loglarını incele
