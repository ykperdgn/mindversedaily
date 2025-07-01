#!/usr/bin/env python3
"""
MindVerse Performance Monitor
Site performansı ve uptime monitoring sistemi
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class PerformanceMonitor:
    def __init__(self):
        self.setup_logging()
        self.config = self.load_config()

    def setup_logging(self):
        """Logging kurulumu"""
        log_dir = Path("scripts/logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / "performance_monitor.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('PerformanceMonitor')

    def load_config(self):
        """Monitoring konfigürasyonu"""
        return {
            "sites": [
                {
                    "name": "MindVerse Main",
                    "url": "https://mindverse.vercel.app/",
                    "critical": True
                },
                {
                    "name": "MindVerse English",
                    "url": "https://mindverse.vercel.app/en/",
                    "critical": True
                },
                {
                    "name": "MindVerse Horoscope",
                    "url": "https://mindverse.vercel.app/blog/horoscope",
                    "critical": False
                }
            ],
            "thresholds": {
                "response_time_warning": 2.0,  # seconds
                "response_time_critical": 5.0,
                "uptime_warning": 98.0,  # percentage
                "uptime_critical": 95.0
            },
            "check_interval": 300,  # 5 minutes
            "alert_cooldown": 1800,  # 30 minutes
            "retention_days": 30
        }

    def check_site_health(self, site: Dict) -> Dict:
        """Site sağlık kontrolü"""
        result = {
            "site": site["name"],
            "url": site["url"],
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "response_time": None,
            "status_code": None,
            "error": None,
            "details": {}
        }

        try:
            start_time = time.time()

            # HTTP request with timeout
            response = requests.get(
                site["url"],
                timeout=10,
                headers={'User-Agent': 'MindVerse-Monitor/1.0'}
            )

            end_time = time.time()
            response_time = end_time - start_time

            result["response_time"] = round(response_time, 3)
            result["status_code"] = response.status_code

            # Status determination
            if response.status_code == 200:
                if response_time <= self.config["thresholds"]["response_time_warning"]:
                    result["status"] = "healthy"
                elif response_time <= self.config["thresholds"]["response_time_critical"]:
                    result["status"] = "warning"
                else:
                    result["status"] = "critical"
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"

            # Additional checks
            content_length = len(response.content)
            result["details"] = {
                "content_length": content_length,
                "content_type": response.headers.get("content-type", ""),
                "server": response.headers.get("server", ""),
                "has_content": content_length > 1000  # Basic content check
            }

            # Content validation
            if result["status"] == "healthy":
                content = response.text.lower()
                if "mindverse" not in content:
                    result["status"] = "warning"
                    result["error"] = "Missing expected content"

        except requests.Timeout:
            result["status"] = "critical"
            result["error"] = "Timeout"
        except requests.ConnectionError:
            result["status"] = "critical"
            result["error"] = "Connection failed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def monitor_all_sites(self) -> List[Dict]:
        """Tüm siteleri kontrol et"""
        self.logger.info("🔍 Starting site monitoring cycle")

        results = []

        for site in self.config["sites"]:
            self.logger.info(f"Checking {site['name']}...")
            result = self.check_site_health(site)
            results.append(result)

            # Log result
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "🔴",
                "error": "❌",
                "unknown": "❓"
            }

            emoji = status_emoji.get(result["status"], "❓")
            response_time = result["response_time"]
            time_str = f"{response_time:.3f}s" if response_time else "N/A"

            self.logger.info(f"{emoji} {site['name']}: {result['status']} ({time_str})")

            if result["error"]:
                self.logger.warning(f"   Error: {result['error']}")

        return results

    def save_monitoring_data(self, results: List[Dict]):
        """Monitoring verilerini kaydet"""
        data_dir = Path("scripts/monitoring")
        data_dir.mkdir(exist_ok=True)

        # Daily file
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = data_dir / f"monitoring_{today}.json"

        # Load existing data
        if daily_file.exists():
            with open(daily_file, 'r', encoding='utf-8') as f:
                daily_data = json.load(f)
        else:
            daily_data = {"date": today, "checks": []}

        # Add new results
        daily_data["checks"].extend(results)

        # Save updated data
        with open(daily_file, 'w', encoding='utf-8') as f:
            json.dump(daily_data, f, indent=2, ensure_ascii=False)

        # Update latest status
        latest_file = data_dir / "latest_status.json"
        latest_data = {
            "last_check": datetime.now().isoformat(),
            "sites": results,
            "summary": self.calculate_summary(results)
        }

        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(latest_data, f, indent=2, ensure_ascii=False)

    def calculate_summary(self, results: List[Dict]) -> Dict:
        """Özet istatistikler hesapla"""
        summary = {
            "total_sites": len(results),
            "healthy": 0,
            "warning": 0,
            "critical": 0,
            "error": 0,
            "average_response_time": 0,
            "all_systems_operational": True
        }

        response_times = []

        for result in results:
            status = result["status"]
            summary[status] = summary.get(status, 0) + 1

            if result["response_time"]:
                response_times.append(result["response_time"])

            if status in ["critical", "error"]:
                summary["all_systems_operational"] = False

        if response_times:
            summary["average_response_time"] = round(sum(response_times) / len(response_times), 3)

        return summary

    def generate_uptime_report(self, days: int = 7) -> Dict:
        """Uptime raporu oluştur"""
        data_dir = Path("scripts/monitoring")

        if not data_dir.exists():
            return {"error": "No monitoring data found"}

        report = {
            "period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "sites": {}
        }

        # Load data for specified period
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_file = data_dir / f"monitoring_{date}.json"

            if daily_file.exists():
                with open(daily_file, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)

                for check in daily_data.get("checks", []):
                    site_name = check["site"]

                    if site_name not in report["sites"]:
                        report["sites"][site_name] = {
                            "total_checks": 0,
                            "healthy_checks": 0,
                            "uptime_percentage": 0,
                            "avg_response_time": 0,
                            "response_times": []
                        }

                    site_data = report["sites"][site_name]
                    site_data["total_checks"] += 1

                    if check["status"] == "healthy":
                        site_data["healthy_checks"] += 1

                    if check["response_time"]:
                        site_data["response_times"].append(check["response_time"])

        # Calculate percentages
        for site_name, site_data in report["sites"].items():
            if site_data["total_checks"] > 0:
                site_data["uptime_percentage"] = round(
                    (site_data["healthy_checks"] / site_data["total_checks"]) * 100, 2
                )

            if site_data["response_times"]:
                site_data["avg_response_time"] = round(
                    sum(site_data["response_times"]) / len(site_data["response_times"]), 3
                )
                # Remove raw response times from report
                del site_data["response_times"]

        return report

    def check_alerts(self, results: List[Dict]) -> List[Dict]:
        """Alert kontrolü"""
        alerts = []

        for result in results:
            alert = None

            if result["status"] == "critical":
                alert = {
                    "level": "critical",
                    "site": result["site"],
                    "message": f"Site critical: {result.get('error', 'Unknown error')}",
                    "timestamp": result["timestamp"]
                }
            elif result["status"] == "error":
                alert = {
                    "level": "error",
                    "site": result["site"],
                    "message": f"Site error: {result.get('error', 'Unknown error')}",
                    "timestamp": result["timestamp"]
                }
            elif result["status"] == "warning":
                if result["response_time"] and result["response_time"] > self.config["thresholds"]["response_time_warning"]:
                    alert = {
                        "level": "warning",
                        "site": result["site"],
                        "message": f"Slow response time: {result['response_time']:.3f}s",
                        "timestamp": result["timestamp"]
                    }

            if alert:
                alerts.append(alert)
                self.logger.warning(f"🚨 ALERT: {alert['message']}")

        return alerts

    def cleanup_old_data(self):
        """Eski monitoring verilerini temizle"""
        data_dir = Path("scripts/monitoring")

        if not data_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=self.config["retention_days"])
        cleaned_count = 0

        for file in data_dir.glob("monitoring_*.json"):
            file_date_str = file.stem.split("_", 1)[1]
            try:
                file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                if file_date < cutoff_date:
                    file.unlink()
                    cleaned_count += 1
            except ValueError:
                continue

        if cleaned_count > 0:
            self.logger.info(f"🧹 Cleaned {cleaned_count} old monitoring files")

    def run_monitoring_cycle(self):
        """Tek monitoring döngüsü"""
        results = self.monitor_all_sites()
        self.save_monitoring_data(results)
        alerts = self.check_alerts(results)

        # Cleanup old data
        self.cleanup_old_data()

        return results, alerts

    def generate_status_page(self):
        """Basit HTML status sayfası oluştur"""
        try:
            latest_file = Path("scripts/monitoring/latest_status.json")

            if not latest_file.exists():
                self.logger.warning("No monitoring data for status page")
                return

            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MindVerse Status</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .status-item {{ padding: 15px; margin: 10px 0; border-radius: 6px; }}
        .healthy {{ background: #d4edda; border-left: 4px solid #28a745; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .critical {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .summary {{ background: #e7f1ff; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 MindVerse System Status</h1>

        <div class="summary">
            <h3>Overall Status: {"✅ All Systems Operational" if data["summary"]["all_systems_operational"] else "⚠️ Issues Detected"}</h3>
            <p>Last checked: {data["last_check"]}</p>
            <p>Average response time: {data["summary"]["average_response_time"]}s</p>
        </div>

        <h3>Service Status</h3>
"""

            for site in data["sites"]:
                status_class = site["status"]
                status_icon = {"healthy": "✅", "warning": "⚠️", "critical": "🔴", "error": "❌"}.get(status_class, "❓")

                html += f"""
        <div class="status-item {status_class}">
            <strong>{status_icon} {site["site"]}</strong><br>
            Status: {site["status"].title()}<br>
            Response time: {site["response_time"]}s<br>
            {"Error: " + site["error"] + "<br>" if site.get("error") else ""}
            <div class="timestamp">Checked: {site["timestamp"]}</div>
        </div>
"""

            html += """
    </div>
</body>
</html>
"""

            status_file = Path("public/status.html")
            with open(status_file, 'w', encoding='utf-8') as f:
                f.write(html)

            self.logger.info("📄 Status page generated")

        except Exception as e:
            self.logger.error(f"❌ Status page generation failed: {e}")

def main():
    """Ana fonksiyon"""
    import sys

    monitor = PerformanceMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "check":
            results, alerts = monitor.run_monitoring_cycle()
            print(f"Monitored {len(results)} sites, {len(alerts)} alerts")
        elif command == "report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            report = monitor.generate_uptime_report(days)
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif command == "status":
            monitor.generate_status_page()
        else:
            print("Usage: python performance_monitor.py [check|report|status]")
    else:
        # Default: run monitoring cycle
        monitor.run_monitoring_cycle()

if __name__ == "__main__":
    main()
