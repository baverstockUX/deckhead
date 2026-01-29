# Deckhead

AI-powered PowerPoint presentation generator using Google Gemini.

Transform plain text or markdown content into professional presentations with AI-generated images, smart content structuring, and interactive clarification questions.

## Features

- **Smart Content Parsing**: Gemini Flash analyzes your content and structures it into logical slides
- **AI Image Generation**: Gemini Imagen generates professional images for each slide
- **Brand Consistency**: Pass reference images to maintain visual style across all slides
- **Interactive Clarification**: AI asks questions to refine the presentation
- **Parallel Processing**: Async image generation for fast performance
- **Beautiful CLI**: Rich terminal interface with progress tracking

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up your Gemini API key**:

Create a `.env` file in the project root (already exists) with your API key:
```bash
gemini_key='your-api-key-here'
```

Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Quick Start

Run the interactive CLI:
```bash
python -m src.deck_factory
```

Or from the project root:
```bash
cd /Users/christian.baverstock/code/pow
python -m src.deck_factory
```

### Step-by-Step Workflow

1. **Content Input**: Provide a markdown or text file with your content
2. **Brand Assets** (Optional): Add reference images for style consistency
3. **AI Analysis**: Gemini parses content and structures slides
4. **Clarification**: Answer AI-generated questions to refine the deck
5. **Generation**: Images are generated and presentation is assembled

### Example

Try the sample content:
```bash
python -m src.deck_factory
# When prompted, enter: examples/sample_presentation.md
```

## Project Structure

```
pow/
├── .env                          # API key configuration
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── src/deck_factory/
│   ├── __main__.py               # Entry point
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Configuration loader
│   │   ├── models.py             # Data models
│   │   └── exceptions.py         # Custom exceptions
│   ├── ai/                       # AI components
│   │   ├── gemini_client.py      # Gemini API wrapper
│   │   ├── content_parser.py     # Content parsing
│   │   ├── clarifier.py          # Question generation
│   │   └── image_factory.py      # Image generation
│   ├── deck/                     # PowerPoint assembly
│   │   └── assembler.py          # PPTX creation
│   └── cli/                      # User interface
│       └── interactive.py        # Interactive CLI
│
├── examples/                     # Example content files
│   └── sample_presentation.md
│
├── output/                       # Generated presentations (created automatically)
└── temp_assets/                  # Temporary files (created automatically)
```

## Content Format

Write your content in plain text or markdown. The AI will automatically:
- Break it into logical slides
- Generate titles and summaries
- Create image prompts
- Write speaker notes

### Example Content

```markdown
# My Presentation Title

## Introduction
Your introduction content here...

## Main Topic 1
Key points and details...

## Main Topic 2
More content...

## Conclusion
Wrap up your presentation...
```

## Brand Assets

To maintain visual consistency, provide reference images:

1. Place brand images (logos, colors, style examples) in a directory
2. When prompted, enter the directory path or comma-separated file paths
3. All generated images will match the style of your references

Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`

## Configuration

Optional environment variables (in `.env`):

```bash
# API Configuration
GEMINI_API_KEY=your_api_key_here
gemini_key=your_api_key_here  # Alternative format (currently used)

# Generation Settings (optional)
MAX_CONCURRENT_IMAGES=5       # Concurrent image generations
TEMP_DIR=./temp_assets        # Temporary file directory
OUTPUT_DIR=./output           # Output directory for presentations
```

## API Models Used

- **Text Generation**: `gemini-2.0-flash-exp` - Fast, efficient content parsing
- **Image Generation**: `imagen-3.0-generate-001` - High-quality image generation

## Performance

- **Parsing**: ~3 seconds for 2000-word content
- **Image Generation**: ~4 seconds per image (API dependent)
- **10-slide deck**: ~30 seconds total (with 5 concurrent requests)

## Troubleshooting

### "Missing API Key" Error
- Check that `.env` file exists in project root
- Verify API key is set: `gemini_key='your-key'` or `GEMINI_API_KEY=your-key`

### Image Generation Fails
- Check API quota at https://console.cloud.google.com/
- Reduce concurrent requests by lowering `MAX_CONCURRENT_IMAGES`
- Verify reference images are in supported formats

### "Module not found" Error
- Install dependencies: `pip install -r requirements.txt`
- Run from project root: `python -m src.deck_factory`

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
```

### Type Checking
```bash
mypy src/
```

## Architecture

Deckhead uses a modular architecture:

1. **ConfigLoader**: Manages environment and settings
2. **GeminiClient**: Unified API wrapper for text and image generation
3. **ContentParser**: Parses content into structured format
4. **Clarifier**: Generates and validates clarification questions
5. **ImageFactory**: Async parallel image generation
6. **DeckAssembler**: Creates PowerPoint with python-pptx
7. **InteractiveCLI**: Rich terminal interface

All components use Pydantic models for type safety and validation.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- File an issue on GitHub
- Check existing issues for solutions
- Contribute via pull requests

## Credits

Built with:
- Google Gemini API
- python-pptx
- Rich (terminal UI)
- Pydantic (validation)
- asyncio (concurrency)

---

**Made with ❤️ using Google Gemini**
