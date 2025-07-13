
#!/usr/bin/env python3
"""
Comprehensive Content Fixer - Hatalı içerikleri tespit et ve düzelt
"""

import os
import re
import glob
import json
from pathlib import Path
from datetime import datetime
import yaml

CONTENT_DIR = Path("src/content/blog")

class ComprehensiveContentFixer:
    def __init__(self):
        self.fixed_count = 0
        self.error_count = 0
        self.issues_found = []

    def fix_turkish_spelling_errors(self, text):
        """Türkçe yazım hatalarını düzelt"""
        spelling_fixes = {
            # Yaygın yazım hataları
            'ağaç': 'ağaç', 'agac': 'ağaç', 'aağaç': 'ağaç',
            'çiçek': 'çiçek', 'cicek': 'çiçek', 'ççiçek': 'çiçek',
            'öğretmen': 'öğretmen', 'ogretmen': 'öğretmen',
            'üzgün': 'üzgün', 'uzgun': 'üzgün',
            'şehir': 'şehir', 'sehir': 'şehir',
            'ığğ': 'ığ', 'iıı': 'ı', 'öööü': 'öü', 'şşş': 'ş',
            
            # İçeriklerde sık görülen hatalar
            'araştırma': 'araştırma', 'arastirma': 'araştırma',
            'çözüm': 'çözüm', 'cozum': 'çözüm',
            'değişim': 'değişim', 'degisim': 'değişim',
            'gelişim': 'gelişim', 'gelisim': 'gelişim',
            'güçlü': 'güçlü', 'guclu': 'güçlü',
            'hızlı': 'hızlı', 'hizli': 'hızlı',
            'müzik': 'müzik', 'muzik': 'müzik',
            'önemli': 'önemli', 'onemli': 'önemli',
            'yüksek': 'yüksek', 'yuksek': 'yüksek',
            
            # Bozuk kelimeler
            'baklk': 'bağışıklık',
            'srlarn': 'sırlarını',
            'keifler': 'keşifler',
            'gemii': 'geçmişi',
            'gelecei': 'geleceği',
            'deiimi': 'değişimi',
            'aratrmas': 'araştırması',
            'nasl': 'nasıl',
            'ykseliyor': 'yükseliyor',
            'iin': 'için',
            'zmek': 'çözmek',
            'sren': 'süren',
            'byk': 'büyük',
            'dnya': 'dünya'
        }

        fixed_text = text
        for wrong, correct in spelling_fixes.items():
            fixed_text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, fixed_text, flags=re.IGNORECASE)

        return fixed_text

    def fix_title_issues(self, title):
        """Başlık sorunlarını düzelt"""
        if not title:
            return "MindVerse Blog - Güncel İçerik"

        # Çok uzun başlıkları kısalt
        if len(title) > 100:
            title = title[:97] + "..."

        # Duplicate başlıkları temizle
        title = re.sub(r'"([^"]*)"([^"]*)"', r'"\1\2"', title)
        
        # Varsayılan kötü başlıkları değiştir
        if "Sağlık ve Yaşam Rehberi" in title or "Türkçe Başlık" in title or title.strip() == "":
            return "MindVerse - Güncel Bilgiler"

        # Yazım hatalarını düzelt
        title = self.fix_turkish_spelling_errors(title)

        return title.strip()

    def fix_description_issues(self, description):
        """Açıklama sorunlarını düzelt"""
        if not description:
            return "MindVerse Daily'den güncel ve kapsamlı bilgiler."

        # Çok uzun açıklamaları kısalt
        if len(description) > 160:
            description = description[:157] + "..."

        # Nested quotes'ları temizle
        description = re.sub(r'"Türkçe[^"]*?"([^"]+)"[^"]*"?', r'"\1"', description)
        description = re.sub(r'"[^"]*"([^"]+)"[^"]*"', r'"\1"', description)

        # Test kelimelerini kaldır
        description = re.sub(r'\btest\b', '', description, flags=re.IGNORECASE)

        # Yazım hatalarını düzelt
        description = self.fix_turkish_spelling_errors(description)

        return description.strip()

    def fix_content_structure(self, content):
        """İçerik yapısını düzelt"""
        # Çok uzun paragrafları böl
        paragraphs = content.split('\n\n')
        fixed_paragraphs = []

        for para in paragraphs:
            if len(para) > 500:  # Çok uzun paragraf
                # Cümleleri ayır
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current_para = ""
                
                for sentence in sentences:
                    if len(current_para + sentence) > 400:
                        if current_para:
                            fixed_paragraphs.append(current_para.strip())
                        current_para = sentence
                    else:
                        current_para += " " + sentence if current_para else sentence
                
                if current_para:
                    fixed_paragraphs.append(current_para.strip())
            else:
                fixed_paragraphs.append(para)

        # Başlık yapısını ekle
        content = "\n\n".join(fixed_paragraphs)
        
        # Eğer içerikte başlık yoksa ekle
        if not re.search(r'^##\s+', content, re.MULTILINE):
            # İlk paragraftan başlık oluştur
            first_para = fixed_paragraphs[0] if fixed_paragraphs else ""
            if first_para and len(first_para) > 50:
                # İlk cümleyi başlık yap
                first_sentence = re.split(r'[.!?]', first_para)[0]
                if len(first_sentence) < 80:
                    content = f"## {first_sentence.strip()}\n\n{content}"

        # Yazım hatalarını düzelt
        content = self.fix_turkish_spelling_errors(content)

        return content

    def fix_single_file(self, file_path):
        """Tek dosyayı düzelt"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Frontmatter ve content'i ayır
            if not original_content.startswith('---'):
                self.issues_found.append(f"❌ {file_path}: Frontmatter eksik")
                return False

            parts = original_content.split('---', 2)
            if len(parts) < 3:
                self.issues_found.append(f"❌ {file_path}: Geçersiz frontmatter")
                return False

            frontmatter_text = parts[1]
            content = parts[2].strip()

            # YAML parse et
            try:
                frontmatter = yaml.safe_load(frontmatter_text)
            except yaml.YAMLError as e:
                self.issues_found.append(f"❌ {file_path}: YAML hatası - {e}")
                return False

            changed = False

            # Title düzelt
            if 'title' in frontmatter:
                original_title = frontmatter['title']
                fixed_title = self.fix_title_issues(original_title)
                if fixed_title != original_title:
                    frontmatter['title'] = fixed_title
                    changed = True
                    self.issues_found.append(f"🔧 {file_path}: Başlık düzeltildi")

            # Description düzelt
            if 'description' in frontmatter:
                original_desc = frontmatter['description']
                fixed_desc = self.fix_description_issues(original_desc)
                if fixed_desc != original_desc:
                    frontmatter['description'] = fixed_desc
                    changed = True
                    self.issues_found.append(f"🔧 {file_path}: Açıklama düzeltildi")

            # Hero image ekle
            if 'heroImage' not in frontmatter:
                frontmatter['heroImage'] = '/assets/blog-placeholder-1.jpg'
                changed = True
                self.issues_found.append(f"🔧 {file_path}: HeroImage eklendi")

            # Content düzelt
            fixed_content = self.fix_content_structure(content)
            if fixed_content != content:
                content = fixed_content
                changed = True
                self.issues_found.append(f"🔧 {file_path}: İçerik yapısı düzeltildi")

            if changed:
                # Dosyayı yeniden yaz
                new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
                new_content = f"---\n{new_frontmatter}---\n{content}"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                self.fixed_count += 1
                return True

            return False

        except Exception as e:
            self.error_count += 1
            self.issues_found.append(f"❌ {file_path}: Hata - {e}")
            return False

    def scan_and_fix_all_files(self):
        """Tüm dosyaları tara ve düzelt"""
        print("🔧 Kapsamlı İçerik Düzeltici Başlatılıyor...")
        print("=" * 60)

        total_files = 0
        for category_dir in CONTENT_DIR.iterdir():
            if category_dir.is_dir():
                pattern = str(category_dir / "*.tr.md")
                files = glob.glob(pattern)
                total_files += len(files)

                print(f"\n📁 {category_dir.name} kategorisi ({len(files)} dosya):")

                for file_path in files:
                    filename = os.path.basename(file_path)
                    if self.fix_single_file(file_path):
                        print(f"   ✅ Düzeltildi: {filename}")
                    else:
                        print(f"   ⚪ Değişiklik yok: {filename}")

        # Özet rapor
        print(f"\n📊 DÜZELTME RAPORU:")
        print(f"📁 Toplam dosya: {total_files}")
        print(f"✅ Düzeltilen: {self.fixed_count}")
        print(f"❌ Hata: {self.error_count}")

        # Detaylı sorunlar
        if self.issues_found:
            print(f"\n📋 DETAYLI SORUN LİSTESİ:")
            for issue in self.issues_found[:20]:  # İlk 20 sorunu göster
                print(f"   {issue}")
            
            if len(self.issues_found) > 20:
                print(f"   ... ve {len(self.issues_found) - 20} sorun daha")

        # Raporu dosyaya kaydet
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_files': total_files,
            'fixed_count': self.fixed_count,
            'error_count': self.error_count,
            'issues': self.issues_found
        }

        report_file = f"scripts/reports/content_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Rapor kaydedildi: {report_file}")

def main():
    fixer = ComprehensiveContentFixer()
    fixer.scan_and_fix_all_files()

if __name__ == "__main__":
    main()
