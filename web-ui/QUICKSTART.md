# Quick Start Guide - Deckhead Web UI

Get your Deckhead web interface up and running in minutes!

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Backend API running (see backend setup below)

## Installation & Setup

### 1. Install Dependencies

```bash
cd web-ui
npm install
```

This will install all required packages including:
- React 18
- TypeScript
- Tailwind CSS
- Framer Motion (animations)
- Axios (HTTP client)
- Lucide React (icons)

### 2. Start Development Server

```bash
npm run dev
```

The application will start at **http://localhost:5173**

You should see:
```
VITE v5.0.11  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 3. Open in Browser

Navigate to [http://localhost:5173](http://localhost:5173) in your browser.

You should see the Deckhead welcome screen!

## Backend Setup (Required)

The frontend needs the FastAPI backend running. From the project root:

```bash
# Install Python dependencies (if not done)
pip install fastapi uvicorn[standard] websockets python-multipart

# Run the backend
python -m uvicorn src.web.app:app --reload --port 8000
```

The backend should start at **http://localhost:8000**

## Using the Application

### Step-by-Step Workflow

1. **Welcome** - Click "Get Started"
2. **Mode Selection** - Choose "Minimal" or "Rich" text content mode
3. **Content Upload** - Drag & drop your `.md` or `.txt` file
4. **Brand Assets** - Optionally upload reference images for brand consistency
5. **Parsing** - Wait while AI analyzes your content (automatic)
6. **Clarifications** - Answer AI-generated questions (if any)
7. **Confirm** - Review the presentation structure
8. **Generate** - Watch real-time progress as your presentation is created!

### Real-Time Progress

During generation (Step 8), you'll see:
- Live progress updates via WebSocket
- Circular progress indicator showing percentage
- Status messages for each generation phase
- Image count tracker

When complete, click **Download Presentation** to get your `.pptx` file!

## Development Commands

```bash
# Start dev server (hot reload enabled)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run tsc

# Linting
npm run lint
```

## Troubleshooting

### Port Already in Use

If port 5173 is busy:
```bash
# Kill process using port 5173
lsof -ti:5173 | xargs kill -9

# Or specify a different port
npm run dev -- --port 3000
```

### Backend Connection Error

If you see "Failed to connect" errors:

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status": "ok"}`

2. **Check CORS settings** in backend `app.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Check browser console** for detailed error messages

### WebSocket Issues

If real-time progress isn't working:

1. Check browser WebSocket support (DevTools → Network → WS)
2. Verify backend WebSocket endpoint is accessible
3. Check for firewall/proxy blocking WebSocket connections

### Styling Issues

If styles don't load:

```bash
# Rebuild Tailwind
npm run build
```

## Project Structure

```
web-ui/
├── src/
│   ├── components/
│   │   ├── wizard/       # 8 wizard steps
│   │   ├── ui/           # Button, Card, Progress
│   │   └── shared/       # FileUpload
│   ├── hooks/            # useWizardState, useWebSocket
│   ├── services/         # API client
│   ├── types/            # TypeScript definitions
│   ├── lib/              # Utilities
│   ├── styles/           # Global CSS
│   ├── App.tsx           # Main app
│   └── main.tsx          # Entry point
├── index.html            # HTML template
├── package.json          # Dependencies
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
└── tsconfig.json         # TypeScript configuration
```

## Features Overview

### Design Highlights

- **Modern Aesthetic** - Refined professional studio feel
- **Smooth Animations** - Framer Motion-powered transitions
- **Glass Morphism** - Subtle glassmorphic cards
- **Gradient Accents** - Blue to purple color scheme
- **Responsive** - Works on desktop and tablet (optimized for desktop)

### Technical Highlights

- **TypeScript** - Fully typed for safety
- **React Hooks** - Modern React patterns
- **Context API** - Wizard state management
- **WebSocket** - Real-time progress updates
- **Axios** - HTTP client with interceptors
- **Tailwind CSS** - Utility-first styling
- **Vite** - Lightning-fast dev server

### Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Environment Variables (Optional)

Create `.env` file in `web-ui/` directory:

```env
# Optional: Override API URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

## Production Deployment

### Build for Production

```bash
npm run build
```

This creates a `dist/` folder with optimized static files.

### Serve Static Build

```bash
# Using Vite preview
npm run preview

# Or use any static file server
npx serve -s dist
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

## Getting Help

- Check browser console for errors
- Review `README.md` for detailed documentation
- Check backend logs for API issues
- Verify all dependencies are installed

## Next Steps

1. Customize colors in `tailwind.config.js`
2. Add custom fonts in `src/styles/globals.css`
3. Extend wizard with additional steps
4. Add user authentication
5. Implement presentation history

## License

Part of the Deckhead project.

---

**Happy deck building!** 🎉
