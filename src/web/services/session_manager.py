"""
Session manager for web interface.

Manages in-memory session state for user workflows.
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class SessionManager:
    """
    In-memory session storage.

    Stores session state for ongoing deck generation workflows.
    """

    def __init__(self, timeout_minutes: int = 30):
        """
        Initialize session manager.

        Args:
            timeout_minutes: Session timeout in minutes (default: 30)
        """
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._timeout = timedelta(minutes=timeout_minutes)

    def create_session(self) -> str:
        """
        Create a new session.

        Returns:
            Session ID (UUID string)
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'session_id': session_id,
            'created_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow(),
            'mode': None,
            'files': {},
            'deck_structure': None,
            'clarification_questions': [],
            'clarification_responses': [],
            'job_id': None,
            'output_path': None,
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        session = self._sessions.get(session_id)
        if session:
            # Check timeout
            if datetime.utcnow() - session['last_accessed'] > self._timeout:
                self.delete_session(session_id)
                return None

            # Update last accessed
            session['last_accessed'] = datetime.utcnow()
            return session
        return None

    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session ID
            data: Data to update (merged with existing)

        Returns:
            True if successful, False if session not found
        """
        session = self.get_session(session_id)
        if session:
            session.update(data)
            session['last_accessed'] = datetime.utcnow()
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        now = datetime.utcnow()
        expired = [
            sid for sid, sess in self._sessions.items()
            if now - sess['last_accessed'] > self._timeout
        ]

        for sid in expired:
            del self._sessions[sid]

        return len(expired)


# Global session manager instance
session_manager = SessionManager()
