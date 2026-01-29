"""
Gemini API client wrapper for Deckhead.

Provides unified interface for both text generation (Flash) and
image generation (Pro) using Google's Gemini API.
"""

import asyncio
import io
from typing import Optional, List
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from ..core.exceptions import (
    APIError,
    RateLimitError,
    QuotaExceededError,
    GenerationFailedError,
    InvalidResponseError
)


class GeminiClient:
    """
    Unified client for Gemini API interactions.

    Handles both text generation (Flash) and image generation (Pro)
    with retry logic, rate limiting, and error handling.
    """

    def __init__(self, api_key: str, max_concurrent: int = 5):
        """
        Initialize Gemini client.

        Args:
            api_key: Gemini API key
            max_concurrent: Maximum concurrent requests
        """
        self.api_key = api_key
        self.max_concurrent = max_concurrent
        self.flash_model = "gemini-3-flash-preview"  # Gemini Flash for text generation
        self.image_model = "gemini-3-pro-image-preview"  # Gemini Pro for image generation

        # Create Gemini client (using API key from environment or passed directly)
        self.client = genai.Client(api_key=api_key)

        # Semaphore for rate limiting
        self._semaphore = asyncio.Semaphore(max_concurrent)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        reraise=True
    )
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_mime_type: str = "application/json",
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using Gemini Flash.

        Args:
            prompt: Input prompt
            system_instruction: Optional system instruction (not used currently)
            response_mime_type: Expected response format (default: application/json)
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Generated text

        Raises:
            RateLimitError: If rate limit is exceeded
            GenerationFailedError: If generation fails
            InvalidResponseError: If response is invalid
        """
        async with self._semaphore:
            try:
                # Enhance prompt if JSON response is requested
                enhanced_prompt = prompt
                if response_mime_type == "application/json":
                    enhanced_prompt = f"""{prompt}

