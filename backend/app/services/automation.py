"""
Playwright-based browser automation engine for job applications.

Launches headless Chromium, navigates to job posting URLs, detects form fields,
fills them from user profile data, uploads resumes, and captures screenshots.
"""

import os
import logging
from datetime import datetime

from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from app.models import Application, ApplicationStatus, ApplicationStatusEvent
from app.services import cover_letter, form_detector

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = "uploads/screenshots"
# dry_run=True fills forms but does NOT click Submit (safe for development)
DRY_RUN = True


def run_automation(application_id: int, db: Session):
    """
    Main automation entry point. Called as a BackgroundTask from the swipe endpoint.

    1. Loads application, user profile, resume, job posting
    2. Generates cover letter
    3. Launches Playwright, navigates to job URL
    4. Detects and fills form fields
    5. Captures screenshot
    6. Updates application status
    """
    logger.info(f"[Automation] Starting for application {application_id}")

    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        logger.error(f"[Automation] Application {application_id} not found")
        return

    job_posting = application.job_posting
    user = application.user
    profile = user.profile
    resume = user.resume

    # --- Step 1: Generate cover letter ---
    resume_text = resume.raw_text if resume else "No resume uploaded"
    job_desc = job_posting.description or "No description available"

    user_profile_dict = None
    if profile:
        user_profile_dict = {
            "name": profile.name,
            "desired_roles": profile.desired_roles,
            "field_of_work": profile.field_of_work,
        }

    letter = cover_letter.generate_cover_letter(resume_text, job_desc, user_profile_dict)
    application.cover_letter_text = letter
    db.commit()
    logger.info(f"[Automation] Cover letter generated ({len(letter)} chars)")

    # --- Step 2: Check if job has a URL ---
    if not job_posting.url:
        _mark_status(db, application, ApplicationStatus.MANUAL_INTERVENTION_REQUIRED,
                     "No job URL available. Please apply manually.")
        return

    # --- Step 3: Launch Playwright ---
    try:
        _run_browser_automation(application, db, profile, resume, letter)
    except PlaywrightTimeout:
        logger.error(f"[Automation] Timeout navigating to {job_posting.url}")
        _capture_error_screenshot(application)
        _mark_status(db, application, ApplicationStatus.FAILED,
                     f"Navigation timeout for {job_posting.url}")
    except Exception as e:
        logger.error(f"[Automation] Unexpected error: {e}")
        _capture_error_screenshot(application)
        _mark_status(db, application, ApplicationStatus.FAILED,
                     f"Automation error: {str(e)[:200]}")


def _run_browser_automation(application: Application, db: Session,
                            profile, resume, cover_letter_text: str):
    """Core browser automation logic."""
    job_url = application.job_posting.url

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            # Navigate to job posting
            logger.info(f"[Automation] Navigating to {job_url}")
            page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)  # Let dynamic content load

            # Check for CAPTCHA
            if form_detector.detect_captcha(page):
                screenshot_path = _capture_screenshot(page, application, "captcha")
                application.screenshot_path = screenshot_path
                _mark_status(db, application, ApplicationStatus.MANUAL_INTERVENTION_REQUIRED,
                             f"CAPTCHA detected. Please apply manually at: {job_url}")
                return

            # Detect form fields
            fields = form_detector.detect_form_fields(page)

            if not fields:
                # No form found — could be an external ATS link or info-only page
                screenshot_path = _capture_screenshot(page, application, "no_form")
                application.screenshot_path = screenshot_path
                _mark_status(db, application, ApplicationStatus.MANUAL_INTERVENTION_REQUIRED,
                             f"No application form detected. Apply manually at: {job_url}")
                return

            # Fill detected fields
            fields_filled = _fill_form_fields(page, fields, profile, resume, cover_letter_text)
            logger.info(f"[Automation] Filled {fields_filled} form fields")

            # Take screenshot of filled form
            screenshot_path = _capture_screenshot(page, application, "filled")
            application.screenshot_path = screenshot_path

            if DRY_RUN:
                logger.info("[Automation] DRY RUN — skipping form submission")
                _mark_status(db, application, ApplicationStatus.APPLIED,
                             f"Form filled successfully (dry run). {fields_filled} fields completed.")
            else:
                # Find and click submit button
                submit_btn = form_detector.detect_apply_button(page)
                if submit_btn:
                    submit_btn.click()
                    page.wait_for_timeout(3000)

                    # Screenshot the confirmation/result page
                    screenshot_path = _capture_screenshot(page, application, "submitted")
                    application.screenshot_path = screenshot_path
                    _mark_status(db, application, ApplicationStatus.APPLIED,
                                 f"Application submitted successfully. {fields_filled} fields filled.")
                else:
                    _mark_status(db, application, ApplicationStatus.MANUAL_INTERVENTION_REQUIRED,
                                 f"Form filled but no submit button found. Apply manually at: {job_url}")

        finally:
            browser.close()


