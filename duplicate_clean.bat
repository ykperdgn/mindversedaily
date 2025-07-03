@echo off
chcp 65001 > nul
echo.
echo 🗑️ DUPLICATE CONTENT CLEANER
echo ============================
echo.
echo ⚠️ Bu araç duplicate içerikleri SİLER!
echo Önce duplicate_check.bat ile kontrol edin
echo.

cd /d "%~dp0"

echo 🔍 Duplicate analiz yapılıyor...
python scripts/smart_duplicate_detector.py

echo.
echo ✅ Temizlik tamamlandı!
echo.
pause
