@echo off
echo 🇺🇸 GROQ ENGLISH CONTENT GENERATOR
echo ================================
echo.

echo Available categories: health, psychology, history, space, quotes, love
echo.

set /p categories="Enter categories (space-separated) or press Enter for all: "
set /p count="Enter number of articles per category (default 5): "

if "%count%"=="" set count=5

echo.
echo 📝 Generating %count% English articles per category using Groq API...
echo.

if "%categories%"=="" (
    python scripts/groq_english_generator.py --count %count%
) else (
    python scripts/groq_english_generator.py --categories %categories% --count %count%
)

echo.
echo ✅ English content generation completed!
pause
