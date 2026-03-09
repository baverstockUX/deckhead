"""
Workflow service for deck generation.

Wraps existing deck_factory business logic for web interface.
"""

import asyncio
from typing import Optional, Tuple, List, Callable
from pathlib import Path

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
from web.services.session_manager import session_manager


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
        session_id: str,
        content: str,
        mode: str
    ) -> Tuple[DeckStructure, List[ClarificationQuestion]]:
        """
        Parse content with AI.

        Args:
            session_id: Session ID
            content: Content text
            mode: Text mode ('minimal' or 'rich')

        Returns:
            Tuple of (DeckStructure, list of ClarificationQuestions)
        """
        # Initialize parser
        content_parser = ContentParser(self.gemini_client, mode=mode)

        # Parse content
        deck_structure, clarification_questions = await content_parser.parse_content(content)

        # Store in session
        session_manager.update_session(session_id, {
            'deck_structure': deck_structure.model_dump(),
            'clarification_questions': [q.model_dump() for q in clarification_questions],
        })

        return deck_structure, clarification_questions

    async def refine_structure(
        self,
        session_id: str,
        clarifications: List[ClarificationResponse]
    ) -> DeckStructure:
        """
        Refine deck structure based on clarifications.

        Args:
            session_id: Session ID
            clarifications: User responses to clarification questions

        Returns:
            Refined DeckStructure
        """
        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError('Session not found')

        # Get stored deck structure
        deck_structure = DeckStructure(**session['deck_structure'])

        # Initialize parser
        mode = session.get('mode', 'minimal')
        content_parser = ContentParser(self.gemini_client, mode=mode)

        # Refine structure
        refined_structure = await content_parser.refine_structure(
            deck_structure,
            clarifications
        )

        # Update session
        session_manager.update_session(session_id, {
            'deck_structure': refined_structure.model_dump(),
            'clarification_responses': [c.model_dump() for c in clarifications],
        })

        return refined_structure

    async def generate_deck(
        self,
        session_id: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Path:
        """
        Generate complete deck with images and assembly.

        Args:
            session_id: Session ID
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            Path to generated presentation
        """
        session = session_manager.get_session(session_id)
        if not session:
            raise ValueError('Session not found')

        # Get deck structure
        deck_structure = DeckStructure(**session['deck_structure'])

        # Get brand assets
        brand_asset_paths = session.get('files', {}).get('brand_asset_paths', [])
        brand_assets = BrandAssets(
            reference_images=[Path(p) for p in brand_asset_paths]
        )

        # Initialize components
        image_factory = ImageFactory(
            self.gemini_client,
            self.config.max_concurrent_images
        )
        deck_assembler = DeckAssembler()

        # Create image generation requests
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

        # Generate images
        images = await image_factory.generate_images(
            image_requests,
            brand_assets,
            progress_callback=progress_callback
        )

        # Assemble presentation
        output_filename = deck_structure.deck_title.replace(' ', '_') + '.pptx'
        output_path = self.config.output_dir / output_filename

        final_path = deck_assembler.create_deck(
            deck_structure,
            images,
            output_path
        )

        # Update session
        session_manager.update_session(session_id, {
            'output_path': str(final_path)
        })

        return final_path


# Global workflow service instance
workflow_service = WorkflowService()
