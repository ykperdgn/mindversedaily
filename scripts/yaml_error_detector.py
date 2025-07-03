#!/usr/bin/env python3
"""
YAML Error Detector - Detects and fixes common YAML frontmatter errors
"""

import os
import re
import yaml
from pathlib import Path

def detect_yaml_errors():
    """Detect files with YAML frontmatter errors"""
    content_dir = Path("src/content/blog")
    error_files = []

    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    try:
                        yaml.safe_load(frontmatter)
                    except yaml.YAMLError as e:
                        error_files.append({
                            'file': str(md_file),
                            'error': str(e),
                            'frontmatter': frontmatter[:200] + "..." if len(frontmatter) > 200 else frontmatter
                        })

        except Exception as e:
            error_files.append({
                'file': str(md_file),
                'error': f"File read error: {str(e)}",
                'frontmatter': 'N/A'
            })

    return error_files

def fix_duplicate_titles():
    """Fix duplicate titles in frontmatter"""
    content_dir = Path("src/content/blog")
    fixed_files = []

    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for duplicate title pattern
            if 'title: "' in content and content.count('title: "') == 1:
                # Look for pattern like: title: "Text1"Text2"
                title_match = re.search(r'title: "([^"]*)"([^"\n]*)"', content)
                if title_match:
                    # Keep the second (Turkish) title
                    old_title = title_match.group(0)
                    new_title = f'title: "{title_match.group(2).strip()}"'

                    new_content = content.replace(old_title, new_title)

                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    fixed_files.append({
                        'file': str(md_file),
                        'old': old_title,
                        'new': new_title
                    })

        except Exception as e:
            print(f"Error processing {md_file}: {e}")

    return fixed_files

def main():
    print("🔍 YAML Error Detector başlatılıyor...")

    # First, fix duplicate titles
    print("\n1. Duplicate title'ları düzeltiliyor...")
    fixed_files = fix_duplicate_titles()

    if fixed_files:
        print(f"✅ {len(fixed_files)} dosyada duplicate title düzeltildi:")
        for fix in fixed_files:
            print(f"   📁 {fix['file']}")
            print(f"      🔄 {fix['old']} → {fix['new']}")
    else:
        print("   ℹ️ Duplicate title problemi bulunamadı.")

    # Then detect remaining errors
    print("\n2. YAML hatalarını tespit ediliyor...")
    error_files = detect_yaml_errors()

    if error_files:
        print(f"❌ {len(error_files)} dosyada YAML hatası bulundu:")
        for error in error_files:
            print(f"\n📁 {error['file']}")
            print(f"❌ Hata: {error['error']}")
            print(f"📄 Frontmatter preview:")
            print("   " + "\n   ".join(error['frontmatter'].split('\n')[:5]))
    else:
        print("✅ YAML hatası bulunamadı!")

    return len(error_files)

if __name__ == "__main__":
    error_count = main()
    print(f"\n🏁 Toplam {error_count} YAML hatası tespit edildi.")
