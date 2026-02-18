"""
Gmail integration service — real Gmail API polling + GPT-4 classification.

Replaces the mock implementation with:
1. Authenticated Gmail API access via stored refresh tokens
2. Fetching recent recruiter-like emails
3. GPT-4 classification of email intent (confirmation, interview, rejection, etc.)
4. Fuzzy company-name matching to existing applications
5. Automatic status updates on the Kanban board
"""

import logging
import json
import base64
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings
from app.models import User, Application, ApplicationStatus, ApplicationStatusEvent

logger = logging.getLogger(__name__)

# Email domains commonly used by recruiters / ATS platforms
RECRUITER_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "icims.com", "taleo.net",
    "smartrecruiters.com", "jobvite.com", "myworkdayjobs.com", "breezy.hr",
    "ashbyhq.com", "jazz.co", "recruitee.com", "bamboohr.com",
    "linkedin.com", "indeed.com", "glassdoor.com", "ziprecruiter.com",
    "noreply", "no-reply", "careers", "recruiting", "talent", "hr@", "jobs@",
]

# Subject patterns that suggest job-related emails
SUBJECT_PATTERNS = [
    r"application",
    r"interview",
    r"offer",
    r"reject",
    r"unfortunately",
    r"next steps",
    r"follow.?up",
    r"congratulations",
    r"thank you for (applying|your interest)",
    r"we.*(received|reviewed)",
    r"position",
    r"candidat",
    r"screening",
    r"assessment",
    r"opportunity",
]

# Status mapping from GPT classification
STATUS_MAP = {
    "confirmation": ApplicationStatus.EMAIL_CONFIRMATION_RECEIVED,
    "interview": ApplicationStatus.INTERVIEW_INVITED,
    "rejection": ApplicationStatus.REJECTED,
    "follow_up": ApplicationStatus.FOLLOW_UP_RECEIVED,
    "offer": ApplicationStatus.OTHER_UPDATE,
    "other": ApplicationStatus.OTHER_UPDATE,
}


def build_gmail_service(refresh_token: str):
    """
    Create an authenticated Gmail API client from a stored refresh token.
    Returns a Gmail API resource object.
    """
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=settings.GMAIL_SCOPES,
    )

    service = build("gmail", "v1", credentials=credentials)
    return service


def fetch_recent_emails(service, after_date: datetime, max_results: int = 50) -> List[Dict]:
    """
    Fetch recent emails that look like recruiter/job-related messages.
    
    Uses Gmail search query to filter by date and common job-related terms.
    Returns a list of message dicts with subject, from, snippet, and body preview.
    """
    # Build Gmail search query
    date_str = after_date.strftime("%Y/%m/%d")
    query = (
        f"after:{date_str} "
        f"(subject:(application OR interview OR offer OR position OR candidate) "
        f"OR from:(noreply OR no-reply OR careers OR recruiting OR talent OR hr OR jobs))"
    )

    messages = []
    try:
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results,
        ).execute()

        message_ids = results.get("messages", [])
        logger.info(f"[Gmail] Found {len(message_ids)} candidate messages")

        for msg_ref in message_ids:
            try:
                msg = service.users().messages().get(
                    userId="me",
                    id=msg_ref["id"],
                    format="metadata",
                    metadataHeaders=["Subject", "From", "Date"],
                ).execute()

                headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
                snippet = msg.get("snippet", "")

                messages.append({
                    "id": msg_ref["id"],
                    "subject": headers.get("Subject", ""),
                    "from": headers.get("From", ""),
                    "date": headers.get("Date", ""),
                    "snippet": snippet,
                })
            except Exception as e:
                logger.warning(f"[Gmail] Error fetching message {msg_ref['id']}: {e}")
                continue

    except HttpError as e:
        logger.error(f"[Gmail] API error fetching messages: {e}")
    except Exception as e:
        logger.error(f"[Gmail] Unexpected error: {e}")

    return messages


