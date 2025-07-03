@echo off
chcp 65001 > nul
echo.
echo 🔍 DUPLICATE CONTENT DETECTOR
echo ============================
echo.
echo Bu araç duplicate içerikleri tespit eder ve temizler
echo.

cd /d "%~dp0"

echo 📋 Duplicate raporu oluşturuluyor...
python scripts/smart_duplicate_detector.py --report-only

echo.
echo 📊 Rapor tamamlandı!
echo.
pause
