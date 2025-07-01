#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tüm burçlar için sistematik horoskop içerikleri oluşturan script
"""

import subprocess
import os

# Tüm burçlar
signs = ['koc', 'boga', 'ikizler', 'yengec', 'aslan', 'basak',
         'terazi', 'akrep', 'yay', 'oglak', 'kova', 'balik']

# Tüm tipler
types = ['daily', 'weekly', 'monthly']

def run_command(sign, type_name):
    """Horoskop içeriği oluştur"""
    cmd = [
        'python',
        'scripts/astrology_bot.py',
        '--action', 'horoscope',
        '--sign', sign,
        '--type', type_name,
        '--output', 'content'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print(f"✅ {sign} {type_name} - Başarılı")
            return True
        else:
            print(f"❌ {sign} {type_name} - Hata: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {sign} {type_name} - Exception: {e}")
        return False

def main():
    print("🔮 Tüm burç yorumları oluşturuluyor...")

    success_count = 0
    total_count = len(signs) * len(types)

    for sign in signs:
        print(f"\n📅 {sign.upper()} burcu işleniyor...")
        for type_name in types:
            if run_command(sign, type_name):
                success_count += 1

    print(f"\n🎉 Tamamlandı! {success_count}/{total_count} içerik oluşturuldu.")

if __name__ == "__main__":
    main()
