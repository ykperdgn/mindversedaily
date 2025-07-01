import os
import requests
import random
import time
import json
import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

class ImageFetcher:
    def __init__(self):
        self.pixabay_key = os.getenv('PIXABAY_API_KEY')
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.nasa_api_url = os.getenv('NASA_API_KEY', 'https://images-api.nasa.gov')

        # Kullanılan görsel URL'lerini takip et
        self.used_images_file = 'used_images.json'
        self.used_images = self.load_used_images()

    def load_used_images(self):
        """Daha önce kullanılan görselleri yükle"""
        if os.path.exists(self.used_images_file):
            with open(self.used_images_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_used_images(self):
        """Kullanılan görselleri kaydet"""
        with open(self.used_images_file, 'w', encoding='utf-8') as f:
            json.dump(self.used_images, f, indent=2)

    def add_used_image(self, image_url):
        """Kullanılan görsel listesine ekle"""
        if image_url not in self.used_images:
            self.used_images.append(image_url)
            self.save_used_images()

    def get_pixabay_image(self, keywords, category=None):
        """Pixabay'den görsel al"""
        if not self.pixabay_key:
            return None

        # Kategori bazlı anahtar kelimeler
        category_keywords = {
            'health': ['health', 'medical', 'wellness', 'fitness', 'medicine', 'doctor', 'hospital'],
            'psychology': ['brain', 'mind', 'psychology', 'mental', 'therapy', 'meditation', 'consciousness'],
            'history': ['ancient', 'historical', 'museum', 'archaeology', 'civilization', 'monument'],
            'space': ['space', 'planet', 'galaxy', 'stars', 'astronomy', 'cosmos', 'universe'],
            'quotes': ['inspiration', 'motivation', 'wisdom', 'books', 'writing', 'light', 'nature'],
            'love': ['love', 'heart', 'romance', 'couple', 'relationship', 'affection', 'together']
        }

        # Kategori için ek anahtar kelimeler ekle
        search_terms = keywords.lower()
        if category and category in category_keywords:
            search_terms += f" {random.choice(category_keywords[category])}"

        try:
            url = "https://pixabay.com/api/"
            params = {
                'key': self.pixabay_key,
                'q': search_terms,
                'image_type': 'photo',
                'category': 'backgrounds,science,education,health,people',
                'min_width': 800,
                'min_height': 400,
                'safesearch': 'true',
                'per_page': 20,
                'order': 'popular'
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['hits']:
                    # Kullanılmamış görselleri filtrele
                    unused_images = [img for img in data['hits'] if img['webformatURL'] not in self.used_images]
                    if unused_images:
                        image = random.choice(unused_images)
                        image_url = image['webformatURL']
                        self.add_used_image(image_url)
                        return {
                            'url': image_url,
                            'description': f"Photo by {image.get('user', 'Unknown')} from Pixabay",
                            'source': 'Pixabay'
                        }

        except Exception as e:
            print(f"Pixabay API error: {e}")

        return None

    def get_pexels_image(self, keywords, category=None):
        """Pexels'dan görsel al"""
        if not self.pexels_key:
            return None

        # Kategori bazlı anahtar kelimeler
        category_keywords = {
            'health': ['healthcare', 'medical', 'wellness', 'fitness', 'nutrition'],
            'psychology': ['brain', 'mind', 'mental health', 'meditation', 'therapy'],
            'history': ['ancient', 'historical', 'architecture', 'culture', 'museum'],
            'space': ['space', 'astronomy', 'planets', 'stars', 'galaxy'],
            'quotes': ['inspiration', 'books', 'wisdom', 'nature', 'light'],
            'love': ['love', 'heart', 'romance', 'relationships', 'couple']
        }

        # Kategori için ek anahtar kelimeler ekle
        search_terms = keywords.lower()
        if category and category in category_keywords:
            search_terms += f" {random.choice(category_keywords[category])}"

        try:
            url = f"https://api.pexels.com/v1/search"
            headers = {'Authorization': self.pexels_key}
            params = {
                'query': search_terms,
                'per_page': 20,
                'page': 1,
                'size': 'large'
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['photos']:
                    # Kullanılmamış görselleri filtrele
                    unused_images = [img for img in data['photos'] if img['src']['large'] not in self.used_images]
                    if unused_images:
                        image = random.choice(unused_images)
                        image_url = image['src']['large']
                        self.add_used_image(image_url)
                        return {
                            'url': image_url,
                            'description': f"Photo by {image['photographer']} from Pexels",
                            'source': 'Pexels'
                        }

        except Exception as e:
            print(f"Pexels API error: {e}")

        return None

    def get_nasa_image(self, keywords):
        """NASA'dan görsel al (space kategorisi için)"""
        if not keywords.lower() in ['space', 'astronomy', 'planet', 'mars', 'earth', 'galaxy', 'star']:
            return None

        try:
            # NASA Images API kullan
            search_terms = keywords.replace(' ', '%20')
            url = f"https://images-api.nasa.gov/search?q={search_terms}&media_type=image"

            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['collection']['items']:
                    # Kullanılmamış görselleri filtrele
                    items = data['collection']['items']
                    for item in random.sample(items, min(10, len(items))):
                        if 'links' in item and item['links']:
                            image_url = item['links'][0]['href']
                            if image_url not in self.used_images:
                                self.add_used_image(image_url)
                                title = item['data'][0].get('title', 'NASA Image')
                                return {
                                    'url': image_url,
                                    'description': f"NASA Image: {title}",
                                    'source': 'NASA'
                                }

        except Exception as e:
            print(f"NASA API error: {e}")

        return None

    def get_image_for_content(self, title, category, description=None):
        """İçerik için en uygun görseli bul"""

        # Başlıktan anahtar kelimeler çıkar
        keywords = self.extract_keywords(title, category)

        # Farklı API'leri dene
        apis = []

        # Space kategorisi için NASA'yı önceliklendir
        if category == 'space':
            apis = ['nasa', 'pixabay', 'pexels']
        else:
            apis = ['pexels', 'pixabay']

        for api in apis:
            try:
                image = None
                if api == 'pixabay':
                    image = self.get_pixabay_image(keywords, category)
                elif api == 'pexels':
                    image = self.get_pexels_image(keywords, category)
                elif api == 'nasa':
                    image = self.get_nasa_image(keywords)

                if image:
                    print(f"✅ Found image from {api}: {image['source']}")
                    return image['url']

                # API rate limiting için bekle
                time.sleep(1)

            except Exception as e:
                print(f"Error with {api}: {e}")
                continue

        # Hiç görsel bulunamazsa varsayılan SVG'yi döndür
        print("❌ No suitable image found, using placeholder")
        return "/assets/blog-placeholder-1.svg"

    def extract_keywords(self, title, category):
        """Başlıktan anahtar kelimeler çıkar"""
        # Ortak kelimeleri filtrele
        stop_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an']

        # Başlığı kelimelerine ayır ve temizle
        words = title.lower().replace('-', ' ').replace(':', '').split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # İlk 3-4 anahtar kelimeyi al
        return ' '.join(keywords[:4])

# Test fonksiyonu
if __name__ == "__main__":
    fetcher = ImageFetcher()
    test_image = fetcher.get_image_for_content(
        "The Future of Space Exploration",
        "space",
        "Exploring new frontiers in space technology"
    )
    print(f"Test image URL: {test_image}")
