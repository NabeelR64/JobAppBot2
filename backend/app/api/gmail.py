from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User
from app.services import gmail

router = APIRouter()

@router.post("/poll")
def trigger_gmail_poll(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Trigger Gmail polling manually.
    """
    gmail.poll_gmail_mock(db)
    return {"message": "Gmail polling triggered"}
