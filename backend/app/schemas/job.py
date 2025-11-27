from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class JobPostingBase(BaseModel):
    external_id: str
    title: str
    company_name: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    description: Optional[str] = None
    employment_type: Optional[str] = None
    url: Optional[str] = None

class JobPostingCreate(JobPostingBase):
    pass

class JobPosting(JobPostingBase):
    id: int
    fetched_at: datetime

    class Config:
        from_attributes = True

class SwipeActionCreate(BaseModel):
    job_posting_id: int
    direction: str # LEFT, RIGHT
