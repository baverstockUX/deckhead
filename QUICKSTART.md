# Quick Start Guide - Deckhead

Get started with Deckhead in 3 simple steps!

## Prerequisites

- Python 3.10 or higher
- Gemini API key (already in your `.env` file)

## Installation

Dependencies are already installed! If you need to reinstall:

```bash
python3 -m pip install -r requirements.txt
```

## Usage

### Run the application:

```bash
cd /Users/christian.baverstock/code/pow
python3 -m src.deck_factory
```

### Follow the interactive prompts:

1. **Content File**: Enter path to your markdown/text file
   - Try the sample: `examples/sample_presentation.md`
   - Or create your own content file

2. **Brand Assets** (Optional):
   - Choose whether to add brand reference images
   - If yes, provide directory or file paths

3. **AI Analysis**:
   - Wait while AI structures your content
   - Review the proposed slide structure

4. **Clarification Questions**:
   - Answer 2-5 questions to refine the presentation
   - Questions cover structure, style, brand, and content

5. **Generation**:
   - Confirm to start generation
   - Watch progress as images are created
   - Wait for PowerPoint assembly

### Output

Your presentation will be saved in the `output/` directory with the name based on your deck title.

## Example Run

```bash
$ python3 -m src.deck_factory

Welcome to Deckhead
AI-Powered PowerPoint Generator

Step 1/5: Content Input
Enter path to content file (.md or .txt): examples/sample_presentation.md
✓ Loaded: sample_presentation.md (1,234 bytes)

Step 2/5: Brand Assets (Optional)
Add brand reference images for style consistency? (y/n): n
Skipping brand assets

Step 3/5: Parsing Content
Analyzing content with AI...
✓ Found structure for 9 slides

Step 4/5: Clarification Questions
The AI has 3 question(s) to improve your deck:

Question 1/3 [STYLE]
What visual style do you prefer?
  1. Modern minimalist
  2. Corporate professional
  3. Creative bold
  4. Data-focused

Your answer: 2

... (more questions)

Step 5/5: Generation
Generate 9 images and create presentation? (y/n): y

Generating images...
[████████████████████] 100% (9/9)
✓ Generated 9 images

Assembling presentation...
✓ Building slides...

Success!
Deck saved to: ./output/Q1_Strategy_Overview.pptx
Generated in 28.3 seconds

Open presentation now? (y/n): y
```

## Tips

### Creating Good Content

- Use markdown headings (`#`, `##`) to structure content
- Each major section typically becomes a slide
- Include details for better image prompts
- Be specific about visual concepts

### Brand Consistency

- Use 2-5 reference images showing your brand style
- Include images with your color palette
- Add examples of preferred visual styles

### Performance

- Generation time depends on number of slides
- 5 images are generated concurrently by default
- Typical: 3-5 seconds per image

## Troubleshooting

### Import Error
```bash
# Make sure you're in the project root
cd /Users/christian.baverstock/code/pow
python3 -m src.deck_factory
```

### API Key Error
- Check `.env` file has: `gemini_key='your-api-key-here'`
- Get API key from: https://makersuite.google.com/app/apikey

### No Images Generated
- Check API quota at Google Cloud Console
- Verify internet connection
- Try reducing concurrent requests

## Next Steps

1. Try the sample: `examples/sample_presentation.md`
2. Create your own content file
3. Experiment with brand assets
4. Customize the output

## Advanced Usage

### Environment Variables

Edit `.env` to customize:

```bash
# API key
gemini_key='your-api-key'

# Optional settings
MAX_CONCURRENT_IMAGES=5
TEMP_DIR=./temp_assets
OUTPUT_DIR=./output
```

### Programmatic Usage

You can also use Deckhead as a library:

```python
import asyncio
from pathlib import Path
from deck_factory import (
    ConfigLoader,
    GeminiClient,
    ContentParser,
    ImageFactory,
    DeckAssembler,
    BrandAssets
)

async def generate_deck():
    # Load config
    config = ConfigLoader.from_env()

    # Initialize components
    client = GeminiClient(config.gemini_api_key)
    parser = ContentParser(client)
    factory = ImageFactory(client)
    assembler = DeckAssembler()

    # Load content
    with open('content.md') as f:
        content = f.read()

    # Parse
    structure, _ = await parser.parse_content(content)

    # Generate images
    requests = [...]  # Create image requests
    images = await factory.generate_images(requests, BrandAssets())

    # Assemble
    output = assembler.create_deck(structure, images, Path('output.pptx'))
    print(f"Deck created: {output}")

# Run
asyncio.run(generate_deck())
```

## Support

- Check README.md for full documentation
- Review examples/ for sample content
- Report issues on GitHub

---

Happy presenting! 🎉
