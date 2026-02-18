from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User, Resume
from app.services import resume_parser, embedding

import os
import shutil
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "uploads"

# Magic bytes for file type validation (prevents renamed malicious files)
MAGIC_BYTES = {
    ".pdf": b"%PDF",           # PDF header
    ".docx": b"PK\x03\x04",   # DOCX is a ZIP archive
}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a resume. Extracts text from PDF/DOCX, generates an embedding vector,
    and parses structured data (name, email, phone).
    """
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF and DOCX are supported.")

    content = await file.read()

    # Magic byte validation — verify the file is genuinely what the extension claims
    ext = os.path.splitext(file.filename)[1].lower()
    expected_magic = MAGIC_BYTES.get(ext)
    if expected_magic and not content[:len(expected_magic)] == expected_magic:
        raise HTTPException(
            status_code=400,
            detail=f"File content does not match {ext} format. The file may be corrupted or renamed."
        )

    # Extract real text from the file
    text = resume_parser.extract_text_from_file(content, file.filename)
    if not text:
        logger.warning(f"No text could be extracted from {file.filename}")

    # Generate embedding vector
    embedding_vector = embedding.generate_embedding(text) if text else []

    # Save file to disk
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = f"{UPLOAD_DIR}/{current_user.id}_{file.filename}"

    # Reset cursor after reading
    await file.seek(0)

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    # Save to DB
    resume = current_user.resume
    if not resume:
        resume = Resume(
            user_id=current_user.id,
            file_path=file_location,
            raw_text=text,
            embedding_vector=embedding_vector if embedding_vector else None
        )
        db.add(resume)
    else:
        resume.file_path = file_location
        resume.raw_text = text
        resume.embedding_vector = embedding_vector if embedding_vector else None

    db.commit()
    db.refresh(resume)

    # Parse structured data from the extracted text
    parsed_data = resume_parser.parse_resume_text(text) if text else {}

    return {
        "filename": file.filename,
        "extracted_text": text,
        "suggested_profile": parsed_data,
        "embedding_generated": bool(embedding_vector)
    }


@router.get("/download")
def download_resume(
    current_user: User = Depends(deps.get_current_user),
):
    """
    Download the current user's resume.
    """
    if not current_user.resume or not current_user.resume.file_path:
        raise HTTPException(status_code=404, detail="Resume not found")

    file_path = current_user.resume.file_path

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on server")

    return FileResponse(file_path, filename=os.path.basename(file_path))
