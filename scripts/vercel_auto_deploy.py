#!/usr/bin/env python3
"""
Vercel Production Auto-Deploy Script
Bu script Vercel API'sini kullanarak direkt production deployment yapar
"""

import os
import subprocess
import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file
load_env()

class VercelAutoDeployer:
    def __init__(self):
        self.project_id = "prj_AGaMnVDNwQRriAJoIR6DbhRDgLnA"
        self.org_id = "team_5XQ40Tu4e43isnrwOOCQ7gxC"
        self.vercel_token = os.getenv('VERCEL_TOKEN')

        if not self.vercel_token:
            print("⚠️ VERCEL_TOKEN environment variable not found")
            print("💡 Using git push method for deployment")
            self.use_api = False
        else:
            print(f"✅ VERCEL_TOKEN loaded: {self.vercel_token[:8]}...")
            self.use_api = True

    def run_command(self, command, description):
        """Terminal komutunu çalıştır"""
        print(f"🔄 {description}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {description} completed")
                if result.stdout.strip():
                    print(f"📋 Output: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ {description} failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ {description} error: {e}")
            return False

    def check_git_status(self):
        """Git status kontrolü"""
        result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def deploy_via_git(self):
        """Git push ile deployment"""
        print("\n🔄 Using Git-based deployment method")

        # Check if there are changes
        changes = self.check_git_status()
        if not changes:
            print("⚠️ No changes detected, skipping deployment")
            return True

        # Build first
        if not self.run_command("npm run build", "Building project"):
            return False

        # Git operations
        if not self.run_command("git add .", "Adding changes"):
            return False

        commit_msg = f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M')} [production]"
        if not self.run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
            print("⚠️ No new changes to commit")

        # Push to trigger Vercel deployment
        if not self.run_command("git push origin master", "Pushing to master (triggers production deploy)"):
            return False

        print("🚀 Production deployment triggered via Git!")
        print("📱 Live site: https://mindverse-new.vercel.app")
        return True

    def deploy(self):
        """Ana deployment fonksiyonu"""
        print(f"\n🌟 Starting Vercel Production Auto-Deploy at {datetime.now()}")
        print("=" * 60)

        # Use Git-based deployment (API method can be added later)
        return self.deploy_via_git()

    def status_check(self):
        """Deployment status kontrolü"""
        if not self.use_api:
            print("⚠️ Cannot check detailed status without VERCEL_TOKEN")
            print("🔄 Checking git status instead...")
            changes = self.check_git_status()
            if changes:
                print(f"📊 Uncommitted changes found: {len(changes.split())}")
            else:
                print("✅ Git repository is clean")
            return

        headers = {
            'Authorization': f'Bearer {self.vercel_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'https://api.vercel.com/v6/deployments?projectId={self.project_id}&limit=3',
                headers=headers
            )

            if response.status_code == 200:
                deployments = response.json().get('deployments', [])
                if deployments:
                    print("📊 Recent deployments:")
                    for i, deployment in enumerate(deployments[:3], 1):
                        state = deployment.get('state', 'unknown')
                        url = deployment.get('url', 'N/A')
                        created = deployment.get('createdAt', 'N/A')

                        # Convert timestamp
                        if created != 'N/A':
                            try:
                                created_time = datetime.fromtimestamp(int(created) / 1000)
                                created = created_time.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass

                        status_icon = {
                            'READY': '✅',
                            'ERROR': '❌',
                            'BUILDING': '🔄',
                            'QUEUED': '⏳'
                        }.get(state, '❓')

                        print(f"  {i}. {status_icon} {state}")
                        print(f"     🔗 https://{url}")
                        print(f"     ⏰ {created}")
                        print()

                    # Show latest status prominently
                    latest = deployments[0]
                    latest_state = latest.get('state', 'unknown')
                    if latest_state == 'READY':
                        print(f"🟢 Latest deployment is LIVE: https://mindverse-new.vercel.app")
                    elif latest_state == 'ERROR':
                        print(f"🔴 Latest deployment FAILED!")
                    else:
                        print(f"🟡 Latest deployment is {latest_state}")
                else:
                    print("📊 No deployments found")
            else:
                print(f"❌ Status check failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Status check error: {e}")

if __name__ == "__main__":
    import sys

    deployer = VercelAutoDeployer()

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        deployer.status_check()
    else:
        success = deployer.deploy()
        if success:
            print("\n✅ Deployment completed successfully!")
            # Wait a bit and check status
            time.sleep(5)
            deployer.status_check()
        else:
            print("\n❌ Deployment failed!")
            exit(1)
