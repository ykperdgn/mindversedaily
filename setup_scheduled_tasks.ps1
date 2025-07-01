# MindVerse Scheduled Tasks Setup
Write-Host "Setting up Windows Scheduled Tasks for MindVerse..." -ForegroundColor Green

$scriptPath = $PSScriptRoot
$pythonPath = (Get-Command python).Source

# Task 1: Daily Content Creation (9 AM, 3 PM, 9 PM)
$action1 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\master_automation.py content"
$trigger1_1 = New-ScheduledTaskTrigger -Daily -At "09:00"
$trigger1_2 = New-ScheduledTaskTrigger -Daily -At "15:00"
$trigger1_3 = New-ScheduledTaskTrigger -Daily -At "21:00"
$principal1 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "MindVerse-ContentCreation" -Action $action1 -Trigger $trigger1_1,$trigger1_2,$trigger1_3 -Principal $principal1 -Settings $settings1 -Force

# Task 2: Performance Monitoring (every 5 minutes)
$action2 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\performance_monitor.py check"
$trigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$principal2 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "MindVerse-PerformanceMonitoring" -Action $action2 -Trigger $trigger2 -Principal $principal2 -Settings $settings2 -Force

# Task 3: Quality Control (daily at 2 AM)
$action3 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\quality_control.py both"
$trigger3 = New-ScheduledTaskTrigger -Daily -At "02:00"
$principal3 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings3 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "MindVerse-QualityControl" -Action $action3 -Trigger $trigger3 -Principal $principal3 -Settings $settings3 -Force

# Task 4: Weekly Maintenance (Sundays at 3 AM)
$action4 = New-ScheduledTaskAction -Execute $pythonPath -Argument "$scriptPath\scripts\master_automation.py maintenance"
$trigger4 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "03:00"
$principal4 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings4 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "MindVerse-WeeklyMaintenance" -Action $action4 -Trigger $trigger4 -Principal $principal4 -Settings $settings4 -Force

Write-Host "✅ Scheduled tasks created successfully!" -ForegroundColor Green
Write-Host "Tasks created:" -ForegroundColor Yellow
Write-Host "  - MindVerse-ContentCreation ^(3x daily^)" -ForegroundColor White
Write-Host "  - MindVerse-PerformanceMonitoring ^(every 5 min^)" -ForegroundColor White
Write-Host "  - MindVerse-QualityControl ^(daily 2 AM^)" -ForegroundColor White
Write-Host "  - MindVerse-WeeklyMaintenance ^(Sunday 3 AM^)" -ForegroundColor White
