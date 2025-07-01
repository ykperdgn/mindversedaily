#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindVerse Astroloji Bot - Horoskop ve Astroloji Yorumları
Gelişmiş burç yorumları, doğum haritası analizi ve astrolojik tahminler
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

# Set UTF-8 encoding for stdout
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class AstrologyBot:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        self.api_base = "https://api.groq.com/openai/v1"

        # Burç bilgileri
        self.zodiac_signs = {
            'koc': {'name': 'Koç', 'emoji': '♈', 'element': 'Ateş', 'dates': '21 Mart - 19 Nisan'},
            'boga': {'name': 'Boğa', 'emoji': '♉', 'element': 'Toprak', 'dates': '20 Nisan - 20 Mayıs'},
            'ikizler': {'name': 'İkizler', 'emoji': '♊', 'element': 'Hava', 'dates': '21 Mayıs - 20 Haziran'},
            'yengec': {'name': 'Yengeç', 'emoji': '♋', 'element': 'Su', 'dates': '21 Haziran - 22 Temmuz'},
            'aslan': {'name': 'Aslan', 'emoji': '♌', 'element': 'Ateş', 'dates': '23 Temmuz - 22 Ağustos'},
            'basak': {'name': 'Başak', 'emoji': '♍', 'element': 'Toprak', 'dates': '23 Ağustos - 22 Eylül'},
            'terazi': {'name': 'Terazi', 'emoji': '♎', 'element': 'Hava', 'dates': '23 Eylül - 22 Ekim'},
            'akrep': {'name': 'Akrep', 'emoji': '♏', 'element': 'Su', 'dates': '23 Ekim - 21 Kasım'},
            'yay': {'name': 'Yay', 'emoji': '♐', 'element': 'Ateş', 'dates': '22 Kasım - 21 Aralık'},
            'oglak': {'name': 'Oğlak', 'emoji': '♑', 'element': 'Toprak', 'dates': '22 Aralık - 19 Ocak'},
            'kova': {'name': 'Kova', 'emoji': '♒', 'element': 'Hava', 'dates': '20 Ocak - 18 Şubat'},
            'balik': {'name': 'Balık', 'emoji': '♓', 'element': 'Su', 'dates': '19 Şubat - 20 Mart'}
        }

        # Astrolojik terimler
        self.astrological_terms = {
            'ascendant': 'Yükselen Burç',
            'retrograde': 'Retrograd',
            'conjunction': 'Kavuşum',
            'opposition': 'Karşıtlık',
            'trine': 'Üçlü',
            'square': 'Dörtlü'
        }

    def generate_daily_horoscope(self, sign: str, date: str = None) -> Dict:
        """Günlük burç yorumu üret"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        sign_info = self.zodiac_signs.get(sign.lower())
        if not sign_info:
            return {"error": "Geçersiz burç"}

        prompt = f"""
        {sign_info['name']} burcu için {date} tarihinde günlük horoskop yorumu yaz.

        Aşağıdaki konuları kapsa:
        - Genel enerji durumu
        - Aşk ve ilişkiler
        - Kariyer ve iş
        - Sağlık ve enerji
        - Şanslı sayı ve renk
        - Önemli astrolojik geçişler

        Pozitif ve motive edici bir dil kullan. 200-300 kelime arası olsun.
        Markdown formatında yaz.
        """

        return self._call_groq_api(prompt)

    def generate_weekly_horoscope(self, sign: str, week_start: str = None) -> Dict:
        """Haftalık burç yorumu üret"""
        if not week_start:
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            week_start = monday.strftime("%Y-%m-%d")

        sign_info = self.zodiac_signs.get(sign.lower())
        if not sign_info:
            return {"error": "Geçersiz burç"}

        prompt = f"""
        {sign_info['name']} burcu için {week_start} haftası detaylı haftalık horoskop analizi yaz.

        Kapsamlı analiz içersin:
        - Haftanın genel enerji akışı
        - Günlük detaylı öngörüler (Pazartesi-Pazar)
        - Aşk hayatında önemli gelişmeler
        - Kariyer fırsatları ve zorluklar
        - Finansal durum
        - Sağlık önerileri
        - Astrolojik geçişlerin etkileri
        - Haftanın en şanslı günü
        - Dikkat edilmesi gereken konular

        Profesyonel astroloji dili kullan. 400-500 kelime arası.
        Markdown formatında yaz ve emoji kullan.
        """

        return self._call_groq_api(prompt)

    def generate_monthly_horoscope(self, sign: str, month: str, year: str) -> Dict:
        """Aylık burç yorumu üret"""
        sign_info = self.zodiac_signs.get(sign.lower())
        if not sign_info:
            return {"error": "Geçersiz burç"}

        prompt = f"""
        {sign_info['name']} burcu için {month} {year} ayı kapsamlı aylık horoskop analizi yaz.

        Detaylı analiz kapsamı:
        - Ayın genel teması ve enerji akışı
        - Önemli astrolojik olaylar (Yeni Ay, Dolunay, gezegen geçişleri)
        - Aşk ve ilişkilerde beklentiler
        - Kariyer ve iş hayatında fırsatlar
        - Finansal planlama önerileri
        - Sağlık ve enerji yönetimi
        - Kişisel gelişim önerileri
        - Ayın kritik tarihleri
        - Şanslı dönemler
        - Dikkatli olunması gereken zamanlar

        Derinlemesine astrolojik analiz yap. 600-800 kelime arası.
        Markdown formatında ve profesyonel dil kullan.
        """

        return self._call_groq_api(prompt)

    def generate_cosmic_forecast(self, period: str = "week") -> Dict:
        """Genel kozmik öngörü"""
        prompt = f"""
        Önümüzdeki {period} için genel astrolojik öngörü ve kozmik enerji analizi yaz.

        Kapsamlı analiz:
        - Önemli gezegen hareketleri
        - Yeni Ay ve Dolunay etkileri
        - Tüm burçları etkileyecek genel eğilimler
        - Retrograd gezegen etkileri
        - Enerji yönetimi önerileri
        - Manevi gelişim fırsatları
        - Dikkat edilmesi gereken dönemler
        - Manifestasyon için uygun zamanlar

        Bütüncül bir yaklaşım kullan. 400-600 kelime.
        Markdown formatında ve mistik dil kullan.
        """

        return self._call_groq_api(prompt)

    def analyze_compatibility(self, sign1: str, sign2: str) -> Dict:
        """İki burç arasında uyumluluk analizi"""
        sign1_info = self.zodiac_signs.get(sign1.lower())
        sign2_info = self.zodiac_signs.get(sign2.lower())

        if not sign1_info or not sign2_info:
            return {"success": False, "error": "Geçersiz burç"}

        # Mock uyumluluk analizi
        compatibility_scores = {
            ('koc', 'aslan'): 95, ('koc', 'yay'): 90, ('koc', 'ikizler'): 85,
            ('boga', 'basak'): 95, ('boga', 'oglak'): 90, ('boga', 'balik'): 80,
            ('ikizler', 'terazi'): 95, ('ikizler', 'kova'): 90, ('ikizler', 'aslan'): 85,
            ('yengec', 'akrep'): 95, ('yengec', 'balik'): 90, ('yengec', 'boga'): 80,
            ('aslan', 'yay'): 95, ('aslan', 'koc'): 90, ('aslan', 'ikizler'): 85,
            ('basak', 'oglak'): 95, ('basak', 'boga'): 90, ('basak', 'akrep'): 80,
            ('terazi', 'kova'): 95, ('terazi', 'ikizler'): 90, ('terazi', 'aslan'): 85,
            ('akrep', 'balik'): 95, ('akrep', 'yengec'): 90, ('akrep', 'boga'): 80,
            ('yay', 'koc'): 95, ('yay', 'aslan'): 90, ('yay', 'terazi'): 85,
            ('oglak', 'boga'): 95, ('oglak', 'basak'): 90, ('oglak', 'akrep'): 80,
            ('kova', 'ikizler'): 95, ('kova', 'terazi'): 90, ('kova', 'yay'): 85,
            ('balik', 'yengec'): 95, ('balik', 'akrep'): 90, ('balik', 'oglak'): 80
        }

        # Uyumluluk skorunu bul
        pair = (sign1.lower(), sign2.lower())
        reverse_pair = (sign2.lower(), sign1.lower())
        score = compatibility_scores.get(pair, compatibility_scores.get(reverse_pair, 75))

        # Element uyumluluğu
        element_compatibility = {
            ('Ateş', 'Ateş'): 'Yüksek enerji, tutkulu ilişki',
            ('Ateş', 'Hava'): 'Dinamik ve heyecanlı bağ',
            ('Ateş', 'Toprak'): 'Kararlılık ve tutku dengesi',
            ('Ateş', 'Su'): 'Karşıtlıklar çeken güçlü bağ',
            ('Toprak', 'Toprak'): 'İstikrarlı ve güvenli ilişki',
            ('Toprak', 'Su'): 'Derin ve besleyici bağ',
            ('Hava', 'Hava'): 'Zihinsel uyum ve iletişim',
            ('Hava', 'Su'): 'Duygusal ve entelektüel denge',
            ('Su', 'Su'): 'Derin duygusal bağlantı'
        }

        element_pair = (sign1_info['element'], sign2_info['element'])
        element_desc = element_compatibility.get(element_pair,
                       element_compatibility.get((sign2_info['element'], sign1_info['element']),
                       'Dengeli bir ilişki potansiyeli'))

        return {
            "success": True,
            "compatibility_score": score,
            "sign1": {"name": sign1_info['name'], "emoji": sign1_info['emoji'], "element": sign1_info['element']},
            "sign2": {"name": sign2_info['name'], "emoji": sign2_info['emoji'], "element": sign2_info['element']},
            "element_compatibility": element_desc,
            "general_analysis": f"{sign1_info['name']} ve {sign2_info['name']} arasında %{score} uyumluluk. " +
                               element_desc + " Bu ilişkide karşılıklı anlayış ve sabır anahtardır."
        }

    def _call_groq_api(self, prompt: str) -> Dict:
        """Groq API çağrısı"""
        if not self.groq_api_key:
            # Test modu - API key yoksa örnek içerik döndür
            return self._generate_mock_response(prompt)

        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [
                {
                    "role": "system",
                    "content": "Sen uzman bir astroloğ ve burç yorumcususun. Derinlemesine astroloji bilgin var ve insanları motive edici, pozitif yorumlar yapıyorsun. Türkçe yazmaya odaklan."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "content": result['choices'][0]['message']['content']
                }
            else:
                return {"error": f"API hatası: {response.status_code}"}

        except Exception as e:
            return {"error": f"İstek hatası: {str(e)}"}

    def _generate_mock_response(self, prompt: str) -> Dict:
        """Test için örnek yanıt oluştur"""
        sign_templates = {
            'weekly': """## 🔮 Bu Hafta Sizin İçin

