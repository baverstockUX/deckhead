"""WebSocket progress handler."""

import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


class ProgressManager:
    """
    Manages WebSocket connections for progress updates.

    Broadcasts progress messages to all connected clients for a session.
    """

    def __init__(self):
        """Initialize progress manager."""
        self._connections: Dict[str, Set[WebSocket]] = {}

    def register(self, session_id: str, websocket: WebSocket):
        """
        Register a WebSocket connection for a session.

        Args:
            session_id: Session ID
            websocket: WebSocket connection
        """
        if session_id not in self._connections:
            self._connections[session_id] = set()
        self._connections[session_id].add(websocket)

    def unregister(self, session_id: str, websocket: WebSocket):
        """
        Unregister a WebSocket connection.

        Args:
            session_id: Session ID
            websocket: WebSocket connection
        """
        if session_id in self._connections:
            self._connections[session_id].discard(websocket)
            if not self._connections[session_id]:
                del self._connections[session_id]

    async def send(self, session_id: str, message: dict):
        """
        Send message to all connections for a session.

        Args:
            session_id: Session ID
            message: Message dict to send
        """
        if session_id not in self._connections:
            return

        # Send to all connected clients
        dead_connections = set()
        for websocket in self._connections[session_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                # Mark for removal
                dead_connections.add(websocket)

        # Remove dead connections
        for websocket in dead_connections:
            self.unregister(session_id, websocket)


# Global progress manager instance
progress_manager = ProgressManager()


async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for progress updates.

    Args:
        websocket: WebSocket connection
        session_id: Session ID
    """
    await websocket.accept()
    progress_manager.register(session_id, websocket)

    try:
        # Keep connection alive
        while True:
            # Wait for any messages from client (e.g., ping)
            data = await websocket.receive_text()
            # Echo back for ping/pong
            if data == 'ping':
                await websocket.send_text('pong')

    except WebSocketDisconnect:
        progress_manager.unregister(session_id, websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        progress_manager.unregister(session_id, websocket)
