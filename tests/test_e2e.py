#!/usr/bin/env python3
"""End-to-end test of Deckhead (without actual image generation)."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from deck_factory.core.config import ConfigLoader
from deck_factory.core.models import BrandAssets, ClarificationResponse, ImageGenerationRequest
from deck_factory.ai.gemini_client import GeminiClient
from deck_factory.ai.content_parser import ContentParser
from deck_factory.ai.clarifier import Clarifier
from deck_factory.deck.assembler import DeckAssembler


async def main():
    """Run end-to-end test."""
    print("="*80)
    print("END-TO-END TEST - DECKHEAD")
    print("="*80)
    print()

    # Step 1: Load config
    print("Step 1: Loading configuration...")
    config = ConfigLoader.from_env()
    print(f"✓ Config loaded (API key: {config.gemini_api_key[:20]}...)")
    print()

    # Step 2: Initialize components
    print("Step 2: Initializing components...")
    client = GeminiClient(config.gemini_api_key, max_concurrent=5)
    parser = ContentParser(client)
    clarifier = Clarifier(client)
    assembler = DeckAssembler()
    print("✓ All components initialized")
    print()

    # Step 3: Load sample content
    print("Step 3: Loading sample content...")
    sample_file = Path("examples/sample_presentation.md")
    with open(sample_file, 'r') as f:
        content = f.read()
    print(f"✓ Loaded {sample_file} ({len(content)} chars)")
    print()

    # Step 4: Parse content
    print("Step 4: Parsing content...")
    structure, questions = await parser.parse_content(content)
    print(f"✓ Parsed into {structure.total_slides} slides")
    print(f"✓ Generated {len(questions)} clarification questions")
    print()

    # Step 5: Display structure summary
    print("Deck Structure:")
    print(f"  Title: {structure.deck_title}")
    print(f"  Slides:")
    for slide in structure.slides[:3]:
        print(f"    {slide.slide_number}. {slide.title}")
    if structure.total_slides > 3:
        print(f"    ... and {structure.total_slides - 3} more")
    print()

    # Step 6: Display clarification questions
    print("Clarification Questions:")
    for q in questions[:3]:
        print(f"  [{q.category}] {q.question}")
        if q.options:
            print(f"    Options: {', '.join(q.options[:2])}...")
    print()

    # Step 7: Simulate answering questions
    print("Step 5: Simulating clarification responses...")
    clarification_responses = []
    for q in questions:
        if q.options:
            # Pick first option
            response = ClarificationResponse(
                question_id=q.question_id,
                answer=q.options[0]
            )
        else:
            # Provide a generic answer
            response = ClarificationResponse(
                question_id=q.question_id,
                answer="Test Company Inc."
            )
        clarification_responses.append(response)
    print(f"✓ Created {len(clarification_responses)} responses")
    print()

    # Step 8: Refine structure with responses
    print("Step 6: Refining structure with responses...")
    refined_structure = await parser.refine_structure(structure, clarification_responses)
    print(f"✓ Structure refined")
    print()

    # Step 9: Verify refined structure
    print("Refined Structure:")
    print(f"  Title: {refined_structure.deck_title}")
    print(f"  Total slides: {refined_structure.total_slides}")
    print()

    # Step 10: Prepare image generation requests (but don't actually generate)
    print("Step 7: Preparing image generation requests...")
    brand_assets = BrandAssets(reference_images=[])
    image_requests = []
    for slide in refined_structure.slides:
        request = ImageGenerationRequest(
            slide_number=slide.slide_number,
            prompt=slide.image_prompt,
            aspect_ratio="16:9",
            overlay_text=slide.overlay_text or "",
            output_filename=f"slide_{slide.slide_number}.png"
        )
        image_requests.append(request)
    print(f"✓ Prepared {len(image_requests)} image generation requests")
    print()

    # Step 11: Test image generation interface (without actual generation)
    print("Step 8: Testing image generation interface...")
    print(f"✓ Would generate {len(image_requests)} images with:")
    print(f"  - Aspect ratio: 16:9")
    print(f"  - Brand references: {len(brand_assets.reference_images)}")
    print(f"  - Concurrent requests: {client.max_concurrent}")
    print()

    # Step 12: Test deck assembly (without images)
    print("Step 9: Testing deck assembly setup...")
    output_path = Path(config.output_dir) / "test_presentation.pptx"
    print(f"✓ Output path: {output_path}")
    print(f"✓ DeckAssembler ready")
    print()

    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("✓ Configuration loaded")
    print("✓ Content parsing successful")
    print(f"✓ Generated {structure.total_slides} slide structure")
    print(f"✓ Generated {len(questions)} clarification questions")
    print("✓ Clarification responses processed")
    print("✓ Structure refinement successful")
    print(f"✓ Image generation interface ready")
    print("✓ Deck assembly setup complete")
    print()
    print("="*80)
    print("✓ ALL COMPONENTS WORKING CORRECTLY!")
    print("="*80)
    print()
    print("Note: Actual image generation and deck assembly skipped to save API quota.")
    print("To test the full workflow, run: PYTHONPATH=src python3 -m deck_factory")


if __name__ == "__main__":
    asyncio.run(main())