**Genel Enerji:** Bu hafta enerjiniz yüksek olacak ve yeni fırsatlar kapınızı çalacak.

### ❤️ Aşk ve İlişkiler
- Romantik gelişmeler sizi bekliyor
- İletişim kanalları açık
- Duygusal bağlılık güçlenecek

### 💼 Kariyer ve İş
- Yaratıcı projelerinizde ilerleme
- Yeni iş bağlantıları
- Başarı için ideal zaman

### 🍀 Şanslı Detaylar
- **En Şanslı Gün:** Çarşamba
- **Şanslı Renk:** Mavi
- **Şanslı Sayı:** 7

*Yıldızlar size rehberlik ediyor, sezgilerinize güvenin!*""",

            'daily': """## ⭐ Bugün Sizin İçin

**Genel Durum:** Bugün pozitif enerjiler etrafınızı saracak.

- 🌅 Sabah: Yeni başlangıçlar için ideal
- 🌞 Öğlen: Sosyal aktivitelere odaklanın
- 🌙 Akşam: Sevdiklerinizle kaliteli zaman

**Dikkat:** Aşırı aceleci davranmaktan kaçının.""",

            'monthly': """## 🌙 Bu Ay Sizin İçin

**Genel Tema:** Dönüşüm ve yenilenme ayı

