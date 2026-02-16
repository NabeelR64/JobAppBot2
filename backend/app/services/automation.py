"""
Playwright-based browser automation engine for job applications.

Launches headless Chromium, navigates to job posting URLs, detects form fields,
fills them from user profile data, uploads resumes, and captures screenshots.

Supports pause-and-resume: when the bot can't fill a field, it saves progress
and marks the application as USER_INPUT_NEEDED. The user provides missing values
via the API, and the bot resumes with all fields filled.
"""

import os
import logging
from typing import Tuple, Dict, List
from datetime import datetime

from sqlalchemy.orm import Session
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from app.models import Application, ApplicationStatus, ApplicationStatusEvent
from app.services import cover_letter, form_detector

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = "uploads/screenshots"
# dry_run=True fills forms but does NOT click Submit (safe for development)
DRY_RUN = True

# Fields the bot knows how to fill from user profile data
KNOWN_FIELD_TYPES = {
    "full_name", "first_name", "last_name", "email", "phone",
    "address", "city", "linkedin", "cover_letter", "resume_upload"
}


def run_automation(application_id: int, db: Session):
    """
    Main automation entry point. Called as a BackgroundTask from the swipe endpoint.

    1. Loads application, user profile, resume, job posting
    2. Generates cover letter
    3. Launches Playwright, navigates to job URL
    4. Detects and fills form fields
    5. If missing fields → saves state, sets USER_INPUT_NEEDED
    6. If all filled → captures screenshot, updates status
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


def resume_automation(application_id: int, user_fields: dict, db: Session):
    """
    Resume automation after user provides missing field values.

    Re-launches Playwright, navigates to the saved page URL,
    fills ALL fields (saved + user-provided), and submits.
    """
    logger.info(f"[Automation] Resuming for application {application_id}")

    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        logger.error(f"[Automation] Application {application_id} not found")
        return

    state = application.automation_state
    if not state:
        logger.error(f"[Automation] No saved state for application {application_id}")
        _mark_status(db, application, ApplicationStatus.FAILED,
                     "No saved automation state found.")
        return

    page_url = state.get("page_url")
    filled_fields = state.get("filled_fields", {})
    cover_letter_text = state.get("cover_letter_text", application.cover_letter_text or "")
    resume = application.user.resume

    # Merge user-provided fields into filled fields
    all_fields = {**filled_fields, **user_fields}

    try:
        _run_resume_browser(application, db, page_url, all_fields, cover_letter_text, resume)
    except PlaywrightTimeout:
        logger.error(f"[Automation] Timeout during resume for {page_url}")
        _mark_status(db, application, ApplicationStatus.FAILED,
                     f"Navigation timeout during resume for {page_url}")
    except Exception as e:
        logger.error(f"[Automation] Resume error: {e}")
        _mark_status(db, application, ApplicationStatus.FAILED,
                     f"Resume automation error: {str(e)[:200]}")


def _run_browser_automation(application: Application, db: Session,
                            profile, resume, cover_letter_text: str):
    """Core browser automation logic — initial run."""
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

            # Detect form fields using known patterns
            fields = form_detector.detect_form_fields(page)

            if not fields:
                # No form found — external ATS link or info-only page
                screenshot_path = _capture_screenshot(page, application, "no_form")
                application.screenshot_path = screenshot_path
                _mark_status(db, application, ApplicationStatus.MANUAL_INTERVENTION_REQUIRED,
                             f"No application form detected. Apply manually at: {job_url}")
                return

            # Fill detected fields and track what was filled vs missing
            filled_report, missing_from_profile = _fill_form_fields_with_report(
                page, fields, profile, resume, cover_letter_text
            )
            logger.info(f"[Automation] Filled: {list(filled_report.keys())}, "
                        f"Missing (no profile data): {[m['key'] for m in missing_from_profile]}")

            # Detect unknown fields (custom employer questions not in our patterns)
            known_keys = set()
            for field_key, locator in fields.items():
                try:
                    name = locator.get_attribute("name") or ""
                    el_id = locator.get_attribute("id") or ""
                    known_keys.add(name)
                    known_keys.add(el_id)
                    known_keys.add(field_key)
                except Exception:
                    known_keys.add(field_key)

            unknown_fields = form_detector.get_all_visible_inputs(page, known_keys)

            # Combine all missing fields
            all_missing = missing_from_profile + unknown_fields

            if all_missing:
                # PAUSE: save state and ask user for input
                screenshot_path = _capture_screenshot(page, application, "needs_input")
                application.screenshot_path = screenshot_path

                application.automation_state = {
                    "filled_fields": filled_report,
                    "missing_fields": all_missing,
                    "page_url": job_url,
                    "cover_letter_text": cover_letter_text,
                }
                db.commit()

                missing_labels = ", ".join(m["label"] for m in all_missing[:5])
                extra = f" (+{len(all_missing) - 5} more)" if len(all_missing) > 5 else ""
                _mark_status(db, application, ApplicationStatus.USER_INPUT_NEEDED,
                             f"Filled {len(filled_report)} fields. Need your input for: {missing_labels}{extra}")
                return

            # All fields filled — proceed
            screenshot_path = _capture_screenshot(page, application, "filled")
            application.screenshot_path = screenshot_path

            _complete_submission(page, application, db, job_url, len(filled_report))

        finally:
            browser.close()


def _run_resume_browser(application: Application, db: Session,
                        page_url: str, all_fields: dict,
                        cover_letter_text: str, resume):
    """Browser automation for resumed applications — re-fill everything and submit."""
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
            logger.info(f"[Automation] Resuming — navigating to {page_url}")
            page.goto(page_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            if form_detector.detect_captcha(page):
                screenshot_path = _capture_screenshot(page, application, "captcha_resume")
                application.screenshot_path = screenshot_path
                _mark_status(db, application, ApplicationStatus.MANUAL_INTERVENTION_REQUIRED,
                             f"CAPTCHA detected on resume. Apply manually at: {page_url}")
                return

            # Re-detect form fields
            fields = form_detector.detect_form_fields(page)

            # Fill known pattern fields with saved values
            filled_count = 0
            for field_key, locator in fields.items():
                if field_key in all_fields:
                    if field_key == "resume_upload" and resume and resume.file_path:
                        try:
                            abs_path = os.path.abspath(resume.file_path)
                            if os.path.exists(abs_path):
                                locator.set_input_files(abs_path)
                                filled_count += 1
                        except Exception as e:
                            logger.warning(f"[Automation] Resume upload failed on resume: {e}")
                    else:
                        _safe_fill(locator, str(all_fields[field_key]))
                        filled_count += 1

            # Fill user-provided custom fields by name/id
            for key, value in all_fields.items():
                if key in KNOWN_FIELD_TYPES:
                    continue  # Already handled above
                # Try to find by name, then by id
                for selector in [f'[name="{key}"]', f'[id="{key}"]']:
                    try:
                        locator = page.locator(selector).first
                        if locator.count() > 0 and locator.is_visible():
                            _safe_fill(locator, str(value))
                            filled_count += 1
                            break
                    except Exception:
                        continue

            # Fill cover letter textarea if present
            cover_letter_fields = form_detector.FIELD_PATTERNS.get("cover_letter", [])
            for selector in cover_letter_fields:
                try:
                    locator = page.locator(selector).first
                    if locator.count() > 0 and locator.is_visible():
                        _safe_fill(locator, cover_letter_text)
                        filled_count += 1
                        break
                except Exception:
                    continue

            screenshot_path = _capture_screenshot(page, application, "resumed_filled")
            application.screenshot_path = screenshot_path

            # Clear saved state
            application.automation_state = None
            db.commit()

            _complete_submission(page, application, db, page_url, filled_count)

        finally:
            browser.close()


def _complete_submission(page, application: Application, db: Session,
                         job_url: str, fields_filled: int):
    """Handle the final submission step (or dry run)."""
    if DRY_RUN:
        logger.info("[Automation] DRY RUN — skipping form submission")
        _mark_status(db, application, ApplicationStatus.APPLIED,
                     f"Form filled successfully (dry run). {fields_filled} fields completed.")
    else:
        submit_btn = form_detector.detect_apply_button(page)
        if submit_btn:
            submit_btn.click()
            page.wait_for_timeout(3000)

            screenshot_path = _capture_screenshot(page, application, "submitted")
            application.screenshot_path = screenshot_path
            _mark_status(db, application, ApplicationStatus.APPLIED,
                         f"Application submitted successfully. {fields_filled} fields filled.")
        else:
            _mark_status(db, application, ApplicationStatus.MANUAL_INTERVENTION_REQUIRED,
                         f"Form filled but no submit button found. Apply manually at: {job_url}")


def _fill_form_fields_with_report(page, fields: dict, profile, resume,
                                   cover_letter_text: str) -> Tuple[Dict, List]:
    """
    Fill detected form fields with user data.
    Returns (filled_report, missing_fields):
      - filled_report: { field_key: value_used }
      - missing_fields: [{ key, label, type }] for fields we had no data for
    """
    filled_report = {}
    missing_fields = []

    # Name fields
    name = profile.name if profile else ""
    name_parts = name.split(" ", 1) if name else ["", ""]
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    for field_key, value, label in [
        ("full_name", name, "Full Name"),
        ("first_name", first_name, "First Name"),
        ("last_name", last_name, "Last Name"),
    ]:
        if field_key in fields:
            if value:
                _safe_fill(fields[field_key], value)
                filled_report[field_key] = value
            else:
                missing_fields.append({"key": field_key, "label": label, "type": "text"})

    # Email
    email = ""
    if profile and hasattr(profile, "user") and profile.user:
        email = profile.user.email or ""
    if "email" in fields:
        if email:
            _safe_fill(fields["email"], email)
            filled_report["email"] = email
        else:
            missing_fields.append({"key": "email", "label": "Email Address", "type": "email"})

    # Phone
    phone = profile.phone_number if profile and profile.phone_number else ""
    if "phone" in fields:
        if phone:
            _safe_fill(fields["phone"], phone)
            filled_report["phone"] = phone
        else:
            missing_fields.append({"key": "phone", "label": "Phone Number", "type": "tel"})

    # Address
    address = profile.address if profile and profile.address else ""
    if "address" in fields:
        if address:
            _safe_fill(fields["address"], address)
            filled_report["address"] = address
        else:
            missing_fields.append({"key": "address", "label": "Address", "type": "text"})

    # City
    city = profile.location if profile and profile.location else ""
    if "city" in fields:
        if city:
            _safe_fill(fields["city"], city)
            filled_report["city"] = city
        else:
            missing_fields.append({"key": "city", "label": "City", "type": "text"})

    # LinkedIn
    if "linkedin" in fields:
        missing_fields.append({"key": "linkedin", "label": "LinkedIn URL", "type": "url"})

    # Cover letter
    if "cover_letter" in fields:
        if cover_letter_text:
            _safe_fill(fields["cover_letter"], cover_letter_text)
            filled_report["cover_letter"] = cover_letter_text
        else:
            missing_fields.append({"key": "cover_letter", "label": "Cover Letter", "type": "textarea"})

    # Resume upload
    if "resume_upload" in fields and resume and resume.file_path:
        try:
            abs_path = os.path.abspath(resume.file_path)
            if os.path.exists(abs_path):
                fields["resume_upload"].set_input_files(abs_path)
                filled_report["resume_upload"] = abs_path
                logger.info(f"[Automation] Uploaded resume: {abs_path}")
            else:
                logger.warning(f"[Automation] Resume file not found: {abs_path}")
                missing_fields.append({"key": "resume_upload", "label": "Resume File", "type": "file"})
        except Exception as e:
            logger.error(f"[Automation] Resume upload failed: {e}")
            missing_fields.append({"key": "resume_upload", "label": "Resume File", "type": "file"})
    elif "resume_upload" in fields:
        missing_fields.append({"key": "resume_upload", "label": "Resume File", "type": "file"})

    return filled_report, missing_fields


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
