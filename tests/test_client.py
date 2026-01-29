#!/usr/bin/env python3
"""Quick test of GeminiClient to verify API integration."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from deck_factory.core.config import ConfigLoader
from deck_factory.ai.gemini_client import GeminiClient


async def test_text_generation():
    """Test text generation with JSON response."""
    print("Testing text generation with JSON response...")

    # Load config
    config = ConfigLoader.from_env()
    print(f"✓ Loaded config with API key: {config.gemini_api_key[:20]}...")

    # Create client
    client = GeminiClient(config.gemini_api_key, max_concurrent=5)
    print("✓ Created GeminiClient")

    # Test simple JSON generation
    prompt = """Generate a simple JSON object with the following structure:
{
  "title": "Test Presentation",
  "slide_count": 3,
  "topics": ["Introduction", "Main Content", "Conclusion"]
}
"""

    try:
        response = await client.generate_text(
            prompt=prompt,
            response_mime_type="application/json",
            temperature=0.7
        )
        print(f"✓ Received response ({len(response)} chars)")
        print("\nResponse:")
        print(response[:500])  # Print first 500 chars

        # Try to parse as JSON
        import json
        data = json.loads(response)
        print("\n✓ Successfully parsed as JSON!")
        print(f"  Title: {data.get('title')}")
        print(f"  Slide count: {data.get('slide_count')}")
        print(f"  Topics: {data.get('topics')}")

        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_image_generation():
    """Test image generation (without actual execution to save quota)."""
    print("\n" + "="*80)
    print("Testing image generation setup...")

    # Load config
    config = ConfigLoader.from_env()

    # Create client
    client = GeminiClient(config.gemini_api_key, max_concurrent=5)
    print("✓ GeminiClient initialized for image generation")

    # Check method signature
    import inspect
    sig = inspect.signature(client.generate_image)
    params = list(sig.parameters.keys())
    print(f"✓ generate_image() parameters: {params}")

    # Verify number_of_images parameter exists
    if 'number_of_images' in params:
        print("✓ number_of_images parameter present (compatibility fix working)")
    else:
        print("✗ number_of_images parameter missing!")
        return False

    print("\n✓ Image generation setup looks correct")
    print("  (Skipping actual image generation to save API quota)")

    return True


async def main():
    """Run all tests."""
    print("="*80)
    print("GEMINI CLIENT TEST SUITE")
    print("="*80)
    print()

    # Test 1: Text generation with JSON
    text_ok = await test_text_generation()

    # Test 2: Image generation setup
    image_ok = await test_image_generation()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Text generation (JSON): {'✓ PASS' if text_ok else '✗ FAIL'}")
    print(f"Image generation setup: {'✓ PASS' if image_ok else '✗ FAIL'}")

    if text_ok and image_ok:
        print("\n✓ All tests passed! GeminiClient is ready.")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
