from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import User, UserProfile
from app.schemas import user as user_schema

router = APIRouter()

@router.get("/me", response_model=user_schema.User)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me/profile", response_model=user_schema.UserProfile)
def update_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: user_schema.UserProfileUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update user profile.
    """
    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    profile_data = profile_in.dict(exclude_unset=True)
    for field, value in profile_data.items():
        setattr(profile, field, value)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.delete("/me", response_model=user_schema.User)
def delete_user_me(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete own user account and all associated data.
    """
    # 1. Delete Profile
    if current_user.profile:
        db.delete(current_user.profile)
        
    # 2. Delete Resume and file
    if current_user.resume:
        import os
        if current_user.resume.file_path and os.path.exists(current_user.resume.file_path):
            try:
                os.remove(current_user.resume.file_path)
            except OSError:
                pass # Log error
        db.delete(current_user.resume)
        
    # 3. Delete Swipes
    for swipe in current_user.swipes:
        db.delete(swipe)
        
    # 4. Delete Applications and their events
    # Note: ApplicationStatusEvent has FK to Application. If we strictly follow, we should delete events first if cascade not set.
    # Checking Application model: relationship to events is default.
    # To be safe, iterate applications, delete their events, then delete application.
    for app in current_user.applications:
        for event in app.events:
            db.delete(event)
        db.delete(app)
        
    # 5. Delete User
    db.delete(current_user)
    
    db.commit()
    return current_user
