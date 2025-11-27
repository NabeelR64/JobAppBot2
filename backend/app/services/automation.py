import time
from sqlalchemy.orm import Session
from app.models import Application, ApplicationStatus, ApplicationStatusEvent

from app.services import cover_letter

def run_automation(application_id: int, db: Session):
    """
    Simulate browser automation to apply for a job.
    """
    print(f"Starting automation for application {application_id}")
    
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        return
        
    # Generate Cover Letter
    resume_text = application.user.resume.raw_text if application.user.resume else "No resume"
    job_desc = application.job_posting.description
    letter = cover_letter.generate_cover_letter(resume_text, job_desc)
    print(f"Generated Cover Letter:\n{letter}")
    
    # Simulate processing time
    time.sleep(5)

    # Update status to APPLIED
    application.status = ApplicationStatus.APPLIED
    
    # Add event
    event = ApplicationStatusEvent(
        application_id=application.id,
        status=ApplicationStatus.APPLIED,
        message="Successfully applied via automation."
    )
    db.add(event)
    db.commit()
    print(f"Automation completed for application {application_id}")
