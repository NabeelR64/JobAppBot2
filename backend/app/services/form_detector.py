"""
Form field detection heuristics for job application pages.

Scans a Playwright page for common form inputs by inspecting
name, id, placeholder, label, and aria-label attributes.
"""

import logging
from typing import Optional
from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)

# Patterns to match common form field attributes
FIELD_PATTERNS = {
    "first_name": [
        'input[name*="first" i][name*="name" i]',
        'input[id*="first" i][id*="name" i]',
        'input[placeholder*="first name" i]',
        'input[aria-label*="first name" i]',
        'input[name="firstName" i]',
        'input[name="first_name" i]',
    ],
    "last_name": [
        'input[name*="last" i][name*="name" i]',
        'input[id*="last" i][id*="name" i]',
        'input[placeholder*="last name" i]',
        'input[aria-label*="last name" i]',
        'input[name="lastName" i]',
        'input[name="last_name" i]',
    ],
    "full_name": [
        'input[name="name" i]',
        'input[name="full_name" i]',
        'input[name="fullName" i]',
        'input[id="name" i]',
        'input[placeholder*="full name" i]',
        'input[aria-label*="full name" i]',
        'input[placeholder="Name" i]',
    ],
    "email": [
        'input[type="email"]',
        'input[name*="email" i]',
        'input[id*="email" i]',
        'input[placeholder*="email" i]',
        'input[aria-label*="email" i]',
    ],
    "phone": [
        'input[type="tel"]',
        'input[name*="phone" i]',
        'input[name*="mobile" i]',
        'input[id*="phone" i]',
        'input[placeholder*="phone" i]',
        'input[aria-label*="phone" i]',
    ],
    "linkedin": [
        'input[name*="linkedin" i]',
        'input[id*="linkedin" i]',
        'input[placeholder*="linkedin" i]',
        'input[aria-label*="linkedin" i]',
    ],
    "resume_upload": [
        'input[type="file"][name*="resume" i]',
        'input[type="file"][name*="cv" i]',
        'input[type="file"][id*="resume" i]',
        'input[type="file"][id*="cv" i]',
        'input[type="file"][accept*="pdf" i]',
        'input[type="file"][accept*=".doc" i]',
        'input[type="file"]',  # Fallback: any file input
    ],
    "cover_letter": [
        'textarea[name*="cover" i]',
        'textarea[name*="letter" i]',
        'textarea[id*="cover" i]',
        'textarea[placeholder*="cover letter" i]',
        'textarea[aria-label*="cover letter" i]',
        'textarea[name*="message" i]',
        'textarea[placeholder*="why" i]',
    ],
    "address": [
        'input[name*="address" i]',
        'input[id*="address" i]',
        'input[placeholder*="address" i]',
        'input[aria-label*="address" i]',
    ],
    "city": [
        'input[name*="city" i]',
        'input[id*="city" i]',
        'input[placeholder*="city" i]',
    ],
}

APPLY_BUTTON_SELECTORS = [
    'button[type="submit"]',
    'input[type="submit"]',
    'button:has-text("Apply")',
    'button:has-text("Submit")',
    'button:has-text("Submit Application")',
    'a:has-text("Apply")',
    'button:has-text("Send")',
    'button:has-text("Send Application")',
]

CAPTCHA_SELECTORS = [
    'iframe[src*="recaptcha"]',
    'iframe[src*="hcaptcha"]',
    'iframe[title*="reCAPTCHA"]',
    '.g-recaptcha',
    '.h-captcha',
    '#captcha',
]


def detect_form_fields(page: Page) -> dict:
    """
    Scan the page for common job application form fields.
    Returns a dict mapping field type -> first matching Locator.
    """
    detected = {}

    for field_type, selectors in FIELD_PATTERNS.items():
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                if locator.count() > 0 and locator.is_visible():
                    detected[field_type] = locator
                    logger.info(f"Detected form field: {field_type} via '{selector}'")
                    break
            except Exception:
                continue

    logger.info(f"Total detected fields: {list(detected.keys())}")
    return detected


def detect_captcha(page: Page) -> bool:
    """Check if the page contains a CAPTCHA challenge."""
    for selector in CAPTCHA_SELECTORS:
        try:
            if page.locator(selector).count() > 0:
                logger.warning(f"CAPTCHA detected via '{selector}'")
                return True
        except Exception:
            continue
    return False


def detect_apply_button(page: Page) -> Optional[Locator]:
    """Find the apply/submit button on the page."""
    for selector in APPLY_BUTTON_SELECTORS:
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible():
                logger.info(f"Found apply button via '{selector}'")
                return locator
        except Exception:
            continue

    logger.warning("No apply/submit button found")
    return None
