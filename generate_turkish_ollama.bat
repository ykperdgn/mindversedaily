@echo off
echo 🇹🇷 TÜRKÇE İÇERİK OLUŞTURUCU (OLLAMA)
echo ====================================
echo.

echo Ollama kullanarak Türkçe içerik oluşturuluyor...
echo.

echo Kategoriler:
echo - health (sağlık)
echo - psychology (psikoloji)
echo - history (tarih)
echo - space (uzay)
echo - quotes (alıntılar)
echo - love (aşk)
echo.

echo 📝 Türkçe içerik oluşturma başlıyor...
echo.

REM Direkt Türkçe content oluştur - bulk_content_generator.py'de option 4 kullan
(
echo 4
) | python scripts/bulk_content_generator.py

echo.
echo ✅ Turkish content generation completed!
pause
