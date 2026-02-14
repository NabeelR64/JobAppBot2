import logging
from typing import Optional

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional cover letter writer. Write concise, compelling cover letters \
that highlight the candidate's relevant experience and skills for the specific job. \
The letter should be 3-4 paragraphs, professional in tone, and personalized to the job description. \
Do not include placeholder brackets like [Company Name] — use the actual details provided. \
Do not include a date or address header — start directly with the salutation."""


def generate_cover_letter(
    resume_text: str,
    job_description: str,
    user_profile: Optional[dict] = None
) -> str:
    """
    Generate a tailored cover letter using OpenAI GPT-4o-mini.

    Falls back to a basic template if the API key is missing or the call fails,
    so the application flow never breaks.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set — using fallback cover letter template.")
        return _fallback_cover_letter(resume_text, job_description)

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        user_message = _build_user_prompt(resume_text, job_description, user_profile)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=800
        )

        cover_letter = response.choices[0].message.content.strip()
        logger.info("Successfully generated cover letter via OpenAI.")
        return cover_letter

    except Exception as e:
        logger.error(f"OpenAI cover letter generation failed: {e}")
        return _fallback_cover_letter(resume_text, job_description)


def _build_user_prompt(
    resume_text: str,
    job_description: str,
    user_profile: Optional[dict] = None
) -> str:
    """Build the user prompt for cover letter generation."""
    prompt_parts = [
        "Write a cover letter for the following job based on the candidate's resume.\n"
    ]

    prompt_parts.append(f"## Job Description\n{job_description[:3000]}\n")
    prompt_parts.append(f"## Candidate Resume\n{resume_text[:4000]}\n")

    if user_profile:
        profile_info = []
        if user_profile.get("name"):
            profile_info.append(f"Name: {user_profile['name']}")
        if user_profile.get("desired_roles"):
            roles = user_profile["desired_roles"]
            if isinstance(roles, list):
                roles = ", ".join(roles)
            profile_info.append(f"Desired Roles: {roles}")
        if user_profile.get("field_of_work"):
            profile_info.append(f"Field: {user_profile['field_of_work']}")

        if profile_info:
            prompt_parts.append(f"## Candidate Profile\n" + "\n".join(profile_info) + "\n")

    return "\n".join(prompt_parts)


def _fallback_cover_letter(resume_text: str, job_description: str) -> str:
    """Basic template fallback when OpenAI is unavailable."""
    return f"""Dear Hiring Manager,

I am writing to express my interest in the position described in your job posting.

Based on my experience and qualifications, I believe I would be a strong fit for this role. \
My background includes relevant skills and experience that align with your requirements.

I would welcome the opportunity to discuss how my skills and experience can contribute to your team. \
Thank you for considering my application.

Sincerely,
Candidate"""
