"""
Image factory for Deckhead.

Handles async parallel image generation with brand consistency
using Gemini Imagen API.
"""

import asyncio
import time
from typing import List, Optional, Callable
from pathlib import Path

from .gemini_client import GeminiClient
from ..core.models import (
    ImageGenerationRequest,
    GeneratedImage,
    BrandAssets,
    TextContent
)
from ..core.exceptions import GenerationFailedError


# Layout instruction templates for prompt engineering
LAYOUT_INSTRUCTIONS = {
    "split-left": (
        "Create a split-screen composition with 16:9 aspect ratio. "
        "LEFT HALF: Visual content (image, illustration, or graphic). "
        "RIGHT HALF: Text content area with clean background. "
        "Maintain clear vertical division."
    ),
    "split-right": (
        "Create a split-screen composition with 16:9 aspect ratio. "
        "LEFT HALF: Text content area with clean background. "
        "RIGHT HALF: Visual content (image, illustration, or graphic). "
        "Maintain clear vertical division."
    ),
    "panel": (
        "Create a vertical composition with 16:9 aspect ratio. "
        "TOP TWO-THIRDS: Visual content (image, illustration, or graphic). "
        "BOTTOM THIRD: Text panel with distinct background. "
        "Clear horizontal separation between sections."
    ),
    "overlay": (
        "Create a full-frame visual composition with 16:9 aspect ratio. "
        "BACKGROUND: Complete visual (image or illustration). "
        "FOREGROUND: Minimal text overlaid at bottom with semi-transparent dark background behind text for readability."
    ),
    "image-only": ""  # No layout instruction needed
}

# Typography specifications for text rendering
TYPOGRAPHY_SPECS = (
    "Typography: Clean modern sans-serif fonts, clear visual hierarchy (large bold titles, readable body text), "
    "high contrast (dark text on light background or vice versa), generous whitespace, proper alignment and spacing. "
    "Professional business presentation aesthetic."
)


