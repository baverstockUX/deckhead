"""Production entry point for Deckhead web app."""
import sys
import os

# Add src to Python path so 'from web.services...' imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Export app at module level so platforms can find it via 'main:app'
from web.app import app  # noqa: E402

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
