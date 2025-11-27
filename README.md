# Jinder - Tinder for Jobs

Jinder is a web application that simplifies the job application process using a "swipe" interface. It automates job discovery, matching, and application submission.

## Features

- **Google Sign-In**: Easy onboarding.
- **Resume Parsing**: Upload your resume to get tailored job recommendations.
- **Smart Matching**: Jobs are matched based on your profile and resume using AI embeddings.
- **Swipe Interface**: Swipe right to apply, left to skip.
- **Auto-Apply**: Automatically fills out applications for jobs you swipe right on.
- **Dashboard**: Track your application status in real-time.
- **Gmail Integration**: Automatically updates application status based on emails from recruiters.

## Tech Stack

- **Frontend**: Angular (v16+)
- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL
- **AI/ML**: OpenAI Embeddings & GPT-4
- **Automation**: Playwright

## Setup

### Backend

1. Navigate to `backend/`
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the server: `uvicorn app.main:app --reload`

### Frontend

1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run the app: `ng serve`

## License

Proprietary.
