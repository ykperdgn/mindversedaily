@echo off
chcp 65001 > nul
echo.
echo 🇹🇷 TÜRKÇE İÇERİK OLUŞTURUCU
echo ============================
echo.
echo Ollama ile Türkçe içerik oluşturuluyor...
echo Lütfen bekleyin...
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

REM Bulk content generator'ı çalıştır - Seçenek 4 (Sadece Türkçe)
echo 📝 Türkçe içerik oluşturma başlıyor...
echo.
(
echo 4
) | python scripts/bulk_content_generator.py

echo.
echo ✅ Türkçe içerik oluşturma tamamlandı!
echo.
echo 📂 Oluşturulan dosyalar: src/content/blog/ klasöründe .tr.md uzantılı
echo.
pause
