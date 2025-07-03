@echo off
chcp 65001 > nul
echo.
echo 🇹🇷 BASİT AMA ETKİLİ ÇEVİRMEN
echo ================================
echo.
echo Son İngilizce makaleleri Türkçeye çeviriliyor...
echo Agresif temizleme ile kaliteli sonuçlar!
echo.

cd /d "%~dp0"

REM Ollama kontrolü
echo 🔍 Ollama kontrol ediliyor...
curl -s http://localhost:11434/api/version > nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama çalışmıyor! Lütfen önce Ollama'yı başlatın.
    pause
    exit /b 1
)

echo ✅ Ollama çalışıyor
echo.

REM Basit çevirmeni çalıştır
echo 📝 Çeviri başlıyor...
python scripts/simple_translator.py

echo.
echo ✅ Çeviri tamamlandı!
echo.
echo 📂 Yeni Türkçe dosyalar: src/content/blog/*/*.tr.md
echo.
pause
