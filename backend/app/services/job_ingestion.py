from sqlalchemy.orm import Session
from app.models import JobPosting, User
from app.services.theirstack import theirstack_service
import random # For mocking

def ingest_jobs(db: Session):
    """
    Mock ingestion for now or simple manual trigger.
    """
    pass

def fetch_jobs_for_user(db: Session, user: User, limit: int = 20):
    """
    Fetch jobs specifically tailored to the user's profile from TheirStack.
    """
    if not user.profile:
        print("User has no profile, skipping fetch.")
        return

    # Extract preferences
    roles = []
    if user.profile.desired_roles:
        # Assuming comma separated string or list
        if isinstance(user.profile.desired_roles, list):
             roles = user.profile.desired_roles
        elif isinstance(user.profile.desired_roles, str):
             roles = [r.strip() for r in user.profile.desired_roles.split(",") if r.strip()]
    
    locations = []
    if user.profile.desired_locations:
        if isinstance(user.profile.desired_locations, list):
             locations = user.profile.desired_locations
        elif isinstance(user.profile.desired_locations, str):
             locations = [l.strip() for l in user.profile.desired_locations.split(",") if l.strip()]

    remote = user.profile.remote_preference == "REMOTE"

    # Default if no roles specified
    if not roles:
        roles = ["Software Engineer"] # Fallback

    # Call API
    # We might want to make multiple calls if multiple roles, but for now let's just use the list
    # Theirstack service takes patterns list
    
    jobs_data = theirstack_service.search_jobs(
        job_title_patterns=roles,
        locations=locations,
        remote=remote,
        limit=limit
    )
    
    print(f"Fetched {len(jobs_data)} jobs from TheirStack for user {user.email}")

    for job_data in jobs_data:
        # Avoid dupes
        external_id = str(job_data.get("id"))
        existing = db.query(JobPosting).filter(JobPosting.external_id == external_id).first()
        if existing:
            continue
            
        # Map fields
        # TheirStack: job_title, company, location, salary_string, url (apply link)
        new_job = JobPosting(
            external_id=external_id,
            title=job_data.get("job_title", "Unknown Title"),
            company_name=job_data.get("company", "Unknown Company"),
            location=job_data.get("location", ""),
            salary_range=job_data.get("salary_string"),
            description=job_data.get("description") or job_data.get("Snippet") or "",
            url=job_data.get("url"), # This is the apply link usually 
            employment_type="FULL_TIME" # Default or map from data if available
        )
        db.add(new_job)
    
    db.commit()
