def generate_cover_letter(resume_text: str, job_description: str) -> str:
    """
    Generate a cover letter using LLM (Stub).
    """
    return f"""
    Dear Hiring Manager,
    
    I am writing to express my interest in the position.
    Based on my experience: {resume_text[:50]}...
    And your requirements: {job_description[:50]}...
    
    I believe I am a great fit.
    
    Sincerely,
    Candidate
    """
