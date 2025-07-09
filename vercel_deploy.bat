@echo off
setlocal enabledelayedexpansion
echo.
echo ========================================
echo   MindVerse - Vercel Auto Deploy
echo ========================================
echo.

echo Starting production deployment...
echo.

:: Change to project directory
cd /d "c:\Users\Jacob\MindVerse\mindverse_blog\public\mindverse_new"

:: Check git status
echo Checking git status...
git status --porcelain > temp_status.txt
set /p git_changes=<temp_status.txt
del temp_status.txt

if "%git_changes%"=="" (
    echo No changes detected, skipping deployment
    goto :end
)

:: Run build
echo Building project...
call npm run build
if errorlevel 1 (
    echo Build failed!
    goto :error
)

:: Add changes
echo Adding changes to git...
git add .
if errorlevel 1 (
    echo Git add failed!
    goto :error
)

:: Create commit message
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (
    set mydate=%%c-%%a-%%b
)
for /f "tokens=1-2 delims=/:" %%a in ("%TIME%") do (
    set mytime=%%a-%%b
)
set commit_msg=Auto-deploy: !mydate! !mytime! [production]

:: Commit changes
echo Committing changes...
git commit -m "!commit_msg!"
if errorlevel 1 (
    echo Nothing new to commit
)

:: Push to trigger deployment
echo Pushing to master (triggers production deploy)...
git push origin master
if errorlevel 1 (
    echo Git push failed!
    goto :error
)

echo.
echo Production deployment triggered successfully!
echo Live site: https://mindverse-new.vercel.app
echo Deployment will be live in 2-3 minutes
echo.
goto :end

:error
echo.
echo Deployment failed!
echo.
pause
exit /b 1

:end
echo.
echo Press any key to continue...
pause > nul
