@echo off
REM Quick English Content Generation
echo 🇺🇸 Generating English content with Groq API...
python scripts/unified_content_generator.py --mode manual --language en --categories %* --count 1
echo.
echo ✅ English content generation completed!
pause