CRITICAL INSTRUCTIONS:
- You MUST respond with ONLY valid JSON
- Do NOT use markdown code blocks (no ```)
- Do NOT add any explanations or text outside the JSON
- The response should start with {{ and end with }}
- Ensure all JSON is properly formatted and valid"""

                # Run sync API in thread pool
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.flash_model,
                    contents=[enhanced_prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT'],
                        temperature=temperature
                    )
                )

                # Extract text from response
                if not response or not response.parts:
                    raise InvalidResponseError("Empty response from Gemini API")

                text = None
                for part in response.parts:
                    if part.text:
                        text = part.text.strip()
                        break

                if not text:
                    raise InvalidResponseError("No text found in response")

                # Clean response if JSON was requested
                if response_mime_type == "application/json":
                    text = self._clean_json_response(text)

                return text

            except Exception as e:
                error_msg = str(e).lower()

                # Check for rate limiting
                if "rate limit" in error_msg or "429" in error_msg:
                    raise RateLimitError(f"Rate limit exceeded: {e}")

                # Check for quota exceeded
                if "quota" in error_msg or "insufficient" in error_msg:
                    raise QuotaExceededError(f"API quota exceeded: {e}")

                # Check for invalid response
                if "invalid" in error_msg or "malformed" in error_msg:
                    raise InvalidResponseError(f"Invalid API response: {e}")

                # Generic API error
                raise GenerationFailedError(f"Text generation failed: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        reraise=True
    )
    async def generate_image(
        self,
        prompt: str,
        reference_images: Optional[List[Path]] = None,
        aspect_ratio: str = "16:9",
        image_size: str = "2K",
        number_of_images: int = 1
    ) -> bytes:
        """
        Generate image using Gemini Pro with Imagen 3.

        Args:
            prompt: Image generation prompt
            reference_images: Optional paths to brand reference images for style consistency
            aspect_ratio: Image aspect ratio (16:9, 4:3, 1:1, etc.)
            image_size: Image resolution (1K, 2K, 4K)
            number_of_images: Number of images to generate (always 1, parameter for compatibility)

        Returns:
            Generated image as bytes (PNG format)

        Raises:
            RateLimitError: If rate limit is exceeded
            GenerationFailedError: If generation fails

        Note:
            The number_of_images parameter is accepted for API compatibility but only
            1 image is generated per call.
        """
        async with self._semaphore:
            try:
                # Build contents list: start with prompt
                contents = [prompt]

                # Add reference images as PIL Images
                if reference_images:
                    for img_path in reference_images:
                        if not img_path.exists():
                            raise FileNotFoundError(f"Reference image not found: {img_path}")
                        contents.append(Image.open(img_path))

                # Generate image using sync API in thread pool
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.image_model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE'],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=image_size
                        )
                    )
                )

                # Extract generated image from response
                if not response or not response.parts:
                    raise InvalidResponseError("Empty response from Gemini API")

                for part in response.parts:
                    if image := part.as_image():
                        # google.genai Image object has image_bytes property
                        # that contains the raw image data (already in PNG format)
                        return image.image_bytes

                raise InvalidResponseError("No image found in response")

            except FileNotFoundError:
                raise  # Re-raise file not found errors as-is

            except Exception as e:
                error_msg = str(e).lower()

                # Check for rate limiting
                if "rate limit" in error_msg or "429" in error_msg:
                    raise RateLimitError(f"Rate limit exceeded: {e}")

                # Check for quota exceeded
                if "quota" in error_msg or "insufficient" in error_msg:
                    raise QuotaExceededError(f"API quota exceeded: {e}")

                # Generic API error
                raise GenerationFailedError(f"Image generation failed: {e}")

    async def load_reference_images(self, image_paths: List[Path]) -> List[Path]:
        """
        Validate and return reference image paths.

        With the new API, we pass Path objects directly and open them
        as PIL Images during generation.

        Args:
            image_paths: List of paths to reference images

        Returns:
            List of validated image paths

        Raises:
            FileNotFoundError: If image file not found
        """
        for path in image_paths:
            if not path.exists():
                raise FileNotFoundError(f"Reference image not found: {path}")
            if not path.is_file():
                raise ValueError(f"Not a file: {path}")

        return image_paths

    def validate_api_key(self) -> bool:
        """
        Validate API key by making a simple request.

        Returns:
            True if API key is valid

        Raises:
            InvalidAPIKeyError: If API key is invalid
        """
        try:
            # Try a simple text generation
            response = self.client.models.generate_content(
                model=self.flash_model,
                contents=["Hello"],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT']
                )
            )
            return True
        except Exception as e:
            error_msg = str(e).lower()
            if "api key" in error_msg or "invalid" in error_msg or "unauthorized" in error_msg:
                from ..core.exceptions import InvalidAPIKeyError
                raise InvalidAPIKeyError(f"Invalid Gemini API key: {e}")
            raise

    def _clean_json_response(self, text: str) -> str:
        """
        Clean JSON response by removing markdown code blocks and other formatting.

        Args:
            text: Raw response text

        Returns:
            Cleaned JSON string
        """
        text = text.strip()

        # Remove markdown code blocks (```json ... ``` or ``` ... ```)
        if text.startswith("```"):
            lines = text.split('\n')
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = '\n'.join(lines).strip()

        # Remove "json" prefix if present (sometimes appears after removing ```)
        if text.lower().startswith("json"):
            text = text[4:].strip()

        # Ensure text starts with { or [ (valid JSON start)
        if not text.startswith('{') and not text.startswith('['):
            # Try to find first { or [
            json_start = min(
                (text.find('{') if text.find('{') != -1 else len(text)),
                (text.find('[') if text.find('[') != -1 else len(text))
            )
            if json_start < len(text):
                text = text[json_start:]

        # Ensure text ends with } or ] (valid JSON end)
        if not text.endswith('}') and not text.endswith(']'):
            # Try to find last } or ]
            json_end = max(text.rfind('}'), text.rfind(']'))
            if json_end != -1:
                text = text[:json_end + 1]

        return text.strip()
