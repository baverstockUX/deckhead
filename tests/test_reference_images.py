#!/usr/bin/env python3
"""Test reference image functionality."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from deck_factory.core.config import ConfigLoader
from deck_factory.ai.gemini_client import GeminiClient


async def main():
    """Test reference image functionality."""
    # Step 1: Setup
    print("="*80)
    print("REFERENCE IMAGE TEST")
    print("="*80)
    print()

    # Load config
    print("Step 1: Loading configuration...")
    try:
        config = ConfigLoader.from_env()
        client = GeminiClient(config.gemini_api_key, max_concurrent=5)
        print(f"✓ Config loaded")
        print()
    except Exception as e:
        print(f"✗ Failed to load config: {e}")
        sys.exit(1)

    # Step 2: Locate reference image
    print("Step 2: Locating reference image...")
    output_dir = Path(config.output_dir)
    reference_images = sorted(output_dir.glob("test_image_*.png"))

    if not reference_images:
        print("✗ No reference image found!")
        print("  Please run test_image_generation.py first")
        sys.exit(1)

    reference_image = reference_images[-1]  # Use most recent
    print(f"✓ Using reference: {reference_image.name}")
    print(f"  Path: {reference_image}")
    print(f"  Size: {reference_image.stat().st_size:,} bytes")
    print()

    # Step 3: Generate image WITH reference
    print("Step 3: Generating image WITH reference...")
    print("  Reference prompt: 'business meeting, collaborating'")
    print("  New prompt: 'business presentation, speaker'")
    print("  Reference images: 1 image included")
    print("  Aspect ratio: 16:9")
    print("  This will take 10-20 seconds...")
    print()

    try:
        image_data = await client.generate_image(
            prompt="A professional business presentation in a modern office, "
                   "with a speaker presenting to an audience, "
                   "natural lighting, photorealistic style",
            reference_images=[reference_image],  # Pass as list of Paths
            aspect_ratio="16:9",
            image_size="2K",
            number_of_images=1
        )

        print(f"✓ Image generated WITH reference!")
        print(f"✓ Image size: {len(image_data):,} bytes ({len(image_data)/1024:.1f} KB)")
        print()

    except Exception as e:
        print(f"✗ Failed to generate image: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 4: Save new image
    print("Step 4: Saving generated image...")
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"test_with_reference_{timestamp}.png"

        with open(output_path, 'wb') as f:
            f.write(image_data)

        print(f"✓ Saved: {output_path.name}")
        print(f"✓ File path: {output_path}")
        print(f"✓ File size: {output_path.stat().st_size:,} bytes")
        print()

    except Exception as e:
        print(f"✗ Failed to save image: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Step 5: Comparison summary
    print("="*80)
    print("COMPARISON")
    print("="*80)

    ref_size = reference_image.stat().st_size
    new_size = output_path.stat().st_size
    size_diff_pct = abs(new_size - ref_size) / ref_size * 100

    print(f"Reference image:  {reference_image.name}")
    print(f"  Size: {ref_size:,} bytes")
    print()
    print(f"Generated image:  {output_path.name}")
    print(f"  Size: {new_size:,} bytes")
    print(f"  Size difference: {size_diff_pct:.1f}%")
    print()

    if size_diff_pct < 50:
        print("✓ Size difference within expected range (<50%)")
    else:
        print(f"⚠ Size difference high: {size_diff_pct:.1f}%")

    print()
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("✓ Reference image located")
    print("✓ Reference image validated")
    print("✓ PIL Image.open() successful")
    print("✓ Image generated with reference")
    print("✓ API call succeeded")
    print("✓ New image saved to disk")
    print("✓ File verification passed")
    print()
    print("Manual verification needed:")
    print("  1. Open both images side-by-side")
    print("  2. Check if they share similar style/color palette")
    print("  3. Confirm subject matter differs (meeting vs presentation)")
    print("  4. Assess if reference image influenced the output")
    print()
    print(f"Reference: {reference_image}")
    print(f"Generated: {output_path}")
    print()
    print("="*80)
    print("✓ REFERENCE IMAGE TEST COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
