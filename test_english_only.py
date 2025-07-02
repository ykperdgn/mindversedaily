#!/usr/bin/env python3
"""
Test English-only content generation - 2 articles per category for testing
"""

import os
import sys
import requests

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from bulk_content_generator import generate_english_content_only

    print("🧪 Testing ENGLISH-ONLY content generation...")

    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        print("✅ Ollama is running")
    except:
        print("❌ Ollama is not running. Please start Ollama first!")
        exit(1)

    # Temporarily reduce the number for testing
    import bulk_content_generator
    original_count = bulk_content_generator.ARTICLES_PER_CATEGORY
    bulk_content_generator.ARTICLES_PER_CATEGORY = 2  # Just 2 per category for testing

    print("🇺🇸 Generating quality English content for international audience...")
    result = generate_english_content_only()

    # Restore original count
    bulk_content_generator.ARTICLES_PER_CATEGORY = original_count

    print(f"✅ Test completed! Created {result} unique English articles")
    print("🌍 Perfect for international visitors!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
