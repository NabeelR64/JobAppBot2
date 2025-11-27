from fastapi import APIRouter
from app.api import auth, users, resume, jobs, application, gmail

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(application.router, prefix="/applications", tags=["applications"])
api_router.include_router(gmail.router, prefix="/gmail", tags=["gmail"])
