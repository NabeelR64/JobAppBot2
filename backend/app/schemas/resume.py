from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ResumeBase(BaseModel):
    file_path: str
    raw_text: Optional[str] = None

class ResumeCreate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