### 📅 Önemli Tarihler
- **5-10:** Yeni fırsatlar dönemi
- **15-20:** Duygusal yoğunluk
- **25-30:** Başarı zamanı

### 🎯 Odaklanmanız Gerekenler
1. Kişisel gelişim
2. İlişkilerde denge
3. Kariyer hedefleri

*Bu ay sizin için büyük değişimler getirecek!*"""
        }

        # Prompt'tan tür belirle
        if 'günlük' in prompt.lower() or 'daily' in prompt.lower():
            template = sign_templates['daily']
        elif 'aylık' in prompt.lower() or 'monthly' in prompt.lower():
            template = sign_templates['monthly']
        else:
            template = sign_templates['weekly']

        return {
            "success": True,
            "content": template
        }

    def create_horoscope_content(self, sign: str, type: str = "weekly") -> tuple:
        """Blog yazısı formatında horoskop içeriği oluştur"""
        sign_info = self.zodiac_signs.get(sign.lower())
        if not sign_info:
            return None

        today = datetime.now()

        if type == "daily":
            result = self.generate_daily_horoscope(sign)
            title = f"{sign_info['name']} Burcu Günlük Yorumu - {today.strftime('%d %B %Y')}"
            filename = f"{today.strftime('%Y-%m-%d')}-{sign}-burcu-gunluk-yorum.tr.md"
        elif type == "weekly":
            result = self.generate_weekly_horoscope(sign)
            title = f"{sign_info['name']} Burcu Haftalık Yorumu - {today.strftime('%d %B %Y')}"
            filename = f"{today.strftime('%Y-%m-%d')}-{sign}-burcu-haftalik-yorum.tr.md"
        elif type == "monthly":
            result = self.generate_monthly_horoscope(sign, today.strftime('%B'), today.strftime('%Y'))
            title = f"{sign_info['name']} Burcu Aylık Yorumu - {today.strftime('%B %Y')}"
            filename = f"{today.strftime('%Y-%m-%d')}-{sign}-burcu-aylik-yorum.tr.md"

        if "error" in result:
            return None

        # Markdown içerik oluştur
        content = f"""---
