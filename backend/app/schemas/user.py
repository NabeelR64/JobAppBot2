from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.models import RemotePreference

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    desired_locations: Optional[List[str]] = []
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    desired_roles: Optional[List[str]] = []
    remote_preference: Optional[RemotePreference] = None
    seniority_preference: Optional[str] = None
    disallowed_categories: Optional[List[str]] = []
    phone_number: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    google_sub: str

class User(UserBase):
    id: int
    profile: Optional[UserProfile] = None

    class Config:
        from_attributes = True
