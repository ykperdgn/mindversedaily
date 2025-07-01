#!/usr/bin/env python3
"""
MindVerse Master Automation System
Sitenin tamamen otomatik olarak sürdürülmesi için ana kontrol sistemi
"""

import os
import sys
import json
import time
import logging
import schedule
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class MasterAutomationSystem:
    def __init__(self):
        self.setup_logging()
        self.config = self.load_config()
        self.is_running = False
        self.last_content_time = None
        self.last_deploy_time = None

    def setup_logging(self):
        """Gelişmiş logging sistemi kurulumu"""
        log_dir = Path("scripts/logs")
        log_dir.mkdir(exist_ok=True)

        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # Daily rotating log files
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f"mindverse_automation_{today}.log"

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('MasterAutomation')
        self.logger.info("🚀 MindVerse Master Automation System Started")

    def load_config(self):
        """Konfigürasyon yükleme"""
        config_path = Path("scripts/automation_config.json")

        default_config = {
            "content_schedule": {
                "daily_times": ["09:00", "15:00", "21:00"],
                "categories_per_run": [2, 4],
                "rate_limit_seconds": 15
            },
            "deployment": {
                "auto_deploy": True,
                "deploy_after_content": True,
                "deploy_times": ["09:30", "15:30", "21:30"]
            },
            "monitoring": {
                "health_check_interval": 30,
                "max_consecutive_failures": 3,
                "notification_enabled": True
            },
            "backup": {
                "enabled": True,
                "interval_hours": 24,
                "keep_days": 7
            },
            "maintenance": {
                "cleanup_logs": True,
                "cleanup_interval_days": 7,
                "update_dependencies": True
            }
        }

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info("✅ Configuration loaded from file")
                return config
            except Exception as e:
                self.logger.error(f"❌ Config file error: {e}")

        # Save default config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        self.logger.info("📝 Default configuration created")
        return default_config

    def run_command(self, command, description, timeout=300):
        """Güvenli komut çalıştırma"""
        self.logger.info(f"🔄 {description}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )

            if result.returncode == 0:
                self.logger.info(f"✅ {description} completed successfully")
                return True, result.stdout
            else:
                self.logger.error(f"❌ {description} failed: {result.stderr}")
                return False, result.stderr

        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ {description} timed out after {timeout}s")
            return False, "Timeout"
        except Exception as e:
            self.logger.error(f"❌ {description} error: {e}")
            return False, str(e)

    def create_daily_content(self):
        """Günlük içerik üretimi"""
        if self.is_running:
            self.logger.warning("⚠️ Content creation already in progress")
            return False

        self.is_running = True

        try:
            self.logger.info("🌅 Starting daily content creation")

            # Advanced scheduler kullan
            success, output = self.run_command(
                "python scripts/advanced_scheduler.py",
                "Daily content creation",
                timeout=1800  # 30 minutes
            )

            if success:
                self.last_content_time = datetime.now()
                self.logger.info("✅ Daily content creation completed")

                # Auto deploy if enabled
                if self.config["deployment"]["deploy_after_content"]:
                    time.sleep(30)  # Wait a bit before deploying
                    self.deploy_site()

                return True
            else:
                self.logger.error(f"❌ Content creation failed: {output}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Content creation error: {e}")
            return False
        finally:
            self.is_running = False

    def deploy_site(self):
        """Site deployment - Vercel production auto-deploy"""
        try:
            self.logger.info("🚀 Starting Vercel production deployment")

            # Use the new Vercel auto deployer
            from vercel_auto_deploy import VercelAutoDeployer

            deployer = VercelAutoDeployer()
            success = deployer.deploy()

            if success:
                self.last_deploy_time = datetime.now()
                self.logger.info("✅ Vercel production deployment completed successfully")

                # Update monitoring data
                self.update_monitoring_data({
                    'last_deployment': self.last_deploy_time.isoformat(),
                    'deployment_status': 'success',
                    'deployment_method': 'vercel_auto_deploy'
                })

                return True
            else:
                self.logger.error("❌ Vercel production deployment failed")
                return False

        except Exception as e:
            self.logger.error(f"❌ Deployment error: {e}")
            return False

    def update_monitoring_data(self, data):
        """Monitoring verilerini güncelle"""
        try:
            monitoring_dir = Path("scripts/monitoring")
            monitoring_dir.mkdir(exist_ok=True)

            latest_file = monitoring_dir / "latest_status.json"

            # Load existing data or create new
            if latest_file.exists():
                with open(latest_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            else:
                existing_data = {}

            # Update with new data
            existing_data.update(data)
            existing_data['last_update'] = datetime.now().isoformat()

            # Save updated data
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"📊 Monitoring data updated")

        except Exception as e:
            self.logger.error(f"❌ Failed to update monitoring data: {e}")

    def system_health_check(self):
        """Sistem sağlık kontrolü"""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "content_files": 0,
                "disk_space": 0,
                "git_status": "unknown",
                "last_content": self.last_content_time.isoformat() if self.last_content_time else None,
                "last_deploy": self.last_deploy_time.isoformat() if self.last_deploy_time else None
            }

            # Count content files
            content_dir = Path("src/content/blog")
            if content_dir.exists():
                health_status["content_files"] = len(list(content_dir.rglob("*.md")))

            # Check git status
            success, output = self.run_command("git status --porcelain", "Git status check")
            if success:
                health_status["git_status"] = "clean" if not output.strip() else "dirty"

            # Save health status
            health_file = Path("scripts/logs/health_status.json")
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💓 Health check completed - Files: {health_status['content_files']}")
            return health_status

        except Exception as e:
            self.logger.error(f"❌ Health check error: {e}")
            return None

    def cleanup_old_logs(self):
        """Eski log dosyalarını temizle"""
        try:
            log_dir = Path("scripts/logs")
            if not log_dir.exists():
                return

            cutoff_date = datetime.now() - timedelta(days=self.config["maintenance"]["cleanup_interval_days"])
            cleaned_count = 0

            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    cleaned_count += 1

            if cleaned_count > 0:
                self.logger.info(f"🧹 Cleaned {cleaned_count} old log files")

        except Exception as e:
            self.logger.error(f"❌ Log cleanup error: {e}")

    def backup_content(self):
        """İçerik yedekleme"""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"mindverse_content_{timestamp}.tar.gz"

            # Create compressed backup
            success, output = self.run_command(
                f"tar -czf backups/{backup_name} src/content/",
                "Content backup creation"
            )

            if success:
                self.logger.info(f"💾 Content backup created: {backup_name}")

                # Cleanup old backups
                keep_days = self.config["backup"]["keep_days"]
                cutoff_date = datetime.now() - timedelta(days=keep_days)

                for backup_file in backup_dir.glob("mindverse_content_*.tar.gz"):
                    if backup_file.stat().st_mtime < cutoff_date.timestamp():
                        backup_file.unlink()
                        self.logger.info(f"🗑️ Removed old backup: {backup_file.name}")

                return True
            else:
                self.logger.error(f"❌ Backup failed: {output}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Backup error: {e}")
            return False

    def schedule_jobs(self):
        """Zamanlanmış görevleri kur"""
        # Content creation
        for time_str in self.config["content_schedule"]["daily_times"]:
            schedule.every().day.at(time_str).do(self.create_daily_content)
            self.logger.info(f"📅 Scheduled content creation at {time_str}")

        # Deployment
        for time_str in self.config["deployment"]["deploy_times"]:
            schedule.every().day.at(time_str).do(self.deploy_site)
            self.logger.info(f"🚀 Scheduled deployment at {time_str}")

        # Health checks
        schedule.every(self.config["monitoring"]["health_check_interval"]).minutes.do(self.system_health_check)

        # Backup
        if self.config["backup"]["enabled"]:
            schedule.every(self.config["backup"]["interval_hours"]).hours.do(self.backup_content)
            self.logger.info(f"💾 Scheduled backup every {self.config['backup']['interval_hours']} hours")

        # Maintenance
        schedule.every().day.at("02:00").do(self.cleanup_old_logs)
        schedule.every().week.do(self.weekly_maintenance)

        self.logger.info("⏰ All scheduled jobs configured")

    def weekly_maintenance(self):
        """Haftalık bakım işlemleri"""
        try:
            self.logger.info("🔧 Starting weekly maintenance")

            # Update dependencies if enabled
            if self.config["maintenance"]["update_dependencies"]:
                success, output = self.run_command(
                    "pip install -r scripts/requirements.txt --upgrade",
                    "Dependencies update"
                )
                if success:
                    self.logger.info("📦 Dependencies updated")

            # Git cleanup
            self.run_command("git gc --prune=now", "Git cleanup")

            # Generate summary report
            self.generate_weekly_report()

            self.logger.info("✅ Weekly maintenance completed")

        except Exception as e:
            self.logger.error(f"❌ Weekly maintenance error: {e}")

    def generate_weekly_report(self):
        """Haftalık rapor oluştur"""
        try:
            report = {
                "week": datetime.now().strftime("%Y-W%U"),
                "content_files": 0,
                "deployments": 0,
                "health_checks": 0,
                "errors": 0
            }

            # Count content files
            content_dir = Path("src/content/blog")
            if content_dir.exists():
                report["content_files"] = len(list(content_dir.rglob("*.md")))

            # Save report
            reports_dir = Path("scripts/reports")
            reports_dir.mkdir(exist_ok=True)

            report_file = reports_dir / f"weekly_report_{report['week']}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📊 Weekly report generated: {report['week']}")

        except Exception as e:
            self.logger.error(f"❌ Report generation error: {e}")

    def run_forever(self):
        """Ana döngü - sürekli çalıştır"""
        self.logger.info("🔄 Master automation system running...")

        # Initial health check
        self.system_health_check()

        # Schedule all jobs
        self.schedule_jobs()

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("⏹️ Master automation system stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Master automation system error: {e}")

    def run_once(self, task="content"):
        """Tek seferlik görev çalıştır"""
        if task == "content":
            return self.create_daily_content()
        elif task == "deploy":
            return self.deploy_site()
        elif task == "health":
            return self.system_health_check()
        elif task == "backup":
            return self.backup_content()
        elif task == "maintenance":
            return self.weekly_maintenance()
        else:
            self.logger.error(f"❌ Unknown task: {task}")
            return False

def main():
    """Ana fonksiyon"""
    master_system = MasterAutomationSystem()

    if len(sys.argv) > 1:
        task = sys.argv[1]
        success = master_system.run_once(task)
        sys.exit(0 if success else 1)
    else:
        master_system.run_forever()

if __name__ == "__main__":
    main()
