from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.models import User, Application, ApplicationStatus, ApplicationStatusEvent
from app.schemas import application as application_schema
from app.services.automation import resume_automation

router = APIRouter()


class StatusUpdate(BaseModel):
    status: str


class ProvideFieldsRequest(BaseModel):
    fields: Dict[str, str]


@router.get("/", response_model=List[application_schema.Application])
def get_applications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user applications.
    """
    return current_user.applications


@router.patch("/{application_id}/status", response_model=application_schema.Application)
def update_application_status(
    application_id: int,
    status_update: StatusUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Manually update an application's status (e.g. from Kanban drag-and-drop).
    Creates an ApplicationStatusEvent for audit trail.
    """
    # Find the application and verify ownership
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Validate the status value
    try:
        new_status = ApplicationStatus(status_update.status)
    except ValueError:
        valid = [s.value for s in ApplicationStatus]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid}"
        )

    # Update the application status
    application.status = new_status

    # Create audit event
    event = ApplicationStatusEvent(
        application_id=application.id,
        status=new_status,
        message=f"Status manually updated to {new_status.value}"
    )
    db.add(event)
    db.commit()
    db.refresh(application)

    return application


@router.post("/{application_id}/provide-fields", response_model=application_schema.Application)
def provide_fields(
    application_id: int,
    request: ProvideFieldsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Provide missing field values for an application that needs user input.
    Triggers resume_automation as a background task.
    """
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.status != ApplicationStatus.USER_INPUT_NEEDED:
        raise HTTPException(
            status_code=400,
            detail=f"Application is not awaiting user input (status: {application.status.value})"
        )

    if not application.automation_state:
        raise HTTPException(
            status_code=400,
            detail="No saved automation state found for this application"
        )

    # Update status to show we're resuming
    application.status = ApplicationStatus.PENDING_AUTOMATION
    event = ApplicationStatusEvent(
        application_id=application.id,
        status=ApplicationStatus.PENDING_AUTOMATION,
        message=f"User provided {len(request.fields)} missing field(s). Resuming automation."
    )
    db.add(event)
    db.commit()
    db.refresh(application)

    # Trigger resume in background
    background_tasks.add_task(resume_automation, application.id, request.fields, db)

    return application
