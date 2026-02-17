# Deckhead

AI-powered PowerPoint presentation generator using Google Gemini.

Transform plain text or markdown content into professional presentations with AI-generated images, intelligent text layouts, and interactive clarification questions.

**Available Interfaces:**
- **Web UI**: Modern web interface with drag-and-drop, real-time progress, and live WebSocket updates
- **CLI**: Interactive terminal interface with rich formatting and progress tracking

## Features

### Core Features
- **Text Content Modes**: Choose between minimal (titles only) or rich (full content) text modes
- **Smart Content Parsing**: Gemini Flash analyzes your content and structures it into logical slides
- **AI Image Generation**: Gemini Imagen generates professional images for each slide with integrated titles
- **Intelligent Text Layouts**: AI selects optimal layouts per slide (image-only, split, panel, overlay)
- **Infographics Support**: Generates chart and diagram-style visuals for data-heavy slides
- **Structured Text Content**: Bullets, statistics, paragraphs, and callout boxes automatically extracted
- **Brand Consistency**: Pass reference images to maintain visual style across all slides
- **Interactive Clarification**: AI asks questions to refine the presentation
- **Parallel Processing**: Async image generation for fast performance

### Interface Options
- **Modern Web UI**:
  - Drag-and-drop file upload
  - Real-time WebSocket progress updates
  - 8-step wizard workflow
  - Smooth animations and professional design
  - Live generation tracking with percentage and status
- **Rich CLI**:
  - Interactive terminal interface
  - Progress bars and spinners
  - File path autocomplete
  - Color-coded output

## Quick Start

### Option A: Web UI (Recommended)

#### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd web-ui
npm install
cd ..
```

#### 2. Set Up API Key

Create a `.env` file in the project root with your Gemini API key:
```bash
gemini_key='your-api-key-here'
```

Get your API key from: https://makersuite.google.com/app/apikey

#### 3. Start the Backend

```bash
python -m uvicorn src.web.app:app --reload --port 8000
```

#### 4. Start the Frontend

In a separate terminal:
```bash
cd web-ui
npm run dev
```

#### 5. Open in Browser

Navigate to `http://localhost:5173` and enjoy the modern web interface with:
- Drag-and-drop file upload
- Real-time WebSocket progress updates
- Interactive wizard workflow
- Live generation tracking

### Option B: CLI

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Set Up API Key

Create a `.env` file in the project root with your Gemini API key:
```bash
gemini_key='your-api-key-here'
```

Get your API key from: https://makersuite.google.com/app/apikey

#### 3. Create Your Content

Create a markdown or text file in the `content/` directory:

```markdown
# My Presentation Title

## Introduction
Your introduction content here...

## Main Topic 1
Key points and details...

## Conclusion
Wrap up your presentation...
```

#### 4. Run Deckhead

```bash
python -m src.deck_factory
```

Follow the interactive prompts:
1. Select text content mode (`minimal` for titles only, `rich` for full content)
2. Enter path to your content file (e.g., `content/my_presentation.md`)
3. Optionally add brand reference images
4. Answer clarification questions from the AI
5. Wait for images to generate
6. Get your PowerPoint file in the `src/output/` directory!

## Text Content Modes

Choose between two generation modes at startup:

### Minimal Mode (Default)
- **Titles only**: Clean visual storytelling with titles integrated into images
- **All slides use image-only layout**: No bullets, statistics, or text content
- **Faster generation**: Skips text content analysis
- **Best for**: Executive summaries, pitch decks, visual presentations

### Rich Mode
- **Full content**: Bullets, statistics, paragraphs, and callouts baked into images
- **AI layout selection**: Intelligent choice of layout per slide based on content
- **Information-dense**: More text content for detailed presentations
- **Best for**: Educational content, detailed proposals, data-driven presentations

## Slide Layouts

In rich mode, the AI automatically selects the best layout for each slide based on content:

