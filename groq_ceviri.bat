@echo off
chcp 65001 > nul
echo.
echo 🌟 GROQ İNGİLİZCE-TÜRKÇE ÇEVİRİCİ
echo ================================
echo.
echo Groq API ile yüksek kaliteli çeviri
echo Ollama'dan çok daha iyi sonuçlar!
echo.

cd /d "%~dp0"

echo 🔍 Son makalelerin durumu kontrol ediliyor...
echo.

echo Seçenekler:
echo 1. Son 1 günün makalelerini çevir (5-10 makale)
echo 2. Son 3 günün makalelerini çevir (15-20 makale)
echo 3. Son 7 günün makalelerini çevir (tüm son makaleler)
echo.

set /p choice="Seçiminizi yapın (1-3): "

echo.
echo 🚀 Groq çeviri başlıyor...
echo.

if "%choice%"=="1" (
    echo 📅 Son 1 günün makaleleri çevriliyor...
    python scripts/groq_translator.py --days 1
) else if "%choice%"=="2" (
    echo 📅 Son 3 günün makaleleri çevriliyor...
    python scripts/groq_translator.py --days 3
) else if "%choice%"=="3" (
    echo 📅 Son 7 günün makaleleri çevriliyor...
    python scripts/groq_translator.py --days 7
) else (
    echo ❌ Geçersiz seçim! Varsayılan olarak son 1 günün makaleleri çevriliyor...
    python scripts/groq_translator.py --days 1
)

echo.
echo ✅ Groq çeviri tamamlandı!
echo.
echo 📂 Çevrilen makaleler: src/content/blog/ klasöründe .tr.md uzantılı
echo 🌐 Artık sitenizde hem İngilizce hem Türkçe içerik var!
echo.
pause
