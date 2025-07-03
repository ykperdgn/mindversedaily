#!/usr/bin/env python3
"""
Image Path Fixer - Blog placeholder image path'ini düzeltir
"""

import os
import re
from pathlib import Path

def fix_image_paths():
    """Bozuk image path'lerini düzeltir"""
    content_dir = Path("src/content/blog")
    fixed_files = []

    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Eski image path'lerini yenileriyle değiştir
            replacements = [
                ('image: "/assets/blog-placeholder-1.svg"', 'image: "/assets/blog-placeholder.svg"'),
                ('heroImage: /assets/blog-placeholder-1.svg', 'heroImage: /assets/blog-placeholder.svg'),
                ('heroImage: "/assets/blog-placeholder-1.svg"', 'heroImage: "/assets/blog-placeholder.svg"'),
            ]

            for old_path, new_path in replacements:
                content = content.replace(old_path, new_path)

            if content != original_content:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                fixed_files.append(str(md_file))

        except Exception as e:
            print(f"Hata {md_file}: {e}")

    return fixed_files

def main():
    print("🖼️ Image Path Fixer başlatılıyor...")

    fixed_files = fix_image_paths()

    if fixed_files:
        print(f"✅ {len(fixed_files)} dosyada image path düzeltildi:")
        for file_path in fixed_files[:10]:  # İlk 10'unu göster
            print(f"   📁 {file_path}")
        if len(fixed_files) > 10:
            print(f"   ... ve {len(fixed_files) - 10} dosya daha")
    else:
        print("   ℹ️ Düzeltilecek image path bulunamadı.")

    return len(fixed_files)

if __name__ == "__main__":
    count = main()
    print(f"\n🏁 Toplam {count} dosya düzeltildi!")
