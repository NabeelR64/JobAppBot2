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


def get_all_visible_inputs(page: Page, known_field_keys: set) -> list:
    """
    Find all visible input/textarea fields on the page that were NOT
    already matched by our pattern-based detection.

    Returns a list of dicts: [{ key, label, type }]
    These represent fields the bot couldn't auto-fill.
    """
    unknown_fields = []
    seen_keys = set()

    for tag in ["input", "textarea"]:
        try:
            elements = page.locator(tag).all()
            for el in elements:
                try:
                    if not el.is_visible():
                        continue

                    input_type = el.get_attribute("type") or "text"
                    # Skip hidden, submit, button, checkbox, radio — not text fields
                    if input_type in ("hidden", "submit", "button", "checkbox", "radio", "file"):
                        continue

                    name = el.get_attribute("name") or ""
                    el_id = el.get_attribute("id") or ""
                    placeholder = el.get_attribute("placeholder") or ""
                    aria_label = el.get_attribute("aria-label") or ""

                    key = name or el_id or placeholder.lower().replace(" ", "_")[:30]
                    if not key or key in seen_keys:
                        continue

                    # Skip if this field was already matched by pattern detection
                    if key in known_field_keys:
                        continue

                    # Try to find a label
                    label = aria_label or placeholder
                    if not label and el_id:
                        try:
                            label_el = page.locator(f'label[for="{el_id}"]').first
                            if label_el.count() > 0:
                                label = label_el.inner_text().strip()
                        except Exception:
                            pass
                    if not label:
                        label = name.replace("_", " ").replace("-", " ").title()

                    field_type = "textarea" if tag == "textarea" else input_type
                    unknown_fields.append({
                        "key": key,
                        "label": label,
                        "type": field_type,
                    })
                    seen_keys.add(key)

                except Exception:
                    continue
        except Exception:
            continue

    logger.info(f"Found {len(unknown_fields)} unknown fields: {[f['key'] for f in unknown_fields]}")
    return unknown_fields
