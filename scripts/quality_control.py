#!/usr/bin/env python3
"""
MindVerse Quality Control System
İçerik kalitesi kontrolü ve otomatik düzeltme sistemi
"""

import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class ContentQualityController:
    def __init__(self):
        self.setup_logging()
        self.quality_rules = self.load_quality_rules()
        self.min_word_count = 300
        self.max_word_count = 2000

    def setup_logging(self):
        """Logging kurulumu"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('QualityControl')

    def load_quality_rules(self):
        """Kalite kurallarını yükle"""
        return {
            "required_fields": ["title", "description", "pubDate", "category", "heroImage"],
            "title_min_length": 20,
            "title_max_length": 100,
            "description_min_length": 50,
            "description_max_length": 200,
            "forbidden_words": ["lorem", "ipsum", "placeholder", "test", "example"],
            "required_sections": ["introduction", "main_content", "conclusion"],
            "image_requirements": {
                "alt_text_required": True,
                "min_width": 800,
                "max_file_size": "2MB"
            }
        }

    def analyze_frontmatter(self, frontmatter: Dict) -> List[str]:
        """Frontmatter analizi"""
        issues = []

        # Required fields check
        for field in self.quality_rules["required_fields"]:
            if field not in frontmatter or not frontmatter[field]:
                issues.append(f"Missing required field: {field}")

        # Title checks
        if "title" in frontmatter:
            title_len = len(frontmatter["title"])
            if title_len < self.quality_rules["title_min_length"]:
                issues.append(f"Title too short: {title_len} < {self.quality_rules['title_min_length']}")
            elif title_len > self.quality_rules["title_max_length"]:
                issues.append(f"Title too long: {title_len} > {self.quality_rules['title_max_length']}")

        # Description checks
        if "description" in frontmatter:
            desc_len = len(frontmatter["description"])
            if desc_len < self.quality_rules["description_min_length"]:
                issues.append(f"Description too short: {desc_len} < {self.quality_rules['description_min_length']}")
            elif desc_len > self.quality_rules["description_max_length"]:
                issues.append(f"Description too long: {desc_len} > {self.quality_rules['description_max_length']}")

        # Forbidden words check
        text_to_check = f"{frontmatter.get('title', '')} {frontmatter.get('description', '')}"
        for word in self.quality_rules["forbidden_words"]:
            if word.lower() in text_to_check.lower():
                issues.append(f"Contains forbidden word: {word}")

        return issues

    def analyze_content(self, content: str) -> List[str]:
        """İçerik analizi"""
        issues = []

        # Word count
        word_count = len(content.split())
        if word_count < self.min_word_count:
            issues.append(f"Content too short: {word_count} < {self.min_word_count} words")
        elif word_count > self.max_word_count:
            issues.append(f"Content too long: {word_count} > {self.max_word_count} words")

        # Structure checks
        if not re.search(r'#{1,3}\s+', content):
            issues.append("No proper headings found")

        # Paragraph length
        paragraphs = content.split('\n\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
        if long_paragraphs:
            issues.append(f"Found {len(long_paragraphs)} very long paragraphs")

        # Link checks
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, url in links:
            if not text.strip():
                issues.append("Empty link text found")
            if not url.startswith(('http://', 'https://', '/')):
                issues.append(f"Invalid URL format: {url}")

        # Image checks
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        for alt_text, img_url in images:
            if not alt_text.strip() and self.quality_rules["image_requirements"]["alt_text_required"]:
                issues.append("Image missing alt text")

        return issues

    def analyze_file(self, file_path: Path) -> Dict:
        """Dosya analizi"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Frontmatter ve content ayırma
            if content.startswith('---\n'):
                parts = content.split('---\n', 2)
                if len(parts) >= 3:
                    frontmatter_text = parts[1]
                    body_content = parts[2]
                else:
                    return {"error": "Invalid frontmatter format"}
            else:
                return {"error": "No frontmatter found"}

            # Frontmatter parsing (basit YAML parser)
            frontmatter = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"\'')

            # Analysis
            frontmatter_issues = self.analyze_frontmatter(frontmatter)
            content_issues = self.analyze_content(body_content)

            # Calculate quality score
            total_issues = len(frontmatter_issues) + len(content_issues)
            quality_score = max(0, 100 - (total_issues * 10))

            return {
                "file": str(file_path),
                "quality_score": quality_score,
                "frontmatter_issues": frontmatter_issues,
                "content_issues": content_issues,
                "word_count": len(body_content.split()),
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": f"Analysis failed: {e}"}

    def fix_common_issues(self, file_path: Path) -> bool:
        """Yaygın sorunları otomatik düzelt"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Fix double spaces
            content = re.sub(r'  +', ' ', content)

            # Fix line endings
            content = re.sub(r'\n{3,}', '\n\n', content)

            # Fix quotation marks
            content = content.replace('"', '"').replace('"', '"')
            content = content.replace(''', "'").replace(''', "'")

            # Fix common typos (Türkçe)
            typo_fixes = {
                'ı': 'ı', 'İ': 'İ', 'ş': 'ş', 'Ş': 'Ş',
                'ğ': 'ğ', 'Ğ': 'Ğ', 'ü': 'ü', 'Ü': 'Ü',
                'ö': 'ö', 'Ö': 'Ö', 'ç': 'ç', 'Ç': 'Ç'
            }

            for wrong, correct in typo_fixes.items():
                content = content.replace(wrong, correct)

            # Save if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"✅ Fixed issues in {file_path.name}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Fix failed for {file_path}: {e}")
            return False

    def scan_content_directory(self, content_dir: Path = None) -> Dict:
        """İçerik dizinini tara"""
        if content_dir is None:
            content_dir = Path("src/content/blog")

        if not content_dir.exists():
            return {"error": "Content directory not found"}

        results = {
            "scanned_at": datetime.now().isoformat(),
            "total_files": 0,
            "analyzed_files": 0,
            "quality_scores": [],
            "files": [],
            "summary": {
                "high_quality": 0,  # 80+ score
                "medium_quality": 0,  # 60-79 score
                "low_quality": 0,  # <60 score
                "errors": 0
            }
        }

        for md_file in content_dir.rglob("*.md"):
            results["total_files"] += 1

            analysis = self.analyze_file(md_file)
            if "error" not in analysis:
                results["analyzed_files"] += 1
                results["files"].append(analysis)

                score = analysis["quality_score"]
                results["quality_scores"].append(score)

                if score >= 80:
                    results["summary"]["high_quality"] += 1
                elif score >= 60:
                    results["summary"]["medium_quality"] += 1
                else:
                    results["summary"]["low_quality"] += 1
            else:
                results["summary"]["errors"] += 1
                self.logger.error(f"❌ {md_file}: {analysis['error']}")

        # Calculate average score
        if results["quality_scores"]:
            results["average_quality"] = sum(results["quality_scores"]) / len(results["quality_scores"])
        else:
            results["average_quality"] = 0

        return results

    def generate_quality_report(self, save_report: bool = True) -> Dict:
        """Kalite raporu oluştur"""
        self.logger.info("🔍 Starting quality analysis...")

        results = self.scan_content_directory()

        if save_report:
            reports_dir = Path("scripts/reports")
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"quality_report_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📊 Quality report saved: {report_file}")

        # Print summary
        print(f"\n📊 QUALITY ANALYSIS SUMMARY")
        print(f"{'='*50}")
        print(f"Total files: {results['total_files']}")
        print(f"Analyzed files: {results['analyzed_files']}")
        print(f"Average quality score: {results.get('average_quality', 0):.1f}/100")
        print(f"\nQuality Distribution:")
        print(f"  🟢 High quality (80+): {results['summary']['high_quality']}")
        print(f"  🟡 Medium quality (60-79): {results['summary']['medium_quality']}")
        print(f"  🔴 Low quality (<60): {results['summary']['low_quality']}")
        print(f"  ❌ Errors: {results['summary']['errors']}")

        return results

    def auto_fix_all(self, min_score: int = 60) -> int:
        """Düşük kaliteli dosyaları otomatik düzelt"""
        self.logger.info("🔧 Starting auto-fix process...")

        results = self.scan_content_directory()
        fixed_count = 0

        for file_analysis in results.get("files", []):
            if file_analysis["quality_score"] < min_score:
                file_path = Path(file_analysis["file"])
                if self.fix_common_issues(file_path):
                    fixed_count += 1

        self.logger.info(f"✅ Auto-fixed {fixed_count} files")
        return fixed_count

def main():
    """Ana fonksiyon"""
    import sys

    controller = ContentQualityController()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "scan":
            controller.generate_quality_report()
        elif command == "fix":
            controller.auto_fix_all()
        elif command == "both":
            controller.generate_quality_report()
            controller.auto_fix_all()
        else:
            print("Usage: python quality_control.py [scan|fix|both]")
    else:
        controller.generate_quality_report()

if __name__ == "__main__":
    main()
