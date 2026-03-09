"""File upload routes."""

from pathlib import Path
from typing import List
import uuid
import aiofiles

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

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
):
    """Upload content file (.md or .txt)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail='Invalid file')

    ext = file.filename.lower().split('.')[-1]
    if ext not in ['md', 'txt', 'markdown']:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid file type: .{ext}. Accepted: .md, .txt, .markdown'
        )

    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    return UploadFileResponse(file_id=file_id, filename=file.filename)


@router.post('/brand-assets', response_model=List[UploadFileResponse])
async def upload_brand_assets(
    files: List[UploadFile] = File(...),
):
    """Upload brand asset images."""
    uploaded = []

    for file in files:
        if not file.filename:
            continue

        ext = file.filename.lower().split('.')[-1]
        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
            raise HTTPException(
                status_code=400,
                detail=f'Invalid file type: .{ext}. Accepted: .jpg, .jpeg, .png, .webp'
            )

        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        uploaded.append(UploadFileResponse(file_id=file_id, filename=file.filename))

    return uploaded
