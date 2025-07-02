@echo off
echo.
echo =====================================
echo  MindVerse Bulk Content Generator
echo =====================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required modules are available
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ❌ Required module 'requests' not found
    echo Installing requests...
    pip install requests
)

REM Check if Ollama is running
echo 🔍 Checking if Ollama is running...
curl -s http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama is not running!
    echo.
    echo Please start Ollama first:
    echo   1. Open terminal/command prompt
    echo   2. Run: ollama serve
    echo   3. Wait for "Listening on 127.0.0.1:11434"
    echo   4. Then run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Ollama is running!
echo.

echo 🚀 Starting bulk content generation...
echo 📊 This will create 20 articles per category (120 total)
echo 🌍 Each article will be generated in both English and Turkish
echo ⏱️ Estimated time: 30-45 minutes
echo.

set /p confirm=Continue? (y/n):
if /i not "%confirm%"=="y" (
    echo Cancelled by user
    pause
    exit /b 0
)

echo.
echo 🎯 Starting generation process...
python scripts\bulk_content_generator.py

echo.
echo 🎉 Process completed!
pause
