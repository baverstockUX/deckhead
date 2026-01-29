"""
Data models for Deckhead.

Defines Pydantic models for type safety, validation, and data structures
used throughout the application.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from pathlib import Path


class TextContent(BaseModel):
    """Structured text content for slide layouts."""

    bullets: Optional[List[str]] = Field(None, description="Bullet points (max 7)")
    statistics: Optional[List[Dict[str, str]]] = Field(None, description="Statistics with key-value pairs")
    paragraphs: Optional[List[str]] = Field(None, description="Short paragraphs (max 200 chars)")
    callouts: Optional[List[Dict[str, str]]] = Field(None, description="Callout boxes with title and text")

    @field_validator('bullets')
    @classmethod
    def validate_bullet_count(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that bullets don't exceed maximum count."""
        if v and len(v) > 7:
            raise ValueError('Maximum 7 bullets per slide')
        return v


class SlideContent(BaseModel):
    """Single slide definition."""

    slide_number: int = Field(ge=1, description="Slide number (1-indexed)")
    title: Optional[str] = Field(None, description="Slide title")
    content_summary: str = Field(min_length=1, description="Brief description of slide content")
    image_prompt: str = Field(min_length=10, description="Prompt for image generation")
    overlay_text: Optional[str] = Field(None, description="Text to overlay on the slide")
    speaker_notes: Optional[str] = Field(None, description="Speaker notes for the slide")

    # New fields for text content and layout
    layout_type: str = Field(
        default="image-only",
        description="Layout type: image-only, split-left, split-right, panel, overlay"
    )
    text_content: Optional[TextContent] = Field(
        None,
        description="Structured text content for non-image-only layouts"
    )
    infographic_style: bool = Field(
        default=False,
        description="Whether to generate image in infographic style"
    )

    @field_validator('layout_type')
    @classmethod
    def validate_layout(cls, v: str) -> str:
        """Validate layout type is one of the allowed values."""
        allowed = {'image-only', 'split-left', 'split-right', 'panel', 'overlay'}
        if v not in allowed:
            raise ValueError(f'Invalid layout_type: {v}. Must be one of {allowed}')
        return v


class DeckStructure(BaseModel):
    """Complete deck specification."""

    deck_title: str = Field(min_length=1, description="Title of the presentation")
    slides: List[SlideContent] = Field(min_items=1, max_items=50, description="List of slides")
    total_slides: int = Field(ge=1, description="Total number of slides")

    @field_validator('total_slides')
    @classmethod
    def validate_slide_count(cls, v: int, info) -> int:
        """Validate that total_slides matches the actual slide count."""
        if 'slides' in info.data and v != len(info.data['slides']):
            raise ValueError(f'total_slides ({v}) must match slides list length ({len(info.data["slides"])})')
        return v


class ClarificationQuestion(BaseModel):
    """AI-generated clarification question."""

    question_id: int = Field(ge=1, description="Unique question identifier")
    category: str = Field(description="Question category: structure, style, brand, or content")
    question: str = Field(min_length=1, description="The question text")
    options: Optional[List[str]] = Field(None, description="Multiple choice options (if applicable)")
    required: bool = Field(default=True, description="Whether the question must be answered")

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate that category is one of the allowed values."""
        allowed = {'structure', 'style', 'brand', 'content'}
        if v.lower() not in allowed:
            raise ValueError(f'category must be one of {allowed}, got: {v}')
        return v.lower()


class ClarificationResponse(BaseModel):
    """User's answer to a clarification question."""

    question_id: int = Field(ge=1, description="ID of the question being answered")
    answer: str = Field(min_length=1, description="User's answer")


class ImageGenerationRequest(BaseModel):
    """Request for single image generation."""

    slide_number: int = Field(ge=1, description="Slide number for this image")
    prompt: str = Field(min_length=10, description="Image generation prompt")
    reference_images: Optional[List[Path]] = Field(None, description="Brand reference image paths")
    aspect_ratio: str = Field(default="16:9", description="Image aspect ratio")
    infographic_style: bool = Field(default=False, description="Generate infographic-style image")

    @field_validator('aspect_ratio')
    @classmethod
    def validate_aspect_ratio(cls, v: str) -> str:
        """Validate aspect ratio format."""
        if v not in ['16:9', '4:3', '1:1']:
            raise ValueError(f'aspect_ratio must be one of 16:9, 4:3, 1:1, got: {v}')
        return v


class GeneratedImage(BaseModel):
    """Generated image result."""

    slide_number: int = Field(ge=1, description="Slide number for this image")
    image_data: bytes = Field(description="Raw image data")
    format: str = Field(default="png", description="Image format")
    generation_time: float = Field(ge=0, description="Time taken to generate (seconds)")


class BrandAssets(BaseModel):
    """Brand reference materials."""

    reference_images: List[Path] = Field(default_factory=list, description="Paths to brand reference images")
    style_description: Optional[str] = Field(None, description="Text description of brand style")

    @field_validator('reference_images')
    @classmethod
    def validate_image_paths(cls, v: List[Path]) -> List[Path]:
        """Validate that all image paths exist and have valid formats."""
        for path in v:
            if not path.exists():
                raise ValueError(f'Image not found: {path}')
            if not path.is_file():
                raise ValueError(f'Not a file: {path}')
            if path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValueError(f'Unsupported format: {path.suffix}. Use .jpg, .jpeg, .png, or .webp')
        return v


class DeckGenerationConfig(BaseModel):
    """Complete configuration for deck generation."""

    content_file: Path = Field(description="Path to content file (markdown/text)")
    brand_assets: BrandAssets = Field(default_factory=BrandAssets, description="Brand reference materials")
    deck_structure: Optional[DeckStructure] = Field(None, description="Parsed deck structure")
    clarifications: List[ClarificationResponse] = Field(default_factory=list, description="User's clarification responses")
    output_path: Optional[Path] = Field(None, description="Output path for generated presentation")

    @field_validator('content_file')
    @classmethod
    def validate_content_file(cls, v: Path) -> Path:
        """Validate that content file exists and has valid format."""
        if not v.exists():
            raise ValueError(f'Content file not found: {v}')
        if not v.is_file():
            raise ValueError(f'Not a file: {v}')
        if v.suffix.lower() not in ['.md', '.txt', '.markdown']:
            raise ValueError(f'Unsupported format: {v.suffix}. Use .md, .txt, or .markdown')
        return v
