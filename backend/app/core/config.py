from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jinder"
    API_V1_STR: str = "/api/v1"

    # Deployment URLs
    FRONTEND_URL: str = "http://localhost:4200"
    BACKEND_URL: str = "http://localhost:8000"

    # CORS — allow both localhost (dev) and production frontend
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:4200"]
    
    # Database — set DATABASE_URL in .env for Postgres, otherwise falls back to SQLite
    DATABASE_URL: Optional[str] = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "jinder"
    
    # Auth — no defaults, must be set in .env
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External APIs
    THEIRSTACK_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Gmail OAuth
    GMAIL_REDIRECT_URI: Optional[str] = None
    GMAIL_SCOPES: list[str] = ["https://www.googleapis.com/auth/gmail.readonly"]

    # Rate limiting
    RATE_LIMIT_GLOBAL: str = "100/minute"
    RATE_LIMIT_PER_USER: str = "30/minute"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Fallback to SQLite for local dev without Docker/Postgres
        return "sqlite:///./jinder.db"

    @property
    def gmail_redirect_uri(self) -> str:
        if self.GMAIL_REDIRECT_URI:
            return self.GMAIL_REDIRECT_URI
        return f"{self.BACKEND_URL}/api/v1/gmail/callback"

    @property
    def cors_origins(self) -> list[str]:
        """Combine configured origins with FRONTEND_URL for production."""
        origins = list(self.BACKEND_CORS_ORIGINS)
        if self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)
        return origins

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

