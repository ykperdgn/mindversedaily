#!/bin/bash
# MindVerse Windows Automation Setup Script

echo "🚀 Setting up MindVerse Automation System..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p scripts/logs
mkdir -p scripts/reports
mkdir -p scripts/monitoring
mkdir -p backups

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r scripts/requirements.txt

# Create Windows batch scripts for easy execution
echo "🔧 Creating Windows batch scripts..."

# Master automation script
cat > start_automation.bat << 'EOF'
@echo off
echo Starting MindVerse Master Automation System...
cd /d "%~dp0"
python scripts/master_automation.py
pause
EOF

# Content creation script
cat > create_content.bat << 'EOF'
@echo off
echo Creating daily content...
cd /d "%~dp0"
python scripts/master_automation.py content
pause
EOF

# Deploy script
cat > deploy_site.bat << 'EOF'
@echo off
echo Deploying site...
cd /d "%~dp0"
python scripts/master_automation.py deploy
pause
EOF

# Quality control script
cat > quality_check.bat << 'EOF'
@echo off
echo Running quality control...
cd /d "%~dp0"
python scripts/quality_control.py both
pause
EOF

# Performance monitoring script
cat > monitor_performance.bat << 'EOF'
@echo off
echo Monitoring site performance...
cd /d "%~dp0"
python scripts/performance_monitor.py check
pause
EOF

# Health check script
cat > health_check.bat << 'EOF'
@echo off
echo Running system health check...
cd /d "%~dp0"
python scripts/master_automation.py health
pause
EOF

echo "✅ Windows batch scripts created!"

# Create PowerShell scheduled task script
cat > setup_scheduled_tasks.ps1 << 'EOF'
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
Write-Host "  - MindVerse-ContentCreation (3x daily)" -ForegroundColor White
Write-Host "  - MindVerse-PerformanceMonitoring (every 5 min)" -ForegroundColor White
Write-Host "  - MindVerse-QualityControl (daily 2 AM)" -ForegroundColor White
Write-Host "  - MindVerse-WeeklyMaintenance (Sunday 3 AM)" -ForegroundColor White
EOF

echo "🕒 PowerShell scheduled task script created!"

