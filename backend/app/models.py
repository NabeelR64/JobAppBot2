from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Enum, Text, ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class RemotePreference(str, enum.Enum):
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    ON_SITE = "ON_SITE"

class ApplicationStatus(str, enum.Enum):
    PENDING_AUTOMATION = "PENDING_AUTOMATION"
    APPLIED = "APPLIED"
    EMAIL_CONFIRMATION_RECEIVED = "EMAIL_CONFIRMATION_RECEIVED"
    INTERVIEW_INVITED = "INTERVIEW_INVITED"
    REJECTED = "REJECTED"
    FOLLOW_UP_RECEIVED = "FOLLOW_UP_RECEIVED"
    OTHER_UPDATE = "OTHER_UPDATE"
    FAILED = "FAILED"
    MANUAL_INTERVENTION_REQUIRED = "MANUAL_INTERVENTION_REQUIRED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    google_sub = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    resume = relationship("Resume", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
    swipes = relationship("SwipeAction", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String)
    desired_locations = Column(JSON)
    desired_salary_min = Column(Integer)
    desired_salary_max = Column(Integer)
    desired_roles = Column(JSON)
    remote_preference = Column(Enum(RemotePreference))
    seniority_preference = Column(String)
    company_size_prefs = Column(JSON)
    disallowed_categories = Column(JSON)
    phone_number = Column(String)
    # New fields
    region = Column(String)
    location = Column(String)
    address = Column(String)
    field_of_work = Column(String)
    experience = Column(JSON)
    education = Column(JSON)
    age = Column(Integer)

    user = relationship("User", back_populates="profile")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    file_path = Column(String, nullable=False)
    raw_text = Column(Text)
    embedding_vector = Column(JSON)  # Stores 1536-dim float array as JSON (migrate to pgvector Vector(1536) with Postgres)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resume")

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    location = Column(String)
    salary_range = Column(String)
    description = Column(Text)
    employment_type = Column(String)
    url = Column(String)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    applications = relationship("Application", back_populates="job_posting")
    swipes = relationship("SwipeAction", back_populates="job_posting")

class SwipeAction(Base):
    __tablename__ = "swipe_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    action = Column(String, nullable=False) # LEFT, RIGHT
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="swipes")
    job_posting = relationship("JobPosting", back_populates="swipes")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING_AUTOMATION)
    screenshot_path = Column(String)
    cover_letter_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="applications")
    job_posting = relationship("JobPosting", back_populates="applications")
    events = relationship("ApplicationStatusEvent", back_populates="application")

class ApplicationStatusEvent(Base):
    __tablename__ = "application_status_events"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    status = Column(Enum(ApplicationStatus), nullable=False)
    message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    application = relationship("Application", back_populates="events")
