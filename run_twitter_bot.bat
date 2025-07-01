@echo off
echo 🐦 MindVerse Daily Twitter Bot - Manuel Çalıştırma
echo.

:: Önce test modunda çalıştır
echo 🧪 Test modunda çalıştırılıyor...
set TWITTER_TEST_MODE=true
python scripts\twitter_bot.py

echo.
echo ✅ Test tamamlandı!
echo.

:: Production modda çalıştırmak için onay al
set /p "confirm=🔴 GERÇEK tweet atmak istiyor musunuz? (test/real): "

if /i "%confirm%"=="real" (
    echo 🚀 Production modda çalıştırılıyor...
    set TWITTER_TEST_MODE=false
    python scripts\twitter_bot.py
) else (
    echo ✅ Sadece test modunda çalıştırıldı.
)

echo.
echo 🎉 İşlem tamamlandı!
pause
