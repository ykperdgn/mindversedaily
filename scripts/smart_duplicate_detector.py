#!/usr/bin/env python3
"""
Smart Duplicate Content Detector and Cleaner
Detects and removes duplicate articles, prevents re-translation
"""

import os
import re
import glob
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import difflib

# Configuration
CONTENT_DIR = Path("src/content/blog")
SIMILARITY_THRESHOLD = 0.8  # 80% similarity = duplicate

class DuplicateDetector:
    def __init__(self):
        self.all_articles = {}  # filename -> content
        self.title_map = {}     # title -> [filenames]
        self.content_hashes = {}  # hash -> filename
        self.similar_groups = []  # groups of similar articles

    def extract_article_info(self, file_path: str) -> Dict:
        """Extract title, description, and content from article"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter
            if not content.startswith('---'):
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            frontmatter_text = parts[1]
            article_content = parts[2].strip()

            # Parse frontmatter
            title = ""
            description = ""

            for line in frontmatter_text.split('\n'):
                if line.strip().startswith('title:'):
                    title = line.split(':', 1)[1].strip().strip('"\'')
                elif line.strip().startswith('description:'):
                    description = line.split(':', 1)[1].strip().strip('"\'')

            # Clean content for comparison
            clean_content = self.clean_content_for_comparison(article_content)

            return {
                'file_path': file_path,
                'title': title,
                'description': description,
                'content': article_content,
                'clean_content': clean_content,
                'content_hash': hashlib.md5(clean_content.encode()).hexdigest(),
                'word_count': len(clean_content.split()),
                'is_english': file_path.endswith('.en.md'),
                'is_turkish': file_path.endswith('.tr.md')
            }

        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return None

    def clean_content_for_comparison(self, content: str) -> str:
        """Clean content for similarity comparison"""
        # Remove markdown formatting
        content = re.sub(r'#+\s*', '', content)  # Headers
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*([^*]+)\*', r'\1', content)  # Italic
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)  # Links

        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)

        # Convert to lowercase for comparison
        return content.lower().strip()

    def calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two contents"""
        return difflib.SequenceMatcher(None, content1, content2).ratio()

    def scan_all_articles(self):
        """Scan all articles and build maps"""
        print("🔍 Tüm makaleler taranıyor...")

        article_count = 0

        for category_dir in CONTENT_DIR.iterdir():
            if not category_dir.is_dir():
                continue

            pattern = str(category_dir / "*.md")
            md_files = glob.glob(pattern)

            for file_path in md_files:
                if file_path.endswith('.en.md') or file_path.endswith('.tr.md'):
                    article_info = self.extract_article_info(file_path)

                    if article_info:
                        filename = os.path.basename(file_path)
                        self.all_articles[filename] = article_info

                        # Title mapping
                        title_key = article_info['title'].lower().strip()
                        if title_key:
                            if title_key not in self.title_map:
                                self.title_map[title_key] = []
                            self.title_map[title_key].append(filename)

                        # Content hash mapping
                        content_hash = article_info['content_hash']
                        if content_hash in self.content_hashes:
                            print(f"⚠️ Exact duplicate content found: {filename} vs {self.content_hashes[content_hash]}")
                        else:
                            self.content_hashes[content_hash] = filename

                        article_count += 1

        print(f"📚 {article_count} makale tarandı")
        print(f"🔗 {len(self.title_map)} benzersiz başlık")
        print(f"🧩 {len(self.content_hashes)} benzersiz içerik")

    def find_exact_duplicates(self) -> List[Tuple[str, str]]:
        """Find exact content duplicates"""
        duplicates = []
        hash_to_files = defaultdict(list)

        for filename, article_info in self.all_articles.items():
            hash_to_files[article_info['content_hash']].append(filename)

        for content_hash, files in hash_to_files.items():
            if len(files) > 1:
                # Sort by date to keep the oldest
                files.sort()
                for duplicate_file in files[1:]:
                    duplicates.append((files[0], duplicate_file))

        return duplicates

    def find_similar_content(self) -> List[List[str]]:
        """Find similar content groups"""
        print("🔍 Benzer içerikler aranıyor...")

        similar_groups = []
        processed = set()

        filenames = list(self.all_articles.keys())

        for i, filename1 in enumerate(filenames):
            if filename1 in processed:
                continue

            article1 = self.all_articles[filename1]
            similar_group = [filename1]

            for j, filename2 in enumerate(filenames[i+1:], i+1):
                if filename2 in processed:
                    continue

                article2 = self.all_articles[filename2]

                # Skip if one is English and other is Turkish (could be translation)
                if (article1['is_english'] and article2['is_turkish']) or \
                   (article1['is_turkish'] and article2['is_english']):
                    continue

                # Calculate similarity
                similarity = self.calculate_similarity(
                    article1['clean_content'],
                    article2['clean_content']
                )

                if similarity >= SIMILARITY_THRESHOLD:
                    similar_group.append(filename2)
                    processed.add(filename2)

            if len(similar_group) > 1:
                similar_groups.append(similar_group)
                for filename in similar_group:
                    processed.add(filename)

        return similar_groups

    def find_translation_pairs(self) -> List[Tuple[str, str]]:
        """Find English-Turkish translation pairs"""
        translation_pairs = []

        english_files = {f: info for f, info in self.all_articles.items() if info['is_english']}
        turkish_files = {f: info for f, info in self.all_articles.items() if info['is_turkish']}

        for en_file, en_info in english_files.items():
            # Look for Turkish equivalent
            base_name = en_file.replace('.en.md', '')
            potential_tr_file = base_name + '.tr.md'

            if potential_tr_file in turkish_files:
                translation_pairs.append((en_file, potential_tr_file))

        return translation_pairs

    def recommend_deletions(self) -> Dict[str, List[str]]:
        """Recommend which files to delete"""
        recommendations = {
            'exact_duplicates': [],
            'similar_content': [],
            'keep_newest': []
        }

        # Exact duplicates - delete all but first
        exact_duplicates = self.find_exact_duplicates()
        for original, duplicate in exact_duplicates:
            recommendations['exact_duplicates'].append(duplicate)

        # Similar content groups - keep the one with most words
        similar_groups = self.find_similar_content()
        for group in similar_groups:
            # Sort by word count (descending)
            group_with_info = [
                (filename, self.all_articles[filename]['word_count'])
                for filename in group
            ]
            group_with_info.sort(key=lambda x: x[1], reverse=True)

            # Keep the first (longest), delete others
            for filename, _ in group_with_info[1:]:
                recommendations['similar_content'].append(filename)

        return recommendations

    def check_translation_status(self) -> Dict[str, List[str]]:
        """Check which English articles need translation"""
        translation_status = {
            'needs_translation': [],
            'already_translated': [],
            'orphaned_turkish': []
        }

        english_files = [f for f in self.all_articles.keys() if f.endswith('.en.md')]
        turkish_files = [f for f in self.all_articles.keys() if f.endswith('.tr.md')]

        for en_file in english_files:
            base_name = en_file.replace('.en.md', '')
            tr_file = base_name + '.tr.md'

            if tr_file in turkish_files:
                translation_status['already_translated'].append((en_file, tr_file))
            else:
                translation_status['needs_translation'].append(en_file)

        # Find orphaned Turkish files (no English equivalent)
        for tr_file in turkish_files:
            base_name = tr_file.replace('.tr.md', '')
            en_file = base_name + '.en.md'

            if en_file not in english_files:
                translation_status['orphaned_turkish'].append(tr_file)

        return translation_status

