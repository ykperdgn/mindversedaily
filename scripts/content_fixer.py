#!/usr/bin/env python3
"""
Content Fixer - Bozuk dosyaları düzelt, silme!
YAML hatalarını ve encoding problemlerini çözer
"""

import os
import re
import glob
from pathlib import Path
import unicodedata

CONTENT_DIR = Path("src/content/blog")

class ContentFixer:
    def __init__(self):
        self.fixed_count = 0
        self.error_count = 0

    def fix_turkish_encoding(self, text):
        """Fix common Turkish encoding issues"""
        replacements = {
            # Common garbled patterns
            'ğ': 'ğ', 'Ğ': 'Ğ', 'ı': 'ı', 'İ': 'İ',
            'ö': 'ö', 'Ö': 'Ö', 'ü': 'ü', 'Ü': 'Ü',
            'ş': 'ş', 'Ş': 'Ş', 'ç': 'ç', 'Ç': 'Ç',

            # Common broken patterns
            'aa': 'ğ', 'ii': 'ı', 'uu': 'ü', 'oo': 'ö',
            'sss': 'ş', 'ccc': 'ç',

            # Specific broken words
            'baklk': 'bağışıklık',
            'srlarn': 'sırlarını',
            'keifler': 'keşifler',
            'gemii': 'geçmişi',
            'gelecei': 'geleceği',
            'deiimi': 'değişimi',
            'aratrmas': 'araştırması',
            'nasl': 'nasıl',
            'ekillendirdii': 'şekillendirdiği',
            'yolculuu': 'yolculuğu',
            'zmlenmesi': 'çözümlenmesi',
            'gizemlerini-zme': 'gizemlerini-çözme',
            'baar': 'başarı',
            'baarszln': 'başarısızlığın',
            'kltrel': 'kültürel',
            'yaamn': 'yaşamın',
            'ykseliyor': 'yükseliyor',
            'iin': 'için',
            'karma': 'çıkarma',
            'zmek': 'çözmek',
            'sren': 'süren',
            'byk': 'büyük',
            'dnya': 'dünya'
        }

        fixed_text = text
        for broken, correct in replacements.items():
            fixed_text = fixed_text.replace(broken, correct)

        return fixed_text

    def fix_yaml_frontmatter(self, content):
        """Fix YAML frontmatter issues"""
        lines = content.split('\n')

        if not lines[0].strip() == '---':
            return content

        fixed_lines = ['---']
        in_frontmatter = True

        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---' and in_frontmatter:
                fixed_lines.append('---')
                in_frontmatter = False
                # Add rest of content
                fixed_lines.extend(lines[i+1:])
                break
            elif in_frontmatter:
                # Fix common YAML issues
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    # Fix description field
                    if key == 'description':
                        # Remove nested quotes and Turkish prefixes
                        value = re.sub(r'"Türkçe[^"]*?"([^"]+)"[^"]*"?', r'"\1"', value)
                        value = re.sub(r'"[^"]*"([^"]+)"[^"]*"', r'"\1"', value)

                        # Ensure proper quoting
                        if not value.startswith('"'):
                            value = f'"{value}"'
                        if not value.endswith('"'):
                            value = f'{value}"'

                        # Limit length
                        if len(value) > 162:  # 160 + quotes
                            clean_value = value.strip('"')[:157] + "..."
                            value = f'"{clean_value}"'

                    # Fix title field
                    elif key == 'title':
                        if not value.startswith('"'):
                            value = f'"{value}"'
                        if not value.endswith('"'):
                            value = f'{value}"'

                    # Fix category field
                    elif key == 'category':
                        value = value.strip('"')  # Remove quotes from category

                    # Fix image field
                    elif key == 'image':
                        if not value.startswith('"'):
                            value = f'"{value}"'
                        if not value.endswith('"'):
                            value = f'{value}"'

                    fixed_lines.append(f'{key}: {value}')
                else:
                    fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def generate_clean_title(self, original_title, filename):
        """Generate a clean title from filename if title is broken"""
        if not original_title or 'here-is-the-article' in original_title.lower():
            # Extract meaningful parts from filename
            clean_name = filename.replace('.tr.md', '').replace('.en.md', '')
            clean_name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', clean_name)  # Remove date
            clean_name = clean_name.replace('-', ' ').title()

            # Fix Turkish characters
            clean_name = self.fix_turkish_encoding(clean_name)

            return clean_name

        return self.fix_turkish_encoding(original_title)

    def fix_single_file(self, file_path):
        """Fix a single markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Fix Turkish encoding issues
            content = self.fix_turkish_encoding(content)

            # Fix YAML frontmatter
            content = self.fix_yaml_frontmatter(content)

            # Extract and fix title if needed
            frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                title_match = re.search(r'title:\s*"([^"]*)"', frontmatter)

                if title_match:
                    title = title_match.group(1)
                    clean_title = self.generate_clean_title(title, os.path.basename(file_path))
                    content = content.replace(f'title: "{title}"', f'title: "{clean_title}"')

            # Only write if there are changes
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

            return False

        except Exception as e:
            print(f"❌ Hata: {os.path.basename(file_path)} - {e}")
            self.error_count += 1
            return False

    def fix_all_files(self):
        """Fix all Turkish markdown files"""
        print("🔧 İçerik Düzeltici - Bozuk dosyaları düzelt!")
        print("=" * 50)

        for category_dir in CONTENT_DIR.iterdir():
            if category_dir.is_dir():
                pattern = str(category_dir / "*.tr.md")
                files = glob.glob(pattern)

                print(f"\n📁 {category_dir.name} kategorisi:")

                for file_path in files:
                    if self.fix_single_file(file_path):
                        print(f"   ✅ Düzeltildi: {os.path.basename(file_path)}")
                        self.fixed_count += 1
                    else:
                        print(f"   ⚪ Değişiklik yok: {os.path.basename(file_path)}")

        print(f"\n🎉 Düzeltme tamamlandı!")
        print(f"✅ Düzeltilen dosya: {self.fixed_count}")
        print(f"❌ Hata: {self.error_count}")

def main():
    fixer = ContentFixer()
    fixer.fix_all_files()

if __name__ == "__main__":
    main()
