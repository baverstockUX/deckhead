"""
FastAPI application for Deckhead web interface.

Provides REST API and WebSocket endpoints for deck generation workflow.
"""

import os
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .api.routes import session, files, generation
from .api.websockets.progress import websocket_endpoint

# Create FastAPI app
app = FastAPI(
    title='Deckhead API',
    description='AI-Powered PowerPoint Generator',
    version='1.0.0'
)

# Configure CORS
cors_origins = [
    'http://localhost:5173',  # Vite dev server
    'http://localhost:3000',  # Alternative port
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
]
# Allow additional origins from environment
if os.environ.get('CORS_ORIGINS'):
    cors_origins.extend(os.environ['CORS_ORIGINS'].split(','))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include routers
app.include_router(session.router)
app.include_router(files.router)
app.include_router(generation.router)


# WebSocket endpoint
@app.websocket('/ws/progress/{session_id}')
async def websocket_progress(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await websocket_endpoint(websocket, session_id)


# Health check
@app.get('/api/health')
async def health_check():
    """Health check endpoint."""
    return {'status': 'ok'}


# Serve built frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / 'web-ui' / 'dist'


@app.get('/')
async def root():
    """Serve frontend index.html or API info."""
    if FRONTEND_DIR.is_dir():
        return FileResponse(str(FRONTEND_DIR / 'index.html'))
    return {'message': 'Deckhead API', 'docs': '/docs', 'health': '/api/health'}


# Mount static assets if frontend is built
if FRONTEND_DIR.is_dir() and (FRONTEND_DIR / 'assets').is_dir():
    app.mount('/assets', StaticFiles(directory=str(FRONTEND_DIR / 'assets')), name='frontend-assets')


# SPA catch-all: serve index.html for any non-API route (must be registered last)
@app.get('/{path:path}')
async def serve_frontend(path: str):
    """Serve frontend static files or index.html for SPA routing."""
    if FRONTEND_DIR.is_dir():
        file_path = FRONTEND_DIR / path
        if file_path.is_file() and file_path.resolve().is_relative_to(FRONTEND_DIR.resolve()):
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / 'index.html'))
    return JSONResponse(status_code=404, content={'detail': 'Not found'})


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={'detail': str(exc)}
    )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
