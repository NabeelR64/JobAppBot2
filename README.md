# Jinder - Tinder for Jobs

Jinder is a web application that simplifies the job application process using a "swipe" interface. It automates job discovery, matching, and application submission.

## Table of Contents
1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Setup](#setup)
4. [Frontend Development](#frontend-development)
5. [Future Work & Agent Prompts](#future-work--agent-prompts)
6. [Phase 2 — Three-Week Roadmap](#phase-2--three-week-roadmap)
7. [Original Requirements & Analysis](#original-requirements--analysis)
8. [Change Log](#change-log)
9. [License](#license)

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

### 1. Fully Integrate Google OAuth (Completed)

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

### 2. Fully Integrate Job Search API (Completed)

**Current Status:** **DONE.** The application now integrates with the **TheirStack API** to fetch real job listings.
**Implementation Details:**
- `TheirStackService` queries for jobs matching the user's "Desired Roles" and "Desired Locations".
- Jobs are automatically ingested when recommendations allow.
- Duplicate detection is implemented via `external_id`.

#### Agent Prompt (Reference)
*This task has been completed.*
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

## Phase 2 — Three-Week Roadmap

Phase 1 delivered a working MVP: Google OAuth, user profile & resume upload, TheirStack job API integration, a swipe interface, and a basic applications dashboard. Phase 2 focuses on replacing every remaining stub with production-quality implementations and polishing the user experience so the app is genuinely useful end-to-end.

---

### Goal 1 — Real Resume Parsing & AI-Powered Cover Letters (Completed)

| Field | Details |
|:---|:---|
| **Goal** | Replace the placeholder resume parser and hardcoded cover letter stub with real implementations |
| **Expected Duration** | Week 1 (Days 1–4) |
| **Short Description** | Extract actual text from PDF/DOCX resumes and generate tailored cover letters with OpenAI |

**Long Description:**
The current `resume_parser.py` returns a dummy string like "Extracted text from PDF: filename" and `cover_letter.py` outputs a static template. We will integrate PyPDF2 and python-docx to extract real resume text, then use OpenAI embeddings to create a semantic vector for each resume. The cover letter service will call GPT-4 with the user's parsed resume, profile preferences, and the specific job description to produce a professional, customized letter. This is foundational because every downstream feature (job matching, auto-apply) depends on having real resume data.

**Game Plan:**
1. Install and integrate `PyPDF2` and `python-docx` into `resume_parser.py` for actual text extraction.
2. Call the OpenAI embeddings API after extraction and store the vector in the `Resume` model (add `embedding_vector` column).
3. Rewrite `cover_letter.py` to call GPT-4 with a structured prompt containing resume text, user profile, and job description.
4. Add unit tests for parsing various resume formats (PDF, DOCX) and verifying cover letter output structure.
5. Update the resume upload API to return richer parsed data (skills, experience, education extracted by GPT).

**Resources Affected:**
- `backend/app/services/resume_parser.py` — full rewrite
- `backend/app/services/cover_letter.py` — full rewrite
- `backend/app/models.py` — add `embedding_vector` column to `Resume`
- `backend/app/api/resume.py` — update response to include richer parsed data
- `backend/requirements.txt` — add `PyPDF2`, `python-docx`

---

### Goal 2 — Browser Automation for Auto-Apply (Playwright)

| Field | Details |
|:---|:---|
| **Goal** | Replace the `time.sleep(5)` automation stub with real Playwright-based form filling |
| **Expected Duration** | Week 1–2 (Days 4–9) |
| **Short Description** | Use Playwright to navigate to job URLs, detect form fields, and submit applications automatically |

**Long Description:**
The current `automation.py` simply sleeps for 5 seconds and marks every application as "APPLIED" without visiting any website. We will build a Playwright-powered automation engine that launches a headless browser, navigates to the job posting URL, and uses heuristics (and optionally an LLM) to identify form fields like name, email, phone, and resume upload. The service will fill these fields from the user's profile data, attach the resume file, and submit. A screenshot of the confirmation page will be captured as proof. Jobs with forms too complex to automate will be marked as `MANUAL_INTERVENTION_REQUIRED` with a direct link for the user.

**Game Plan:**
1. Set up Playwright in headless mode within the automation service; ensure browser binaries are installed via `playwright install`.
2. Build a generic form-detection module that identifies common input fields (name, email, phone, resume upload) by label text, placeholder, and `name`/`id` attributes.
3. Implement field-to-profile mapping logic that fills detected fields with `UserProfile` and `Resume` data.
4. Add resume file upload handling (detect `<input type="file">` and attach the stored PDF/DOCX).
5. Capture a screenshot on success/failure; add a `screenshot_path` column to `Application` model.
6. Implement error handling: catch navigation timeouts, CAPTCHA detection, and unsupported multi-step forms — mark these as `FAILED` or `MANUAL_INTERVENTION_REQUIRED`.
7. Add a new `ApplicationStatus.MANUAL_INTERVENTION_REQUIRED` enum value.

**Resources Affected:**
- `backend/app/services/automation.py` — full rewrite
- `backend/app/models.py` — add `screenshot_path` to `Application`, add `MANUAL_INTERVENTION_REQUIRED` status
- `backend/app/api/jobs.py` — move automation to a proper async background task (Celery or similar)
- `backend/uploads/` — store screenshots alongside resumes

---

### Goal 3 — Dashboard Redesign (Kanban Board) (Completed)

| Field | Details |
|:---|:---|
| **Goal** | Replace the plain HTML table dashboard with a visual Kanban-style board |
| **Expected Duration** | Week 2 (Days 8–11) |
| **Short Description** | Build a column-based board with cards organized by application status (Applied, Interview, Offer, Rejected) |

**Long Description:**
The current dashboard is a basic `<table>` with four columns (Company, Role, Status, Applied On) and no interactivity beyond a delete-account button. We will redesign it as a Kanban board with swim-lane columns for each status (Applied, Interview Invited, Offer, Rejected, Manual Intervention). Each application becomes a draggable card showing the company logo (or initials), role title, date, and a link to the original posting. Users will be able to manually update a card's status via dropdown and filter/sort by date or company. This significantly improves the user experience and makes tracking dozens of applications manageable.

**Game Plan:**
1. Create an `ApplicationCardComponent` to display job title, company, date, status badge, and external link.
2. Build a `KanbanBoardComponent` with columns dynamically generated from `ApplicationStatus` values.
3. Implement drag-and-drop between columns using Angular CDK `DragDropModule` to allow manual status updates.
4. Add a backend endpoint `PATCH /applications/{id}/status` to allow users to manually update application status.
5. Add filtering controls (by date range, company name, status) and sorting (newest first, alphabetical).
6. Style with responsive CSS so the board scrolls horizontally on mobile and stacks on narrow screens.

**Resources Affected:**
- `frontend/src/app/features/dashboard/` — rewrite `dashboard.component.html`, `dashboard.component.ts`, `dashboard.component.css`
- `frontend/src/app/features/dashboard/application-card/` — new component
- `frontend/src/app/core/services/application.service.ts` — add `updateStatus()` method
- `backend/app/api/application.py` — add `PATCH /{id}/status` endpoint
- `frontend/package.json` — add `@angular/cdk`

---

### Goal 4 — Gmail Integration for Status Tracking

| Field | Details |
|:---|:---|
| **Goal** | Connect to the user's Gmail (read-only) to automatically detect application status updates |
| **Expected Duration** | Week 2–3 (Days 10–14) |
| **Short Description** | Poll Gmail for recruiter emails and use GPT classification to update application statuses automatically |

**Long Description:**
The current `gmail.py` service is a mock that randomly flips 30% of "APPLIED" applications to "INTERVIEW_INVITED" without touching any real email. We will implement proper Gmail API OAuth 2.0 with read-only scope, requesting consent during onboarding. A background worker will periodically poll the user's inbox for emails from known recruiting domains and job-related subject lines. Each candidate email will be classified by GPT-4 into categories (confirmation, interview invite, rejection, follow-up) and matched to an existing application by company name. Detected status changes will create `ApplicationStatusEvent` entries and update the Kanban board in real-time.

**Game Plan:**
1. Add Gmail OAuth consent screen to the onboarding flow — request `gmail.readonly` scope after profile completion.
2. Store OAuth refresh tokens securely in the `User` model (add `gmail_refresh_token` column, encrypted at rest).
3. Rewrite `backend/app/services/gmail.py` to use the Gmail API (`google-api-python-client`) to fetch recent messages.
4. Build a GPT-4 classification prompt that takes email subject + body snippet and returns a status category + confidence score.
5. Implement company-name matching logic to link detected emails to existing `Application` records.
6. Set up a periodic background task (e.g., every 15 minutes per user) using FastAPI's `BackgroundTasks` or an APScheduler job.
7. Create `ApplicationStatusEvent` entries for each detected update.

**Resources Affected:**
- `backend/app/services/gmail.py` — full rewrite
- `backend/app/models.py` — add `gmail_refresh_token` to `User`
- `backend/app/api/gmail.py` — add OAuth callback and consent endpoints
- `frontend/src/app/features/onboarding/` — add Gmail consent step
- `backend/app/core/config.py` — add Gmail API scopes config

---

### Goal 5 — Daily Swipe Limits & Usage Analytics

| Field | Details |
|:---|:---|
| **Goal** | Limit right-swipes to 10 per day and show usage stats on the dashboard |
| **Expected Duration** | Week 3 (Days 14–16) |
| **Short Description** | Enforce a daily application cap to manage API costs and show users their remaining swipes and weekly stats |

**Long Description:**
Currently users can swipe right an unlimited number of times, which creates unbounded automation and API costs. We will add a 10-swipe-per-day rolling limit checked server-side on every right-swipe request. The frontend will display a "Swipes remaining: X/10" counter on the swipe page and gracefully disable the Apply button when the limit is reached, showing a modal explaining the reset time. Additionally, we will add a small analytics section to the dashboard showing weekly application counts, success rates, and most-applied-to companies — giving users insight into their job search activity.

**Game Plan:**
1. In `backend/app/api/jobs.py` swipe endpoint, query `SwipeAction` count for the current user in the last 24 hours; return `429` if ≥ 10.
2. Add a `GET /users/me/swipe-stats` endpoint returning daily count, remaining swipes, and reset time.
3. Update the swipe component to fetch and display the remaining count; disable the "Apply & Next" button at limit.
4. Add a limit-reached modal with countdown timer to next reset window.
5. Build a small analytics widget on the dashboard: weekly applications chart, top companies, success/rejection ratio.
6. Add frontend service method to fetch analytics data from a new `GET /users/me/analytics` endpoint.

**Resources Affected:**
- `backend/app/api/jobs.py` — add rate-limiting logic to swipe endpoint
- `backend/app/api/users.py` — add `/me/swipe-stats` and `/me/analytics` endpoints
- `frontend/src/app/features/swipe/swipe.component.ts` — add counter, disable logic, modal
- `frontend/src/app/features/swipe/swipe.component.html` — UI for counter and limit modal
- `frontend/src/app/features/dashboard/` — add analytics widget
- `frontend/src/app/core/services/job.service.ts` — add `getSwipeStats()` method

---

### Goal 6 — PostgreSQL Migration & Production Hardening

| Field | Details |
|:---|:---|
| **Goal** | Migrate from SQLite to PostgreSQL and add essential security measures |
| **Expected Duration** | Week 3 (Days 16–20) |
| **Short Description** | Switch to PostgreSQL with pgvector support, add rate limiting, file validation, and environment-based configuration |

**Long Description:**
The app currently runs on SQLite, which cannot handle concurrent users and lacks the `pgvector` extension needed for semantic job matching. We will set up a local PostgreSQL instance (via Docker), update the connection config to use it by default, and generate fresh Alembic migrations. With Postgres in place, we will enable the `embedding_vector` column using `pgvector` and implement cosine-similarity job ranking. On the security side, we will add file-type validation (magic number checks) on resume uploads, rate limiting via `slowapi`, and ensure all sensitive config (API keys, secrets) comes from environment variables with no defaults in code.

**Game Plan:**
1. Create a `docker-compose.yml` with PostgreSQL 16 + pgvector extension for local development.
2. Update `backend/app/core/config.py` to default to the Postgres connection string instead of SQLite.
3. Generate and run Alembic migrations against the new Postgres database.
4. Enable the `embedding_vector` column in `Resume` model using `pgvector`'s `Vector` type.
5. Implement cosine-similarity matching in `job_ingestion.py` to rank jobs by resume embedding proximity.
6. Add `slowapi` rate limiting middleware to `main.py` (global 100 req/min, per-user 30 req/min).
7. Add magic-number file validation in `resume.py` to verify uploaded files are genuine PDF/DOCX.
8. Audit and remove all hardcoded secrets from `config.py`; ensure `.env` is the sole source.
9. Create a `Dockerfile` for the backend to prepare for future deployment.

**Resources Affected:**
- `docker-compose.yml` — new file
- `backend/Dockerfile` — new file
- `backend/app/core/config.py` — update database_url default
- `backend/app/models.py` — enable `embedding_vector` with pgvector
- `backend/app/main.py` — add rate limiting middleware
- `backend/app/api/resume.py` — add file validation
- `backend/app/services/job_ingestion.py` — add embedding-based ranking
- `backend/alembic/` — new migration scripts
- `backend/requirements.txt` — add `slowapi`, `python-magic`

---

### Phase 2 Summary Timeline

| Week | Goals | Key Deliverables |
|:-----|:------|:-----------------|
| **Week 1** (Days 1–7) | Goal 1 (Resume + Cover Letter), Goal 2 start (Automation) | Real PDF/DOCX parsing, GPT cover letters, Playwright scaffolding |
| **Week 2** (Days 8–14) | Goal 2 finish (Automation), Goal 3 (Dashboard), Goal 4 start (Gmail) | Working auto-apply, Kanban board, Gmail OAuth consent |
| **Week 3** (Days 15–21) | Goal 4 finish (Gmail), Goal 5 (Swipe Limits), Goal 6 (Postgres + Security) | Email status detection, rate limits, PostgreSQL migration, Dockerfile |

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
| 2026-01-27 | Integration & UX Polish | **TheirStack Integration**: Integrated external job search API to fetch real jobs tailored to user profile. <br> **Account Deletion**: Added comprehensive account deletion (cascades to all data). <br> **UX**: Improved Swipe card layout with badges, truncated descriptions, and external apply links. Added user dropdown in navbar. |
| 2026-02-13 | Phase 2 Roadmap | Added a comprehensive 3-week Phase 2 roadmap to `README.md` covering 6 goals: real resume parsing & AI cover letters, Playwright auto-apply, Kanban dashboard redesign, Gmail status tracking, daily swipe limits with analytics, and PostgreSQL migration with security hardening. |
| 2026-02-13 | Goal 1: Resume Parsing & Cover Letters | **Resume Parser**: Rewrote `resume_parser.py` with real PDF (PyPDF2) and DOCX (python-docx) text extraction. <br> **Cover Letter**: Rewrote `cover_letter.py` to generate tailored letters via OpenAI GPT-4o-mini with graceful fallback. <br> **Embeddings**: Created `embedding.py` service using OpenAI `text-embedding-3-small` (1536-dim vectors stored as JSON in SQLite). <br> **Config**: Added `OPENAI_API_KEY` and `OPENAI_EMBEDDING_MODEL` settings; moved `THEIRSTACK_API_KEY` from hardcoded default to `.env`. |
| 2026-02-15 | Goal 3: Dashboard Redesign (Kanban Board) | **Kanban Board**: Replaced flat HTML table with a 5-column Kanban board (Pending, Applied, Interview, Offer/Other, Rejected) using Angular CDK `DragDropModule`. <br> **Drag-and-Drop**: Cards can be dragged between columns to update status via new `PATCH /applications/{id}/status` endpoint. <br> **ApplicationCardComponent**: New reusable card with company avatar, status badge, date, external link, and manual status dropdown. <br> **Filtering & Sorting**: Search by company/role and toggle sort (newest first vs. alphabetical). <br> **Backend**: Added PATCH endpoint with ownership validation and `ApplicationStatusEvent` audit trail. |

## License

Proprietary.

## Contact

Nabeel Rahman - [nabeel.a.rahman64@gmail.com](mailto:nabeel.a.rahman64@gmail.com)
