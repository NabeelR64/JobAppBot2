from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from datetime import timedelta
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models import User, UserProfile
from pydantic import BaseModel

router = APIRouter()

class GoogleLogin(BaseModel):
    credential: str # The JWT token from Google

@router.post("/google")
def login_google(
    login_data: GoogleLogin,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Login with Google.
    """
    # Verify the token
    idinfo = security.verify_google_token(login_data.credential)
    if not idinfo:
         raise HTTPException(status_code=400, detail="Invalid Google token")

    email = idinfo['email']
    google_sub = idinfo['sub']
    name = idinfo.get('name')
    
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create new user
        user = User(email=email, google_sub=google_sub)
        db.add(user)
        db.flush() # Flush to get the ID
        
        # Create empty profile
        profile = UserProfile(user_id=user.id, name=name)
        db.add(profile)
        db.commit()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.get("/me")
def read_users_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.profile.name if current_user.profile else None,
        # Add other fields as needed
    }
