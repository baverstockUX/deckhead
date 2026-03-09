"""Session management routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from web.services.session_manager import session_manager

router = APIRouter(prefix='/api/session', tags=['session'])


class CreateSessionResponse(BaseModel):
    """Create session response."""
    session_id: str


@router.post('/create', response_model=CreateSessionResponse)
async def create_session():
    """Create a new session."""
    session_id = session_manager.create_session()
    return CreateSessionResponse(session_id=session_id)


@router.get('/{session_id}')
async def get_session(session_id: str):
    """Get session data."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')
    return session


@router.delete('/{session_id}')
async def delete_session(session_id: str):
    """Delete a session."""
    deleted = session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Session not found')
    return {'status': 'deleted'}