class ImageFactory:
    """
    Manages parallel async image generation.

    Generates images with brand consistency, handles rate limiting,
    implements retry logic, and provides progress callbacks.
    """

    def __init__(self, gemini_client: GeminiClient, max_concurrent: int = 5):
        """
        Initialize image factory.

        Args:
            gemini_client: Configured Gemini API client
            max_concurrent: Maximum concurrent image generations
        """
        self.client = gemini_client
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_images(
        self,
        requests: List[ImageGenerationRequest],
        brand_assets: BrandAssets,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[GeneratedImage]:
        """
        Generate multiple images in parallel.

        Args:
            requests: List of image generation requests
            brand_assets: Brand reference materials
            progress_callback: Optional callback function (current, total)

        Returns:
            List of GeneratedImage objects

        Raises:
            GenerationFailedError: If all retries fail for any image
        """
        # Load brand reference images if provided
        reference_image_data = None
        if brand_assets.reference_images:
            reference_image_data = await self.client.load_reference_images(
                brand_assets.reference_images
            )

        # Create tasks for all images
        tasks = []
        for request in requests:
            # Add brand references to request if available
            if reference_image_data:
                request.reference_images = brand_assets.reference_images

            task = self._generate_single_image(
                request,
                reference_image_data,
                progress_callback,
                len(requests)
            )
            tasks.append(task)

        # Generate all images concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for failures
        images = []
        errors = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Slide {requests[i].slide_number}: {result}")
            else:
                images.append(result)

        if errors:
            error_msg = "\n".join(errors)
            raise GenerationFailedError(
                f"Failed to generate {len(errors)} images:\n{error_msg}"
            )

        # Sort by slide number
        images.sort(key=lambda img: img.slide_number)

        return images

    async def _generate_single_image(
        self,
        request: ImageGenerationRequest,
        reference_image_data: Optional[List[bytes]],
        progress_callback: Optional[Callable[[int, int], None]],
        total: int
    ) -> GeneratedImage:
        """
        Generate a single image with retry logic.

        Args:
            request: Image generation request
            reference_image_data: Brand reference image data
            progress_callback: Progress callback function
            total: Total number of images being generated

        Returns:
            GeneratedImage object

        Raises:
            GenerationFailedError: If generation fails after retries
        """
        async with self._semaphore:
            start_time = time.time()

            try:
                # Enhance prompt with layout, text content, and brand style
                enhanced_prompt = self._build_image_prompt(
                    request.prompt,
                    reference_image_data,
                    infographic_style=getattr(request, 'infographic_style', False),
                    layout_type=getattr(request, 'layout_type', None),
                    text_content=getattr(request, 'text_content', None)
                )

                # Generate image
                image_data = await self.client.generate_image(
                    prompt=enhanced_prompt,
                    reference_images=reference_image_data,
                    aspect_ratio=request.aspect_ratio,
                    number_of_images=1
                )

                generation_time = time.time() - start_time

                # Create GeneratedImage object
                generated = GeneratedImage(
                    slide_number=request.slide_number,
                    image_data=image_data,
                    format="png",
                    generation_time=generation_time
                )

                # Call progress callback if provided
                if progress_callback:
                    progress_callback(request.slide_number, total)

                return generated

            except Exception as e:
                raise GenerationFailedError(
                    f"Failed to generate image for slide {request.slide_number}: {e}"
                )

    def _build_image_prompt(
        self,
        base_prompt: str,
        reference_image_data: Optional[List[bytes]],
        infographic_style: bool = False,
        layout_type: Optional[str] = None,
        text_content: Optional[TextContent] = None
    ) -> str:
        """
        Enhance image prompt with layout, text content, and style context.

        Args:
            base_prompt: Base image generation prompt (visual description)
            reference_image_data: Brand reference images (if available)
            infographic_style: Whether to generate infographic-style image
            layout_type: Layout type for positioning instructions
            text_content: Structured text content to bake into image

        Returns:
            Enhanced prompt string with all instructions
        """
        prompt_parts = []

        # 1. Layout instructions (positioning)
        layout_instruction = self._get_layout_instructions(layout_type)
        if layout_instruction:
            prompt_parts.append(layout_instruction)

        # 2. Text content instructions (what text to render)
        if text_content:
            text_instruction = self._convert_text_content_to_prompt(text_content)
            if text_instruction:
                prompt_parts.append(text_instruction)

        # 3. Typography specifications (if text content exists)
        if text_content:
            prompt_parts.append(TYPOGRAPHY_SPECS)

        # 4. Infographic style prefix (existing logic)
        if infographic_style:
            infographic_instruction = (
                "Create an infographic-style data visualization: clean charts, graphs, or diagrams "
                "with clear labels, modern color palette, minimal text, professional business style. "
            )
            prompt_parts.append(infographic_instruction)

        # 5. Base visual prompt (existing)
        prompt_parts.append(base_prompt)

        # 6. Brand style instruction (existing logic)
        if reference_image_data:
            style_instruction = (
                "Match the visual style, color palette, and aesthetic of the provided reference images. "
                "Maintain brand consistency throughout the composition."
            )
            prompt_parts.append(style_instruction)
        else:
            # General quality instructions (existing)
            quality_prefix = (
                "Professional quality, photorealistic or illustrated style, "
                "clean composition, 16:9 aspect ratio, suitable for business presentation."
            )
            prompt_parts.append(quality_prefix)

        # Combine all parts
        return " ".join(prompt_parts)

    def _convert_text_content_to_prompt(self, content: TextContent) -> str:
        """
        Convert structured TextContent into natural language prompt instructions.

        Args:
            content: Structured text content (bullets, statistics, paragraphs, callouts)

        Returns:
            Natural language text rendering instructions for image generation
        """
        instructions = []

        # Bullets
        if content.bullets:
            bullet_text = " • ".join(content.bullets)
            instructions.append(f"Include bullet points: {bullet_text}")

        # Statistics (prominently displayed)
        if content.statistics:
            stats_text = ", ".join([f"{s['label']}: {s['value']}" for s in content.statistics])
            instructions.append(f"Display statistics prominently with visual emphasis: {stats_text}")

        # Paragraphs
        if content.paragraphs:
            for para in content.paragraphs:
                instructions.append(f"Include text: {para}")

        # Callouts (visually distinct)
        if content.callouts:
            for callout in content.callouts:
                instructions.append(
                    f"Include highlighted callout box - Title: '{callout['title']}', "
                    f"Content: '{callout['text']}'"
                )

        return " ".join(instructions)

    def _get_layout_instructions(self, layout_type: Optional[str]) -> str:
        """
        Get layout positioning instructions for the given layout type.

        Args:
            layout_type: Layout type identifier

        Returns:
            Layout instruction string for prompt
        """
        if not layout_type:
            return ""

        return LAYOUT_INSTRUCTIONS.get(layout_type, "")

    async def generate_single_with_retry(
        self,
        request: ImageGenerationRequest,
        brand_assets: BrandAssets,
        max_retries: int = 3
    ) -> GeneratedImage:
        """
        Generate a single image with explicit retry control.

        Useful for regenerating failed images.

        Args:
            request: Image generation request
            brand_assets: Brand reference materials
            max_retries: Maximum number of retry attempts

        Returns:
            GeneratedImage object

        Raises:
            GenerationFailedError: If all retries fail
        """
        # Load brand references
        reference_image_data = None
        if brand_assets.reference_images:
            reference_image_data = await self.client.load_reference_images(
                brand_assets.reference_images
            )

        last_error = None
        for attempt in range(max_retries):
            try:
                return await self._generate_single_image(
                    request,
                    reference_image_data,
                    None,
                    1
                )
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(2 ** attempt)

        raise GenerationFailedError(
            f"Failed to generate image after {max_retries} attempts: {last_error}"
        )

    def estimate_generation_time(self, num_images: int) -> float:
        """
        Estimate total generation time.

        Args:
            num_images: Number of images to generate

        Returns:
            Estimated time in seconds
        """
        # Assume ~4 seconds per image on average
        avg_time_per_image = 4.0

        # Calculate batches based on concurrency
        num_batches = (num_images + self.max_concurrent - 1) // self.max_concurrent

        # Each batch runs in parallel, so time is avg_time * num_batches
        estimated_time = avg_time_per_image * num_batches

        return estimated_time
