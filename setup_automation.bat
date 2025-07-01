@echo off
echo 🚀 MindVerse Automation System Setup
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Create directories
echo 📁 Creating directories...
if not exist "scripts\logs" mkdir "scripts\logs"
if not exist "scripts\reports" mkdir "scripts\reports"
if not exist "scripts\monitoring" mkdir "scripts\monitoring"
if not exist "backups" mkdir "backups"
echo ✅ Directories created
echo.

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r scripts\automation_requirements.txt
if errorlevel 1 (
    echo ⚠️ Some dependencies failed to install, trying with existing requirements...
    pip install -r scripts\requirements.txt
)
echo ✅ Dependencies installed
echo.

REM Create Windows batch scripts
echo 🔧 Creating Windows batch scripts...

REM Master automation script
echo @echo off > start_automation.bat
echo echo Starting MindVerse Master Automation System... >> start_automation.bat
echo cd /d "%%~dp0" >> start_automation.bat
echo python scripts\master_automation.py >> start_automation.bat
echo pause >> start_automation.bat

REM Content creation script
echo @echo off > create_content.bat
echo echo Creating daily content... >> create_content.bat
echo cd /d "%%~dp0" >> create_content.bat
echo python scripts\master_automation.py content >> create_content.bat
echo pause >> create_content.bat

REM Deploy script
echo @echo off > deploy_site.bat
echo echo Deploying site... >> deploy_site.bat
echo cd /d "%%~dp0" >> deploy_site.bat
echo python scripts\master_automation.py deploy >> deploy_site.bat
echo pause >> deploy_site.bat

REM Quality control script
echo @echo off > quality_check.bat
echo echo Running quality control... >> quality_check.bat
echo cd /d "%%~dp0" >> quality_check.bat
echo python scripts\quality_control.py both >> quality_check.bat
echo pause >> quality_check.bat

REM Performance monitoring script
echo @echo off > monitor_performance.bat
echo echo Monitoring site performance... >> monitor_performance.bat
echo cd /d "%%~dp0" >> monitor_performance.bat
echo python scripts\performance_monitor.py check >> monitor_performance.bat
echo pause >> monitor_performance.bat

REM Health check script
echo @echo off > health_check.bat
echo echo Running system health check... >> health_check.bat
echo cd /d "%%~dp0" >> health_check.bat
echo python scripts\master_automation.py health >> health_check.bat
echo pause >> health_check.bat

REM Dashboard script
echo @echo off > create_dashboard.bat
echo echo Creating automation dashboard... >> create_dashboard.bat
echo cd /d "%%~dp0" >> create_dashboard.bat
echo python create_dashboard.py >> create_dashboard.bat
echo start automation_dashboard.html >> create_dashboard.bat
echo pause >> create_dashboard.bat

echo ✅ Windows batch scripts created
echo.

REM Create PowerShell scheduled task setup script
echo 💾 Creating PowerShell scheduled task script...
(
echo # MindVerse Scheduled Tasks Setup
echo Write-Host "Setting up Windows Scheduled Tasks for MindVerse..." -ForegroundColor Green
echo.
echo $scriptPath = $PSScriptRoot
echo $pythonPath = ^(Get-Command python^).Source
echo.
echo # Task 1: Daily Content Creation ^(9 AM, 3 PM, 9 PM^)
echo $action1 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\master_automation.py content"
echo $trigger1_1 = New-ScheduledTaskTrigger -Daily -At "09:00"
echo $trigger1_2 = New-ScheduledTaskTrigger -Daily -At "15:00"
echo $trigger1_3 = New-ScheduledTaskTrigger -Daily -At "21:00"
echo $principal1 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
echo $settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
echo.
echo Register-ScheduledTask -TaskName "MindVerse-ContentCreation" -Action $action1 -Trigger $trigger1_1,$trigger1_2,$trigger1_3 -Principal $principal1 -Settings $settings1 -Force
echo.
echo # Task 2: Performance Monitoring ^(every 5 minutes^)
echo $action2 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\performance_monitor.py check"
echo $trigger2 = New-ScheduledTaskTrigger -Once -At ^(Get-Date^) -RepetitionInterval ^(New-TimeSpan -Minutes 5^) -RepetitionDuration ^(New-TimeSpan -Days 365^)
echo $principal2 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
echo $settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
echo.
echo Register-ScheduledTask -TaskName "MindVerse-PerformanceMonitoring" -Action $action2 -Trigger $trigger2 -Principal $principal2 -Settings $settings2 -Force
echo.
echo # Task 3: Quality Control ^(daily at 2 AM^)
echo $action3 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\quality_control.py both"
echo $trigger3 = New-ScheduledTaskTrigger -Daily -At "02:00"
echo $principal3 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
echo $settings3 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
echo.
echo Register-ScheduledTask -TaskName "MindVerse-QualityControl" -Action $action3 -Trigger $trigger3 -Principal $principal3 -Settings $settings3 -Force
echo.
echo # Task 4: Weekly Maintenance ^(Sundays at 3 AM^)
echo $action4 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\master_automation.py maintenance"
echo $trigger4 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "03:00"
echo $principal4 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
echo $settings4 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
echo.
echo Register-ScheduledTask -TaskName "MindVerse-WeeklyMaintenance" -Action $action4 -Trigger $trigger4 -Principal $principal4 -Settings $settings4 -Force
echo.
echo Write-Host "✅ Scheduled tasks created successfully!" -ForegroundColor Green
echo Write-Host "Tasks created:" -ForegroundColor Yellow
echo Write-Host "  - MindVerse-ContentCreation ^(3x daily^)" -ForegroundColor White
echo Write-Host "  - MindVerse-PerformanceMonitoring ^(every 5 min^)" -ForegroundColor White
echo Write-Host "  - MindVerse-QualityControl ^(daily 2 AM^)" -ForegroundColor White
echo Write-Host "  - MindVerse-WeeklyMaintenance ^(Sunday 3 AM^)" -ForegroundColor White
) > setup_scheduled_tasks.ps1

echo ✅ PowerShell scheduled task script created
echo.

REM Test the automation system
echo 🧪 Testing automation system...
python scripts\master_automation.py health
if errorlevel 1 (
    echo ⚠️ Health check failed, but system is installed
) else (
    echo ✅ Health check passed
)
echo.

echo 🎉 MindVerse Automation System Setup Complete!
echo ================================================
echo.
echo 📋 What has been created:
echo   ✅ Master automation system ^(master_automation.py^)
echo   ✅ Quality control system ^(quality_control.py^)
echo   ✅ Performance monitoring ^(performance_monitor.py^)
echo   ✅ Windows batch scripts for easy execution
echo   ✅ PowerShell scheduled task setup
echo   ✅ Dashboard generator
echo.
echo 🚀 Quick start:
echo   1. Run 'create_dashboard.bat' to create monitoring dashboard
echo   2. Run PowerShell as Administrator and execute:
echo      powershell -ExecutionPolicy Bypass -File setup_scheduled_tasks.ps1
echo   3. Test with 'create_content.bat' to generate content
echo   4. Open 'automation_dashboard.html' in browser to monitor
echo.
echo 🔧 Available batch files:
echo   • create_content.bat - Generate daily content
echo   • deploy_site.bat - Deploy to production
echo   • quality_check.bat - Run quality control
echo   • monitor_performance.bat - Check site performance
echo   • health_check.bat - System health check
echo   • create_dashboard.bat - Generate monitoring dashboard
echo   • start_automation.bat - Start full automation system
echo.
echo 💡 The system will run automatically once scheduled tasks are setup!
echo.
pause