def _fill_form_fields(page, fields: dict, profile, resume, cover_letter_text: str) -> int:
    """Fill detected form fields with user data. Returns count of fields filled."""
    filled = 0

    # Name fields
    name = profile.name if profile else ""
    name_parts = name.split(" ", 1) if name else ["", ""]
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    if "full_name" in fields:
        _safe_fill(fields["full_name"], name)
        filled += 1
    if "first_name" in fields:
        _safe_fill(fields["first_name"], first_name)
        filled += 1
    if "last_name" in fields:
        _safe_fill(fields["last_name"], last_name)
        filled += 1

    # Email
    email = ""
    if profile and hasattr(profile, "user") and profile.user:
        email = profile.user.email or ""
    if "email" in fields:
        _safe_fill(fields["email"], email)
        filled += 1

    # Phone
    phone = profile.phone_number if profile and profile.phone_number else ""
    if "phone" in fields:
        _safe_fill(fields["phone"], phone)
        filled += 1

    # Address
    address = profile.address if profile and profile.address else ""
    if "address" in fields:
        _safe_fill(fields["address"], address)
        filled += 1

    # City
    city = profile.location if profile and profile.location else ""
    if "city" in fields:
        _safe_fill(fields["city"], city)
        filled += 1

    # LinkedIn (leave blank if not available)
    if "linkedin" in fields:
        _safe_fill(fields["linkedin"], "")

    # Cover letter
    if "cover_letter" in fields and cover_letter_text:
        _safe_fill(fields["cover_letter"], cover_letter_text)
        filled += 1

    # Resume upload
    if "resume_upload" in fields and resume and resume.file_path:
        try:
            abs_path = os.path.abspath(resume.file_path)
            if os.path.exists(abs_path):
                fields["resume_upload"].set_input_files(abs_path)
                logger.info(f"[Automation] Uploaded resume: {abs_path}")
                filled += 1
            else:
                logger.warning(f"[Automation] Resume file not found: {abs_path}")
        except Exception as e:
            logger.error(f"[Automation] Resume upload failed: {e}")

    return filled


def _safe_fill(locator, value: str):
    """Safely fill a form field, clearing existing content first."""
    try:
        locator.click()
        locator.fill(value)
    except Exception as e:
        logger.warning(f"[Automation] Failed to fill field: {e}")


def _capture_screenshot(page, application: Application, suffix: str) -> str:
    """Capture a screenshot and save it to the screenshots directory."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"app_{application.id}_{suffix}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    try:
        page.screenshot(path=filepath, full_page=True)
        logger.info(f"[Automation] Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"[Automation] Screenshot failed: {e}")
        return ""


def _capture_error_screenshot(application: Application):
    """Attempt to capture a screenshot during error handling (best-effort)."""
    # In error cases we may not have a page reference, so this is a no-op placeholder
    pass


def _mark_status(db: Session, application: Application,
                 status: ApplicationStatus, message: str):
    """Update application status and add an event."""
    application.status = status

    event = ApplicationStatusEvent(
        application_id=application.id,
        status=status,
        message=message
    )
    db.add(event)
    db.commit()
    logger.info(f"[Automation] Status → {status.value}: {message}")
