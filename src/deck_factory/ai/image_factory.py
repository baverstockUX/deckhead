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
    BrandAssets
)
from ..core.exceptions import GenerationFailedError


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
                # Enhance prompt with brand style if provided
                enhanced_prompt = self._build_image_prompt(
                    request.prompt,
                    reference_image_data,
                    infographic_style=getattr(request, 'infographic_style', False)
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
        infographic_style: bool = False
    ) -> str:
        """
        Enhance image prompt with style context.

        Args:
            base_prompt: Base image generation prompt
            reference_image_data: Brand reference images (if available)
            infographic_style: Whether to generate infographic-style image

        Returns:
            Enhanced prompt string
        """
        # Add infographic style prefix if needed
        if infographic_style:
            infographic_instruction = (
                "Create an infographic-style data visualization: clean charts, graphs, or diagrams "
                "with clear labels, modern color palette, minimal text, professional business style. "
            )
            enhanced_prompt = infographic_instruction + base_prompt
        else:
            enhanced_prompt = base_prompt

        # If brand references provided, add style consistency instruction
        if reference_image_data:
            style_instruction = (
                "Match the visual style, color palette, and aesthetic of the provided reference images. "
                "Maintain brand consistency while incorporating the following concept: "
            )
            return style_instruction + enhanced_prompt

        # Otherwise, add general quality instructions
        quality_prefix = (
            "Professional quality, photorealistic or illustrated style, "
            "clean composition, 16:9 aspect ratio, suitable for business presentation. "
        )
        return quality_prefix + enhanced_prompt

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
