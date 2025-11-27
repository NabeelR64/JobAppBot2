from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User, Resume
from app.services import resume_parser

router = APIRouter()

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a resume.
    """
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Invalid file format. Only PDF and DOCX are supported.")
    
    content = await file.read()
    text = resume_parser.extract_text_from_file(content, file.filename)
    
    # Save to DB (or S3 in production)
    # For MVP, we'll just save the path as the filename and text
    resume = current_user.resume
    if not resume:
        resume = Resume(user_id=current_user.id, file_path=file.filename, raw_text=text)
        db.add(resume)
    else:
        resume.file_path = file.filename
        resume.raw_text = text
    
    db.commit()
    db.refresh(resume)
    
    return {"filename": file.filename, "extracted_text": text}
