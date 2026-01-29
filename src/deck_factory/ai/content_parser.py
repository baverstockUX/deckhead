"""
Content parser for Deckhead.

Parses plain text/markdown content into structured deck format
using Gemini Flash for intelligent analysis and structuring.
"""

import json
from typing import Tuple, List

from .gemini_client import GeminiClient
from ..core.models import DeckStructure, SlideContent, ClarificationQuestion, ClarificationResponse, TextContent
from ..core.exceptions import InvalidResponseError, GenerationFailedError


class ContentParser:
    """
    Parses content files into structured deck format.

    Uses Gemini Flash to intelligently analyze content and generate
    slide structure with image prompts.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize content parser.

        Args:
            gemini_client: Configured Gemini API client
        """
        self.client = gemini_client

    async def parse_content(self, content: str) -> Tuple[DeckStructure, List[ClarificationQuestion]]:
        """
        Parse content into deck structure.

        Args:
            content: Raw content text (markdown/plain text)

        Returns:
            Tuple of (DeckStructure, List of ClarificationQuestions)

        Raises:
            InvalidResponseError: If API response is malformed
            GenerationFailedError: If parsing fails
        """
        # Build parsing prompt
        prompt = self._build_parsing_prompt(content)

        # Generate structured response
        response_text = await self.client.generate_text(
            prompt=prompt,
            response_mime_type="application/json",
            temperature=0.7
        )

        # Parse JSON response
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Failed to parse API response as JSON: {e}")

        # Extract deck structure
        deck_data = response_data.get("deck_structure")
        if not deck_data:
            raise InvalidResponseError("Missing 'deck_structure' in API response")

        # Build SlideContent objects
        slides = []
        for slide_data in deck_data.get("slides", []):
            # Extract text_content if present
            text_content = None
            if slide_data.get("text_content"):
                text_content = TextContent(**slide_data.get("text_content"))

            slide = SlideContent(
                slide_number=slide_data.get("slide_number"),
                title=slide_data.get("title"),
                content_summary=slide_data.get("content_summary"),
                image_prompt=slide_data.get("image_prompt"),
                overlay_text=slide_data.get("overlay_text"),
                speaker_notes=slide_data.get("speaker_notes"),
                # New fields for text content feature
                layout_type=slide_data.get("layout_type", "image-only"),
                text_content=text_content,
                infographic_style=slide_data.get("infographic_style", False)
            )
            slides.append(slide)

        # Create DeckStructure
        deck_structure = DeckStructure(
            deck_title=deck_data.get("deck_title", "Untitled Presentation"),
            slides=slides,
            total_slides=len(slides)
        )

        # Extract clarification questions
        questions = []
        for q_data in response_data.get("clarification_questions", []):
            question = ClarificationQuestion(
                question_id=q_data.get("question_id"),
                category=q_data.get("category"),
                question=q_data.get("question"),
                options=q_data.get("options"),
                required=q_data.get("required", True)
            )
            questions.append(question)

        return deck_structure, questions

    async def refine_structure(
        self,
        structure: DeckStructure,
        clarifications: List[ClarificationResponse]
    ) -> DeckStructure:
        """
        Refine deck structure based on user clarifications.

        Args:
            structure: Initial deck structure
            clarifications: User's answers to clarification questions

        Returns:
            Refined DeckStructure

        Raises:
            GenerationFailedError: If refinement fails
        """
        # Build refinement prompt
        prompt = self._build_refinement_prompt(structure, clarifications)

        # Generate refined structure
        response_text = await self.client.generate_text(
            prompt=prompt,
            response_mime_type="application/json",
            temperature=0.5  # Lower temperature for more consistent refinement
        )

        # Parse response
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Failed to parse refinement response: {e}")

        # Extract refined deck structure
        deck_data = response_data.get("refined_structure")
        if not deck_data:
            raise InvalidResponseError("Missing 'refined_structure' in refinement response")

        # Build refined SlideContent objects
        slides = []
        for slide_data in deck_data.get("slides", []):
            # Extract text_content if present
            text_content = None
            if slide_data.get("text_content"):
                text_content = TextContent(**slide_data.get("text_content"))

            slide = SlideContent(
                slide_number=slide_data.get("slide_number"),
                title=slide_data.get("title"),
                content_summary=slide_data.get("content_summary"),
                image_prompt=slide_data.get("image_prompt"),
                overlay_text=slide_data.get("overlay_text"),
                speaker_notes=slide_data.get("speaker_notes"),
                # New fields for text content feature
                layout_type=slide_data.get("layout_type", "image-only"),
                text_content=text_content,
                infographic_style=slide_data.get("infographic_style", False)
            )
            slides.append(slide)

        # Create refined DeckStructure
        refined_structure = DeckStructure(
            deck_title=deck_data.get("deck_title", structure.deck_title),
            slides=slides,
            total_slides=len(slides)
        )

        return refined_structure

    def _build_parsing_prompt(self, content: str) -> str:
        """
        Build prompt for initial content parsing.

        Args:
            content: Raw content text

        Returns:
            Formatted prompt string
        """
        return f"""You are an expert presentation designer. Analyze the following content and structure it into a PowerPoint presentation.

CONTENT:
{content}

INSTRUCTIONS:
1. Break the content into logical slides (minimum 1, maximum 20)
2. For each slide, decide the OPTIMAL LAYOUT based on content:
   - "image-only": Pure visual storytelling, no substantial text needed (default)
   - "split-left": Image left, text content right (for balanced visual + text)
   - "split-right": Image right, text content left
   - "panel": Full-width image top, text panel below
   - "overlay": Minimal text overlaid on image (use sparingly)

3. For each slide:
   - Create a concise title
   - Decide if substantial TEXT CONTENT exists (3+ bullets, statistics, or meaningful paragraphs)
   - If YES: Choose appropriate layout (split-left/split-right/panel) and structure the content
   - If NO: Use "image-only" layout
   - Generate detailed image prompt with title integrated (16:9 aspect ratio, professional quality)
   - For data-heavy slides with statistics/numbers, set infographic_style: true to generate chart-like visuals
   - Write speaker notes

4. TEXT CONTENT STRUCTURE (only if substantial content exists):
   - bullets: Array of concise bullet points (3-7 items, max 60 chars each)
   - statistics: Array of {{"label": "Metric", "value": "123%"}} for key numbers
   - paragraphs: Array of short paragraphs (1-3 sentences, max 200 chars)
   - callouts: Array of {{"title": "Title", "text": "content"}} for highlighted information

5. LAYOUT SELECTION GUIDANCE:
   - split-left/split-right: Best for balanced visual + text (bullets, lists)
   - panel: Best for image-first with supporting text below
   - overlay: Only for minimal text (1-2 short lines)
   - image-only: Default when visual tells the complete story

6. Generate clarification questions for:
   - Ambiguous structure (should topics be combined/split?)
   - Visual style preferences (if not clear from content)
   - Missing information (deck title, specific details)
   - Content organization improvements

Return a JSON response with this EXACT structure:
{{
  "deck_structure": {{
    "deck_title": "string",
    "slides": [
      {{
        "slide_number": 1,
        "title": "string",
        "content_summary": "string (brief description)",
        "layout_type": "image-only|split-left|split-right|panel|overlay",
        "text_content": {{
          "bullets": ["point 1", "point 2"],
          "statistics": [{{"label": "Metric", "value": "123%"}}],
          "paragraphs": ["text"],
          "callouts": [{{"title": "Important", "text": "key info"}}]
        }},
        "image_prompt": "string (detailed image generation prompt with title integrated, minimum 20 words)",
        "infographic_style": true|false,
        "overlay_text": null,
        "speaker_notes": "string (what presenter should say)"
      }}
    ]
  }},
  "clarification_questions": [
    {{
      "question_id": 1,
      "category": "structure|style|brand|content",
      "question": "string",
      "options": ["option1", "option2", "option3"] (optional),
      "required": true|false
    }}
  ]
}}

IMPORTANT:
- Image prompts must include the slide title visually integrated into the image
- Only include text_content if substantial content exists (not just rephrasing the title)
- Default to "image-only" layout when in doubt
- For statistics/data slides, use infographic_style: true to generate chart-like images
- Bullet points must be concise and scannable (max 60 chars each)
- Text content should complement, not duplicate, the image
- Set overlay_text to null (deprecated field)
- Maintain professional presentation standards (not cluttered)
- Only ask necessary clarification questions (2-5 questions)
- Make smart assumptions where reasonable"""

    def _build_refinement_prompt(
        self,
        structure: DeckStructure,
        clarifications: List[ClarificationResponse]
    ) -> str:
        """
        Build prompt for structure refinement.

        Args:
            structure: Initial deck structure
            clarifications: User's clarification responses

        Returns:
            Formatted prompt string
        """
        # Convert structure to dict for prompt
        structure_dict = structure.model_dump()

        # Format clarifications
        clarifications_text = "\n".join([
            f"Q{c.question_id}: {c.answer}"
            for c in clarifications
        ])

        return f"""You are refining a presentation structure based on user feedback.

CURRENT STRUCTURE:
{json.dumps(structure_dict, indent=2)}

USER CLARIFICATIONS:
{clarifications_text}

INSTRUCTIONS:
1. Apply the user's feedback to refine the deck structure
2. Maintain the same JSON structure format
3. Ensure image prompts include slide titles visually integrated
4. Ensure layout decisions are appropriate for content (image-only, split-left, split-right, panel, overlay)
5. Maintain or adjust text_content structure based on feedback
6. Improve image prompts based on style feedback
7. Adjust slide organization based on structure feedback
8. Fill in missing information from content feedback
9. Ensure brand consistency if mentioned
10. Use infographic_style: true for data-heavy slides

Return a JSON response with this EXACT structure:
{{
  "refined_structure": {{
    "deck_title": "string",
    "slides": [
      {{
        "slide_number": 1,
        "title": "string",
        "content_summary": "string",
        "layout_type": "image-only|split-left|split-right|panel|overlay",
        "text_content": {{
          "bullets": ["point 1", "point 2"],
          "statistics": [{{"label": "Metric", "value": "123%"}}],
          "paragraphs": ["text"],
          "callouts": [{{"title": "Important", "text": "key info"}}]
        }},
        "image_prompt": "string (refined based on feedback, with title integrated)",
        "infographic_style": true|false,
        "overlay_text": null,
        "speaker_notes": "string"
      }}
    ]
  }}
}}

IMPORTANT:
- Incorporate ALL user feedback
- Maintain slide numbering sequence
- Ensure slide titles are incorporated into image prompts
- Ensure appropriate layout_type for each slide's content
- Include text_content only when substantial content exists
- Use infographic_style: true for data-heavy slides
- Enhance image prompts with style preferences
- Keep 16:9 aspect ratio in mind"""
