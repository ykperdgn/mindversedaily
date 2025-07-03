@echo off
chcp 65001 > nul
echo.
echo 🌟 GROQ SMART TRANSLATOR
echo =========================
echo.
echo Bu araç Groq ile İngilizce makaleleri Türkçeye çevirir
echo ✅ Duplicate kontrol ile - zaten çevrilmiş makaleler atlanır
echo ✅ API rate limit kontrollü
echo ✅ Kaliteli başlık/açıklama çevirisi
echo.

cd /d "%~dp0"

echo 🔍 Groq API ve duplicate kontrol yapılıyor...
echo.

echo Seçenekler:
echo 1. Son 1 günün makalelerini çevir
echo 2. Son 3 günün makalelerini çevir
echo 3. Son 7 günün makalelerini çevir
echo.

set /p choice="Seçiminizi yapın (1-3): "

echo.
echo 📝 Akıllı çeviri başlıyor...
echo.

if "%choice%"=="1" (
    echo 📅 Son 1 günün çevrilmemiş makaleleri çevriliyor...
    python scripts/groq_translator.py --days 1
) else if "%choice%"=="2" (
    echo 📅 Son 3 günün çevrilmemiş makaleleri çevriliyor...
    python scripts/groq_translator.py --days 3
) else if "%choice%"=="3" (
    echo 📅 Son 7 günün çevrilmemiş makaleleri çevriliyor...
    python scripts/groq_translator.py --days 7
) else (
    echo ❌ Geçersiz seçim! Varsayılan olarak son 1 günün makaleleri çevriliyor...
    python scripts/groq_translator.py --days 1
)

echo.
echo ✅ Groq çeviri tamamlandı!
echo.
echo 💡 Duplicate kontrol için: duplicate_check.bat çalıştırın
echo 📂 Çevrilen makaleler: src/content/blog/ klasöründe .tr.md uzantılı
echo.
pause
