from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from app.api import deps
from app.core import security
from app.models import User, UserProfile
from pydantic import BaseModel

router = APIRouter()

class GoogleLogin(BaseModel):
    credential: str # The JWT token from Google

@router.post("/login/google")
def login_google(
    login_data: GoogleLogin,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Login with Google.
    """
    try:
        # Verify the token
        # In production, specify the CLIENT_ID
        idinfo = id_token.verify_oauth2_token(login_data.credential, requests.Request())

        email = idinfo['email']
        google_sub = idinfo['sub']
        name = idinfo.get('name')
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Create new user
            user = User(email=email, google_sub=google_sub)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create empty profile
            profile = UserProfile(user_id=user.id, name=name)
            db.add(profile)
            db.commit()
        
        access_token_expires = security.timedelta(minutes=60 * 24 * 8)
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")
