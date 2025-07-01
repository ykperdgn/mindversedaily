#!/usr/bin/env python3
"""
Eski makalelerin görsellerini güncelleme scripti
"""

import os
import re
import glob
from image_fetcher import ImageFetcher

def extract_frontmatter(content):
    """Frontmatter'ı ayıkla"""
    if not content.startswith('---'):
        return None, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    return parts[1].strip(), parts[2].strip()

def update_frontmatter_image(frontmatter, new_image):
    """Frontmatter'da image değerini güncelle"""
    lines = frontmatter.split('\n')
    updated_lines = []
    image_updated = False

    for line in lines:
        if line.strip().startswith('image:'):
            updated_lines.append(f'image: "{new_image}"')
            image_updated = True
        else:
            updated_lines.append(line)

    if not image_updated:
        # Eğer image field'ı yoksa ekle
        updated_lines.append(f'image: "{new_image}"')

    return '\n'.join(updated_lines)

def get_category_from_path(file_path):
    """Dosya yolundan kategoriyi çıkar"""
    path_parts = file_path.replace('\\', '/').split('/')
    for i, part in enumerate(path_parts):
        if part == 'blog' and i + 1 < len(path_parts):
            return path_parts[i + 1]
    return None

def extract_title_from_frontmatter(frontmatter):
    """Frontmatter'dan title'ı çıkar"""
    for line in frontmatter.split('\n'):
        if line.strip().startswith('title:'):
            title = line.split(':', 1)[1].strip().strip('"\'')
            return title
    return None

def update_old_images():
    """Eski makalelerin görsellerini güncelle"""
    image_fetcher = ImageFetcher()

    # Blog dizinindeki tüm markdown dosyalarını bul
    blog_dir = os.path.join(os.path.dirname(__file__), "..", "src", "content", "blog")

    # Placeholder veya varsayılan görselli dosyaları bul
    patterns_to_update = [
        "blog-placeholder",
        "mindversedaily.com",
        "default.jpg",
        "/assets/blog-placeholder-1.svg"
    ]

    updated_count = 0

    for root, dirs, files in os.walk(blog_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    frontmatter, body = extract_frontmatter(content)
                    if not frontmatter:
                        continue

                    # Mevcut image değerini kontrol et
                    current_image = None
                    for line in frontmatter.split('\n'):
                        if line.strip().startswith('image:'):
                            current_image = line.split(':', 1)[1].strip().strip('"\'')
                            break

                    # Güncellenecek mi kontrol et
                    should_update = False
                    if not current_image:
                        should_update = True
                    else:
                        for pattern in patterns_to_update:
                            if pattern in current_image:
                                should_update = True
                                break

                    if should_update:
                        # Kategori ve başlığı al
                        category = get_category_from_path(file_path)
                        title = extract_title_from_frontmatter(frontmatter)

                        if category and title:
                            # Yeni görsel getir
                            new_image = image_fetcher.get_image_for_content(title, category)

                            if new_image and new_image != "/assets/blog-placeholder-1.svg":
                                # Frontmatter'ı güncelle
                                updated_frontmatter = update_frontmatter_image(frontmatter, new_image)

                                # Dosyayı güncelle
                                new_content = f"---\n{updated_frontmatter}\n---\n\n{body}"

                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)

                                print(f"✅ Updated {file}: {new_image}")
                                updated_count += 1
                            else:
                                print(f"❌ No image found for {file}")
                        else:
                            print(f"⚠️ Could not extract category/title from {file}")

                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")

    print(f"\n🎉 Updated {updated_count} files with new images!")

if __name__ == "__main__":
    update_old_images()
