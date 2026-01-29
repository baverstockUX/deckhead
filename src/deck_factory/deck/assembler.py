"""
Deck assembler for Deckhead.

Creates PowerPoint presentations using python-pptx with full-bleed images,
text overlays, and speaker notes.
"""

from pathlib import Path
from typing import List
import io

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.dml.color import RGBColor

from ..core.models import DeckStructure, SlideContent, GeneratedImage, TextContent
from ..core.exceptions import AssemblyError, SlideCreationError, ImageProcessingError


class DeckAssembler:
    """
    Assembles PowerPoint presentations from structured content and images.

    Creates 16:9 slides with full-bleed images, text overlays, and speaker notes.
    """

    def __init__(self):
        """Initialize deck assembler with standard 16:9 dimensions."""
        # 16:9 dimensions in inches
        self.slide_width = Inches(13.333)
        self.slide_height = Inches(7.5)

    def create_deck(
        self,
        structure: DeckStructure,
        images: List[GeneratedImage],
        output_path: Path
    ) -> Path:
        """
        Create complete PowerPoint presentation.

        Args:
            structure: Deck structure with slide content
            images: Generated images for slides
            output_path: Path where to save the presentation

        Returns:
            Path to created presentation file

        Raises:
            AssemblyError: If deck creation fails
        """
        try:
            # Create presentation
            prs = Presentation()

            # Set slide dimensions to 16:9
            prs.slide_width = self.slide_width
            prs.slide_height = self.slide_height

            # Map images by slide number for quick lookup
            image_map = {img.slide_number: img for img in images}

            # Create slides
            for slide_content in structure.slides:
                # Get corresponding image
                image = image_map.get(slide_content.slide_number)
                if not image:
                    raise AssemblyError(
                        f"Missing image for slide {slide_content.slide_number}"
                    )

                # Create slide
                self._create_slide(prs, slide_content, image)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save presentation
            prs.save(str(output_path))

            return output_path

        except Exception as e:
            raise AssemblyError(f"Failed to create deck: {e}")

    def _create_slide(
        self,
        prs: Presentation,
        slide_content: SlideContent,
        image: GeneratedImage
    ) -> None:
        """
        Create a single slide with full-bleed image.

        All text content is now baked into the generated image,
        so all slides use the same full-bleed layout.

        Args:
            prs: Presentation object
            slide_content: Slide content definition
            image: Generated image for this slide

        Raises:
            SlideCreationError: If slide creation fails
        """
        try:
            # Add blank slide (layout index 6 is typically blank)
            blank_slide_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(blank_slide_layout)

            # ALL slides now use full-bleed images (text is baked in)
            self._add_full_bleed_image(slide, image.image_data)

            # Add speaker notes if present (non-visual, preserved)
            if slide_content.speaker_notes:
                self._add_speaker_notes(slide, slide_content.speaker_notes)

        except Exception as e:
            raise SlideCreationError(
                f"Failed to create slide {slide_content.slide_number}: {e}"
            )

    def _add_full_bleed_image(self, slide, image_data: bytes) -> None:
        """
        Add full-bleed image to slide.

        Args:
            slide: Slide object
            image_data: Raw image data bytes

        Raises:
            ImageProcessingError: If image insertion fails
        """
        try:
            # Convert bytes to file-like object
            image_stream = io.BytesIO(image_data)

            # Add picture at (0,0) with full slide dimensions
            slide.shapes.add_picture(
                image_stream,
                left=0,
                top=0,
                width=self.slide_width,
                height=self.slide_height
            )

        except Exception as e:
            raise ImageProcessingError(f"Failed to add image to slide: {e}")

    def _add_speaker_notes(self, slide, notes: str) -> None:
        """
        Add speaker notes to slide.

        Args:
            slide: Slide object
            notes: Speaker notes text
        """
        notes_slide = slide.notes_slide
        text_frame = notes_slide.notes_text_frame

        # Clear existing notes
        text_frame.clear()

        # Add notes
        text_frame.text = notes

    def create_title_slide(
        self,
        prs: Presentation,
        title: str,
        subtitle: str = None
    ) -> None:
        """
        Create a title slide (optional, for first slide).

        Args:
            prs: Presentation object
            title: Presentation title
            subtitle: Optional subtitle
        """
        # Use title slide layout (usually index 0)
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)

        # Set title
        title_shape = slide.shapes.title
        title_shape.text = title

        # Set subtitle if provided
        if subtitle and len(slide.placeholders) > 1:
            subtitle_shape = slide.placeholders[1]
            subtitle_shape.text = subtitle
