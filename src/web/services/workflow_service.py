"""
Workflow service for deck generation.

Wraps existing deck_factory business logic for web interface.
"""

import asyncio
from typing import Optional, Tuple, List, Callable
from pathlib import Path
import glob as glob_mod

from deck_factory.core.config import ConfigLoader
from deck_factory.core.models import (
    DeckStructure,
    ClarificationQuestion,
    ClarificationResponse,
    ImageGenerationRequest,
    BrandAssets,
)
from deck_factory.ai.gemini_client import GeminiClient
from deck_factory.ai.content_parser import ContentParser
from deck_factory.ai.clarifier import Clarifier
from deck_factory.ai.image_factory import ImageFactory
from deck_factory.deck.assembler import DeckAssembler

# Upload directory (must match files.py)
UPLOAD_DIR = Path.cwd() / 'temp_assets'


class WorkflowService:
    """
    Orchestrates deck generation workflow for web interface.

    Wraps existing business logic from deck_factory module.
    """

    def __init__(self):
        """Initialize workflow service (lazy - defers config loading)."""
        self._config = None
        self._gemini_client = None

    def _ensure_initialized(self):
        """Load config and create client on first use."""
        if self._config is None:
            self._config = ConfigLoader.from_env()
            self._gemini_client = GeminiClient(
                api_key=self._config.gemini_api_key,
                max_concurrent=self._config.max_concurrent_images
            )

    @property
    def config(self):
        self._ensure_initialized()
        return self._config

    @property
    def gemini_client(self):
        self._ensure_initialized()
        return self._gemini_client

    async def parse_content(
        self,
        content: str,
        mode: str
    ) -> Tuple[DeckStructure, List[ClarificationQuestion]]:
        """Parse content with AI."""
        content_parser = ContentParser(self.gemini_client, mode=mode)
        deck_structure, clarification_questions = await content_parser.parse_content(content)
        return deck_structure, clarification_questions

    async def refine_structure(
        self,
        deck_structure_data: dict,
        clarifications: List[ClarificationResponse],
        mode: str
    ) -> DeckStructure:
        """Refine deck structure based on clarifications."""
        deck_structure = DeckStructure(**deck_structure_data)
        content_parser = ContentParser(self.gemini_client, mode=mode)
        refined_structure = await content_parser.refine_structure(
            deck_structure,
            clarifications
        )
        return refined_structure

    async def generate_deck(
        self,
        deck_structure_data: dict,
        brand_asset_file_ids: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Path:
        """Generate complete deck with images and assembly."""
        deck_structure = DeckStructure(**deck_structure_data)

        # Resolve brand asset paths from file IDs
        brand_asset_paths = []
        for file_id in brand_asset_file_ids:
            matches = list(UPLOAD_DIR.glob(f"{file_id}_*"))
            if matches:
                brand_asset_paths.append(matches[0])

        brand_assets = BrandAssets(
            reference_images=brand_asset_paths
        )

        image_factory = ImageFactory(
            self.gemini_client,
            self.config.max_concurrent_images
        )
        deck_assembler = DeckAssembler()

        image_requests = [
            ImageGenerationRequest(
                slide_number=slide.slide_number,
                prompt=slide.image_prompt,
                aspect_ratio='16:9',
                infographic_style=getattr(slide, 'infographic_style', False),
                layout_type=slide.layout_type,
                text_content=slide.text_content
            )
            for slide in deck_structure.slides
        ]

        images = await image_factory.generate_images(
            image_requests,
            brand_assets,
            progress_callback=progress_callback
        )

        output_filename = deck_structure.deck_title.replace(' ', '_') + '.pptx'
        output_path = self.config.output_dir / output_filename

        final_path = deck_assembler.create_deck(
            deck_structure,
            images,
            output_path
        )

        return final_path


# Global workflow service instance
workflow_service = WorkflowService()
