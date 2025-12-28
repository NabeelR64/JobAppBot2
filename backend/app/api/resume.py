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
    

    # Save file to disk
    import os
    import shutil
    
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = f"{UPLOAD_DIR}/{current_user.id}_{file.filename}"
    
    # Reset cursor after reading
    await file.seek(0)
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    # Save to DB
    resume = current_user.resume
    if not resume:
        resume = Resume(user_id=current_user.id, file_path=file_location, raw_text=text)
        db.add(resume)
    else:
        resume.file_path = file_location
        resume.raw_text = text
    
    db.commit()
    db.refresh(resume)
    
    return {"filename": file.filename, "extracted_text": text}

from fastapi.responses import FileResponse

@router.get("/download")
def download_resume(
    current_user: User = Depends(deps.get_current_user),
):
    """
    Download the current user's resume.
    """
    if not current_user.resume or not current_user.resume.file_path:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    image_path = current_user.resume.file_path
    
    import os
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Resume file not found on server")
        
    return FileResponse(image_path, filename=os.path.basename(image_path))
