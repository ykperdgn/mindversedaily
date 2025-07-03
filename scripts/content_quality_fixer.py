#!/usr/bin/env python3
"""
Content Quality Fixer for MindVerse Blog
Fixes common quality issues in Turkish articles
"""

import os
import re
import glob
from pathlib import Path
from typing import List, Tuple

CONTENT_DIR = Path("src/content/blog")

def extract_frontmatter_and_content(markdown_content: str) -> Tuple[dict, str]:
    """Extract frontmatter and content from markdown file"""
    lines = markdown_content.strip().split('\n')

    if not lines[0].strip() == '---':
        return {}, markdown_content

    frontmatter = {}
    content_start = 0

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            content_start = i + 1
            break
        elif ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"')

    content = '\n'.join(lines[content_start:]).strip()
    return frontmatter, content

def fix_default_titles():
    """Fix articles with default title 'Sağlık ve Yaşam Rehberi'"""
    print("🔧 Varsayılan başlıkları düzeltiliyor...")

    fixed_count = 0
    problem_files = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*saglik-ve-yasam-rehberi*.tr.md")
            files = glob.glob(pattern)

            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    frontmatter, article_content = extract_frontmatter_and_content(content)
                    title = frontmatter.get('title', '').strip('"')

                    if title == "Sağlık ve Yaşam Rehberi":
                        # Check content quality
                        word_count = len(article_content.split())
                        english_words = len(re.findall(r'\b[a-zA-Z]{3,}\b', article_content))
                        english_ratio = english_words / max(word_count, 1)

                        if word_count < 200 or english_ratio > 0.4:
                            # Mark for deletion (poor quality)
                            problem_files.append(file_path)
                            print(f"   🗑️ Düşük kalite: {os.path.basename(file_path)}")
                        else:
                            print(f"   ⚠️ Varsayılan başlık: {os.path.basename(file_path)}")
                            fixed_count += 1

                except Exception as e:
                    print(f"   ❌ Hata: {file_path} - {e}")

    print(f"✅ {fixed_count} varsayılan başlık tespit edildi")
    print(f"🗑️ {len(problem_files)} düşük kaliteli dosya bulundu")

    return problem_files

def delete_low_quality_files(problem_files: List[str]):
    """Delete low quality files"""
    if not problem_files:
        print("✨ Silinecek düşük kaliteli dosya yok!")
        return

    print(f"\n🗑️ {len(problem_files)} düşük kaliteli dosya siliniyor...")

    deleted_count = 0
    for file_path in problem_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   ✅ Silindi: {os.path.basename(file_path)}")
                deleted_count += 1
        except Exception as e:
            print(f"   ❌ Silinemedi {file_path}: {e}")

    print(f"🎉 {deleted_count} düşük kaliteli dosya silindi")

def find_mixed_language_articles():
    """Find Turkish articles with too much English content"""
    print("\n🔍 Karışık dil içerikli makaleler bulunuyor...")

    mixed_files = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            pattern = str(category_dir / "*.tr.md")
            files = glob.glob(pattern)

            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    frontmatter, article_content = extract_frontmatter_and_content(content)

                    # Check English word ratio
                    word_count = len(article_content.split())
                    english_words = len(re.findall(r'\b[a-zA-Z]{3,}\b', article_content))
                    english_ratio = english_words / max(word_count, 1)

                    if english_ratio > 0.3:  # More than 30% English
                        mixed_files.append({
                            'path': file_path,
                            'filename': os.path.basename(file_path),
                            'english_ratio': english_ratio,
                            'word_count': word_count
                        })

                except Exception as e:
                    print(f"   ❌ Hata: {file_path} - {e}")

    # Sort by English ratio (worst first)
    mixed_files.sort(key=lambda x: x['english_ratio'], reverse=True)

    print(f"🔍 {len(mixed_files)} karışık dil içerikli makale bulundu")

    # Show worst 10
    print("\n📊 En problemli 10 dosya:")
    for i, file_info in enumerate(mixed_files[:10], 1):
        ratio = file_info['english_ratio'] * 100
        print(f"   {i}. {file_info['filename']} - %{ratio:.1f} İngilizce")

    return mixed_files

def generate_cleanup_recommendations(mixed_files: List[dict]):
    """Generate cleanup recommendations"""
    if not mixed_files:
        return

    print(f"\n💡 TEMİZLİK ÖNERİLERİ:")
    print("=" * 50)

    # Categorize by severity
    severe_cases = [f for f in mixed_files if f['english_ratio'] > 0.5]  # >50% English
    moderate_cases = [f for f in mixed_files if 0.3 < f['english_ratio'] <= 0.5]  # 30-50% English

    if severe_cases:
        print(f"🔴 ÇOK CİDDİ (>%50 İngilizce): {len(severe_cases)} dosya")
        print("   Öneri: Bu dosyalar silinmeli veya yeniden çevrilmeli")
        for file_info in severe_cases[:5]:
            print(f"     - {file_info['filename']}")
        if len(severe_cases) > 5:
            print(f"     ... ve {len(severe_cases) - 5} dosya daha")

    if moderate_cases:
        print(f"\n🟡 ORTA (%30-50 İngilizce): {len(moderate_cases)} dosya")
        print("   Öneri: Bu dosyalar gözden geçirilmeli")
        for file_info in moderate_cases[:5]:
            print(f"     - {file_info['filename']}")
        if len(moderate_cases) > 5:
            print(f"     ... ve {len(moderate_cases) - 5} dosya daha")

    # Generate deletion commands for severe cases
    if severe_cases:
        print(f"\n🗑️ CİDDİ PROBLEMLER İÇİN SİLME KOMUTLARI:")
        for file_info in severe_cases:
            print(f'Remove-Item "{file_info["path"]}" -Force')

def main():
    """Main quality fixing function"""
    print("🔧 MindVerse Blog - İçerik Kalitesi Düzeltici")
    print("=" * 50)

    # Fix default titles and find low quality files
    problem_files = fix_default_titles()

    # Delete low quality files
    if problem_files:
        response = input(f"\n⚠️ {len(problem_files)} düşük kaliteli dosya bulundu. Silmek istiyorum musunuz? (y/N): ")
        if response.lower() == 'y':
            delete_low_quality_files(problem_files)

    # Find mixed language articles
    mixed_files = find_mixed_language_articles()

    # Generate recommendations
    generate_cleanup_recommendations(mixed_files)

    print(f"\n📊 ÖZET:")
    if problem_files:
        print(f"🗑️ Düşük kalite: {len(problem_files)} dosya")
    print(f"🔤 Karışık dil: {len(mixed_files)} dosya")

    # Final recommendations
    print(f"\n💡 FİNAL ÖNERİLER:")
    severe_mixed = len([f for f in mixed_files if f['english_ratio'] > 0.5])
    if severe_mixed > 0:
        print(f"1. {severe_mixed} çok kötü kaliteli dosya silinmeli")

    moderate_mixed = len([f for f in mixed_files if 0.3 < f['english_ratio'] <= 0.5])
    if moderate_mixed > 0:
        print(f"2. {moderate_mixed} orta kaliteli dosya yeniden çevrilmeli")

    print("3. Gelecekte daha iyi çeviri kontrolü için quality gates eklenmeli")

if __name__ == "__main__":
    main()
