#!/usr/bin/env python3
"""Test actual image generation and saving to output folder."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from deck_factory.core.config import ConfigLoader
from deck_factory.ai.gemini_client import GeminiClient


async def main():
    """Test image generation and saving."""
    print("="*80)
    print("IMAGE GENERATION TEST")
    print("="*80)
    print()

    # Step 1: Load config
    print("Step 1: Loading configuration...")
    try:
        config = ConfigLoader.from_env()
        print(f"✓ Config loaded")
        print(f"✓ Output directory: {config.output_dir}")
        print(f"✓ API key: {config.gemini_api_key[:20]}...")
        print()
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        sys.exit(1)

    # Step 2: Create client
    print("Step 2: Initializing Gemini client...")
    try:
        client = GeminiClient(config.gemini_api_key, max_concurrent=5)
        print(f"✓ GeminiClient created")
        print(f"✓ Text model: {client.flash_model}")
        print(f"✓ Image model: {client.image_model}")
        print()
    except Exception as e:
        print(f"✗ Failed to create client: {e}")
        sys.exit(1)

    # Step 3: Generate test image
    print("Step 3: Generating test image...")
    print("  Prompt: 'A professional business meeting in a modern office'")
    print("  Aspect ratio: 16:9")
    print("  This will take 5-10 seconds...")
    print()

    try:
        image_data = await client.generate_image(
            prompt="A professional business meeting in a modern office, "
                   "with people collaborating around a conference table, "
                   "natural lighting, photorealistic style",
            reference_images=None,
            aspect_ratio="16:9",
            image_size="2K",
            number_of_images=1
        )

        print(f"✓ Image generated successfully!")
        print(f"✓ Image size: {len(image_data):,} bytes ({len(image_data)/1024:.1f} KB)")
        print()

    except Exception as e:
        print(f"✗ Failed to generate image: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 4: Save to output folder
    print("Step 4: Saving image to output folder...")
    try:
        # Create output directory if it doesn't exist
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"test_image_{timestamp}.png"

        # Save image
        with open(output_path, 'wb') as f:
            f.write(image_data)

        print(f"✓ Image saved successfully!")
        print(f"✓ File path: {output_path}")
        print(f"✓ File size: {output_path.stat().st_size:,} bytes")
        print()

        # Verify file exists and is readable
        if output_path.exists() and output_path.is_file():
            print("✓ File verification successful")
            print(f"✓ File is readable: {output_path.stat().st_size > 0}")
        else:
            print("✗ File verification failed")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Failed to save image: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 5: Summary
    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("✓ Configuration loaded")
    print("✓ GeminiClient initialized")
    print("✓ Image generated via API")
    print("✓ Image saved to disk")
    print("✓ File verification passed")
    print()
    print(f"Test image saved to: {output_path}")
    print()
    print("="*80)
    print("✓ ALL TESTS PASSED - IMAGE GENERATION WORKING!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
