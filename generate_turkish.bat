@echo off
REM Quick Turkish Content Generation
echo 🇹🇷 Generating Turkish content with Ollama API...
python scripts/unified_content_generator.py --mode manual --language tr --categories %* --count 1
echo.
echo ✅ Turkish content generation completed!
pause
