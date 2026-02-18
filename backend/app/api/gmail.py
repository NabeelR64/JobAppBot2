"""
Gmail OAuth and polling API endpoints.

- GET  /gmail/connect    → returns Google OAuth authorization URL
- GET  /gmail/callback   → OAuth callback, exchanges code for tokens
- GET  /gmail/status     → returns Gmail connection status
- POST /gmail/disconnect → clears refresh token
- POST /gmail/poll       → manually trigger Gmail polling for current user
"""

import logging
from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow

from app.api import deps
from app.core.config import settings
from app.models import User
from app.services import gmail

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_oauth_flow() -> Flow:
    """Build a Google OAuth flow for Gmail readonly scope."""
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GMAIL_REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=settings.GMAIL_SCOPES,
        redirect_uri=settings.GMAIL_REDIRECT_URI,
    )
    return flow


@router.get("/connect")
def gmail_connect(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Returns Google OAuth authorization URL for Gmail readonly access.
    Frontend should redirect or open this URL.
    """
    flow = _build_oauth_flow()

    auth_url, state = flow.authorization_url(
        access_type="offline",       # Gets a refresh token
        include_granted_scopes="true",
        prompt="consent",            # Force consent to get refresh token
        state=str(current_user.id),  # Pass user ID through OAuth state
    )

    return {"auth_url": auth_url}


@router.get("/callback")
def gmail_callback(
    code: str = Query(...),
    state: str = Query(default=""),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    OAuth callback from Google. Exchanges auth code for tokens,
    stores refresh token on the user, and redirects to frontend.
    """
    # Extract user ID from state parameter
    try:
        user_id = int(state)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Exchange authorization code for tokens
    flow = _build_oauth_flow()
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        logger.error(f"[Gmail] Token exchange failed: {e}")
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)[:200]}")

    credentials = flow.credentials

    if not credentials.refresh_token:
        logger.warning("[Gmail] No refresh token received — user may have already granted access")
        # Try to use what we got; it might still work for the session
        # but won't persist across restarts

    # Store refresh token
    user.gmail_refresh_token = credentials.refresh_token or credentials.token
    user.gmail_connected_at = datetime.utcnow()
    db.commit()

    logger.info(f"[Gmail] User {user_id} connected Gmail successfully")

    # Redirect back to frontend
    return RedirectResponse(url="http://localhost:4200/onboarding?gmail=connected")


@router.get("/status")
def gmail_status(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Returns the user's Gmail connection status.
    """
    connected = bool(current_user.gmail_refresh_token)
    return {
        "connected": connected,
        "connected_at": current_user.gmail_connected_at.isoformat() if current_user.gmail_connected_at else None,
    }


@router.post("/disconnect")
def gmail_disconnect(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Disconnect Gmail — clears stored refresh token.
    """
    current_user.gmail_refresh_token = None
    current_user.gmail_connected_at = None
    db.commit()

    logger.info(f"[Gmail] User {current_user.id} disconnected Gmail")
    return {"message": "Gmail disconnected successfully"}


@router.post("/poll")
def trigger_gmail_poll(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Manually trigger Gmail polling for the current user.
    """
    if not current_user.gmail_refresh_token:
        raise HTTPException(status_code=400, detail="Gmail not connected")

    result = gmail.poll_user_gmail(current_user.id, db)
    return {"message": "Gmail polling complete", "updates": result}
