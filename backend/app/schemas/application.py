from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from app.models import ApplicationStatus
from app.schemas.job import JobPosting

class ApplicationStatusEvent(BaseModel):
    status: ApplicationStatus
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Application(BaseModel):
    id: int
    job_posting: JobPosting
    status: ApplicationStatus
    screenshot_path: Optional[str] = None
    cover_letter_text: Optional[str] = None
    automation_state: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    events: List[ApplicationStatusEvent] = []

    class Config:
        from_attributes = True