- **image-only**: Pure visual storytelling with title integrated into image (default)
- **split-left**: Image on left, text content on right (balanced visual + text)
- **split-right**: Image on right, text content on left
- **panel**: Full-width image on top, text panel below
- **overlay**: Minimal text overlaid on image

Text content can include:
- **Bullets**: Concise points (max 7)
- **Statistics**: Key metrics with labels and values
- **Paragraphs**: Short explanatory text
- **Callouts**: Highlighted information boxes

In minimal mode, all slides use **image-only** layout with no text content.

## Web UI Workflow

The web interface provides an 8-step wizard experience:

1. **Welcome** - Introduction and session creation
2. **Mode Selection** - Choose minimal or rich text content mode
3. **Content Upload** - Drag & drop your markdown/text file
4. **Brand Assets** - Optional: Upload reference images for visual consistency
5. **AI Parsing** - Automatic content analysis with loading state
6. **Clarifications** - Answer dynamic AI-generated questions
7. **Structure Preview** - Review and confirm presentation structure
8. **Generation** - Real-time progress via WebSocket with percentage updates

**Key Features:**
- **Live Progress**: WebSocket connection provides real-time updates during image generation
- **Drag & Drop**: Easy file upload with validation and visual feedback
- **Responsive Design**: Glassmorphic cards, smooth animations, gradient accents
- **Download Ready**: One-click PowerPoint download when complete

**Tech Stack:** React 18, TypeScript, Tailwind CSS, Framer Motion, Vite, Axios, WebSocket

## Brand Assets

To maintain visual consistency, provide reference images:

1. Place brand images (logos, colors, style examples) in the `references/` directory
2. When prompted, enter the directory path or comma-separated file paths
3. All generated images will match the style of your references

Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`

## Project Structure

```
pow/
├── .env                          # API key configuration
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── src/deck_factory/             # Core presentation engine
│   ├── __main__.py               # CLI entry point
│   ├── core/                     # Core functionality
│   │   ├── config.py             # Configuration loader
│   │   ├── models.py             # Data models (5 layout types)
│   │   └── exceptions.py         # Custom exceptions
│   ├── ai/                       # AI components
│   │   ├── gemini_client.py      # Gemini API wrapper
│   │   ├── content_parser.py     # Content parsing & layout selection
│   │   ├── clarifier.py          # Question generation
│   │   └── image_factory.py      # Image generation (infographic support)
│   ├── deck/                     # PowerPoint assembly
│   │   └── assembler.py          # PPTX creation (5 layout types)
│   └── cli/                      # CLI user interface
│       └── interactive.py        # Interactive CLI
│
├── src/web/                      # Web API backend (FastAPI)
│   ├── app.py                    # FastAPI application
│   ├── api/                      # API routes
│   │   ├── routes/               # HTTP endpoints (session, files, generation)
│   │   └── websockets/           # WebSocket handlers (real-time progress)
│   ├── services/                 # Business logic
│   │   ├── session_manager.py    # Session management
│   │   └── workflow_service.py   # Presentation workflow
│   └── schemas/                  # Pydantic schemas
│
├── web-ui/                       # Web frontend (React + TypeScript)
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── wizard/           # 8-step wizard
│   │   │   ├── ui/               # Reusable UI components
│   │   │   └── shared/           # Shared components (FileUpload)
│   │   ├── hooks/                # React hooks (useWizardState, useWebSocket)
│   │   ├── services/             # API client (Axios)
│   │   ├── types/                # TypeScript definitions
│   │   └── App.tsx               # Main app component
│   ├── package.json              # Node.js dependencies
│   ├── vite.config.ts            # Vite configuration
│   └── tailwind.config.js        # Tailwind CSS configuration
│
├── content/                      # Your content files (gitignored)
│   └── my_presentation.md
│
├── references/                   # Brand reference images (gitignored)
│   └── brand_logo.png
│
├── src/output/                   # Generated presentations (created automatically)
└── temp_assets/                  # Temporary files (created automatically)
```

## Configuration

### Environment Variables

Optional environment variables (in `.env`):

```bash
# API Configuration (required)
gemini_key=your_api_key_here

