"""Generation workflow routes."""

import asyncio
import uuid
from typing import List, Dict, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from deck_factory.core.models import ClarificationResponse
from web.services.workflow_service import workflow_service
from web.api.websockets.progress import progress_manager

router = APIRouter(prefix='/api/generation', tags=['generation'])

# Track job outputs (job_id -> output_path) for download
_job_outputs: Dict[str, str] = {}


class ParseContentRequest(BaseModel):
    """Parse content request."""
    content: str
    mode: str


class ParseContentResponse(BaseModel):
    """Parse content response."""
    deck_structure: dict
    clarification_questions: List[dict]


class RefineStructureRequest(BaseModel):
    """Refine structure request."""
    deck_structure: dict
    clarifications: List[dict]
    mode: str = 'minimal'


class RefineStructureResponse(BaseModel):
    """Refine structure response."""
    deck_structure: dict


class StartGenerationRequest(BaseModel):
    """Start generation request."""
    deck_structure: dict
    brand_asset_file_ids: List[str] = []


class StartGenerationResponse(BaseModel):
    """Start generation response."""
    job_id: str
    message: str


@router.post('/parse', response_model=ParseContentResponse)
async def parse_content(request: ParseContentRequest):
    """Parse content with AI."""
    try:
        deck_structure, questions = await workflow_service.parse_content(
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
    """Refine deck structure based on clarifications."""
    try:
        clarifications = [
            ClarificationResponse(**c) for c in request.clarifications
        ]

        refined_structure = await workflow_service.refine_structure(
            request.deck_structure,
            clarifications,
            request.mode
        )

        return RefineStructureResponse(
            deck_structure=refined_structure.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_deck_task(job_id: str, deck_structure_data: dict, brand_asset_file_ids: List[str]):
    """Background task for deck generation."""
    try:
        await progress_manager.send(job_id, {
            'type': 'progress',
            'event': 'image_generation_started',
            'data': {
                'message': 'Starting image generation...'
            }
        })

        async def progress_callback(slide_num: int, total: int):
            percentage = int((slide_num / total) * 100)
            await progress_manager.send(job_id, {
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

        output_path = await workflow_service.generate_deck(
            deck_structure_data,
            brand_asset_file_ids,
            progress_callback=lambda s, t: asyncio.create_task(progress_callback(s, t))
        )

        # Store output path for download
        _job_outputs[job_id] = str(output_path)

        await progress_manager.send(job_id, {
            'type': 'progress',
            'event': 'assembly_completed',
            'data': {
                'message': str(output_path),
                'percentage': 100
            }
        })

    except Exception as e:
        await progress_manager.send(job_id, {
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
    """Start deck generation (async)."""
    job_id = str(uuid.uuid4())

    background_tasks.add_task(
        generate_deck_task,
        job_id,
        request.deck_structure,
        request.brand_asset_file_ids
    )

    return StartGenerationResponse(
        job_id=job_id,
        message='Generation started'
    )


@router.get('/download/{job_id}')
async def download_presentation(job_id: str):
    """Download generated presentation."""
    output_path_str = _job_outputs.get(job_id)
    if not output_path_str:
        raise HTTPException(status_code=404, detail='Presentation not found')

    output_path = Path(output_path_str)
    if not output_path.exists():
        raise HTTPException(status_code=404, detail='File not found')

    return FileResponse(
        path=output_path,
        media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
        filename=output_path.name
    )
