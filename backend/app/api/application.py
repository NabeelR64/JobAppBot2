from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User, Application
from app.schemas import application as application_schema

router = APIRouter()

@router.get("/", response_model=List[application_schema.Application])
def get_applications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user applications.
    """
    return current_user.applications
