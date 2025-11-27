from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core import security
from app.core.config import settings
from app.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    # BYPASS AUTH FOR MVP
    # Just return the first user or create one if none exists
    user = db.query(User).first()
    if not user:
        user = User(email="test@example.com", google_sub="test_sub")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
