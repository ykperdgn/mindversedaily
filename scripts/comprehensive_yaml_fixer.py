#!/usr/bin/env python3
"""
Comprehensive YAML Frontmatter Fixer
"""

import os
import re
import yaml
from pathlib import Path

def fix_all_yaml_issues():
    """Fix all YAML frontmatter issues in markdown files"""
    content_dir = Path("src/content/blog")
    fixed_files = []
    error_files = []

    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if file has frontmatter
            if not content.startswith('---'):
                continue

            # Split frontmatter and content
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue

            frontmatter = parts[1].strip()
            markdown_content = parts[2].strip()

            # Check current frontmatter
            try:
                yaml.safe_load(frontmatter)
                continue  # No error, skip
            except yaml.YAMLError:
                pass  # Has error, fix it

            # Extract basic info from filename and content
            filename = md_file.name

            # Extract title from filename or content
            title = ""
            if "title:" in frontmatter:
                title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', frontmatter)
                if title_match:
                    title = title_match.group(1).strip()

            if not title:
                # Try to extract from filename
                title = filename.replace('.tr.md', '').replace('.md', '')
                title = title.split('-', 3)[-1] if len(title.split('-')) > 3 else title
                title = title.replace('-', ' ').title()

            # Extract category from path
            category = md_file.parent.name

            # Extract date from filename
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            pub_date = date_match.group(1) if date_match else "2025-07-02"

            # Create clean frontmatter
            clean_frontmatter = f'''---
title: "{title}"
description: "MindVerse Daily'den güncel bilgiler"
pubDate: {pub_date}
category: {category}
tags: []
image: "/assets/blog-placeholder-1.svg"
---'''

            # Create new content
            new_content = clean_frontmatter + '\n\n' + markdown_content

            # Write back to file
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            fixed_files.append({
                'file': str(md_file),
                'title': title,
                'category': category
            })

        except Exception as e:
            error_files.append({
                'file': str(md_file),
                'error': str(e)
            })

    return fixed_files, error_files

def main():
    print("🔧 Comprehensive YAML Frontmatter Fixer başlatılıyor...")

    fixed_files, error_files = fix_all_yaml_issues()

    if fixed_files:
        print(f"✅ {len(fixed_files)} dosya düzeltildi:")
        for fix in fixed_files[:10]:  # Show first 10
            print(f"   📁 {fix['file']}")
            print(f"      📝 Title: {fix['title']}")
        if len(fixed_files) > 10:
            print(f"   ... ve {len(fixed_files) - 10} dosya daha")
    else:
        print("   ℹ️ Düzeltilecek dosya bulunamadı.")

    if error_files:
        print(f"\n❌ {len(error_files)} dosyada hata:")
        for error in error_files:
            print(f"   📁 {error['file']}: {error['error']}")

    return len(fixed_files)

if __name__ == "__main__":
    fixed_count = main()
    print(f"\n🏁 Toplam {fixed_count} dosya düzeltildi.")
