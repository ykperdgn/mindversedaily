@echo off
REM MindVerse Manual Content Generator
REM Easy commands for manual content generation

echo.
echo 🚀 MindVerse Manual Content Generator
echo ====================================
echo.
echo Select content type:
echo 1. English content (Groq API)
echo 2. Turkish content (Ollama API)
echo 3. Custom configuration
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" goto english_content
if "%choice%"=="2" goto turkish_content
if "%choice%"=="3" goto custom_content
goto invalid_choice

:english_content
echo.
echo 📝 English Content Generation (Groq API)
echo ========================================
echo.
set /p categories="Categories (space-separated, default: health psychology): "
if "%categories%"=="" set categories=health psychology

set /p count="Articles per category (default: 1): "
if "%count%"=="" set count=1

echo.
echo 🔄 Generating English content...
echo Categories: %categories%
echo Count: %count%
echo.

python scripts/unified_content_generator.py --mode manual --language en --categories %categories% --count %count%
goto end

:turkish_content
echo.
echo 📝 Turkish Content Generation (Ollama API)
echo ==========================================
echo.
set /p categories="Categories (space-separated, default: health psychology): "
if "%categories%"=="" set categories=health psychology

set /p count="Articles per category (default: 1): "
if "%count%"=="" set count=1

echo.
echo 🔄 Generating Turkish content...
echo Categories: %categories%
echo Count: %count%
echo.

python scripts/unified_content_generator.py --mode manual --language tr --categories %categories% --count %count%
goto end

:custom_content
echo.
echo 🔧 Custom Content Generation
echo ============================
echo.
set /p mode="Mode (auto/manual, default: manual): "
if "%mode%"=="" set mode=manual

set /p language="Language (en/tr, default: en): "
if "%language%"=="" set language=en

set /p categories="Categories (space-separated): "
if "%categories%"=="" set categories=health psychology

set /p count="Articles per category (default: 1): "
if "%count%"=="" set count=1

echo.
echo 🔄 Generating custom content...
echo Mode: %mode%
echo Language: %language%
echo Categories: %categories%
echo Count: %count%
echo.

python scripts/unified_content_generator.py --mode %mode% --language %language% --categories %categories% --count %count%
goto end

:invalid_choice
echo.
echo ❌ Invalid choice. Please select 1, 2, or 3.
echo.
goto end

:end
echo.
echo ✅ Content generation completed!
echo.
pause
