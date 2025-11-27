from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User, JobPosting, SwipeAction, Application, ApplicationStatus
from app.schemas import job as job_schema
from app.services import job_ingestion, automation

router = APIRouter()

@router.post("/ingest")
def trigger_ingestion(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user), # Admin only in real app
) -> Any:
    """
    Trigger job ingestion manually.
    """
    job_ingestion.ingest_jobs(db)
    return {"message": "Ingestion triggered"}

@router.get("/recommendations", response_model=List[job_schema.JobPosting])
def get_recommendations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 10,
) -> Any:
    """
    Get job recommendations.
    For MVP, just return random jobs that haven't been swiped yet.
    """
    # Get swiped job ids
    swiped_ids = db.query(SwipeAction.job_posting_id).filter(SwipeAction.user_id == current_user.id).all()
    swiped_ids = [id[0] for id in swiped_ids]
    
    jobs = db.query(JobPosting).filter(JobPosting.id.notin_(swiped_ids)).offset(skip).limit(limit).all()
    
    # If no jobs, trigger ingestion and try again (simple hack for MVP)
    if not jobs:
        job_ingestion.ingest_jobs(db)
        jobs = db.query(JobPosting).filter(JobPosting.id.notin_(swiped_ids)).offset(skip).limit(limit).all()
        
    return jobs

@router.post("/{job_id}/swipe")
def swipe_job(
    job_id: int,
    swipe: job_schema.SwipeActionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Swipe on a job.
    """
    # Record swipe
    action = SwipeAction(user_id=current_user.id, job_posting_id=job_id, action=swipe.direction)
    db.add(action)
    
    if swipe.direction == "RIGHT":
        # Create Application
        application = Application(
            user_id=current_user.id,
            job_posting_id=job_id,
            status=ApplicationStatus.PENDING_AUTOMATION
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        
        # Trigger automation worker
        background_tasks.add_task(automation.run_automation, application.id, db)
    else:
        db.commit()
        
    return {"message": "Swipe recorded"}
