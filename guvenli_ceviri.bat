@echo off
chcp 65001 > nul
echo.
echo 🛡️  API-SAFE GROQ ÇEVİRİCİ
echo ============================
echo.
echo Bu sistem API limitlerini önemseyerek çeviri yapar:
echo - Her API çağrısı arası 8 saniye bekler
echo - Hata durumunda akıllı retry yapar
echo - Maksimum 3 makale çevirir (limit için)
echo.

cd /d "%~dp0"

echo 🔍 Groq API bağlantısı kontrol ediliyor...
python -c "from scripts.groq_client import generate_content; print('✅ Groq API hazır')" 2>nul
if errorlevel 1 (
    echo ❌ Groq API sorunu! GROQ_API_KEY kontrol edin.
    pause
    exit /b 1
)

echo.
echo 📝 API-safe çeviri başlıyor...
echo ⏱️  Her makale arası ~15-20 saniye sürecek
echo.

python scripts/safe_groq_translator.py --days 3 --max 3

echo.
echo ✅ API-safe çeviri tamamlandı!
echo.
echo 📂 Çevrilen dosyalar: src/content/blog/ klasöründe .tr.md uzantılı
echo ⚠️  API limitlerine saygı gösterildi
echo.
pause