def generate_duplicate_report():
    """Generate comprehensive duplicate report"""
    detector = DuplicateDetector()
    detector.scan_all_articles()

    print("\n" + "="*60)
    print("📋 DUPLICATE CONTENT REPORT")
    print("="*60)

    # Exact duplicates
    exact_duplicates = detector.find_exact_duplicates()
    print(f"\n🔴 EXACT DUPLICATES: {len(exact_duplicates)}")
    for original, duplicate in exact_duplicates:
        print(f"   Keep: {original}")
        print(f"   Delete: {duplicate}")
        print()

    # Similar content
    similar_groups = detector.find_similar_content()
    print(f"\n🟡 SIMILAR CONTENT GROUPS: {len(similar_groups)}")
    for i, group in enumerate(similar_groups, 1):
        print(f"   Group {i}:")
        for filename in group:
            word_count = detector.all_articles[filename]['word_count']
            title = detector.all_articles[filename]['title'][:50]
            print(f"     - {filename} ({word_count} words) - {title}...")
        print()

    # Translation status
    translation_status = detector.check_translation_status()
    print(f"\n🟢 TRANSLATION STATUS:")
    print(f"   ✅ Already translated: {len(translation_status['already_translated'])}")
    print(f"   ⏳ Needs translation: {len(translation_status['needs_translation'])}")
    print(f"   🔗 Orphaned Turkish: {len(translation_status['orphaned_turkish'])}")

    if translation_status['needs_translation']:
        print(f"\n📝 NEEDS TRANSLATION:")
        for en_file in translation_status['needs_translation'][:10]:  # Show first 10
            title = detector.all_articles[en_file]['title'][:60]
            print(f"   - {en_file} - {title}...")

    # Deletion recommendations
    recommendations = detector.recommend_deletions()
    total_to_delete = (len(recommendations['exact_duplicates']) +
                      len(recommendations['similar_content']))

    print(f"\n🗑️ DELETION RECOMMENDATIONS: {total_to_delete} files")
    print(f"   - Exact duplicates: {len(recommendations['exact_duplicates'])}")
    print(f"   - Similar content: {len(recommendations['similar_content'])}")

    return detector, recommendations

def clean_duplicates(detector, recommendations, confirm=True):
    """Actually delete duplicate files"""
    total_to_delete = (len(recommendations['exact_duplicates']) +
                      len(recommendations['similar_content']))

    if total_to_delete == 0:
        print("✨ No duplicates to delete!")
        return

    if confirm:
        response = input(f"\n⚠️ {total_to_delete} dosya silinecek. Devam etmek istiyor musunuz? (y/N): ")
        if response.lower() != 'y':
            print("❌ İptal edildi")
            return

    deleted_count = 0

    # Delete exact duplicates
    for filename in recommendations['exact_duplicates']:
        file_path = None
        for category_dir in CONTENT_DIR.iterdir():
            potential_path = category_dir / filename
            if potential_path.exists():
                file_path = potential_path
                break

        if file_path and file_path.exists():
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted exact duplicate: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {filename}: {e}")

    # Delete similar content
    for filename in recommendations['similar_content']:
        file_path = None
        for category_dir in CONTENT_DIR.iterdir():
            potential_path = category_dir / filename
            if potential_path.exists():
                file_path = potential_path
                break

        if file_path and file_path.exists():
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted similar content: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {filename}: {e}")

    print(f"\n✅ {deleted_count} duplicate dosya silindi")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Detect and clean duplicate content")
    parser.add_argument("--report-only", action="store_true", help="Only generate report, don't delete")
    parser.add_argument("--auto-clean", action="store_true", help="Clean without confirmation")

    args = parser.parse_args()

    detector, recommendations = generate_duplicate_report()

    if not args.report_only:
        clean_duplicates(detector, recommendations, confirm=not args.auto_clean)
