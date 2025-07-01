@echo off
echo.
echo ========================================
echo   MindVerse - Vercel Deploy Test
echo ========================================
echo.

echo 🧪 Testing Vercel production deployment...
echo.

:: Change to project directory
cd /d "c:\Users\Jacob\MindVerse\mindverse_blog\public\mindverse_new"

echo 📊 Checking git status...
git status --short
echo.

echo 🏗️ Running build test...
call npm run build
if errorlevel 1 (
    echo ❌ Build failed! Cannot deploy.
    goto :error
)
echo ✅ Build successful!
echo.

echo 🚀 Testing Vercel auto-deploy system...
call npm run vercel:deploy
if errorlevel 1 (
    echo ❌ Vercel deployment failed!
    goto :error
) else (
    echo ✅ Vercel deployment initiated successfully!
    echo.
    echo 📱 Your site will be live at: https://mindverse-new.vercel.app
    echo 🕐 Deployment typically takes 2-3 minutes
    echo.
    echo 🔍 Checking deployment status in 10 seconds...
    timeout /t 10 /nobreak >nul
    call npm run vercel:status
)

echo.
echo ✅ Deployment test completed!
echo.
goto :end

:error
echo.
echo ❌ Deployment test failed!
echo.
pause
exit /b 1

:end
echo.
echo Press any key to continue...
pause > nul