# Generation Settings (optional)
MAX_CONCURRENT_IMAGES=5       # Concurrent image generations (default: 5)
TEMP_DIR=./temp_assets        # Temporary file directory (default: ./temp_assets)
OUTPUT_DIR=./src/output       # Output directory for presentations (default: ./src/output)
```

### Dependencies

**Python (Backend & CLI)**
- Core: google-generativeai, python-pptx, pydantic, rich
- Web API: fastapi, uvicorn, websockets, python-multipart
- Utilities: python-dotenv, aiofiles, tenacity

**Node.js (Web UI)**
- Framework: React 18, TypeScript, Vite
- Styling: Tailwind CSS, Framer Motion
- Client: Axios, WebSocket
- See `web-ui/package.json` for full list

## API Models Used

- **Text Generation**: `gemini-3-flash-preview` - Fast, efficient content parsing and layout decisions
- **Image Generation**: `gemini-3-pro-image-preview` - High-quality image generation with infographic support

## Performance

- **Parsing**: ~3 seconds for 2000-word content
- **Image Generation**: ~4 seconds per image (API dependent)
- **10-slide deck**: ~30 seconds total (with 5 concurrent requests)

## Content Format

Write your content in plain text or markdown. The AI will automatically:
- Break it into logical slides
- Generate titles integrated into images
- Decide optimal layout per slide (image-only, split, panel, overlay)
- Extract structured text content (bullets, statistics, paragraphs)
- Generate infographic-style images for data-heavy slides
- Create image prompts matching your content
- Write speaker notes

### Example Content

```markdown
# Product Launch Presentation

## Market Overview
The market is growing at 15% annually. Key trends include:
- Digital transformation
- Mobile-first experiences
- AI integration

Statistics:
- Market size: $50B
- Growth rate: 15% YoY
- Adoption: 78% of enterprises

## Our Solution
A revolutionary platform that combines ease-of-use with enterprise power...

## Competitive Advantage
What sets us apart from competitors...
```

The AI will:
- Create an **image-only** slide for "Our Solution" (visual storytelling)
- Use **split-left** layout for "Market Overview" (image + bullets + stats)
- Generate **infographic-style** image for statistics
- Choose **panel** layout for "Competitive Advantage" (image + text)

## Troubleshooting

### General Issues

#### "Missing API Key" Error
- Check that `.env` file exists in project root
- Verify API key is set: `gemini_key='your-key'`

#### Image Generation Fails
- Check API quota at https://console.cloud.google.com/
- Reduce concurrent requests: `MAX_CONCURRENT_IMAGES=3` in `.env`
- Verify reference images are in supported formats (jpg, png, webp)

#### "Module not found" Error
- Install dependencies: `pip install -r requirements.txt`
- Run from project root: `python -m src.deck_factory`

#### Content Not Displaying on Slides
- Ensure content has substantial text (3+ bullets or meaningful paragraphs)
- AI defaults to image-only layout when content is minimal
- Check that content is structured properly (headings, bullets, etc.)

### Web UI Issues

#### Backend Connection Error
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status": "ok"}`
2. Check CORS settings in `src/web/app.py`
3. Ensure ports 8000 (backend) and 5173 (frontend) are not blocked

#### WebSocket Not Connecting
- Check browser console for WebSocket errors
- Verify backend WebSocket endpoint is accessible
- Check firewall/proxy settings
- Try Chrome/Firefox DevTools → Network → WS tab

#### Port Already in Use
```bash
# Kill process on port 5173 (frontend)
lsof -ti:5173 | xargs kill -9

# Kill process on port 8000 (backend)
lsof -ti:8000 | xargs kill -9
```

#### Styles Not Loading (Web UI)
```bash
cd web-ui
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Development

### Running Tests

**Python/Backend:**
```bash
# Run full test suite
pytest tests/