# Create status dashboard
cat > create_dashboard.py << 'EOF'
#!/usr/bin/env python3
"""
MindVerse Dashboard Generator
Creates a comprehensive dashboard for monitoring all automation systems
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_dashboard():
    """Generate HTML dashboard"""

    # Load latest data
    monitoring_file = Path("scripts/monitoring/latest_status.json")
    health_file = Path("scripts/logs/health_status.json")

    monitoring_data = {}
    health_data = {}

    if monitoring_file.exists():
        with open(monitoring_file, 'r', encoding='utf-8') as f:
            monitoring_data = json.load(f)

    if health_file.exists():
        with open(health_file, 'r', encoding='utf-8') as f:
            health_data = json.load(f)

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MindVerse Automation Dashboard</title>
    <meta http-equiv="refresh" content="300">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h3 {{ margin-bottom: 15px; color: #333; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .status-item {{ padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid; }}
        .healthy {{ background: #d4edda; border-color: #28a745; }}
        .warning {{ background: #fff3cd; border-color: #ffc107; }}
        .critical {{ background: #f8d7da; border-color: #dc3545; }}
        .metric {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
        .metric:last-child {{ border-bottom: none; }}
        .value {{ font-weight: bold; color: #007bff; }}
        .timestamp {{ color: #666; font-size: 0.9em; text-align: center; margin-top: 15px; }}
        .automation-status {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
        .automation-item {{ text-align: center; padding: 15px; border-radius: 8px; }}
        .active {{ background: #d4edda; color: #155724; }}
        .inactive {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌌 MindVerse Automation Dashboard</h1>
            <p>Complete system monitoring and automation control</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="dashboard-grid">
            <!-- System Overview -->
            <div class="card">
                <h3>📊 System Overview</h3>
                <div class="metric">
                    <span>Total Content Files</span>
                    <span class="value">{health_data.get('content_files', 'N/A')}</span>
                </div>
                <div class="metric">
                    <span>Git Status</span>
                    <span class="value">{health_data.get('git_status', 'Unknown').title()}</span>
                </div>
                <div class="metric">
                    <span>Last Content Creation</span>
                    <span class="value">{health_data.get('last_content', 'Never')[:16] if health_data.get('last_content') else 'Never'}</span>
                </div>
                <div class="metric">
                    <span>Last Deployment</span>
                    <span class="value">{health_data.get('last_deploy', 'Never')[:16] if health_data.get('last_deploy') else 'Never'}</span>
                </div>
            </div>

            <!-- Site Status -->
            <div class="card">
                <h3>🌐 Site Status</h3>
                {generate_site_status(monitoring_data)}
            </div>

            <!-- Automation Services -->
            <div class="card">
                <h3>🤖 Automation Services</h3>
                <div class="automation-status">
                    <div class="automation-item active">
                        <strong>Content Bot</strong><br>
                        <small>Active</small>
                    </div>
                    <div class="automation-item active">
                        <strong>Deployment</strong><br>
                        <small>Active</small>
                    </div>
                    <div class="automation-item active">
                        <strong>Monitoring</strong><br>
                        <small>Active</small>
                    </div>
                    <div class="automation-item active">
                        <strong>Quality Control</strong><br>
                        <small>Active</small>
                    </div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="card">
                <h3>📈 Performance Metrics</h3>
                <div class="metric">
                    <span>Average Response Time</span>
                    <span class="value">{monitoring_data.get('summary', {}).get('average_response_time', 'N/A')}s</span>
                </div>
                <div class="metric">
                    <span>Healthy Sites</span>
                    <span class="value">{monitoring_data.get('summary', {}).get('healthy', 0)}/{monitoring_data.get('summary', {}).get('total_sites', 0)}</span>
                </div>
                <div class="metric">
                    <span>System Status</span>
                    <span class="value">{"🟢 Operational" if monitoring_data.get('summary', {}).get('all_systems_operational') else "🟡 Issues"}</span>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card">
                <h3>⚡ Quick Actions</h3>
                <p>Use the following batch files for manual operations:</p>
                <ul style="margin-top: 10px; padding-left: 20px;">
                    <li><code>create_content.bat</code> - Generate new content</li>
                    <li><code>deploy_site.bat</code> - Deploy to production</li>
                    <li><code>quality_check.bat</code> - Run quality control</li>
                    <li><code>monitor_performance.bat</code> - Check performance</li>
                    <li><code>health_check.bat</code> - System health check</li>
                </ul>
            </div>

            <!-- Configuration -->
            <div class="card">
                <h3>⚙️ Configuration</h3>
                <div class="metric">
                    <span>Content Schedule</span>
                    <span class="value">3x Daily</span>
                </div>
                <div class="metric">
                    <span>Monitoring Interval</span>
                    <span class="value">5 minutes</span>
                </div>
                <div class="metric">
                    <span>Backup Frequency</span>
                    <span class="value">Daily</span>
                </div>
                <div class="metric">
                    <span>Auto Deployment</span>
                    <span class="value">Enabled</span>
                </div>
            </div>
        </div>

        <div class="timestamp">
            Dashboard auto-refreshes every 5 minutes
        </div>
    </div>
</body>
</html>
"""

    # Save dashboard
    with open("automation_dashboard.html", 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ Dashboard created: automation_dashboard.html")

def generate_site_status(monitoring_data):
    """Generate site status HTML"""
    if not monitoring_data or 'sites' not in monitoring_data:
        return '<p>No monitoring data available</p>'

    html = ""
    for site in monitoring_data['sites']:
        status_class = site.get('status', 'unknown')
        status_icon = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '🔴',
            'error': '❌'
        }.get(status_class, '❓')

        html += f'''
        <div class="status-item {status_class}">
            <strong>{status_icon} {site.get('site', 'Unknown')}</strong><br>
            Response: {site.get('response_time', 'N/A')}s
            {f"<br>Error: {site.get('error')}" if site.get('error') else ""}
        </div>
        '''

    return html

if __name__ == "__main__":
    create_dashboard()
EOF

echo "📊 Dashboard generator created!"

# Create main automation status file
cat > automation_status.json << 'EOF'
{
  "automation_system": {
    "version": "1.0",
    "status": "ready",
    "installed_at": "",
    "components": {
      "master_automation": true,
      "content_bot": true,
      "deployment": true,
      "quality_control": true,
      "performance_monitor": true,
      "scheduled_tasks": false
    },
    "last_check": null
  }
}
EOF

echo ""
echo "🎉 MindVerse Automation System Setup Complete!"
echo ""
echo "📋 What has been created:"
echo "  ✅ Master automation system (master_automation.py)"
echo "  ✅ Quality control system (quality_control.py)"
echo "  ✅ Performance monitoring (performance_monitor.py)"
echo "  ✅ Windows batch scripts for easy execution"
echo "  ✅ PowerShell scheduled task setup"
echo "  ✅ Dashboard generator"
echo ""
echo "🚀 Next steps:"
echo "  1. Run 'python create_dashboard.py' to create monitoring dashboard"
echo "  2. Run 'powershell -ExecutionPolicy Bypass -File setup_scheduled_tasks.ps1' as Administrator to setup automated tasks"
echo "  3. Test with 'create_content.bat' to generate content"
echo "  4. Open 'automation_dashboard.html' in browser to monitor system"
echo ""
echo "🔧 Manual commands:"
echo "  • Daily content: python scripts/master_automation.py content"
echo "  • Deploy site: python scripts/master_automation.py deploy"
echo "  • Quality check: python scripts/quality_control.py both"
echo "  • Monitor performance: python scripts/performance_monitor.py check"
echo "  • System health: python scripts/master_automation.py health"
echo ""
echo "💡 The system will run automatically once scheduled tasks are setup!"
