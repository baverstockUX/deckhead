"""
Configuration loader for Deckhead.

Handles loading environment variables, validating API keys,
and managing application settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .exceptions import MissingAPIKeyError, InvalidAPIKeyError


class ConfigLoader:
    """
    Loads and validates application configuration.

    Manages environment variables, API keys, and directory settings.
    """

    def __init__(
        self,
        gemini_api_key: str,
        temp_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        max_concurrent_images: int = 5
    ):
        """
        Initialize configuration.

        Args:
            gemini_api_key: Gemini API key
            temp_dir: Directory for temporary files (default: ./temp_assets)
            output_dir: Directory for output files (default: ./output)
            max_concurrent_images: Maximum concurrent image generations (default: 5)
        """
        self.gemini_api_key = gemini_api_key
        self.temp_dir = temp_dir or Path.cwd() / "temp_assets"
        self.output_dir = output_dir or Path.cwd() / "output"
        self.max_concurrent_images = max_concurrent_images

        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls, env_path: Optional[Path] = None) -> "ConfigLoader":
        """
        Create ConfigLoader from environment variables.

        Args:
            env_path: Path to .env file (default: searches current directory and parents)

        Returns:
            ConfigLoader instance

        Raises:
            MissingAPIKeyError: If GEMINI_API_KEY is not found
            InvalidAPIKeyError: If GEMINI_API_KEY format is invalid
        """
        # Load .env file
        if env_path:
            load_dotenv(env_path)
        else:
            # Search for .env in current directory and parents
            load_dotenv()

        # Get API key - try multiple possible env var names
        gemini_api_key = (
            os.getenv("GEMINI_API_KEY") or
            os.getenv("gemini_key") or  # Match the existing .env file format
            os.getenv("GOOGLE_API_KEY")
        )

        if not gemini_api_key:
            raise MissingAPIKeyError(
                "Gemini API key not found. Please set GEMINI_API_KEY or gemini_key in .env file."
            )

        # Basic validation
        if not isinstance(gemini_api_key, str) or len(gemini_api_key) < 10:
            raise InvalidAPIKeyError(
                f"Invalid Gemini API key format. Expected string of at least 10 characters."
            )

        # Get optional configuration
        temp_dir_str = os.getenv("TEMP_DIR")
        output_dir_str = os.getenv("OUTPUT_DIR")
        max_concurrent_str = os.getenv("MAX_CONCURRENT_IMAGES", "5")

        temp_dir = Path(temp_dir_str) if temp_dir_str else None
        output_dir = Path(output_dir_str) if output_dir_str else None

        try:
            max_concurrent = int(max_concurrent_str)
        except ValueError:
            max_concurrent = 5

        return cls(
            gemini_api_key=gemini_api_key,
            temp_dir=temp_dir,
            output_dir=output_dir,
            max_concurrent_images=max_concurrent
        )

    def validate(self) -> bool:
        """
        Validate configuration.

        Returns:
            True if configuration is valid

        Raises:
            InvalidAPIKeyError: If API key is invalid
        """
        # Validate API key format (basic check)
        if not self.gemini_api_key or len(self.gemini_api_key) < 10:
            raise InvalidAPIKeyError("Invalid API key format")

        # Validate directories are writable
        if not os.access(self.temp_dir, os.W_OK):
            raise PermissionError(f"Cannot write to temp directory: {self.temp_dir}")

        if not os.access(self.output_dir, os.W_OK):
            raise PermissionError(f"Cannot write to output directory: {self.output_dir}")

        return True

    def get_gemini_client_config(self) -> dict:
        """
        Get configuration dict for Gemini client.

        Returns:
            Dictionary with client configuration
        """
        return {
            "api_key": self.gemini_api_key,
            "max_concurrent": self.max_concurrent_images
        }

    def __repr__(self) -> str:
        """String representation (masks API key)."""
        masked_key = f"{self.gemini_api_key[:4]}...{self.gemini_api_key[-4:]}" if len(self.gemini_api_key) > 8 else "****"
        return (
            f"ConfigLoader(api_key={masked_key}, "
            f"temp_dir={self.temp_dir}, "
            f"output_dir={self.output_dir}, "
            f"max_concurrent={self.max_concurrent_images})"
        )
