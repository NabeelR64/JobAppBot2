import logging
from sqlalchemy.orm import Session
from app.models import Application, ApplicationStatus, ApplicationStatusEvent
from app.services import cover_letter

logger = logging.getLogger(__name__)


def run_automation(application_id: int, db: Session):
    """
    Simulate browser automation to apply for a job.
    Generates a real cover letter via OpenAI (or fallback template).
    """
    logger.info(f"Starting automation for application {application_id}")

    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        return

    # Gather data for cover letter
    resume_text = application.user.resume.raw_text if application.user.resume else "No resume"
    job_desc = application.job_posting.description or "No description available"

    # Build user profile dict for richer cover letter generation
    user_profile = None
    if application.user.profile:
        profile = application.user.profile
        user_profile = {
            "name": profile.name,
            "desired_roles": profile.desired_roles,
            "field_of_work": profile.field_of_work,
        }

    # Generate Cover Letter (now calls OpenAI or uses fallback)
    letter = cover_letter.generate_cover_letter(resume_text, job_desc, user_profile)
    logger.info(f"Generated Cover Letter for application {application_id}:\n{letter[:200]}...")

    # TODO: Replace with real Playwright automation in Goal 2
    import time
    time.sleep(2)

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
    logger.info(f"Automation completed for application {application_id}")
