#!/usr/bin/env python3
"""
Frontmatter Fixer - Eksik frontmatter'ları toplu olarak düzeltir
"""

import os
import re
from pathlib import Path

def has_frontmatter(content):
    """Dosyada frontmatter var mı kontrol eder"""
    return content.strip().startswith('---') and content.count('---') >= 2

def extract_title_from_filename(filename):
    """Dosya isminden title çıkarır"""
    # Tarih kısmını çıkar
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
    # .tr.md veya .md uzantısını çıkar
    name = re.sub(r'\.(tr\.)?md$', '', name)
    # Tire ve alt çizgileri boşluğa çevir
    name = name.replace('-', ' ').replace('_', ' ')
    # Kelimelerin ilk harflerini büyük yap
    return name.title()

def extract_category_from_path(filepath):
    """Dosya yolundan kategori çıkarır"""
    path_parts = Path(filepath).parts
    if 'blog' in path_parts:
        blog_index = path_parts.index('blog')
        if blog_index + 1 < len(path_parts):
            category = path_parts[blog_index + 1]
            # Kategori eşleşmeleri
            category_map = {
                'health': 'health',
                'science': 'science',
                'space': 'space',
                'history': 'history',
                'psychology': 'psychology',
                'love': 'love',
                'quotes': 'quotes',
                'business': 'business',
                'world': 'world'
            }
            return category_map.get(category, 'science')
    return 'science'

def create_frontmatter(title, category, is_turkish=False):
    """Frontmatter oluşturur"""
    if is_turkish:
        description = f"MindVerse Daily'de {category} kategorisinde son araştırma ve içgörüler keşfedin."
    else:
        description = f"Discover the latest research and insights in {category} category on MindVerse Daily."

    return f"""---
title: "{title}"
description: "{description}"
pubDate: 2025-07-02
category: {category}
tags: []
image: "/assets/blog-placeholder-1.svg"
---

"""

def fix_missing_frontmatter():
    """Eksik frontmatter'ları düzeltir"""
    content_dir = Path("src/content/blog")
    fixed_files = []

    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Frontmatter var mı kontrol et
            if not has_frontmatter(content):
                filename = md_file.name
                title = extract_title_from_filename(filename)
                category = extract_category_from_path(str(md_file))
                is_turkish = filename.endswith('.tr.md')

                # Yeni frontmatter oluştur
                frontmatter = create_frontmatter(title, category, is_turkish)

                # İçeriği temizle (eğer <!-- filepath: --> varsa kaldır)
                content = re.sub(r'<!-- filepath:.*? -->\s*', '', content)

                # Yeni içerik
                new_content = frontmatter + content

                # Dosyayı güncelle
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                fixed_files.append({
                    'file': str(md_file),
                    'title': title,
                    'category': category,
                    'is_turkish': is_turkish
                })

        except Exception as e:
            print(f"Hata {md_file}: {e}")

    return fixed_files

def fix_broken_frontmatter():
    """Bozuk frontmatter'ları düzeltir"""
    content_dir = Path("src/content/blog")
    fixed_files = []

    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Frontmatter var ama bozuk mu kontrol et
            if content.strip().startswith('---'):
                lines = content.split('\n')
                frontmatter_end = -1

                # İkinci --- bulalım
                dash_count = 0
                for i, line in enumerate(lines):
                    if line.strip() == '---':
                        dash_count += 1
                        if dash_count == 2:
                            frontmatter_end = i
                            break

                if frontmatter_end == -1:
                    # İkinci --- bulunamadı, frontmatter bozuk
                    filename = md_file.name
                    title = extract_title_from_filename(filename)
                    category = extract_category_from_path(str(md_file))
                    is_turkish = filename.endswith('.tr.md')

                    # Eski içeriği temizle ve yeni frontmatter ekle
                    # İlk ---'dan sonrasını al
                    content_without_broken_fm = '\n'.join(lines[1:])
                    # Eğer hala --- ile başlıyorsa onu da kaldır
                    content_without_broken_fm = re.sub(r'^---\s*\n', '', content_without_broken_fm)

                    # Yeni frontmatter oluştur
                    frontmatter = create_frontmatter(title, category, is_turkish)

                    # Yeni içerik
                    new_content = frontmatter + content_without_broken_fm

                    # Dosyayı güncelle
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    fixed_files.append({
                        'file': str(md_file),
                        'title': title,
                        'category': category,
                        'is_turkish': is_turkish,
                        'type': 'broken_frontmatter'
                    })

        except Exception as e:
            print(f"Hata {md_file}: {e}")

    return fixed_files

def main():
    print("🔧 Frontmatter Fixer başlatılıyor...")

    # 1. Eksik frontmatter'ları düzelt
    print("\n1. Eksik frontmatter'lar düzeltiliyor...")
    missing_fixed = fix_missing_frontmatter()

    if missing_fixed:
        print(f"✅ {len(missing_fixed)} dosyada eksik frontmatter düzeltildi:")
        for fix in missing_fixed:
            print(f"   📁 {fix['file']}")
            print(f"      📝 Title: {fix['title']}")
            print(f"      📂 Category: {fix['category']}")
            print(f"      🌍 Turkish: {'Evet' if fix['is_turkish'] else 'Hayır'}")
    else:
        print("   ℹ️ Eksik frontmatter bulunamadı.")

    # 2. Bozuk frontmatter'ları düzelt
    print("\n2. Bozuk frontmatter'lar düzeltiliyor...")
    broken_fixed = fix_broken_frontmatter()

    if broken_fixed:
        print(f"✅ {len(broken_fixed)} dosyada bozuk frontmatter düzeltildi:")
        for fix in broken_fixed:
            print(f"   📁 {fix['file']}")
            print(f"      📝 Title: {fix['title']}")
            print(f"      📂 Category: {fix['category']}")
    else:
        print("   ℹ️ Bozuk frontmatter bulunamadı.")

    total_fixed = len(missing_fixed) + len(broken_fixed)
    print(f"\n🏁 Toplam {total_fixed} dosya düzeltildi!")

    return total_fixed

if __name__ == "__main__":
    main()
