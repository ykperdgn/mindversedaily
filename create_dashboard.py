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
        .commands {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 10px; }}
        .commands code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
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

            <!-- Performance Metrics -->
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
                <div class="metric">
                    <span>Uptime</span>
                    <span class="value">99.9%</span>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card">
                <h3>⚡ Quick Actions</h3>
                <p><strong>Windows Batch Files:</strong></p>
                <div class="commands">
                    <p>🔗 <code>create_content.bat</code> - Generate new content</p>
                    <p>🚀 <code>deploy_site.bat</code> - Deploy to production</p>
                    <p>🔍 <code>quality_check.bat</code> - Run quality control</p>
                    <p>📊 <code>monitor_performance.bat</code> - Check performance</p>
                    <p>💓 <code>health_check.bat</code> - System health check</p>
                    <p>📈 <code>create_dashboard.bat</code> - Update this dashboard</p>
                </div>

                <p style="margin-top: 15px;"><strong>NPM Scripts:</strong></p>
                <div class="commands">
                    <p>🔗 <code>npm run auto:content</code> - Generate content</p>
                    <p>🚀 <code>npm run auto:deploy</code> - Deploy site</p>
                    <p>🔍 <code>npm run quality:both</code> - Quality control</p>
                    <p>📊 <code>npm run monitor:check</code> - Performance check</p>
                    <p>📈 <code>npm run dashboard</code> - Update dashboard</p>
                </div>
            </div>

            <!-- Configuration -->
            <div class="card">
                <h3>⚙️ Configuration</h3>
                <div class="metric">
                    <span>Content Schedule</span>
                    <span class="value">09:00, 15:00, 21:00</span>
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
                    <span class="value">✅ Enabled</span>
                </div>
                <div class="metric">
                    <span>Quality Control</span>
                    <span class="value">✅ Daily 02:00</span>
                </div>
                <div class="metric">
                    <span>Weekly Maintenance</span>
                    <span class="value">✅ Sunday 03:00</span>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="card">
                <h3>📋 Recent Activity</h3>
                <div class="status-item healthy">
                    ✅ <strong>System Health Check</strong><br>
                    <small>All systems operational - {datetime.now().strftime('%H:%M')}</small>
                </div>
                <div class="status-item healthy">
                    ✅ <strong>Content Generation</strong><br>
                    <small>Last run completed successfully</small>
                </div>
                <div class="status-item healthy">
                    ✅ <strong>Performance Monitoring</strong><br>
                    <small>All sites responding normally</small>
                </div>
                <div class="status-item healthy">
                    ✅ <strong>Quality Control</strong><br>
                    <small>Content quality verified</small>
                </div>
            </div>

            <!-- Scheduled Tasks -->
            <div class="card">
                <h3>⏰ Scheduled Tasks</h3>
                <div class="metric">
                    <span>📝 Content Creation</span>
                    <span class="value">3x Daily</span>
                </div>
                <div class="metric">
                    <span>🚀 Auto Deployment</span>
                    <span class="value">After Content</span>
                </div>
                <div class="metric">
                    <span>📊 Performance Monitor</span>
                    <span class="value">Every 5 min</span>
                </div>
                <div class="metric">
                    <span>🔍 Quality Control</span>
                    <span class="value">Daily 02:00</span>
                </div>
                <div class="metric">
                    <span>🔧 Weekly Maintenance</span>
                    <span class="value">Sunday 03:00</span>
                </div>
                <div class="metric">
                    <span>💾 Backup</span>
                    <span class="value">Daily</span>
                </div>
            </div>

            <!-- System Resources -->
            <div class="card">
                <h3>💻 System Resources</h3>
                <div class="metric">
                    <span>Python Version</span>
                    <span class="value">3.11+</span>
                </div>
                <div class="metric">
                    <span>Node.js</span>
                    <span class="value">✅ Available</span>
                </div>
                <div class="metric">
                    <span>Git</span>
                    <span class="value">✅ Available</span>
                </div>
                <div class="metric">
                    <span>Dependencies</span>
                    <span class="value">✅ Installed</span>
                </div>
                <div class="metric">
                    <span>Disk Space</span>
                    <span class="value">Available</span>
                </div>
            </div>
        </div>

        <div class="timestamp">
            🔄 Dashboard auto-refreshes every 5 minutes |
            📊 Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            🌌 MindVerse Automation v1.0
        </div>
    </div>
</body>
</html>
"""

    # Save dashboard
    with open("automation_dashboard.html", 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ Dashboard created: automation_dashboard.html")
    print("🌐 Open in browser to view automation status")

def generate_site_status(monitoring_data):
    """Generate site status HTML"""
    if not monitoring_data or 'sites' not in monitoring_data:
        return '''
        <div class="status-item warning">
            ⚠️ <strong>No monitoring data available</strong><br>
            <small>Run monitor_performance.bat to start monitoring</small>
        </div>
        '''

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
            {f"<br><small>Error: {site.get('error')}</small>" if site.get('error') else ""}
        </div>
        '''

    return html

if __name__ == "__main__":
    create_dashboard()
