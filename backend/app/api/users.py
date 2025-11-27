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