title: "{title}"
description: "{sign_info['name']} burcu için detaylı {type} astroloji yorumu. Aşk, kariyer, sağlık ve genel enerji analizi."
pubDate: {today.strftime('%Y-%m-%d')}
category: "horoscope"
tags: ["{sign}", "{type}", "burç yorumu", "astroloji"]
image: "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=800&h=600&fit=crop"
---

{result['content']}

---

*Bu yorum genel astrolojik eğilimlere dayanır. Kişisel doğum haritanız için detaylı analiz yaptırabilirsiniz.*

## 🔮 Diğer Burç Yorumları

Diğer burçların {type} yorumlarını da okuyabilirsiniz:

{self._generate_related_signs_links(sign, type)}
"""

        return content, filename

    def _generate_related_signs_links(self, current_sign: str, type: str) -> str:
        """İlgili burç bağlantıları oluştur"""
        links = []
        for sign_key, sign_info in self.zodiac_signs.items():
            if sign_key != current_sign.lower():
                links.append(f"- [{sign_info['emoji']} {sign_info['name']} Burcu](/blog/horoscope/{sign_key}-{type})")

        return "\n".join(links[:6])  # İlk 6 burcu göster

def main():
    """Ana fonksiyon - komut satırı ve API desteği"""
    import argparse

    parser = argparse.ArgumentParser(description='MindVerse Astrology Bot')
    parser.add_argument('--action', choices=['horoscope', 'compatibility', 'birth-chart', 'cosmic-forecast'], required=True)
    parser.add_argument('--sign', help='Zodiac sign')
    parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], help='Horoscope type')
    parser.add_argument('--language', default='tr', help='Language (tr/en)')
    parser.add_argument('--sign1', help='First sign for compatibility')
    parser.add_argument('--sign2', help='Second sign for compatibility')
    parser.add_argument('--period', default='week', help='Forecast period')
    parser.add_argument('--output', choices=['json', 'content'], default='json', help='Output format')

    args = parser.parse_args()
    bot = AstrologyBot()

    try:
        if args.action == 'horoscope':
            if args.output == 'content':
                # Dosya oluşturma modu
                result = bot.create_horoscope_content(args.sign, args.type)
                if result:
                    content, filename = result
                    print(f"Generated: {filename}")
                    print(content[:500] + "...")
                else:
                    print("Content generation failed!")
            else:
                # JSON API modu
                if args.type == 'daily':
                    result = bot.generate_daily_horoscope(args.sign)
                elif args.type == 'weekly':
                    result = bot.generate_weekly_horoscope(args.sign)
                elif args.type == 'monthly':
                    today = datetime.now()
                    result = bot.generate_monthly_horoscope(args.sign, today.strftime('%B'), today.strftime('%Y'))
                else:
                    result = {"error": "Invalid horoscope type"}

                print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.action == 'compatibility':
            result = bot.analyze_compatibility(args.sign1, args.sign2)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.action == 'birth-chart':
            # Mock doğum haritası analizi
            result = {
                "success": True,
                "analysis": "Doğum haritası analizi geliştirme aşamasında...",
                "elements": ["Güneş: Aslan", "Ay: Balık", "Yükselen: Terazi"]
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif args.action == 'cosmic-forecast':
            result = bot.generate_cosmic_forecast(args.period)
            print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        print(json.dumps(error_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
