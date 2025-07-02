#!/usr/bin/env python3
"""
Test Turkish translation
"""

import os
import sys
import requests

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from bulk_content_generator import translate_to_turkish

    print("🧪 Testing Turkish translation...")

    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        print("✅ Ollama is running")
    except:
        print("❌ Ollama is not running. Please start Ollama first!")
        exit(1)

    print("🇹🇷 Translating to Turkish...")
    result = translate_to_turkish()

    print(f"✅ Translation test completed! Created {result} Turkish articles")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