# Run specific test
python3 tests/test_e2e.py
```

**Web UI:**
```bash
cd web-ui

# Type checking
npm run tsc

# Linting
npm run lint
```

### Code Formatting

**Python:**
```bash
black src/
```

**Web UI:**
```bash
cd web-ui
npm run format  # If configured
```

### Type Checking

**Python:**
```bash
mypy src/
```

**TypeScript:**
```bash
cd web-ui
npm run tsc
```

### Running in Development

**Backend (with hot reload):**
```bash
python -m uvicorn src.web.app:app --reload --port 8000
```

**Frontend (with hot reload):**
```bash
cd web-ui
npm run dev
```

## Architecture

Deckhead uses a modular architecture with AI-driven layout selection:

### Core Engine (Python)
1. **ConfigLoader**: Manages environment and settings
2. **GeminiClient**: Unified API wrapper for text and image generation
3. **ContentParser**: Parses content into structured format with layout decisions
4. **Clarifier**: Generates and validates clarification questions
5. **ImageFactory**: Async parallel image generation with infographic support
6. **DeckAssembler**: Creates PowerPoint with 5 layout types (python-pptx)

### User Interfaces
**CLI Interface:**
- **InteractiveCLI**: Rich terminal interface with progress tracking

**Web Interface:**
- **FastAPI Backend**: RESTful API + WebSocket endpoints for real-time updates
- **Session Manager**: Stateful session management for multi-step workflow
- **Workflow Service**: Orchestrates presentation generation pipeline
- **React Frontend**: TypeScript-based SPA with wizard workflow
- **WebSocket Client**: Real-time progress updates during generation

All components use Pydantic models for type safety and validation.

## Recent Updates

### v0.4 - Web UI Interface (Feb 2026)
- ✨ **New Web UI**: Modern React-based interface with 8-step wizard
- ✨ **Real-time Progress**: WebSocket integration for live generation updates
- ✨ **Drag & Drop**: File upload with visual feedback
- ✨ **FastAPI Backend**: RESTful API with async workflow orchestration
- ✨ **Professional Design**: Glassmorphic UI with smooth animations
- 🏗️ **Architecture**: Separation of core engine from interface layers
- 📚 Comprehensive web UI documentation and quickstart guide

### v0.3 - Text Content Mode Switcher (Jan 2026)
- ✨ Added text content mode selector (minimal vs rich)
- ✨ Minimal mode: Titles only, clean visual storytelling (default)
- ✨ Rich mode: Full text content with intelligent layouts
- ✨ Mode-aware AI prompt generation
- 📚 Comprehensive documentation updates

### v0.2 - Text Content & Infographics (Jan 2026)
- ✨ Added 5 intelligent slide layouts (image-only, split, panel, overlay)
- ✨ AI-driven layout selection per slide
- ✨ Structured text content support (bullets, statistics, paragraphs, callouts)
- ✨ Infographic-style image generation for data-heavy slides
- ✨ Professional typography and spacing

### v0.1 - Title Integration (Jan 2026)
- ✨ Integrated slide titles into images (no more overlays)
- 🐛 Fixed title overlay transparency issues

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- File an issue on GitHub
- Check existing issues for solutions
- Contribute via pull requests

## Credits

Built with:

**AI & Core:**
- Google Gemini API (Gemini 3 Flash + Gemini 3 Pro Image)
- python-pptx (PowerPoint generation)
- Pydantic (validation)
- asyncio (concurrency)

**CLI Interface:**
- Rich (terminal UI)

**Web Backend:**
- FastAPI (API framework)
- Uvicorn (ASGI server)
- WebSockets (real-time updates)

**Web Frontend:**
- React 18 (UI framework)
- TypeScript (type safety)
- Vite (build tool)
- Tailwind CSS (styling)
- Framer Motion (animations)
- Axios (HTTP client)

---

**Made with ❤️ using Google Gemini**
