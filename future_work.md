# Jinder: Future Work & Agent Prompts

This document outlines the roadmap for moving Jinder from MVP to a production-ready application. Each section includes a detailed prompt that can be fed to an AI agent to execute the task.

---

## 1. Fully Integrate Google OAuth

**Current Status:** The MVP uses a mock login flow on the frontend and a bypassed dependency on the backend.
**Goal:** Implement real Google Sign-In, verify tokens on the backend, and create/update users securely.

### Agent Prompt
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

---

## 2. Fully Integrate Job Search API

**Current Status:** The `job_ingestion.py` service generates mock job data.
**Goal:** Integrate a real job search API (e.g., Indeed, LinkedIn, or a rapidapi aggregator) to fetch real listings.

### Agent Prompt
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

---

## 3. Implement Job Application Automation

**Current Status:** The `automation.py` service is a stub that waits 5 seconds and marks the application as "APPLIED".
**Goal:** Use Playwright/Selenium to actually navigate to job URLs and fill out forms.

### Agent Prompt
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

---

## 4. Add Swipe Limits

**Current Status:** Users can swipe indefinitely.
**Goal:** Limit users to 10 right swipes (applications) per day to manage costs/rate limits.

### Agent Prompt
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

---

## 5. Improve Application Status UI

**Current Status:** A basic HTML table.
**Goal:** A Kanban-style board or a more visual timeline view.

### Agent Prompt
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

---

## 6. Proper Database Integration

**Current Status:** Using SQLite for local dev; Models use JSON instead of ARRAY.
**Goal:** Migrate to PostgreSQL for production, utilizing `pgvector` for embeddings.

### Agent Prompt
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

---

## 7. Security Concerns

**Current Status:** Basic JWT, no rate limiting, file upload not sanitized.
**Goal:** Harden the application.

### Agent Prompt
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

---

## 8. Scalability

**Current Status:** Monolithic FastAPI app.
**Goal:** Prepare for high load.

### Agent Prompt
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

---

## 9. Production Deployment

**Current Status:** Local `uvicorn` and `ng serve`.
**Goal:** Live URL.

### Agent Prompt
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
