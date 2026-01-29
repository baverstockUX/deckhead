# Project Spec: Deckhead (Async PPTX Generator)

## 1. Overview
A Python utility that generates a PowerPoint presentation from a JSON manifest. It uses `asyncio` to generate images in parallel (using OpenAI DALL-E 3 or similar) and `python-pptx` to assemble them into full-bleed slides.

## 2. Tech Stack
- **Language:** Python 3.10+
- **Core Libs:** `python-pptx`, `asyncio`, `aiohttp`, `openai`, `pydantic` (for validation).
- **Env:** `.env` file for `OPENAI_API_KEY`.

## 3. Data Structure (manifest.json)
The application must ingest a JSON file with this schema:
```json
{
  "deck_title": "Q1 Strategy",
  "slides": [
    {
      "id": 1,
      "prompt": "Futuristic UI dashboard showing growth metrics, dark mode, neon accents, 16:9 aspect ratio",
      "overlay_text": "Q1 Performance", 
      "notes": "Speaker notes here"
    },
    {
      "id": 2, 
      "prompt": "Abstract network visualization, blue and gold, 16:9",
      "overlay_text": "The Network Effect"
    }
  ]
}
```

## 4. Architecture Components

### A. `ConfigLoader`
- Loads `.env`.
- Validates `manifest.json` against a Pydantic model.

### B. `ImageFactory` (The Async Engine)
- **Input:** List of slide prompts.
- **Process:** 
  - Use `asyncio.gather` to fire API requests concurrently.
  - Handle rate limits (simple retry logic).
  - Save temporary images to a local `/temp_assets` folder (or keep in memory bytes).
- **Output:** Dictionary mapping `slide_id` -> `image_path`.

### C. `DeckAssembler`
- **Input:** JSON data + Generated Images.
- **Process:**
  - Initialize 16:9 Canvas (13.333" x 7.5").
  - Loop through slides.
  - Create blank slide.
  - Insert image at `(0,0)` with width `13.333"` (Full Bleed).
  - (Optional) Add a text box for `overlay_text` if present.
  - Add speaker notes.
- **Output:** Saves `[deck_title].pptx`.

## 5. Implementation Steps (Instructions for Agent)
1. **Setup:** Create virtual env and `requirements.txt`.
2. **Step 1:** Implement `ConfigLoader` and define Pydantic models.
3. **Step 2:** Implement `ImageFactory` with mock data first (to save API costs during dev), then live OpenAI calls.
4. **Step 3:** Implement `DeckAssembler` using `python-pptx`.
5. **Step 4:** Create a `main.py` orchestrator to run the flow.

## 6. Success Criteria
- Script completes generation of a 10-slide deck in < 30 seconds (dependent on API latency, but parallelized).
- Images fit perfectly (no white borders).
- Code is modular and typed.
