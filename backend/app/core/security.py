from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_google_token(token: str) -> dict:
    from google.oauth2 import id_token
    from google.auth.transport import requests
    
    try:
         # Specify the CLIENT_ID of the app that accesses the backend:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        
        # Or, if multiple clients access the backend server:
        # id_info = id_token.verify_oauth2_token(token, requests.Request())
        # if id_info['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, ...]:
        #     raise ValueError('Could not verify audience.')
        
        # ID token is valid. Get the user's Google Account ID from the decoded token.
        return id_info
    except ValueError as e:
        # Invalid token
        print(f"Token verification error: {e}")
        return None
