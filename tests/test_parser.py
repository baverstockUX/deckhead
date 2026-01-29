#!/usr/bin/env python3
"""Test ContentParser with sample presentation."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from deck_factory.core.config import ConfigLoader
from deck_factory.ai.gemini_client import GeminiClient
from deck_factory.ai.content_parser import ContentParser


async def main():
    """Test content parsing."""
    print("="*80)
    print("CONTENT PARSER TEST")
    print("="*80)
    print()

    # Load config
    config = ConfigLoader.from_env()
    print(f"✓ Loaded config")

    # Create client and parser
    client = GeminiClient(config.gemini_api_key, max_concurrent=5)
    parser = ContentParser(client)
    print("✓ Created ContentParser")

    # Load sample content
    sample_file = Path("examples/sample_presentation.md")
    if not sample_file.exists():
        print(f"✗ Sample file not found: {sample_file}")
        sys.exit(1)

    with open(sample_file, 'r') as f:
        content = f.read()

    print(f"✓ Loaded sample content ({len(content)} chars)")
    print()

    # Parse content
    print("Parsing content with AI...")
    try:
        structure, questions = await parser.parse_content(content)

        print("\n" + "="*80)
        print("PARSING RESULTS")
        print("="*80)
        print(f"\nDeck Title: {structure.deck_title}")
        print(f"Total Slides: {structure.total_slides}")
        print()

        # Display slides
        for slide in structure.slides[:3]:  # Show first 3 slides
            print(f"Slide {slide.slide_number}: {slide.title or 'No title'}")
            print(f"  Content: {slide.content_summary[:80]}...")
            print(f"  Image prompt: {slide.image_prompt[:80]}...")
            print()

        if structure.total_slides > 3:
            print(f"... and {structure.total_slides - 3} more slides")
            print()

        # Display clarification questions
        print(f"Clarification Questions: {len(questions)}")
        for q in questions[:3]:  # Show first 3 questions
            print(f"  [{q.category.upper()}] {q.question}")
            if q.options:
                for opt in q.options:
                    print(f"    - {opt}")
            print()

        print("="*80)
        print("✓ Content parsing successful!")
        print("="*80)

    except Exception as e:
        print(f"\n✗ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
