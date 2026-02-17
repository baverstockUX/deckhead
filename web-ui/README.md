# Deckhead Web UI

Professional web interface for Deckhead, the AI-powered PowerPoint generator.

## Features

- 🎨 **Modern Design** - Clean, professional interface with smooth animations
- 🚀 **Real-time Progress** - WebSocket-based live updates during generation
- 📁 **Drag & Drop** - Easy file upload for content and brand assets
- 💬 **Interactive Clarifications** - Dynamic AI-generated questions
- 📊 **Structure Preview** - Review your presentation before generation
- ⚡ **Fast Generation** - Parallel image processing with progress tracking

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Vite** - Fast build tool
- **Axios** - HTTP client
- **WebSocket** - Real-time updates

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── wizard/          # 8-step wizard components
│   ├── ui/              # Reusable UI components (Button, Card, Progress)
│   └── shared/          # Shared components (FileUpload)
├── hooks/
│   ├── useWizardState.tsx   # Wizard state management
│   └── useWebSocket.ts      # WebSocket connection hook
├── services/
│   └── api.ts           # API client
├── types/
│   ├── models.ts        # TypeScript types
│   └── api.ts           # API request/response types
├── styles/
│   └── globals.css      # Global styles
├── lib/
│   └── utils.ts         # Utility functions
├── App.tsx              # Main app component
└── main.tsx             # Entry point
```

## Backend Connection

The frontend expects a FastAPI backend running at `http://localhost:8000`. The Vite config proxies API requests:

- `/api/*` → `http://localhost:8000/api/*`
- `/ws/*` → `ws://localhost:8000/ws/*`

See the main project README for backend setup instructions.

## Development

### Environment Variables

No environment variables needed for development. API connection is configured via Vite proxy.

### Code Style

- TypeScript strict mode enabled
- ESLint for code quality
- Prettier for code formatting (recommended)

### Key Features Implementation

#### Wizard State Management
The wizard uses React Context (`useWizardState`) to manage state across 8 steps:
1. Welcome & session creation
2. Mode selection (minimal/rich)
3. Content file upload
4. Brand assets upload (optional)
5. AI parsing (loading state)
6. Clarification questions (dynamic)
7. Structure confirmation (preview table)
8. Generation with real-time progress (WebSocket)

#### Real-Time Progress
WebSocket connection (`useWebSocket`) provides live updates during image generation:
- Connection status monitoring
- Automatic reconnection on failure
- Progress percentage updates
- Status message updates

#### File Upload
Drag-and-drop file upload with validation:
- File type validation
- File size limits
- Visual feedback
- Multiple file support (brand assets)

## Troubleshooting

### Backend Connection Issues

If you see connection errors:
1. Ensure the backend is running at `http://localhost:8000`
2. Check CORS settings in FastAPI backend
3. Verify WebSocket endpoint is accessible

### Build Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## License

Part of the Deckhead project.
