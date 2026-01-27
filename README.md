# Jinder - Tinder for Jobs

Jinder is a web application that simplifies the job application process using a "swipe" interface. It automates job discovery, matching, and application submission.

## Table of Contents
1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Setup](#setup)
4. [Frontend Development](#frontend-development)
5. [Future Work & Agent Prompts](#future-work--agent-prompts)
6. [Original Requirements & Analysis](#original-requirements--analysis)
7. [Change Log](#change-log)
8. [License](#license)

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

## Frontend Development

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 18.2.4.

### Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

### Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

### Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

### Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

### Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

### Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.

## Future Work & Agent Prompts

This section outlines the roadmap for moving Jinder from MVP to a production-ready application. Each section includes a detailed prompt that can be fed to an AI agent to execute the task.

### 1. Fully Integrate Google OAuth

**Current Status:** The MVP uses a mock login flow on the frontend and a bypassed dependency on the backend.
**Goal:** Implement real Google Sign-In, verify tokens on the backend, and create/update users securely.

#### Agent Prompt
```text
Task: Implement Real Google OAuth Integration

Context:
The current Jinder application uses a mock authentication flow. We need to replace this with actual Google OAuth 2.0.

Requirements:
1. Frontend (Angular):
   - Replace the mock "Sign in with Google" button with the actual Google Identity Services SDK.
   - Retrieve the ID token from Google upon successful sign-in.
   - Send this ID token to the backend `/auth/login/google` endpoint.
2. Backend (FastAPI):
   - Update `app/api/auth.py` to verify the Google ID token using `google-auth` library.
   - Extract user email and sub (subject) from the verified token.
   - Create or update the user in the database.
   - Issue a JWT access token for the session.
   - Revert the `get_current_user` dependency in `app/api/deps.py` to actually validate the JWT token (remove the MVP bypass).
3. Configuration:
   - Ensure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are read from environment variables.

Deliverables:
- Updated `LandingComponent` and `AuthService`.
- Updated `auth.py` and `deps.py`.
- Verified login flow.
```

### 2. Fully Integrate Job Search API

**Current Status:** The `job_ingestion.py` service generates mock job data.
**Goal:** Integrate a real job search API (e.g., Indeed, LinkedIn, or a rapidapi aggregator) to fetch real listings.

#### Agent Prompt
```text
Task: Integrate Real Job Search API

Context:
Jinder currently uses mock data for job postings. We need to fetch real jobs relevant to the user's profile.

Requirements:
1. Select a Job API (e.g., JSearch on RapidAPI or similar).
2. Backend Service:
   - Update `app/services/job_ingestion.py`.
   - Implement a function `fetch_jobs(query: str, location: str)` that calls the external API.
   - Map the API response to the `JobPosting` database model.
   - Ensure duplicate jobs are not inserted (check by `external_id` or URL).
3. Integration:
   - Update the `/jobs/ingest` endpoint to accept search parameters.
   - Create a background task that periodically fetches jobs based on active user profiles (e.g., every 24 hours).

Deliverables:
- `JobIngestionService` with real API integration.
- Updated `JobPosting` model if new fields are needed.
- Tests verifying API response parsing.
```

### 3. Implement Job Application Automation

**Current Status:** The `automation.py` service is a stub that waits 5 seconds and marks the application as "APPLIED".
**Goal:** Use Playwright/Selenium to actually navigate to job URLs and fill out forms.

#### Agent Prompt
```text
Task: Implement Browser Automation for Job Applications

Context:
We need to automate the actual application process. When a user swipes right, the system should attempt to apply for the job.

Requirements:
1. Tooling: Use `playwright` (Python).
2. Service Implementation (`app/services/automation.py`):
   - Launch a headless browser.
   - Navigate to the `job_posting.url`.
   - Detect input fields (First Name, Last Name, Email, Resume Upload).
   - Use heuristics or LLM (OpenAI) to map HTML form fields to User Profile data.
   - Fill out the form.
   - Upload the resume file (from `app/services/resume_parser.py` path).
   - Submit the form.
   - Capture a screenshot of the confirmation page.
3. Error Handling:
   - Handle cases where the form is too complex (mark status as `FAILED` or `MANUAL_INTERVENTION_REQUIRED`).
   - Implement retry logic.

Deliverables:
- Functional `AutomationService` using Playwright.
- Logic to map user profile data to DOM elements.
- Screenshot storage for proof of application.
```

### 4. Add Swipe Limits

**Current Status:** Users can swipe indefinitely.
**Goal:** Limit users to 10 right swipes (applications) per day to manage costs/rate limits.

#### Agent Prompt
```text
Task: Implement Daily Swipe Limits

Context:
To prevent abuse and manage automation costs, limit users to 10 "Right Swipes" (applications) per 24-hour rolling window.

Requirements:
1. Database:
   - No schema change needed if we query `SwipeAction` table, OR add `daily_swipes_count` to UserProfile for performance.
2. Backend Logic:
   - In `app/api/jobs.py` (swipe endpoint):
     - Count number of "RIGHT" swipes by `current_user` in the last 24 hours.
     - If count >= 10, raise `HTTPException(429, "Daily limit reached")`.
3. Frontend:
   - Display a "Swipes remaining: X" counter on the Swipe page.
   - Disable the "Right Swipe" button/gesture when limit is reached.
   - Show a modal explaining the limit.

Deliverables:
- Updated swipe API endpoint with rate limiting logic.
- Updated Swipe UI with counter and limit state.
```

### 5. Improve Application Status UI

**Current Status:** A basic HTML table.
**Goal:** A Kanban-style board or a more visual timeline view.

#### Agent Prompt
```text
Task: Redesign Application Dashboard

Context:
The current dashboard is a simple table. Users need a better way to visualize the progress of their applications.

Requirements:
1. UI Design:
   - Create a Kanban board layout with columns: "Applied", "Interview", "Offer", "Rejected".
   - OR create a list view with a visual progress stepper for each application.
2. Frontend Components:
   - Create `ApplicationCardComponent` to display job details and status.
   - Implement drag-and-drop (optional) or simple status indicators.
3. Features:
   - Allow users to manually update status (e.g., if they get an email outside the system).
   - Filter/Sort by date, company, or status.

Deliverables:
- New `DashboardComponent` design.
- Responsive CSS/Styling.
```

### 6. Proper Database Integration

**Current Status:** Using SQLite for local dev; Models use JSON instead of ARRAY.
**Goal:** Migrate to PostgreSQL for production, utilizing `pgvector` for embeddings.

#### Agent Prompt
```text
Task: Migrate to PostgreSQL and Optimize Schema

Context:
The MVP uses SQLite. Production requires PostgreSQL for concurrency and vector search capabilities.

Requirements:
1. Infrastructure:
   - Provision a PostgreSQL instance (local Docker or AWS RDS).
2. Schema Changes:
   - Revert `JSON` columns in `models.py` to `ARRAY(String)` (or keep JSONB if preferred for Postgres).
   - Install `pgvector` extension.
   - Add `embedding_vector` column to `Resume` and `JobPosting` tables.
3. Migration:
   - Update `alembic/env.py` and `config.py` to prefer Postgres.
   - Generate new migration scripts.
   - Ensure data persistence.

Deliverables:
- Configured PostgreSQL connection.
- Updated SQLAlchemy models.
- Successful Alembic migration.
```

### 7. Security Concerns

**Current Status:** Basic JWT, no rate limiting, file upload not sanitized.
**Goal:** Harden the application.

#### Agent Prompt
```text
Task: Security Hardening

Context:
The application needs to be secured before public release.

Requirements:
1. File Uploads:
   - Validate file magic numbers (signatures) to ensure uploaded resumes are actually PDF/DOCX.
   - Scan files for malware (ClamAV or similar).
   - Store files in AWS S3 (private bucket) instead of local disk.
2. API Security:
   - Implement global rate limiting (e.g., `slowapi`).
   - Ensure all endpoints are behind authentication (except login/landing).
3. Data:
   - Encrypt sensitive fields (phone number, address) at rest if necessary.
   - Sanitize inputs to prevent XSS/SQLi (SQLAlchemy handles SQLi, but check raw queries).

Deliverables:
- S3 Integration for storage.
- Rate limiting middleware.
- File validation logic.
```

### 8. Scalability

**Current Status:** Monolithic FastAPI app.
**Goal:** Prepare for high load.

#### Agent Prompt
```text
Task: Improve Scalability

Context:
As the user base grows, the automation and job ingestion tasks will become bottlenecks.

Requirements:
1. Async Workers:
   - Move `automation.py` and `job_ingestion.py` logic to a task queue (Celery + Redis or AWS SQS + Lambda).
   - The FastAPI app should only *enqueue* tasks, not execute them in the request loop.
2. Caching:
   - Implement Redis caching for `get_current_user` and job recommendations.
3. Database:
   - Set up connection pooling (pgbouncer).

Deliverables:
- Celery/Redis configuration.
- Refactored background tasks.
```

### 9. Production Deployment

**Current Status:** Local `uvicorn` and `ng serve`.
**Goal:** Live URL.

#### Agent Prompt
```text
Task: Production Deployment to AWS

Context:
Deploy the Jinder application to the public internet.

Requirements:
1. Containerization:
   - Create `Dockerfile` for Backend.
   - Create `Dockerfile` (or build script) for Frontend (Nginx serving static files).
2. Infrastructure (Terraform/CDK preferred):
   - AWS ECS (Fargate) for Backend.
   - AWS S3 + CloudFront for Frontend.
   - AWS RDS for PostgreSQL.
   - AWS ElastiCache for Redis (if used).
3. CI/CD:
   - GitHub Actions workflow to build and push images to ECR on push to `main`.
   - Auto-deploy to ECS.

Deliverables:
- Dockerfiles.
- Terraform scripts.
- GitHub Actions workflow.
- Live URL.
```

## Original Requirements & Analysis

You are a senior full-stack engineer and solution architect.
Your task is to design and implement an MVP for Jinder, a “Tinder for jobs” web application.

Jinder lets users:

- Sign in with Google
- Upload a resume
- Answer a few questions to build a profile
- Get suggested job categories and job listings
- Swipe left/right on job cards:
  - Left = skip
  - Right = auto-apply using browser automation and an AI-generated cover letter
- Track applications and statuses in a dashboard
- Allow the system to read their Gmail (read-only) to automatically detect updates (thank-you emails, interview invites, rejections, follow-ups, etc.).

Your output should be:

- A well-structured codebase
- Infrastructure setup notes (or IaC if possible)
- Clear documentation of APIs and flows

Focus on a working MVP first, but structure the code so premium features could be added later.

### 1. High-Level Requirements

#### User flow summary

1. **User signs in via Google Sign-In.**
2. **On first login, user is asked to:**
   - Upload one resume (PDF/DOCX). Only a single resume is supported in this MVP.
   - Answer profile questions: desired roles, locations, salary expectations, seniority, remote/on-site preference, etc.
3. System uses OpenAI embeddings to analyze the resume and build a semantic representation of the user’s skills, experience, and education.
4. System recommends job categories/fields first (e.g., “Backend developer”, “Data analyst”, “Product manager”) based on resume + profile.
5. **User can:**
   - Select categories they like.
   - Explicitly mark categories they don’t want (“not interested in sales roles,” etc.).
6. System pulls jobs from Indeed, ranks them using a hybrid scoring approach, and presents them as swipeable cards (desktop web).
7. User can filter jobs with a filter panel.
8. **For each job:**
   - Swipe left → skip.
   - Swipe right → automatically apply (no extra confirmation pop-up).
9. **System generates a tailored cover letter using LLMs based on:**
   - Job title
   - Job description
   - User’s resume
   - User’s profile preferences
10. System uses browser automation to fill application forms on the job’s external site.
11. System records the application in the database.
12. **A dedicated dashboard page lets users see:**
    - Which jobs they’ve applied to
    - Statuses and a status timeline per job
13. **System requests read-only access to the user’s Gmail and periodically:**
    - Reads new emails
    - Detects job-related messages (thank-you, interview invites, rejections, recruiter follow-ups, general status updates)
    - Updates the application status timeline accordingly
    - Sends notifications by email and SMS.

#### Non-goals (for MVP)

- No mobile-native app yet (later).
- No multi-resume support (MVP = single resume).
- No complex monetization or premium tiers in MVP.
- No support for non-Gmail providers in MVP.

### 2. Tech Stack Constraints

#### Frontend

- **Framework**: Angular (desktop-first design, but responsive enough).
- **Style**:
  - Color palette: sky blue, a complementary darker blue, and white as primary UI colors.
  - Clean, modern, card-based UI for job swiping.
- **Features**:
  - Google Sign-In button and flow integration.
  - Resume upload UI (drag-and-drop or simple file input).
  - Profile wizard (step-by-step).
  - Job browsing/swiping UI (Tinder-style deck).
  - Applied jobs dashboard and status timeline view.
  - Filter panel for:
    - Salary range
    - Remote/hybrid/on-site
    - Job title keywords
    - Seniority level
    - Company size
    - Location

#### Backend

- **Language**: Python.
- **Framework**: Prefer FastAPI (you may optionally include a small Flask adapter or note, but FastAPI should be the main HTTP API).
- **Database**: PostgreSQL (hosted on AWS RDS, or equivalent).
- **Hosting**: AWS (you may choose between ECS Fargate, EC2, or Lambda + API Gateway; choose a practical option and document it).
- **Email integration**: Gmail API with OAuth 2.0, read-only scope.
- **SMS provider**: You can choose a reasonable provider (e.g., Twilio or AWS SNS with SMS), but keep it abstracted.
- **Resume and job embeddings**: Use OpenAI embeddings. Choose a current, cost-effective embedding model and document it (e.g., text-embedding model).
- **Job Source**: Use Indeed as the job source. Design the job ingestion layer as a pluggable service. For MVP, pull job listings by:
  - Location
  - Job title keywords
  - Category
  - Remote/on-site
  - Salary range (if available from API)
- **Browser Automation**: Implement an application automation worker using a browser automation framework (e.g., Playwright or Selenium for Python).

### 3. Core Functional Components & APIs

Design the backend and API in a modular way. At a minimum implement:

#### 3.1 Authentication & Users

- Google OAuth sign-in.
- On first sign-in, create a user record in the database.
- Store user_id, email, and Google OAuth tokens/refresh tokens securely.

#### 3.2 User Profile & Resume

- Models: User, UserProfile, Resume.
- Endpoints: POST /resume/upload, GET /profile, PUT /profile.
- Behavior: On resume upload, store file, extract text, call OpenAI embeddings API, and store embedding vector.

#### 3.3 Job Categories & Recommendations

- Models: JobCategory, UserCategoryPreference.
- Endpoints: GET /jobs/categories/recommendations, POST /jobs/categories/preferences.
- Logic: Derive categories by matching resume embedding.

#### 3.4 Job Fetching & Matching

- Models: JobPosting, JobRecommendation.
- Logic (Hybrid scoring): Compute LLM/embedding similarity + rule-based constraints (skills, location, salary, etc.).
- Endpoints: GET /jobs/recommendations (paginated "deck" for swiping).

#### 3.5 Swiping & Applications

- Models: SwipeAction, Application, ApplicationStatusEvent.
- Endpoints:
  - POST /jobs/{job_id}/swipe (Payload: { "direction": "left" | "right" })
    - If right: Create SwipeAction, Create Application (PENDING_AUTOMATION), Trigger automation worker.
  - GET /applications (List of applications with status)
  - GET /applications/{id}/timeline (Status history)

#### 3.6 Cover Letter Generation

- Service that calls OpenAI model to generate a concise, professional cover letter based on resume, profile, and job details.

#### 3.7 Gmail Integration & Status Detection

- Background worker that polls Gmail using OAuth tokens.
- Detects job-related emails (sender, subject, LLM classification).
- Updates Application status and creates ApplicationStatusEvent.
- Sends notifications.

### 4. Frontend UX Requirements

- **Landing page**: Branding, tagline, "Sign in with Google".
- **Onboarding flow**: Sign-in, Resume upload, Profile questions, Category selection.
- **Job browsing / swipe page**: Tinder-style card deck. Swipe controls. Filters panel.
- **Applications dashboard**: List of applications with status. Detail view with timeline.
- **Settings / account page**: Update profile, reconnect Gmail, view resume.
- **Legal pages**: Privacy Policy, Terms of Use.

### 5. Security, Privacy, and Compliance

- HTTPS everywhere.
- Store PII and resume files securely (Encrypted S3, RDS).
- Secure secrets management.
- Role-based access (user can only see their own data).
- Read-only Gmail scopes.
- User mechanisms for revoking access and deleting account.

## Change Log

| Date       | Change                    | Details                                                                                                                                                             |
| :--------- | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2025-12-28 | Consolidate Documentation | Combined `README.md`, `frontend/README.md`, `future_work.md`, and `main_prompt.md` into a single `README.md` to improve navigability. Added a Table of Contents. |
| 2025-12-28 | Profile & Resume Refactor | Refactored `OnboardingComponent` to support View/Edit modes. Added `Resume` backend schema and endpoints for upload/download. Enabled persistent profile viewing and resume downloading. |
| 2025-12-28 | Update .gitignore | Updated `.gitignore` to include `backend/uploads`, Python/backend ignores, Node/frontend ignores, and secrets/config files. |
| 2026-01-26 | Persistent Profiles & Auth | Implemented persistent storage for user profiles with extended fields (Address, Experience, Education, etc.). Consolidated Frontend Authentication service. Updated Onboarding flow to force profile completion. |
| 2026-01-26 | Profile Enhancements | Added Resume upload/view controls and structured form sections for Experience and Education to the Profile page. |

## License

Proprietary.
