"""File upload routes."""

from pathlib import Path
from typing import List
import uuid
import aiofiles

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from ...services.session_manager import session_manager

router = APIRouter(prefix='/api/files', tags=['files'])

# Upload directory
UPLOAD_DIR = Path.cwd() / 'temp_assets'
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


class UploadFileResponse(BaseModel):
    """File upload response."""
    file_id: str
    filename: str


@router.post('/content', response_model=UploadFileResponse)
async def upload_content_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """
    Upload content file (.md or .txt).

    Args:
        file: Content file
        session_id: Session ID

    Returns:
        File ID and filename
    """
    # Validate session
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail='Invalid file')

    ext = file.filename.lower().split('.')[-1]
    if ext not in ['md', 'txt', 'markdown']:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid file type: .{ext}. Accepted: .md, .txt, .markdown'
        )

    # Save file
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    # Update session
    if 'files' not in session:
        session['files'] = {}
    session['files']['content_file_path'] = str(file_path)
    session_manager.update_session(session_id, session)

    return UploadFileResponse(file_id=file_id, filename=file.filename)


@router.post('/brand-assets', response_model=List[UploadFileResponse])
async def upload_brand_assets(
    files: List[UploadFile] = File(...),
    session_id: str = Form(...)
):
    """
    Upload brand asset images.

    Args:
        files: List of image files
        session_id: Session ID

    Returns:
        List of file IDs and filenames
    """
    # Validate session
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    uploaded = []
    brand_asset_paths = session.get('files', {}).get('brand_asset_paths', [])

    for file in files:
        if not file.filename:
            continue

        # Validate file type
        ext = file.filename.lower().split('.')[-1]
        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
            raise HTTPException(
                status_code=400,
                detail=f'Invalid file type: .{ext}. Accepted: .jpg, .jpeg, .png, .webp'
            )

        # Save file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        brand_asset_paths.append(str(file_path))
        uploaded.append(UploadFileResponse(file_id=file_id, filename=file.filename))

    # Update session
    if 'files' not in session:
        session['files'] = {}
    session['files']['brand_asset_paths'] = brand_asset_paths
    session_manager.update_session(session_id, session)

    return uploaded
