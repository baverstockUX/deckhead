"""
Deckhead - AI-powered PowerPoint generator.

A tool that transforms plain text/markdown content into professional
presentations using Google Gemini for content parsing and image generation.
"""

__version__ = "1.0.0"
__author__ = "Deckhead Team"

from .core.config import ConfigLoader
from .core.models import (
    DeckStructure,
    SlideContent,
    BrandAssets,
    ClarificationQuestion,
    ClarificationResponse,
    ImageGenerationRequest,
    GeneratedImage
)
from .ai.gemini_client import GeminiClient
from .ai.content_parser import ContentParser
from .ai.clarifier import Clarifier
from .ai.image_factory import ImageFactory
from .deck.assembler import DeckAssembler
from .cli.interactive import InteractiveCLI

__all__ = [
    "__version__",
    "ConfigLoader",
    "DeckStructure",
    "SlideContent",
    "BrandAssets",
    "ClarificationQuestion",
    "ClarificationResponse",
    "ImageGenerationRequest",
    "GeneratedImage",
    "GeminiClient",
    "ContentParser",
    "Clarifier",
    "ImageFactory",
    "DeckAssembler",
    "InteractiveCLI",
]
