from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.api import api_router
from app.db.base import Base
from app.db.session import engine, SessionLocal

logger = logging.getLogger(__name__)

# APScheduler for periodic Gmail polling
scheduler = None


def poll_all_users_job():
    """Background job: poll Gmail for all connected users."""
    from app.services.gmail import poll_all_users
    db = SessionLocal()
    try:
        poll_all_users(db)
    except Exception as e:
        logger.error(f"[Scheduler] Gmail poll error: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan: start scheduler on startup, shut down on exit."""
    global scheduler

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Start APScheduler
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            poll_all_users_job,
            "interval",
            minutes=15,
            id="gmail_poll",
            name="Poll Gmail for all connected users",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("[Scheduler] Started — Gmail polling every 15 minutes")
    except Exception as e:
        logger.warning(f"[Scheduler] Failed to start: {e}")

    yield

    # Shutdown
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Shut down")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {"message": "Welcome to Jinder API"}
