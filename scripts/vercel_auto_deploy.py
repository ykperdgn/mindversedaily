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

    def create_deployment_via_api(self):
        """Vercel API ile deployment oluştur"""
        if not self.use_api:
            return False

        headers = {
            'Authorization': f'Bearer {self.vercel_token}',
            'Content-Type': 'application/json'
        }

        # Get latest commit
        result = subprocess.run("git rev-parse HEAD", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to get git commit hash")
            return False

        commit_sha = result.stdout.strip()

        deployment_data = {
            'name': 'mindverse-new',
            'gitSource': {
                'type': 'github',
                'repo': 'jacob-ai-bot/mindverse_blog',
                'ref': 'master',
                'sha': commit_sha
            },
            'projectSettings': {
                'framework': 'astro',
                'buildCommand': 'npm run build',
                'outputDirectory': 'dist',
                'installCommand': 'npm install'
            },
            'target': 'production'
        }

        try:
            response = requests.post(
                f'https://api.vercel.com/v13/deployments',
                headers=headers,
                json=deployment_data
            )

            if response.status_code == 200:
                deployment = response.json()
                print(f"🚀 Production deployment created: {deployment.get('url', 'N/A')}")
                return True
            else:
                print(f"❌ API deployment failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ API deployment error: {e}")
            return False

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

        # Try API method first, fallback to Git
        if self.use_api:
            print("🔄 Attempting deployment via Vercel API...")
            if self.create_deployment_via_api():
                return True
            else:
                print("⚠️ API method failed, falling back to Git method")

        # Git-based deployment
        return self.deploy_via_git()

    def status_check(self):
        """Deployment status kontrolü"""
        if not self.use_api:
            print("⚠️ Cannot check status without VERCEL_TOKEN")
            return

        headers = {
            'Authorization': f'Bearer {self.vercel_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(
                f'https://api.vercel.com/v6/deployments?projectId={self.project_id}&limit=5',
                headers=headers
            )

            if response.status_code == 200:
                deployments = response.json().get('deployments', [])
                if deployments:
                    latest = deployments[0]
                    print(f"📊 Latest deployment status: {latest.get('state', 'unknown')}")
                    print(f"🔗 URL: {latest.get('url', 'N/A')}")
                    print(f"⏰ Created: {latest.get('createdAt', 'N/A')}")
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
            time.sleep(10)
            deployer.status_check()
        else:
            print("\n❌ Deployment failed!")
            exit(1)
