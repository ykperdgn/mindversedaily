@echo off
chcp 65001 > nul
echo.
echo 🧠 AKILLI TÜRKÇE ÇEVİRMEN
echo ===========================
echo.
echo Her makale için benzersiz başlık oluşturur
echo İngilizce kelimeleri tamamen temizler
echo.

cd /d "%~dp0"

echo 🔍 Ollama kontrol ediliyor...
curl -s http://localhost:11434/api/version > nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama çalışmıyor! Lütfen başlatın.
    pause
    exit /b 1
)

echo ✅ Ollama çalışıyor
echo.

echo 📝 Akıllı çeviri başlıyor...
echo.

python scripts/smart_translator.py

echo.
echo ✅ Çeviri tamamlandı!
echo.
echo 📂 Çevrilen dosyalar: src/content/blog/ klasöründe .tr.md uzantılı
echo.
pause
