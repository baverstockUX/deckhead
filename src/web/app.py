"""
FastAPI application for Deckhead web interface.

Provides REST API and WebSocket endpoints for deck generation workflow.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import session, files, generation
from .api.websockets.progress import websocket_endpoint

# Create FastAPI app
app = FastAPI(
    title='Deckhead API',
    description='AI-Powered PowerPoint Generator',
    version='1.0.0'
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',  # Vite dev server
        'http://localhost:3000',  # Alternative port
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000',
    ],
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


# Root endpoint
@app.get('/')
async def root():
    """Root endpoint."""
    return {
        'message': 'Deckhead API',
        'docs': '/docs',
        'health': '/api/health'
    }


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
