"""Generation workflow routes."""

import asyncio
from typing import List
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ....deck_factory.core.models import ClarificationResponse
from ...services.workflow_service import workflow_service
from ...services.session_manager import session_manager
from ...api.websockets.progress import progress_manager

router = APIRouter(prefix='/api/generation', tags=['generation'])


class ParseContentRequest(BaseModel):
    """Parse content request."""
    session_id: str
    content: str
    mode: str


class ParseContentResponse(BaseModel):
    """Parse content response."""
    deck_structure: dict
    clarification_questions: List[dict]


class RefineStructureRequest(BaseModel):
    """Refine structure request."""
    session_id: str
    clarifications: List[dict]


class RefineStructureResponse(BaseModel):
    """Refine structure response."""
    deck_structure: dict


class StartGenerationRequest(BaseModel):
    """Start generation request."""
    session_id: str


class StartGenerationResponse(BaseModel):
    """Start generation response."""
    job_id: str
    message: str


@router.post('/parse', response_model=ParseContentResponse)
async def parse_content(request: ParseContentRequest):
    """
    Parse content with AI.

    Args:
        request: Parse content request

    Returns:
        Deck structure and clarification questions
    """
    try:
        deck_structure, questions = await workflow_service.parse_content(
            request.session_id,
            request.content,
            request.mode
        )

        return ParseContentResponse(
            deck_structure=deck_structure.model_dump(),
            clarification_questions=[q.model_dump() for q in questions]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/refine', response_model=RefineStructureResponse)
async def refine_structure(request: RefineStructureRequest):
    """
    Refine deck structure based on clarifications.

    Args:
        request: Refine structure request

    Returns:
        Refined deck structure
    """
    try:
        # Convert dict clarifications to ClarificationResponse objects
        clarifications = [
            ClarificationResponse(**c) for c in request.clarifications
        ]

        refined_structure = await workflow_service.refine_structure(
            request.session_id,
            clarifications
        )

        return RefineStructureResponse(
            deck_structure=refined_structure.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_deck_task(session_id: str, job_id: str):
    """
    Background task for deck generation.

    Args:
        session_id: Session ID
        job_id: Job ID
    """
    try:
        # Send start event
        await progress_manager.send(session_id, {
            'type': 'progress',
            'event': 'image_generation_started',
            'data': {
                'message': 'Starting image generation...'
            }
        })

        # Progress callback
        async def progress_callback(slide_num: int, total: int):
            percentage = int((slide_num / total) * 100)
            await progress_manager.send(session_id, {
                'type': 'progress',
                'event': 'image_generated',
                'data': {
                    'slide_number': slide_num,
                    'completed': slide_num,
                    'total': total,
                    'percentage': percentage,
                    'message': f'Generating images ({slide_num}/{total})...'
                }
            })

        # Generate deck
        output_path = await workflow_service.generate_deck(
            session_id,
            progress_callback=lambda s, t: asyncio.create_task(progress_callback(s, t))
        )

        # Send completion event
        await progress_manager.send(session_id, {
            'type': 'progress',
            'event': 'assembly_completed',
            'data': {
                'message': str(output_path),
                'percentage': 100
            }
        })

    except Exception as e:
        # Send error event
        await progress_manager.send(session_id, {
            'type': 'progress',
            'event': 'error',
            'data': {
                'error': str(e)
            }
        })


@router.post('/start', response_model=StartGenerationResponse)
async def start_generation(
    request: StartGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start deck generation (async).

    Args:
        request: Start generation request
        background_tasks: FastAPI background tasks

    Returns:
        Job ID and status message
    """
    session = session_manager.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    # Create job ID
    import uuid
    job_id = str(uuid.uuid4())

    # Update session
    session_manager.update_session(request.session_id, {'job_id': job_id})

    # Start background task
    background_tasks.add_task(generate_deck_task, request.session_id, job_id)

    return StartGenerationResponse(
        job_id=job_id,
        message='Generation started'
    )


@router.get('/download/{job_id}')
async def download_presentation(job_id: str):
    """
    Download generated presentation.

    Args:
        job_id: Job ID

    Returns:
        PPTX file
    """
    # Find session with this job_id
    session = None
    for sid, sess in session_manager._sessions.items():
        if sess.get('job_id') == job_id:
            session = sess
            break

    if not session or not session.get('output_path'):
        raise HTTPException(status_code=404, detail='Presentation not found')

    output_path = Path(session['output_path'])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail='File not found')

    return FileResponse(
        path=output_path,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename=output_path.name
    )
