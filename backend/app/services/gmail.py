from sqlalchemy.orm import Session
from app.models import Application, ApplicationStatus, ApplicationStatusEvent

def poll_gmail_mock(db: Session):
    """
    Mock polling Gmail for updates.
    """
    print("Polling Gmail for updates...")
    
    # Find applications that are APPLIED
    applications = db.query(Application).filter(Application.status == ApplicationStatus.APPLIED).all()
    
    for app in applications:
        # Simulate finding an email
        # In real app, we would check sender/subject
        print(f"Checking emails for application {app.id}")
        
        # Randomly update status
        import random
        if random.random() < 0.3:
            app.status = ApplicationStatus.INTERVIEW_INVITED
            event = ApplicationStatusEvent(
                application_id=app.id,
                status=ApplicationStatus.INTERVIEW_INVITED,
                message="Interview invitation detected in Gmail."
            )
            db.add(event)
            print(f"Updated application {app.id} to INTERVIEW_INVITED")
            
    db.commit()
