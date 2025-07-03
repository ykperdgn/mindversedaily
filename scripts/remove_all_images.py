#!/usr/bin/env python3
"""
Image Remover - Tüm markdown dosyalarından image alanlarını kaldırır
"""

import os
import re
from pathlib import Path

def remove_all_images():
    """Tüm dosyalardan image alanlarını kaldırır"""
    content_dir = Path("src/content/blog")
    fixed_files = []

    for md_file in content_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Tüm image alanlarını kaldır
            # image: "..." satırlarını kaldır
            content = re.sub(r'^image:\s*"[^"]*"\s*\n?', '', content, flags=re.MULTILINE)
            content = re.sub(r'^image:\s*[^\n]*\n?', '', content, flags=re.MULTILINE)

            # heroImage: "..." satırlarını kaldır
            content = re.sub(r'^heroImage:\s*"[^"]*"\s*\n?', '', content, flags=re.MULTILINE)
            content = re.sub(r'^heroImage:\s*[^\n]*\n?', '', content, flags=re.MULTILINE)

            if content != original_content:
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                fixed_files.append(str(md_file))

        except Exception as e:
            print(f"Hata {md_file}: {e}")

    return fixed_files

def main():
    print("🗑️ Image Remover başlatılıyor...")
    print("⚠️ Tüm görsel referansları silinecek!")

    fixed_files = remove_all_images()

    if fixed_files:
        print(f"✅ {len(fixed_files)} dosyadan görsel alanları kaldırıldı:")
        for file_path in fixed_files[:10]:  # İlk 10'unu göster
            print(f"   📁 {file_path}")
        if len(fixed_files) > 10:
            print(f"   ... ve {len(fixed_files) - 10} dosya daha")
    else:
        print("   ℹ️ Kaldırılacak görsel alanı bulunamadı.")

    return len(fixed_files)

if __name__ == "__main__":
    count = main()
    print(f"\n🏁 Toplam {count} dosyada görsel alanları kaldırıldı!")
    print("🎯 Artık hiçbir dosyada görsel referansı yok!")
