# Deckhead Test Suite

This directory contains test scripts for verifying Deckhead functionality.

## Test Files

### `test_client.py`
**Purpose**: Test GeminiClient functionality
**What it tests**:
- Text generation with JSON response
- JSON parsing and cleaning
- generate_image() method signature and parameters

**Run**:
```bash
cd /path/to/deckhead
python3 tests/test_client.py
```

---

### `test_parser.py`
**Purpose**: Test ContentParser with sample content
**What it tests**:
- Content parsing from markdown
- Slide structure extraction
- Clarification question generation
- Image prompt generation

**Run**:
```bash
python3 tests/test_parser.py
```

**Requires**: `examples/sample_presentation.md`

---

### `test_image_generation.py`
**Purpose**: Test actual image generation and saving
**What it tests**:
- Complete image generation via Gemini API
- Image data extraction
- File saving to output folder
- Image format validation

**Run**:
```bash
python3 tests/test_image_generation.py
```

**Output**: `output/test_image_YYYYMMDD_HHMMSS.png`

---

### `test_reference_images.py`
**Purpose**: Test reference image functionality (brand assets)
**What it tests**:
- Reference image path validation
- PIL Image loading
- Passing reference images to API
- Style transfer/consistency

**Run**:
```bash
python3 tests/test_reference_images.py
```

**Requires**: Must run `test_image_generation.py` first to create reference image
**Output**: `output/test_with_reference_YYYYMMDD_HHMMSS.png`

---

### `test_e2e.py`
**Purpose**: End-to-end integration test (without actual image generation)
**What it tests**:
- Full workflow from config to deck assembly
- Component initialization
- Content parsing
- Clarification responses
- Structure refinement
- Image generation interface (mocked)

**Run**:
```bash
python3 tests/test_e2e.py
```

---

## Test Order

For complete verification, run in this order:

1. `test_client.py` - Verify GeminiClient works
2. `test_parser.py` - Verify content parsing works
3. `test_image_generation.py` - Verify image generation works (creates reference image)
4. `test_reference_images.py` - Verify reference images work
5. `test_e2e.py` - Verify full workflow

## Quick Test All

```bash
cd /path/to/deckhead
python3 tests/test_client.py && \
python3 tests/test_parser.py && \
python3 tests/test_image_generation.py && \
python3 tests/test_reference_images.py && \
python3 tests/test_e2e.py
```

## Requirements

- Python 3.10+
- All dependencies installed (`pip install -r requirements.txt`)
- Gemini API key in `.env` file
- Internet connection (for API calls)

## Notes

- Tests that call the Gemini API will use your API quota
- Image generation tests take 10-20 seconds each
- Generated test images are saved to `output/` directory
- Test images are gitignored but kept locally for reference

## Troubleshooting

### Import Errors
Make sure to set PYTHONPATH:
```bash
PYTHONPATH=src python3 tests/test_client.py
```

### API Errors
- Check `.env` file has valid `gemini_key`
- Verify API quota not exceeded
- Check internet connection

### Image Generation Fails
- Ensure using correct model names (gemini-3-flash-preview, gemini-3-pro-image-preview)
- Check API has image generation enabled
- Verify output directory exists and is writable
