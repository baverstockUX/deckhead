"""
Clarifier for Deckhead.

Generates and manages clarification questions to improve
presentation quality through user interaction.
"""

import json
from typing import List

from .gemini_client import GeminiClient
from ..core.models import (
    DeckStructure,
    BrandAssets,
    ClarificationQuestion,
    ClarificationResponse
)
from ..core.exceptions import InvalidResponseError


class Clarifier:
    """
    Generates clarification questions using AI.

    Analyzes content, structure, and brand assets to identify
    areas where user input would improve the presentation.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize clarifier.

        Args:
            gemini_client: Configured Gemini API client
        """
        self.client = gemini_client

    async def generate_questions(
        self,
        content: str,
        initial_structure: DeckStructure,
        brand_assets: BrandAssets
    ) -> List[ClarificationQuestion]:
        """
        Generate clarification questions.

        Args:
            content: Original content text
            initial_structure: Initial parsed deck structure
            brand_assets: Brand reference materials

        Returns:
            List of ClarificationQuestion objects

        Raises:
            InvalidResponseError: If API response is malformed
        """
        # Build clarification prompt
        prompt = self._build_clarification_prompt(
            content,
            initial_structure,
            brand_assets
        )

        # Generate questions
        response_text = await self.client.generate_text(
            prompt=prompt,
            response_mime_type="application/json",
            temperature=0.6
        )

        # Parse response
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise InvalidResponseError(f"Failed to parse clarification response: {e}")

        # Extract questions
        questions = []
        for q_data in response_data.get("questions", []):
            question = ClarificationQuestion(
                question_id=q_data.get("question_id"),
                category=q_data.get("category"),
                question=q_data.get("question"),
                options=q_data.get("options"),
                required=q_data.get("required", True)
            )
            questions.append(question)

        return questions

    def validate_response(
        self,
        question: ClarificationQuestion,
        response: ClarificationResponse
    ) -> bool:
        """
        Validate user's response to a question.

        Args:
            question: The clarification question
            response: User's response

        Returns:
            True if response is valid, False otherwise
        """
        # Check question ID matches
        if question.question_id != response.question_id:
            return False

        # Check answer is not empty
        if not response.answer or not response.answer.strip():
            return False

        # If question has options, validate answer is one of them
        if question.options:
            # Allow case-insensitive matching
            valid_options = [opt.lower() for opt in question.options]
            if response.answer.lower() not in valid_options:
                return False

        return True

    def _build_clarification_prompt(
        self,
        content: str,
        structure: DeckStructure,
        brand_assets: BrandAssets
    ) -> str:
        """
        Build prompt for clarification question generation.

        Args:
            content: Original content text
            structure: Parsed deck structure
            brand_assets: Brand assets (if any)

        Returns:
            Formatted prompt string
        """
        has_brand_assets = bool(brand_assets.reference_images)

        brand_info = ""
        if has_brand_assets:
            brand_info = f"""
BRAND ASSETS:
- {len(brand_assets.reference_images)} reference images provided
- Style description: {brand_assets.style_description or 'Not provided'}
"""

        structure_summary = f"""
CURRENT STRUCTURE:
- Deck Title: {structure.deck_title}
- Total Slides: {structure.total_slides}
- Slide Topics: {', '.join([f"#{s.slide_number}: {s.title}" for s in structure.slides[:5]])}{"..." if len(structure.slides) > 5 else ""}
"""

        return f"""You are an expert presentation consultant. Analyze the content and structure below, then generate clarification questions to improve the presentation.

ORIGINAL CONTENT:
{content[:1000]}{"..." if len(content) > 1000 else ""}
{structure_summary}
{brand_info}

TASK:
Generate 2-5 clarification questions across these categories:

1. STRUCTURE: Questions about slide organization, content flow, combining/splitting topics
2. STYLE: Questions about visual preferences, mood, design aesthetic
3. BRAND: Questions about consistency with brand assets (if provided)
4. CONTENT: Questions about missing information, unclear points, deck title

GUIDELINES:
- Ask only NECESSARY questions that would significantly improve the presentation
- Provide multiple choice options when appropriate
- Mark critical questions as required=true
- Focus on ambiguities and unclear aspects
- Don't ask obvious questions
- Consider brand assets in your questions (if provided)

Return a JSON response with this EXACT structure:
{{
  "questions": [
    {{
      "question_id": 1,
      "category": "structure|style|brand|content",
      "question": "Clear, specific question text",
      "options": ["option1", "option2", "option3"] (optional, for multiple choice),
      "required": true|false
    }}
  ]
}}

IMPORTANT:
- Generate 2-5 questions maximum
- Prioritize high-impact questions
- Use clear, non-technical language
- Options should be mutually exclusive when provided"""

    def categorize_questions(
        self,
        questions: List[ClarificationQuestion]
    ) -> dict[str, List[ClarificationQuestion]]:
        """
        Group questions by category.

        Args:
            questions: List of clarification questions

        Returns:
            Dictionary mapping category to questions
        """
        categorized = {
            "structure": [],
            "style": [],
            "brand": [],
            "content": []
        }

        for question in questions:
            category = question.category.lower()
            if category in categorized:
                categorized[category].append(question)

        return categorized

    def get_required_questions(
        self,
        questions: List[ClarificationQuestion]
    ) -> List[ClarificationQuestion]:
        """
        Filter to only required questions.

        Args:
            questions: List of clarification questions

        Returns:
            List of required questions only
        """
        return [q for q in questions if q.required]
