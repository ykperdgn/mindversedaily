# MindVerse Otomatik İçerik ve Deployment Sistemi

## 🚀 Kurulum

### 1. Python Dependencies
```bash
pip install -r scripts/requirements.txt
```

### 2. Ollama Kurulumu
```bash
# Ollama'yı indirin: https://ollama.ai
# Llama 3.1 modelini çekin:
ollama pull llama3.1:8b
```

### 3. API Anahtarları (.env dosyası)
```
GNEWS_API_KEY=your_key
GROQ_API_KEY=your_key
PIXABAY_API_KEY=your_key
PEXELS_API_KEY=your_key
NASA_API_KEY=https://images-api.nasa.gov
```

## 🤖 Kullanım

### Ollama İçerik Üretimi
```bash
# Test (1 makale)
python scripts/ollama_content.py test

# Toplu üretim (her kategoriden 5 makale)
python scripts/ollama_content.py bulk

# Günlük üretim (her kategoriden 1 makale)
python scripts/ollama_content.py daily
```

### Otomatik Deployment
```bash
# Tek seferlik: içerik oluştur + deploy et
python scripts/auto_deploy.py run-once

# Scheduler başlat (günlük otomatik)
python scripts/auto_deploy.py schedule

# Sadece içerik oluştur
python scripts/auto_deploy.py content-only

# Sadece deploy et
python scripts/auto_deploy.py deploy-only
```

### Eski Görselleri Güncelleme
```bash
python scripts/fix_old_images.py
```

## ⏰ Otomatik Sistem

### Günlük Otomasyonu
- **Saat 09:00'da** otomatik çalışır
- Her kategoriden **1-3 makale** üretir
- **İngilizce + Türkçe** içerikler
- **15 saniye arayla** API rate limiting
- **Otomatik build** ve deployment
- **Vercel'e push** eder

### API Rotasyonu
- **Groq** ve **Ollama** arasında rastgele seçim
- API limitlerini aşmamak için **akıllı bekleme**
- **Fallback** mekanizması

## 📊 Özellikler

✅ **Otomatik İçerik Üretimi**
- 6 kategori: health, psychology, history, space, quotes, love
- İngilizce + Türkçe çift dil
- SEO uyumlu başlıklar ve açıklamalar

✅ **Görsel Entegrasyonu**
- Pexels, Pixabay, NASA API
- Kategori bazlı anahtar kelimeler
- Duplicate önleme sistemi

✅ **Deployment Otomasyonu**
- Git otomatik commit/push
- Astro build işlemi
- Vercel otomatik deployment
- Hata yönetimi

✅ **AdSense Hazır**
- ads.txt dosyası otomatik eklendi
- Publisher ID: pub-3096725438789562

## 🔧 Konfigürasyon

### Scheduler Ayarları
`auto_deploy.py` dosyasında:
```python
# Günlük saat 09:00
schedule.every().day.at("09:00").do(self.daily_automation)

# Alternatif: Her 6 saatte
# schedule.every(6).hours.do(self.daily_automation)
```

### İçerik Miktarı
`ollama_content.py` dosyasında:
```python
# Her kategoriden makale sayısı
articles_per_category = 5

# Günlük seçilen kategori sayısı
selected_categories = random.sample(categories, 3)
```

## 🚀 Canlı Sistem

Sistem şu anda **tamamen hazır** ve aşağıdaki şekilde çalışabilir:

1. **Manuel Test**: `python scripts/auto_deploy.py run-once`
2. **Scheduler Başlat**: `python scripts/auto_deploy.py schedule`
3. **Background Service** olarak Windows'ta çalıştırabilirsiniz

Her gün otomatik olarak:
- ✅ Yeni içerikler üretilir
- ✅ Görseller API'den çekilir
- ✅ Build işlemi yapılır
- ✅ Vercel'e deployment yapılır
- ✅ Site güncel tutulur
