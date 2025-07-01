#!/usr/bin/env python3
"""
Eski görselleri güncelleme ve Ollama entegrasyonu
"""

import os
import re
import glob
from image_fetcher import ImageFetcher

def fix_old_images():
    """Eski görsel URL'lerini API'den yeni olanlarla değiştir"""
    image_fetcher = ImageFetcher()
    updated_count = 0

    # Tüm markdown dosyalarını tara
    for root, dirs, files in os.walk("src/content/blog"):
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)

                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Frontmatter'ı ayıkla
                if not content.startswith('---'):
                    continue

                parts = content.split('---', 2)
                if len(parts) < 3:
                    continue

                frontmatter = parts[1].strip()
                article_content = parts[2].strip()

                # Mevcut image URL'sini kontrol et
                image_match = re.search(r'image: ["\']([^"\']*)["\']', frontmatter)
                if not image_match:
                    continue

                current_image = image_match.group(1)

                # Eski format URL'leri tespit et
                needs_update = (
                    'unsplash.com' in current_image or
                    'upload.wikimedia.org' in current_image or
                    'cdn.pixabay.com' in current_image or
                    'www.pexels.com' in current_image or
                    'www.nasa.gov' in current_image or
                    '/assets/' in current_image or
                    'mindversedaily.com' in current_image
                )

                if needs_update:
                    # Başlık ve kategoriyi çıkar
                    title_match = re.search(r'title: ["\']([^"\']*)["\']', frontmatter)
                    category_match = re.search(r'category: ["\']([^"\']*)["\']', frontmatter)

                    if title_match and category_match:
                        title = title_match.group(1)
                        category = category_match.group(1)

                        # Yeni görsel al
                        new_image = image_fetcher.get_image_for_content(title, category)

                        if new_image and new_image != current_image:
                            # Frontmatter'ı güncelle
                            new_frontmatter = re.sub(
                                r'image: ["\'][^"\']*["\']',
                                f'image: "{new_image}"',
                                frontmatter
                            )

                            # Dosyayı güncelle
                            new_content = f"---\n{new_frontmatter}\n---\n\n{article_content}"

                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)

                            print(f"✅ Updated {file}: {new_image}")
                            updated_count += 1
                        else:
                            print(f"⚠️ Could not get new image for {file}")

    print(f"\n🎉 Updated {updated_count} files with new images!")

if __name__ == "__main__":
    fix_old_images()
