@echo off
chcp 65001 > nul
echo.
echo 🇬🇧→🇹🇷 İNGİLİZCE MAKALELERİ TÜRKÇEYE ÇEVİR
echo ==========================================
echo.
echo Bu script Groq ile oluşturulan İngilizce makaleleri
echo Ollama ile kaliteli Türkçeye çevirir.
echo.

cd /d "%~dp0"

REM Ollama'nın çalışıp çalışmadığını kontrol et
echo 🔍 Ollama kontrol ediliyor...
curl -s http://localhost:11434/api/version > nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama çalışmıyor! Lütfen önce Ollama'yı başlatın.
    echo.
    echo Ollama'yı başlatmak için:
    echo 1. Terminal aç
    echo 2. "ollama serve" komutunu çalıştır
    echo.
    pause
    exit /b 1
)

echo ✅ Ollama çalışıyor
echo.

echo 📋 Seçenekler:
echo 1. Son 1 günün makalelerini çevir
echo 2. Son 3 günün makalelerini çevir
echo 3. Son 7 günün makalelerini çevir
echo.

set /p choice="Seçiminizi yapın (1-3): "

if "%choice%"=="1" (
    echo.
    echo 📝 Son 1 günün makaleleri çevriliyor...
    python scripts/english_to_turkish_translator.py
) else if "%choice%"=="2" (
    echo.
    echo 📝 Son 3 günün makaleleri çevriliyor...
    (
    echo 3
    ) | python scripts/english_to_turkish_translator.py
) else if "%choice%"=="3" (
    echo.
    echo 📝 Son 7 günün makaleleri çevriliyor...
    (
    echo 7
    ) | python scripts/english_to_turkish_translator.py
) else (
    echo ❌ Geçersiz seçim!
    pause
    exit /b 1
)

echo.
echo ✅ Çeviri işlemi tamamlandı!
echo.
echo 📂 İngilizce makaleler: src/content/blog/*/*.en.md
echo 📂 Türkçe makaleler: src/content/blog/*/*.tr.md
echo.
echo 🌐 Artık sitenizde hem İngilizce hem Türkçe makaleler var!
echo.
pause