def _is_recruiter_email(from_addr: str, subject: str) -> bool:
    """Quick check if an email looks job-related based on sender and subject."""
    from_lower = from_addr.lower()
    subject_lower = subject.lower()

    # Check sender domain
    for domain in RECRUITER_DOMAINS:
        if domain in from_lower:
            return True

    # Check subject patterns
    for pattern in SUBJECT_PATTERNS:
        if re.search(pattern, subject_lower):
            return True

    return False


def classify_email(subject: str, snippet: str) -> Optional[Dict]:
    """
    Use GPT-4 to classify an email's intent and extract company name.
    
    Returns: { "status": str, "confidence": float, "company_name": str }
    or None if classification fails.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("[Gmail] No OPENAI_API_KEY — skipping classification")
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""Analyze this email and classify it as a job application status update.

Email subject: {subject}
Email snippet: {snippet}

Respond with ONLY valid JSON (no markdown, no code fences):
{{
    "status": "confirmation|interview|rejection|follow_up|offer|other|not_job_related",
    "confidence": 0.0 to 1.0,
    "company_name": "extracted company name or empty string"
}}

Rules:
- "confirmation" = application received/acknowledged
- "interview" = interview invitation or scheduling
- "rejection" = application rejected / position filled
- "follow_up" = follow-up, next steps, or additional info requested
- "offer" = job offer
- "other" = job-related but doesn't fit above categories
- "not_job_related" = not related to a job application at all
- Extract the company name from the email (the employer, not the platform)
- confidence should reflect how certain you are about the classification"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a job application email classifier. Respond only with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=150,
        )

        result_text = response.choices[0].message.content.strip()

        # Clean up potential markdown formatting
        if result_text.startswith("```"):
            result_text = re.sub(r"```\w*\n?", "", result_text).strip()

        result = json.loads(result_text)
        logger.info(f"[Gmail] Classification: {result}")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"[Gmail] Failed to parse GPT response: {e}")
        return None
    except Exception as e:
        logger.error(f"[Gmail] Classification error: {e}")
        return None


def match_to_application(
    company_name: str, applications: List[Application]
) -> Optional[Application]:
    """
    Fuzzy match a company name from an email to an existing application.
    
    Tries exact match first, then substring/contains matching, then
    word-level overlap for fuzzy matching.
    """
    if not company_name or not applications:
        return None

    company_lower = company_name.lower().strip()
    company_words = set(company_lower.split())

    best_match = None
    best_score = 0

    for app in applications:
        app_company = (app.job_posting.company_name or "").lower().strip()
        if not app_company:
            continue

        # Exact match
        if app_company == company_lower:
            return app

        # Contains match (e.g., "Google" in "Google LLC")
        if company_lower in app_company or app_company in company_lower:
            score = 0.8
            if score > best_score:
                best_score = score
                best_match = app
                continue

        # Word overlap (e.g., "Google Inc" vs "Google LLC")
        app_words = set(app_company.split())
        overlap = company_words & app_words
        if overlap:
            # Jaccard-like scoring
            score = len(overlap) / max(len(company_words), len(app_words))
            if score > best_score and score >= 0.5:
                best_score = score
                best_match = app

    if best_match:
        logger.info(f"[Gmail] Matched '{company_name}' → '{best_match.job_posting.company_name}' (score: {best_score:.2f})")

    return best_match


def poll_user_gmail(user_id: int, db: Session) -> List[Dict]:
    """
    Full Gmail polling pipeline for a single user:
    1. Build Gmail service from stored refresh token
    2. Fetch recent emails (last 24 hours)
    3. Classify each email with GPT
    4. Match to existing applications
    5. Update application statuses
    
    Returns a list of updates made.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.gmail_refresh_token:
        logger.warning(f"[Gmail] User {user_id} has no Gmail token")
        return []

    # Build Gmail API client
    try:
        service = build_gmail_service(user.gmail_refresh_token)
    except Exception as e:
        logger.error(f"[Gmail] Failed to build service for user {user_id}: {e}")
        return []

    # Fetch emails from the last 24 hours
    after_date = datetime.utcnow() - timedelta(hours=24)
    emails = fetch_recent_emails(service, after_date)

    if not emails:
        logger.info(f"[Gmail] No new candidate emails for user {user_id}")
        return []

    # Get user's active applications (APPLIED or EMAIL_CONFIRMATION_RECEIVED)
    active_statuses = [
        ApplicationStatus.APPLIED,
        ApplicationStatus.EMAIL_CONFIRMATION_RECEIVED,
        ApplicationStatus.FOLLOW_UP_RECEIVED,
    ]
    applications = (
        db.query(Application)
        .filter(
            Application.user_id == user_id,
            Application.status.in_(active_statuses),
        )
        .all()
    )

    if not applications:
        logger.info(f"[Gmail] No active applications for user {user_id}")
        return []

    updates = []

    for email in emails:
        subject = email.get("subject", "")
        from_addr = email.get("from", "")
        snippet = email.get("snippet", "")

        # Quick filter — skip obviously non-job emails
        if not _is_recruiter_email(from_addr, subject):
            continue

        # Classify with GPT
        classification = classify_email(subject, snippet)
        if not classification:
            continue

        status_key = classification.get("status", "")
        confidence = classification.get("confidence", 0)
        company_name = classification.get("company_name", "")

        # Skip low-confidence or non-job classifications
        if status_key == "not_job_related" or confidence < 0.7:
            logger.info(f"[Gmail] Skipping — status={status_key}, confidence={confidence}")
            continue

        # Map to application status
        new_status = STATUS_MAP.get(status_key)
        if not new_status:
            continue

        # Match to an application
        matched_app = match_to_application(company_name, applications)
        if not matched_app:
            logger.info(f"[Gmail] No application match for company '{company_name}'")
            continue

        # Don't downgrade status (e.g., don't go from INTERVIEW_INVITED back to APPLIED)
        status_priority = {
            ApplicationStatus.APPLIED: 1,
            ApplicationStatus.EMAIL_CONFIRMATION_RECEIVED: 2,
            ApplicationStatus.FOLLOW_UP_RECEIVED: 3,
            ApplicationStatus.INTERVIEW_INVITED: 4,
            ApplicationStatus.REJECTED: 5,
            ApplicationStatus.OTHER_UPDATE: 3,
        }
        current_priority = status_priority.get(matched_app.status, 0)
        new_priority = status_priority.get(new_status, 0)

        if new_priority <= current_priority and new_status != ApplicationStatus.REJECTED:
            logger.info(f"[Gmail] Skipping — would downgrade {matched_app.status} → {new_status}")
            continue

        # Update the application
        old_status = matched_app.status
        matched_app.status = new_status

        event = ApplicationStatusEvent(
            application_id=matched_app.id,
            status=new_status,
            message=(
                f"Gmail detected: {status_key} from {company_name} "
                f"(confidence: {confidence:.0%}). Subject: {subject[:100]}"
            ),
        )
        db.add(event)

        updates.append({
            "application_id": matched_app.id,
            "company": company_name,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "confidence": confidence,
            "email_subject": subject[:100],
        })

        logger.info(
            f"[Gmail] Updated app {matched_app.id} ({company_name}): "
            f"{old_status.value} → {new_status.value}"
        )

    if updates:
        db.commit()
        logger.info(f"[Gmail] Made {len(updates)} status updates for user {user_id}")

    return updates


def poll_all_users(db: Session):
    """
    Poll Gmail for ALL users who have connected their accounts.
    Called by the background scheduler.
    """
    users = db.query(User).filter(User.gmail_refresh_token.isnot(None)).all()
    logger.info(f"[Gmail] Polling {len(users)} connected users")

    total_updates = 0
    for user in users:
        try:
            updates = poll_user_gmail(user.id, db)
            total_updates += len(updates)
        except Exception as e:
            logger.error(f"[Gmail] Error polling user {user.id}: {e}")
            continue

    logger.info(f"[Gmail] Polling complete — {total_updates} total updates across {len(users)} users")
