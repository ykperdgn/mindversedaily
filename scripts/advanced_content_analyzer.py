#!/usr/bin/env python3
"""
Advanced Content Analyzer for MindVerse Blog
Detects duplicates, analyzes quality, and suggests improvements
"""

import os
import re
import glob
import hashlib
import datetime
from typing import Dict, List, Tuple, Set
from pathlib import Path
from collections import defaultdict, Counter
import difflib

# Configuration
CONTENT_DIR = Path("src/content/blog")
SIMILARITY_THRESHOLD = 0.85  # 85% similarity threshold
MIN_CONTENT_LENGTH = 200  # Minimum content length
MAX_TITLE_LENGTH = 80  # Maximum title length

class ContentAnalyzer:
    def __init__(self):
        self.articles = []
        self.duplicates = defaultdict(list)
        self.quality_issues = defaultdict(list)
        self.statistics = {
            'total_articles': 0,
            'turkish_articles': 0,
            'english_articles': 0,
            'duplicates_found': 0,
            'quality_issues': 0
        }

    def extract_frontmatter_and_content(self, markdown_content: str) -> Tuple[dict, str]:
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

    def clean_text_for_comparison(self, text: str) -> str:
        """Clean text for similarity comparison"""
        # Remove markdown formatting
        text = re.sub(r'[#*_`\[\]()]', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase
        text = text.lower().strip()
        return text

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using difflib"""
        clean_text1 = self.clean_text_for_comparison(text1)
        clean_text2 = self.clean_text_for_comparison(text2)

        # Use SequenceMatcher for similarity
        similarity = difflib.SequenceMatcher(None, clean_text1, clean_text2).ratio()
        return similarity

    def get_content_hash(self, content: str) -> str:
        """Generate hash for content comparison"""
        clean_content = self.clean_text_for_comparison(content)
        return hashlib.md5(clean_content.encode()).hexdigest()

    def check_article_quality(self, frontmatter: dict, content: str, filepath: str) -> List[str]:
        """Analyze content quality and return issues"""
        issues = []

        title = frontmatter.get('title', '').strip('"')
        description = frontmatter.get('description', '').strip('"')

        # Title issues
        if not title:
            issues.append("Başlık eksik")
        elif len(title) > MAX_TITLE_LENGTH:
            issues.append(f"Başlık çok uzun ({len(title)} karakter)")
        elif len(title) < 10:
            issues.append("Başlık çok kısa")

        # Description issues
        if not description:
            issues.append("Açıklama eksik")
        elif len(description) > 160:
            issues.append("Açıklama çok uzun (SEO için 160 karakter altında olmalı)")

        # Content issues
        if len(content) < MIN_CONTENT_LENGTH:
            issues.append(f"İçerik çok kısa ({len(content)} karakter)")

        # Turkish content specific checks
        if filepath.endswith('.tr.md'):
            # Check for English words in Turkish content
            english_words = re.findall(r'\b[a-zA-Z]{3,}\b', content)
            if len(english_words) > len(content.split()) * 0.3:  # More than 30% English
                issues.append("Türkçe içerikte çok fazla İngilizce kelime")

            # Check for translation artifacts
            translation_artifacts = [
                'translation', 'translate', 'işte çeviri', 'burada çeviri',
                'here is', 'the translation', 'türkçe çeviri'
            ]
            for artifact in translation_artifacts:
                if artifact.lower() in content.lower():
                    issues.append("Çeviri kalıntıları tespit edildi")
                    break

        # Check for repeated sentences
        sentences = re.split(r'[.!?]+', content)
        sentence_counts = Counter(s.strip() for s in sentences if len(s.strip()) > 20)
        repeated_sentences = [s for s, count in sentence_counts.items() if count > 1]
        if repeated_sentences:
            issues.append(f"Tekrarlanan cümleler ({len(repeated_sentences)} adet)")

        return issues

    def load_all_articles(self):
        """Load all articles from content directory"""
        print("📚 Tüm makaleler yükleniyor...")

        for category_dir in CONTENT_DIR.iterdir():
            if category_dir.is_dir():
                # Get all markdown files
                pattern = str(category_dir / "*.md")
                md_files = glob.glob(pattern)

                for file_path in md_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        frontmatter, article_content = self.extract_frontmatter_and_content(content)

                        article_info = {
                            'filepath': file_path,
                            'filename': os.path.basename(file_path),
                            'category': category_dir.name,
                            'frontmatter': frontmatter,
                            'content': article_content,
                            'content_hash': self.get_content_hash(article_content),
                            'word_count': len(article_content.split()),
                            'is_turkish': file_path.endswith('.tr.md'),
                            'is_english': file_path.endswith('.en.md'),
                            'date_created': datetime.datetime.fromtimestamp(os.path.getctime(file_path)),
                            'date_modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                        }

                        self.articles.append(article_info)

                    except Exception as e:
                        print(f"❌ Hata: {file_path} - {e}")

        # Update statistics
        self.statistics['total_articles'] = len(self.articles)
        self.statistics['turkish_articles'] = sum(1 for a in self.articles if a['is_turkish'])
        self.statistics['english_articles'] = sum(1 for a in self.articles if a['is_english'])

        print(f"✅ {len(self.articles)} makale yüklendi")
        print(f"   📝 Türkçe: {self.statistics['turkish_articles']}")
        print(f"   📝 İngilizce: {self.statistics['english_articles']}")

    def find_duplicates(self):
        """Find duplicate articles using multiple methods"""
        print("\n🔍 Duplicate analizi başlıyor...")

        # Method 1: Exact hash matches
        hash_groups = defaultdict(list)
        for article in self.articles:
            hash_groups[article['content_hash']].append(article)

        exact_duplicates = {h: articles for h, articles in hash_groups.items() if len(articles) > 1}

        # Method 2: Title similarity
        title_duplicates = defaultdict(list)
        for i, article1 in enumerate(self.articles):
            title1 = article1['frontmatter'].get('title', '').strip('"')
            if not title1:
                continue

            for j, article2 in enumerate(self.articles[i+1:], i+1):
                title2 = article2['frontmatter'].get('title', '').strip('"')
                if not title2:
                    continue

                similarity = self.calculate_similarity(title1, title2)
                if similarity > 0.9:  # 90% title similarity
                    key = f"title_sim_{min(i,j)}_{max(i,j)}"
                    title_duplicates[key] = [article1, article2]

        # Method 3: Content similarity (simplified for performance)
        content_duplicates = defaultdict(list)
        print("   📊 İçerik benzerliği analiz ediliyor...")

        # Sample check for performance (check every 5th article)
        sample_articles = self.articles[::5]  # Every 5th article

        for i, article1 in enumerate(sample_articles):
            if i % 10 == 0:
                print(f"   📈 İlerleme: {i}/{len(sample_articles)}")

            for j, article2 in enumerate(sample_articles[i+1:], i+1):
                similarity = self.calculate_similarity(article1['content'], article2['content'])

                if similarity > SIMILARITY_THRESHOLD:
                    key = f"content_sim_{similarity:.2f}_{i}_{j}"
                    content_duplicates[key] = {
                        'articles': [article1, article2],
                        'similarity': similarity
                    }

        # Store all duplicates
        self.duplicates = {
            'exact_hash': exact_duplicates,
            'title_similarity': title_duplicates,
            'content_similarity': content_duplicates
        }

        total_duplicate_groups = (len(exact_duplicates) +
                                len(title_duplicates) +
                                len(content_duplicates))

        self.statistics['duplicates_found'] = total_duplicate_groups

        print(f"✅ Duplicate analizi tamamlandı:")
        print(f"   🔄 Tam eşleşme: {len(exact_duplicates)} grup")
        print(f"   📝 Başlık benzerliği: {len(title_duplicates)} grup")
        print(f"   📄 İçerik benzerliği: {len(content_duplicates)} grup")

    def analyze_quality(self):
        """Analyze quality of all articles"""
        print("\n🎯 Kalite analizi başlıyor...")

        for article in self.articles:
            issues = self.check_article_quality(
                article['frontmatter'],
                article['content'],
                article['filepath']
            )

            if issues:
                self.quality_issues[article['filepath']] = issues

        self.statistics['quality_issues'] = len(self.quality_issues)

        print(f"✅ Kalite analizi tamamlandı:")
        print(f"   ⚠️ Sorunlu makale: {len(self.quality_issues)}")

    def generate_summary_report(self):
        """Generate a quick summary report"""
        print("\n📊 ÖZET RAPOR")
        print("=" * 50)
        print(f"📚 Toplam makale: {self.statistics['total_articles']}")
        print(f"🇹🇷 Türkçe makale: {self.statistics['turkish_articles']}")
        print(f"🇺🇸 İngilizce makale: {self.statistics['english_articles']}")
        print()

        # Exact duplicates
        exact_count = len(self.duplicates['exact_hash'])
        if exact_count > 0:
            print(f"🔄 TAM DUPLICATE: {exact_count} grup bulundu")
            for hash_val, articles in self.duplicates['exact_hash'].items():
                print(f"   Hash {hash_val[:8]}... - {len(articles)} dosya:")
                for article in articles:
                    print(f"     - {article['filename']}")
            print()

        # Title similarities
        title_count = len(self.duplicates['title_similarity'])
        if title_count > 0:
            print(f"📝 BAŞLIK BENZERLİĞİ: {title_count} grup")
            count = 0
            for key, articles in self.duplicates['title_similarity'].items():
                if count < 5:  # Show first 5
                    title1 = articles[0]['frontmatter'].get('title', '').strip('"')
                    title2 = articles[1]['frontmatter'].get('title', '').strip('"')
                    print(f"   - {articles[0]['filename']}")
                    print(f"   - {articles[1]['filename']}")
                    print()
                count += 1
            if title_count > 5:
                print(f"   ... ve {title_count - 5} grup daha")
            print()

        # Content similarities
        content_count = len(self.duplicates['content_similarity'])
        if content_count > 0:
            print(f"📄 İÇERİK BENZERLİĞİ: {content_count} grup")
            count = 0
            for key, dup_info in self.duplicates['content_similarity'].items():
                if count < 3:  # Show first 3
                    articles = dup_info['articles']
                    similarity = dup_info['similarity']
                    print(f"   Benzerlik: {similarity:.1%}")
                    print(f"   - {articles[0]['filename']}")
                    print(f"   - {articles[1]['filename']}")
                    print()
                count += 1
            if content_count > 3:
                print(f"   ... ve {content_count - 3} grup daha")
            print()

        # Quality issues
        if self.statistics['quality_issues'] > 0:
            print(f"⚠️ KALİTE SORUNLARI: {self.statistics['quality_issues']} makale")

            # Group issues by type
            issue_counts = defaultdict(int)
            for issues_list in self.quality_issues.values():
                for issue in issues_list:
                    issue_counts[issue] += 1

            print("   En yaygın sorunlar:")
            for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     - {issue}: {count} makale")
            print()

        # Recommendations
        print("💡 ÖNERİLER:")

        exact_files_to_delete = sum(len(articles)-1 for articles in self.duplicates['exact_hash'].values())
        if exact_files_to_delete > 0:
            print(f"1. {exact_files_to_delete} tam duplicate dosya silinebilir")

        if title_count > 0:
            print(f"2. {title_count} başlık benzerliği kontrol edilmeli")

        if content_count > 0:
            print(f"3. {content_count} içerik benzerliği gözden geçirilmeli")

        if self.statistics['quality_issues'] > 0:
            print(f"4. {self.statistics['quality_issues']} kalite sorunu düzeltilmeli")

    def create_cleanup_commands(self):
        """Create cleanup commands for exact duplicates"""
        if not self.duplicates['exact_hash']:
            print("\n✨ Silinecek exact duplicate bulunamadı!")
            return

        print(f"\n🧹 EXACT DUPLICATE TEMİZLİK KOMUTLARI:")
        print("=" * 50)

        files_to_delete = []
        for hash_val, articles in self.duplicates['exact_hash'].items():
            if len(articles) > 1:
                # Sort by creation date (keep oldest)
                articles.sort(key=lambda x: x['date_created'])
                print(f"\nHash {hash_val[:8]}... - {len(articles)} dosya:")
                print(f"  TUTULACAK: {articles[0]['filename']} (en eski)")

                # Mark newer ones for deletion
                for article in articles[1:]:
                    files_to_delete.append(article['filepath'])
                    print(f"  SİLİNECEK: {article['filename']}")

        if files_to_delete:
            print(f"\n📝 Silme komutları ({len(files_to_delete)} dosya):")
            for file_path in files_to_delete:
                print(f'Remove-Item "{file_path}" -Force')

def main():
    """Main analysis function"""
    print("🔍 MindVerse Blog - Gelişmiş İçerik Analizi")
    print("=" * 50)

    analyzer = ContentAnalyzer()

    # Load all articles
    analyzer.load_all_articles()

    # Find duplicates
    analyzer.find_duplicates()

    # Analyze quality
    analyzer.analyze_quality()

    # Generate summary report
    analyzer.generate_summary_report()

    # Create cleanup commands
    analyzer.create_cleanup_commands()

    return analyzer

if __name__ == "__main__":
    analyzer = main()
