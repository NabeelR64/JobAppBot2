from sqlalchemy.orm import Session
from app.models import JobPosting
from app.schemas import job as job_schema
import random

def fetch_jobs_from_indeed_mock() -> list[job_schema.JobPostingCreate]:
    """
    Mock fetching jobs from Indeed.
    """
    titles = ["Backend Engineer", "Frontend Developer", "Data Scientist", "Product Manager"]
    companies = ["Google", "Amazon", "Startup Inc", "Tech Corp"]
    locations = ["New York, NY", "San Francisco, CA", "Remote", "Austin, TX"]
    
    jobs = []
    for i in range(10):
        jobs.append(job_schema.JobPostingCreate(
            external_id=f"indeed-{random.randint(1000, 9999)}",
            title=random.choice(titles),
            company_name=random.choice(companies),
            location=random.choice(locations),
            salary_range=f"${random.randint(100, 200)}k - ${random.randint(200, 300)}k",
            description="This is a great job opportunity. You should apply.",
            employment_type="Full-time",
            url="https://indeed.com/viewjob?jk=123"
        ))
    return jobs

def ingest_jobs(db: Session):
    """
    Fetch and store jobs.
    """
    jobs_data = fetch_jobs_from_indeed_mock()
    for job_data in jobs_data:
        # Check if exists
        existing = db.query(JobPosting).filter(JobPosting.external_id == job_data.external_id).first()
        if not existing:
            job = JobPosting(**job_data.dict())
            db.add(job)
    db.commit()
