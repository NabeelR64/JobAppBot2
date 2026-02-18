"""
Job ingestion and ranking service.

Fetches jobs from TheirStack API, stores them, and ranks them
using cosine similarity between the user's resume embedding
and job description embeddings.
"""

import logging
import numpy as np
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models import JobPosting, User
from app.services.theirstack import theirstack_service
from app.services import embedding

logger = logging.getLogger(__name__)


def ingest_jobs(db: Session):
    """
    Mock ingestion for now or simple manual trigger.
    """
    pass


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors using numpy.
    Returns a value between -1 and 1 (1 = identical direction).
    """
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)

    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


def rank_jobs_by_embedding(
    user: User, jobs: List[JobPosting], db: Session
) -> List[JobPosting]:
    """
    Rank jobs by cosine similarity between the user's resume embedding
    and each job's description embedding.

    If the user has no resume embedding or jobs have no embeddings,
    the jobs are returned in their original order (no ranking applied).

    Works with both:
    - SQLite (embeddings stored as JSON arrays)
    - PostgreSQL with pgvector (embeddings stored as Vector)
    """
    # Check if user has a resume with an embedding
    if not user.resume or not user.resume.embedding_vector:
        logger.info("[Ranking] No resume embedding — skipping ranking")
        return jobs

    resume_vec = user.resume.embedding_vector

    # Handle both pgvector (list) and JSON (list) formats
    if isinstance(resume_vec, str):
        import json
        resume_vec = json.loads(resume_vec)

    scored_jobs = []
    unscored_jobs = []

    for job in jobs:
        # Generate embedding for job description on-the-fly if not cached
        if job.description:
            try:
                job_vec = embedding.generate_embedding(job.description[:2000])
                if job_vec:
                    score = cosine_similarity(resume_vec, job_vec)
                    scored_jobs.append((score, job))
                    continue
            except Exception as e:
                logger.warning(f"[Ranking] Embedding failed for job {job.id}: {e}")

        unscored_jobs.append(job)

    # Sort scored jobs by similarity (highest first)
    scored_jobs.sort(key=lambda x: x[0], reverse=True)

    # Return scored jobs first, then unscored at the end
    ranked = [job for _, job in scored_jobs] + unscored_jobs

    if scored_jobs:
        logger.info(
            f"[Ranking] Ranked {len(scored_jobs)} jobs by embedding similarity "
            f"(top score: {scored_jobs[0][0]:.3f}, lowest: {scored_jobs[-1][0]:.3f})"
        )

    return ranked


def fetch_jobs_for_user(db: Session, user: User, limit: int = 20):
    """
    Fetch jobs specifically tailored to the user's profile from TheirStack.
    After fetching, ranks jobs by resume embedding cosine similarity.
    """
    if not user.profile:
        print("User has no profile, skipping fetch.")
        return

    # Extract preferences
    roles = []
    if user.profile.desired_roles:
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
        roles = ["Software Engineer"]

    # Call API
    jobs_data = theirstack_service.search_jobs(
        job_title_patterns=roles,
        locations=locations,
        remote=remote,
        limit=limit
    )
    
    logger.info(f"Fetched {len(jobs_data)} jobs from TheirStack for user {user.email}")

    new_jobs = []
    for job_data in jobs_data:
        # Avoid dupes
        external_id = str(job_data.get("id"))
        existing = db.query(JobPosting).filter(JobPosting.external_id == external_id).first()
        if existing:
            continue
            
        new_job = JobPosting(
            external_id=external_id,
            title=job_data.get("job_title", "Unknown Title"),
            company_name=job_data.get("company", "Unknown Company"),
            location=job_data.get("location", ""),
            salary_range=job_data.get("salary_string"),
            description=job_data.get("description") or job_data.get("Snippet") or "",
            url=job_data.get("url"),
            employment_type="FULL_TIME"
        )
        db.add(new_job)
        new_jobs.append(new_job)
    
    db.commit()

    # Rank all available jobs for this user by embedding similarity
    all_jobs = db.query(JobPosting).limit(limit * 2).all()
    ranked_jobs = rank_jobs_by_embedding(user, all_jobs, db)

    return ranked_jobs[:limit]
