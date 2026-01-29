# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Deckhead** is an AI-powered PowerPoint presentation generator using Google Gemini. It transforms markdown/text content into professional presentations with AI-generated images, intelligent layout selection, and structured text content.

## Essential Commands

### Development
```bash
# Run the application
python -m src.deck_factory

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Run individual test files (tests use actual API)
python3 tests/test_client.py           # Test GeminiClient
python3 tests/test_parser.py           # Test ContentParser
python3 tests/test_image_generation.py # Test image generation
python3 tests/test_reference_images.py # Test brand reference images
python3 tests/test_e2e.py             # End-to-end integration test

# Run full test suite in order
python3 tests/test_client.py && \
python3 tests/test_parser.py && \
python3 tests/test_image_generation.py && \
python3 tests/test_reference_images.py && \
python3 tests/test_e2e.py
```

### Code Quality
```bash
# Format code
black src/

# Type checking
mypy src/
```

## Architecture

### Core Flow
1. **ConfigLoader** (`core/config.py`) - Loads `.env` configuration, validates API key
2. **InteractiveCLI** (`cli/interactive.py`) - Rich terminal interface, prompts user for text content mode, content file, and brand assets
3. **ContentParser** (`ai/content_parser.py`) - Uses Gemini Flash to parse content into structured `DeckStructure` with mode-aware layout decisions
4. **Clarifier** (`ai/clarifier.py`) - Generates and validates clarification questions, refines structure based on responses
5. **ImageFactory** (`ai/image_factory.py`) - Async parallel image generation via Gemini Imagen with brand consistency
6. **DeckAssembler** (`deck/assembler.py`) - Creates PowerPoint using python-pptx with full-bleed image slides

### Key Design Patterns

**Async Parallel Processing**: `ImageFactory` uses `asyncio.Semaphore` to generate multiple images concurrently (default: 5 concurrent). Images are generated in batches with progress callbacks.

**Layout System**: ContentParser uses AI to select optimal layout per slide:
- `image-only`: Default, title integrated into image (no text overlay)
- `split-left`: Image left half, text content right half
- `split-right`: Image right half, text content left half
- `panel`: Full-width image top 2/3, text panel bottom 1/3
- `overlay`: Full-bleed image with minimal text overlay

**Structured Text Content**: `TextContent` model (Pydantic) supports:
- `bullets`: Max 7 bullet points
- `statistics`: Key-value pairs for metrics
- `paragraphs`: Short explanatory text
- `callouts`: Highlighted information boxes

**Brand Consistency**: Reference images passed to Imagen API influence generated image style. ImageFactory enhances prompts with style transfer instructions when brand assets provided.

**Infographic Mode**: When `infographic_style: true`, ImageFactory prepends chart/diagram instructions to image prompts for data-heavy slides.

### Data Models (Pydantic)

All models in `core/models.py` use Pydantic for validation:
- `DeckStructure`: Complete presentation structure
- `SlideContent`: Single slide (title, content_summary, image_prompt, layout_type, text_content, infographic_style)
- `TextContent`: Structured text (bullets, statistics, paragraphs, callouts)
- `ClarificationQuestion`: AI-generated questions
- `ImageGenerationRequest`: Image generation parameters
- `GeneratedImage`: Generated image result
- `BrandAssets`: Reference images and style description

### Error Handling

Custom exceptions in `core/exceptions.py`:
- `DeckFactoryError`: Base exception
- `MissingAPIKeyError`: No Gemini API key in `.env`
- `InvalidAPIKeyError`: Malformed API key
- `ConfigError`: Configuration issues
- `InvalidResponseError`: Malformed API response
- `GenerationFailedError`: Image/text generation failure
- `AssemblyError`: PowerPoint creation failure

## Important Implementation Details

### Gemini API Integration

**Models Used**:
- Text: `gemini-3-flash-preview` (content parsing, clarifications)
- Images: `gemini-3-pro-image-preview` (image generation)

**GeminiClient** (`ai/gemini_client.py`):
- `generate_text()`: Structured JSON responses via `response_mime_type="application/json"`
- `generate_image()`: Returns raw PNG bytes
- `load_reference_images()`: Loads brand reference images for style transfer

### ContentParser Prompts

Prompts in `ai/content_parser.py` are critical:
- `_build_parsing_prompt()`: Initial content parsing, includes detailed JSON schema and layout selection guidance
- `_build_refinement_prompt()`: Structure refinement based on clarifications

**Layout Selection Logic**: AI decides layout based on whether substantial text content exists (3+ bullets, statistics, or meaningful paragraphs). Default to `image-only` when content is minimal.

### DeckAssembler Layout Implementation

`deck/assembler.py` implements 5 layout types:
- `_create_split_left_slide()`: Image left 6.667", text right 6"
- `_create_split_right_slide()`: Text left 6", image right 6.667"
- `_create_panel_slide()`: Image top 5", text bottom 2.5"
- `_create_overlay_slide()`: Full-bleed image + minimal overlay
- `_add_full_bleed_image()`: Full slide (13.333" x 7.5")

**Slide Dimensions**: Always 16:9 (13.333" x 7.5")

### Text Content Rendering

`_populate_text_content()` in `deck/assembler.py`:
- Bullets: 18pt, dark gray, 10pt spacing
- Statistics: Label 16pt, value 24pt bold blue
- Paragraphs: 14pt, 1.2 line spacing
- Callouts: Title 16pt bold orange, text 14pt

