#!/usr/bin/env python3
"""
YAML Frontmatter Fixer - Bozuk description alanlarını düzelt
"""

import os
import re
import glob
from pathlib import Path

def fix_yaml_description(file_path):
    """Fix broken YAML description fields"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find problematic description patterns
        patterns = [
            # "Türkçe: "Some text with quotes""
            r'description:\s*"Türkçe:\s*"([^"]+)"[^"]*"',
            # "Türkçe açıklama: "Some text""
            r'description:\s*"Türkçe açıklama:\s*"([^"]+)"[^"]*"',
            # Any description with nested quotes
            r'description:\s*"[^"]*"[^"]*"[^"]*"'
        ]

        original_content = content

        # Pattern 1: Extract clean text from "Türkçe: "text""
        content = re.sub(
            r'description:\s*"Türkçe:\s*"([^"]+)"[^"]*"',
            r'description: "\1"',
            content
        )

        # Pattern 2: Extract clean text from "Türkçe açıklama: "text""
        content = re.sub(
            r'description:\s*"Türkçe açıklama:\s*"([^"]+)"[^"]*"',
            r'description: "\1"',
            content
        )

        # Pattern 3: Fix any remaining nested quotes
        content = re.sub(
            r'description:\s*"([^"]*)"([^"]*)"([^"]*)"',
            r'description: "\1\2\3"',
            content
        )

        # Fallback: Use generic description for very broken ones
        if 'description: "Türkçe' in content:
            content = re.sub(
                r'description:\s*"Türkçe[^"]*"[^"]*"[^"]*',
                'description: "MindVerse Daily\'den güncel bilgiler"',
                content
            )

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Hata: {file_path} - {e}")

    return False

def main():
    print("🔧 YAML Frontmatter Düzeltici")
    print("=" * 40)

    content_dir = Path("src/content/blog")
    fixed_count = 0

    for category_dir in content_dir.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*.tr.md")
            files = glob.glob(pattern)

            for file_path in files:
                if fix_yaml_description(file_path):
                    print(f"✅ Düzeltildi: {os.path.basename(file_path)}")
                    fixed_count += 1

    print(f"\n🎉 {fixed_count} dosya düzeltildi!")

if __name__ == "__main__":
    main()
