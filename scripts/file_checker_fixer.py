#!/usr/bin/env python3
"""
Problematic Files Detector and Fixer
"""

import os
import re
import yaml
from pathlib import Path

def check_and_fix_file(file_path):
    """Check and fix a specific markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has proper frontmatter structure
        if not content.startswith('---'):
            return False, "No frontmatter"

        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "Incomplete frontmatter"

        frontmatter = parts[1].strip()
        markdown_content = parts[2].strip()

        # Try to parse frontmatter
        try:
            data = yaml.safe_load(frontmatter)

            # Check required fields
            if not data or not isinstance(data, dict):
                return False, "Invalid frontmatter data"

            if 'title' not in data or not data['title']:
                return False, "Missing title"

            if 'description' not in data or not data['description']:
                return False, "Missing description"

            if 'pubDate' not in data or not data['pubDate']:
                return False, "Missing pubDate"

            if 'category' not in data or not data['category']:
                return False, "Missing category"

            return True, "OK"

        except yaml.YAMLError as e:
            # Fix the YAML error
            filename = file_path.name

            # Extract title
            title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', frontmatter)
            if title_match:
                title = title_match.group(1).strip()
                # Clean up title
                title = re.sub(r'"[^"]*$', '', title)  # Remove incomplete quotes
                title = title.strip('"').strip("'").strip()
            else:
                # Generate from filename
                title = filename.replace('.tr.md', '').replace('.md', '')
                title = title.split('-', 3)[-1] if len(title.split('-')) > 3 else title
                title = title.replace('-', ' ').title()

            # Extract category from path
            category = file_path.parent.name

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
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True, f"Fixed YAML error: {str(e)[:50]}..."

    except Exception as e:
        return False, f"File error: {str(e)}"

def scan_all_files():
    """Scan all markdown files and fix problems"""
    content_dir = Path("src/content/blog")
    results = {
        'ok': [],
        'fixed': [],
        'errors': []
    }

    for md_file in content_dir.rglob("*.md"):
        success, message = check_and_fix_file(md_file)

        if success:
            if "Fixed" in message:
                results['fixed'].append({'file': str(md_file), 'message': message})
            else:
                results['ok'].append(str(md_file))
        else:
            results['errors'].append({'file': str(md_file), 'error': message})

    return results

def main():
    print("🔍 Problematic Files Detector and Fixer başlatılıyor...")

    results = scan_all_files()

    print(f"\n📊 Sonuçlar:")
    print(f"✅ Sorunsuz dosyalar: {len(results['ok'])}")
    print(f"🔧 Düzeltilen dosyalar: {len(results['fixed'])}")
    print(f"❌ Hata veren dosyalar: {len(results['errors'])}")

    if results['fixed']:
        print(f"\n🔧 Düzeltilen dosyalar:")
        for fix in results['fixed'][:10]:
            print(f"   📁 {fix['file']}")
            print(f"      🔄 {fix['message']}")
        if len(results['fixed']) > 10:
            print(f"   ... ve {len(results['fixed']) - 10} dosya daha")

    if results['errors']:
        print(f"\n❌ Hala hata veren dosyalar:")
        for error in results['errors'][:5]:
            print(f"   📁 {error['file']}")
            print(f"      ❌ {error['error']}")
        if len(results['errors']) > 5:
            print(f"   ... ve {len(results['errors']) - 5} dosya daha")

    return len(results['fixed'])

if __name__ == "__main__":
    fixed_count = main()
    print(f"\n🏁 Toplam {fixed_count} dosya düzeltildi.")