## Configuration

### Environment Variables (`.env`)
```bash
# Required
gemini_key='your-api-key-here'

# Optional
MAX_CONCURRENT_IMAGES=5       # Concurrent image generations (default: 5)
TEMP_DIR=./temp_assets        # Temporary file directory
OUTPUT_DIR=./src/output       # Output directory for presentations
```

### File Structure
```
content/         - User content files (markdown/text) - gitignored
references/      - Brand reference images - gitignored
src/output/      - Generated presentations - created automatically
temp_assets/     - Temporary files - created automatically
```

## Common Workflows

### Using Text Content Modes

**Deckhead supports two text content generation modes:**

#### Minimal Mode (Default)
- **Purpose**: Clean visual storytelling with titles only
- **Behavior**:
  - ALL slides use `image-only` layout
  - NO text_content generated (set to null)
  - Titles visually integrated into images
  - No bullets, statistics, paragraphs, or callouts
  - Faster generation (skips text content analysis)
  - `infographic_style` disabled
- **Best for**: Presentations that rely on strong visuals, executive summaries, pitch decks
- **Example**: Title slide: "Market Expansion" generates a compelling visual with the title integrated as part of the image design

#### Rich Mode
- **Purpose**: Information-dense presentations with structured text content
- **Behavior**:
  - AI selects optimal layout per slide (image-only, split-left, split-right, panel, overlay)
  - Generates structured text_content when substantial content exists
  - Text content baked into generated images (not PowerPoint text boxes)
  - Supports bullets (3-7 items), statistics, paragraphs, and callouts
  - Uses `infographic_style: true` for data-heavy slides
- **Best for**: Educational content, detailed proposals, data-driven presentations
- **Example**: Slide with 4 bullet points and 3 statistics will use split-left layout with text rendered in the generated image

#### How to Select Mode
The mode selector appears as an interactive prompt after the welcome screen:
```
Text Content Mode

Choose text content mode:
  minimal - Titles only, clean visual storytelling (default)
  rich - Full text content (bullets, statistics, callouts)

Select mode [minimal/rich] (minimal):
```

Users select mode at the start of each generation. The mode applies to ALL slides in the presentation.

#### Implementation Details
- Mode passed to `ContentParser` constructor: `ContentParser(gemini_client, mode=text_mode)`
- ContentParser builds mode-specific AI prompts in `_build_parsing_prompt()` and `_build_refinement_prompt()`
- Minimal mode forces `layout_type: "image-only"` and `text_content: null` for all slides
- Rich mode uses intelligent layout selection based on content analysis
- ImageFactory automatically handles `None` text_content (skips text instructions and typography specs)

### Adding New Layout Type
1. Add layout name to `SlideContent.layout_type` validator in `core/models.py`
2. Update `_build_parsing_prompt()` in `ai/content_parser.py` to include layout in instructions
3. Implement `_create_<layout>_slide()` method in `deck/assembler.py`
4. Add routing in `_create_slide()` method in `deck/assembler.py`

### Modifying Image Generation
- Image prompt enhancement: `ImageFactory._build_image_prompt()` in `ai/image_factory.py`
- Infographic style instructions: Prepended in `_build_image_prompt()` when `infographic_style=True`
- Brand consistency: Style transfer instructions added when reference images provided

### Changing Text Content Structure
1. Update `TextContent` model in `core/models.py`
2. Update parsing prompt JSON schema in `ai/content_parser.py` (both minimal and rich mode schemas)
3. Update `ImageFactory._convert_text_content_to_prompt()` to handle new text content types
Note: Text content changes only apply in rich mode. Minimal mode always has `text_content: null`.

## Gotchas

1. **Image Generation Uses API Quota**: Tests that generate images consume Gemini API quota. Be mindful when running test suite.

2. **Title Integration**: Titles are NOT overlaid as text boxes. They must be integrated into the image prompt itself. The AI includes title text in the image generation prompt.

3. **Mode Selection is Per-Presentation**: The text content mode (minimal/rich) applies to ALL slides in a presentation. You cannot mix modes within a single deck. Choose the mode that best fits your overall presentation style.

4. **Layout vs Image-Only**: In rich mode, the AI defaults to `image-only` when text content is minimal. Don't force layouts with substantial text requirements if content doesn't support it. In minimal mode, ALL slides are always image-only.

5. **Async Context**: Image generation must run in async context. Use `asyncio.run()` for CLI entry point (`__main__.py:cli_main()`).

6. **Python Path**: Tests may need `PYTHONPATH=src` when running individually if imports fail.

7. **Image Format**: Generated images are always PNG format (hardcoded in `GeneratedImage.format`).

8. **Slide Numbering**: 1-indexed (not 0-indexed). `slide_number` starts at 1 in all models.

9. **Reference Images**: Must be `.jpg`, `.jpeg`, `.png`, or `.webp`. Validated in `BrandAssets.validate_image_paths()`.

10. **JSON Response Parsing**: AI responses must be valid JSON. Use `response_mime_type="application/json"` in `generate_text()` calls to enforce structured output.

11. **Pydantic Validation**: All models use Pydantic v2. Field validators are `@field_validator` (not `@validator` from v1).
