# Jinder - Tinder for Jobs

Jinder is a web application that simplifies the job application process using a "swipe" interface. It automates job discovery, matching, application submission, and status tracking — all powered by AI.

## Table of Contents
1. [Setup](#setup)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Frontend Development](#frontend-development)
5. [Phase 2 — Roadmap & Progress](#phase-2--roadmap--progress)
6. [Future Work](#future-work)
7. [Original Requirements & Analysis](#original-requirements--analysis)
8. [Change Log](#change-log)
9. [License](#license)

---

## Setup

### Prerequisites

| Dependency | Version | Purpose |
|:-----------|:--------|:--------|
| **Python** | 3.10+ | Backend runtime |
| **Node.js** | 18+ | Frontend tooling |
| **npm** | 9+ | Frontend package manager |
| **Angular CLI** | 18.x | `npm install -g @angular/cli` |
| **PostgreSQL** *(optional)* | 16+ | Production database (SQLite is used by default for local dev) |
| **Docker** *(optional)* | Latest | Required only if using PostgreSQL via `docker-compose` |

### Environment Variables

Before running, configure the backend `.env` file at `backend/.env`:

```env
# Required
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>
SECRET_KEY=<your-jwt-secret-key>

# Optional — enable AI features
OPENAI_API_KEY=<your-openai-api-key>
THEIRSTACK_API_KEY=<your-theirstack-api-key>

# Optional — switch to PostgreSQL (requires docker compose up -d)
# DATABASE_URL=postgresql://postgres:password@localhost:5432/jinder
```

> **Note:** Without `OPENAI_API_KEY`, resume embedding, cover letter generation, and Gmail email classification will use graceful fallbacks. Without `THEIRSTACK_API_KEY`, the job search API will not return real listings.

### Quick Start (One Command)

The easiest way to run both backend and frontend together:

```bash
chmod +x start_dev.sh
./start_dev.sh
```

This script will:
1. Create a Python virtual environment (if it doesn't exist)
2. Install backend dependencies
3. Start the FastAPI backend on `http://localhost:8000`
4. Install frontend dependencies
5. Start the Angular frontend on `http://localhost:4200`

Press `Ctrl+C` to stop all services.

### Manual Setup

#### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

#### Frontend

```bash
cd frontend
npm install
ng serve
```

The app will be available at `http://localhost:4200`.

### PostgreSQL Setup (Optional)

By default, Jinder uses SQLite for zero-config local development. To switch to PostgreSQL with pgvector support:

```bash
# Start PostgreSQL via Docker
docker compose up -d

# Then uncomment DATABASE_URL in backend/.env:
DATABASE_URL=postgresql://postgres:password@localhost:5432/jinder
```

---

## Features

### Core Features (Phase 1 — MVP)
- **Google Sign-In** — OAuth 2.0 authentication with server-side token verification and JWT session management
- **Onboarding Wizard** — Step-by-step profile setup: name, desired roles, locations, salary, seniority, remote preference, experience, education
- **Resume Upload** — Drag-and-drop or file-input upload with PDF/DOCX support and file-type validation (magic byte checks)
- **Smart Job Matching** — Jobs fetched from TheirStack API based on user profile; ranked by AI embedding cosine-similarity when available
- **Swipe Interface** — Tinder-style card deck with swipe left (skip) / swipe right (apply) gestures; includes job badges, truncated descriptions, and external links
- **Applications Dashboard** — Track application statuses in real-time
- **Account Management** — User dropdown in navbar, comprehensive account deletion with cascade

### Phase 2 Features (Completed)
- **Real Resume Parsing** — PDF text extraction via PyPDF2, DOCX via python-docx; parsed text stored in database
- **AI Embeddings** — Resume text embedded via OpenAI `text-embedding-3-small` (1536-dim vectors) for semantic job matching
- **AI Cover Letters** — GPT-4o-mini generates tailored cover letters from resume + profile + job description (with graceful fallback)
- **Browser Automation (Playwright)** — Headless Chromium navigates to job URLs, detects form fields, fills from user profile, uploads resume, captures screenshots; supports dry-run mode
- **Form Detection Engine** — Heuristic-based detection of name, email, phone, resume upload, cover letter, LinkedIn, and address fields; plus CAPTCHA detection
- **Pause & Resume Automation** — When the bot encounters unfillable fields, it saves progress and pauses with `USER_INPUT_NEEDED` status; users provide missing values inline and resume automation
- **Kanban Dashboard** — 5-column drag-and-drop board (Pending, Applied, Interview, Offer/Other, Rejected) with Angular CDK `DragDropModule`; includes filtering by company/role and sort controls
- **Gmail Integration** — OAuth 2.0 `gmail.readonly` scope; background polling every 15 minutes; GPT-4o-mini classifies recruiter emails; fuzzy company-name matching updates application statuses automatically
- **Rate Limiting** — `slowapi` middleware with configurable per-user and global limits
- **File Validation** — Magic byte verification on uploads to reject spoofed file extensions
- **Cosine-Similarity Ranking** — NumPy-based embedding comparison ranks jobs by resume relevance

---

## Tech Stack

| Layer | Technology | Details |
|:------|:-----------|:--------|
| **Frontend** | Angular 18 | TypeScript, Angular CDK (drag-and-drop), RxJS |
| **Backend** | FastAPI | Python 3.10+, Pydantic, async-ready |
| **Database** | SQLite (dev) / PostgreSQL 16 (prod) | SQLAlchemy ORM, Alembic migrations, pgvector support |
| **AI / ML** | OpenAI | `text-embedding-3-small` for embeddings, GPT-4o-mini for cover letters & email classification |
| **Job API** | TheirStack | Real job listings based on role + location preferences |
| **Automation** | Playwright | Headless Chromium for auto-apply form filling |
| **Email** | Gmail API | OAuth 2.0, read-only scope, background polling via APScheduler |
| **Auth** | Google OAuth 2.0 | `google-auth` library, JWT sessions via `python-jose` |
| **Rate Limiting** | slowapi | Per-user and global request rate limiting |
| **Containerization** | Docker | Backend Dockerfile, docker-compose with PostgreSQL + pgvector |

---

## Frontend Development

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 18.2.4.

| Command | Description |
|:--------|:------------|
| `ng serve` | Dev server at `http://localhost:4200/` with live reload |
| `ng build` | Production build → `dist/` directory |
| `ng generate component <name>` | Scaffold a new component |
| `ng test` | Unit tests via Karma |
| `ng e2e` | End-to-end tests (requires e2e package) |
| `ng help` | CLI command reference |

---

## Phase 2 — Roadmap & Progress

Phase 1 delivered a working MVP: Google OAuth, user profile & resume upload, TheirStack job API integration, a swipe interface, and a basic applications dashboard. Phase 2 focused on replacing every remaining stub with production-quality implementations and polishing the user experience so the app is genuinely useful end-to-end.

### Progress Overview

| # | Goal | Status | Summary |
|:--|:-----|:-------|:--------|
| 1 | Resume Parsing & AI Cover Letters | ✅ Completed | Real PDF/DOCX extraction, OpenAI embeddings, GPT-4o-mini cover letters |
| 2 | Browser Automation (Playwright) | ✅ Completed | Headless form filling, screenshot capture, pause & resume for unfillable fields |
| 3 | Dashboard Redesign (Kanban) | ✅ Completed | 5-column drag-and-drop board with filtering and sorting |
| 4 | Gmail Integration | ✅ Completed | OAuth consent, background polling, GPT email classification, auto status updates |
| 5 | Daily Swipe Limits & Analytics | 🔲 Not Started | 10-swipe/day cap, usage counter, weekly analytics widget |
| 6 | PostgreSQL & Production Hardening | ✅ Completed | Docker Compose, rate limiting, file validation, cosine-similarity ranking, Dockerfile |

---

### Goal 1 — Real Resume Parsing & AI-Powered Cover Letters ✅

| Field | Details |
|:---|:---|
| **Status** | Completed |
| **What was built** | Real PDF (PyPDF2) and DOCX (python-docx) text extraction; OpenAI `text-embedding-3-small` embeddings (1536-dim vectors stored as JSON); GPT-4o-mini cover letter generation with graceful fallback |

**Files changed:**
- `backend/app/services/resume_parser.py` — full rewrite with real extraction
- `backend/app/services/cover_letter.py` — GPT-4o-mini integration
- `backend/app/services/embedding.py` — new service for OpenAI embeddings
- `backend/app/models.py` — `embedding_vector` column on `Resume`
- `backend/app/core/config.py` — `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL` settings

---

### Goal 2 — Browser Automation for Auto-Apply (Playwright) ✅

| Field | Details |
|:---|:---|
| **Status** | Completed |
| **What was built** | Playwright headless Chromium engine that navigates to job URLs, detects form fields via heuristics, fills from user profile, uploads resume, captures screenshots. Includes `MANUAL_INTERVENTION_REQUIRED` and `USER_INPUT_NEEDED` statuses with inline form completion. Default `DRY_RUN=True` mode. |

**Files changed:**
- `backend/app/services/automation.py` — full rewrite with Playwright
- `backend/app/services/form_detector.py` — new heuristic form field detector
- `backend/app/models.py` — `screenshot_path`, `cover_letter_text`, `automation_state` columns; `MANUAL_INTERVENTION_REQUIRED` and `USER_INPUT_NEEDED` statuses
- `backend/app/api/application.py` — `POST /applications/{id}/provide-fields` endpoint
- Frontend Kanban board updated with "Needs Input" column and inline field forms

---

### Goal 3 — Dashboard Redesign (Kanban Board) ✅

| Field | Details |
|:---|:---|
| **Status** | Completed |
| **What was built** | 5-column Kanban board (Pending, Applied, Interview, Offer/Other, Rejected) using Angular CDK `DragDropModule`. Drag-and-drop moves cards between columns via `PATCH /applications/{id}/status`. ApplicationCardComponent with company avatar, status badge, date, and external link. Search by company/role, sort by newest or alphabetical. |

**Files changed:**
- `frontend/src/app/features/dashboard/` — full rewrite
- `frontend/src/app/features/dashboard/application-card/` — new component
- `backend/app/api/application.py` — `PATCH /{id}/status` endpoint with ownership validation and audit trail

---

### Goal 4 — Gmail Integration for Status Tracking ✅

| Field | Details |
|:---|:---|
| **Status** | Completed |
| **What was built** | Server-side Gmail OAuth 2.0 flow for `gmail.readonly` scope. Background scheduler (APScheduler) polls all connected users every 15 minutes. GPT-4o-mini classifies emails by status (confirmation, interview invite, rejection, follow-up) with confidence threshold ≥ 0.7. Fuzzy Jaccard company-name matching links emails to applications. Status priority prevents downgrades. Onboarding Step 3 "Connect Gmail" with connect/skip/disconnect. |

**Files changed:**
- `backend/app/services/gmail.py` — full rewrite with Gmail API client
- `backend/app/api/gmail.py` — connect/callback/status/disconnect/poll endpoints
- `backend/app/models.py` — `gmail_refresh_token`, `gmail_connected_at` on `User`
- `backend/app/core/config.py` — `GMAIL_REDIRECT_URI`, `GMAIL_SCOPES`
- `frontend/src/app/features/onboarding/` — Gmail consent step
- `frontend/src/app/core/services/` — `GmailService`

---

### Goal 5 — Daily Swipe Limits & Usage Analytics 🔲

| Field | Details |
|:---|:---|
| **Status** | Not Started |
| **Goal** | Limit right-swipes to 10 per day and show usage stats on the dashboard |

**Planned work:**
- Server-side swipe count check (last 24 hours) returning 429 when limit reached
- `GET /users/me/swipe-stats` endpoint for remaining count and reset time
- Frontend counter, disabled Apply button at limit, reset countdown modal
- Weekly analytics widget on dashboard (application chart, top companies, success/rejection ratio)

---

### Goal 6 — PostgreSQL Migration & Production Hardening ✅

| Field | Details |
|:---|:---|
| **Status** | Completed |
| **What was built** | `docker-compose.yml` with PostgreSQL 16 + pgvector. Backend `Dockerfile`. `DATABASE_URL` env var with SQLite fallback. `slowapi` rate limiting middleware (30 req/min per-user, 100 req/min global). Magic byte file validation on uploads. NumPy cosine-similarity ranking for embedding-based job sorting. All secrets sourced from `.env`. |

**Files changed:**
- `docker-compose.yml` — new
- `backend/Dockerfile` — new
- `backend/app/core/config.py` — `DATABASE_URL`, rate limit settings
- `backend/app/main.py` — rate limiting middleware
- `backend/app/api/resume.py` — file validation
- `backend/app/services/job_ingestion.py` — embedding-based ranking
- `backend/requirements.txt` — `slowapi`, `numpy`, `pgvector`

---

### Phase 2 Summary Timeline

| Week | Goals | Key Deliverables |
|:-----|:------|:-----------------|
| **Week 1** (Days 1–7) | Goal 1 (Resume + Cover Letter), Goal 2 start (Automation) | Real PDF/DOCX parsing, GPT cover letters, Playwright scaffolding |
| **Week 2** (Days 8–14) | Goal 2 finish (Automation), Goal 3 (Dashboard), Goal 4 start (Gmail) | Working auto-apply, Kanban board, Gmail OAuth consent |
| **Week 3** (Days 15–21) | Goal 4 finish (Gmail), Goal 5 (Swipe Limits), Goal 6 (Postgres + Security) | Email status detection, rate limits, PostgreSQL migration, Dockerfile |

---

## Future Work

These items remain on the roadmap beyond Phase 2:

### Daily Swipe Limits & Usage Analytics (Phase 2, Goal 5)
- Limit users to 10 right swipes per day (server-side enforcement)
- Frontend counter + disabled button + countdown modal
- Weekly analytics dashboard widget

### Security Hardening
- S3 integration for resume/screenshot storage (replacing local `uploads/` directory)
- ClamAV or equivalent malware scanning on uploads
- Encrypted PII fields at rest
- Input sanitization audit

### Scalability
- Move automation and job ingestion to a task queue (Celery + Redis or AWS SQS)
- Redis caching for user sessions and job recommendations
- Database connection pooling (pgbouncer)

### Production Deployment
- Dockerfiles for both backend and frontend (Nginx for static serving)
- AWS infrastructure: ECS Fargate (backend), S3 + CloudFront (frontend), RDS (PostgreSQL), ElastiCache (Redis)
- CI/CD via GitHub Actions (build → ECR → auto-deploy to ECS)
- Live URL

---

## Original Requirements & Analysis

You are a senior full-stack engineer and solution architect.
Your task is to design and implement an MVP for Jinder, a "Tinder for jobs" web application.

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
3. System uses OpenAI embeddings to analyze the resume and build a semantic representation of the user's skills, experience, and education.
4. System recommends job categories/fields first (e.g., "Backend developer", "Data analyst", "Product manager") based on resume + profile.
5. **User can:**
   - Select categories they like.
   - Explicitly mark categories they don't want ("not interested in sales roles," etc.).
6. System pulls jobs from TheirStack API, ranks them using a hybrid scoring approach, and presents them as swipeable cards (desktop web).
7. User can filter jobs with a filter panel.
8. **For each job:**
   - Swipe left → skip.
   - Swipe right → automatically apply (no extra confirmation pop-up).
9. **System generates a tailored cover letter using LLMs based on:**
   - Job title
   - Job description
   - User's resume
   - User's profile preferences
10. System uses browser automation to fill application forms on the job's external site.
11. System records the application in the database.
12. **A dedicated dashboard page lets users see:**
    - Which jobs they've applied to
    - Statuses and a status timeline per job
13. **System requests read-only access to the user's Gmail and periodically:**
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
- **Framework**: FastAPI.
- **Database**: PostgreSQL (with SQLite fallback for local dev).
- **Email integration**: Gmail API with OAuth 2.0, read-only scope.
- **Resume and job embeddings**: OpenAI `text-embedding-3-small`.
- **Job Source**: TheirStack API. Designed as a pluggable service.
- **Browser Automation**: Playwright (Python, headless Chromium).

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
- **Onboarding flow**: Sign-in, Resume upload, Profile questions, Gmail consent, Category selection.
- **Job browsing / swipe page**: Tinder-style card deck. Swipe controls. Filters panel.
- **Applications dashboard**: Kanban board with drag-and-drop status management. Detail view with timeline.
- **Settings / account page**: Update profile, reconnect Gmail, view resume.
- **Legal pages**: Privacy Policy, Terms of Use.

### 5. Security, Privacy, and Compliance

- HTTPS everywhere.
- Store PII and resume files securely (Encrypted S3, RDS).
- Secure secrets management.
- Role-based access (user can only see their own data).
- Read-only Gmail scopes.
- User mechanisms for revoking access and deleting account.

---

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
| 2026-02-15 | Goal 2: Browser Automation (Playwright) | **Automation Engine**: Rewrote `automation.py` with Playwright headless Chromium — navigates to job URLs, detects form fields, fills from user profile, uploads resume, captures screenshots. <br> **Form Detector**: Created `form_detector.py` with heuristic-based field detection (name, email, phone, resume upload, cover letter, LinkedIn, address) plus CAPTCHA and submit button detection. <br> **New Status**: Added `MANUAL_INTERVENTION_REQUIRED` to `ApplicationStatus` for CAPTCHAs, missing forms, and complex multi-step applications. <br> **Model Updates**: Added `screenshot_path` and `cover_letter_text` columns to `Application`. <br> **Dry Run Mode**: Default `DRY_RUN=True` fills forms without clicking Submit; set to `False` for production. <br> **Frontend**: Updated Kanban board and card component for new status with warning indicator and direct apply link. |
| 2026-02-15 | Goal 2 Enhancement: User Input for Unfillable Fields | **Pause & Resume**: When the bot encounters fields it can't fill (custom employer questions, missing profile data), it saves progress and pauses instead of giving up. <br> **New Status**: Added `USER_INPUT_NEEDED` to `ApplicationStatus` with `automation_state` JSON column storing filled fields, missing fields, and page URL. <br> **New Kanban Column**: "✍️ Needs Input" column shows applications awaiting user input. <br> **Inline Form**: Application cards show dynamically-rendered input fields for each missing field with labels and types, plus a "🚀 Resume Application" button. <br> **New API**: `POST /applications/{id}/provide-fields` accepts user-provided values and triggers `resume_automation()` as a BackgroundTask. <br> **Form Detector**: Added `get_all_visible_inputs()` to catch custom fields not matched by pattern detection. |
| 2026-02-17 | Goal 4: Gmail Integration for Status Tracking | **Gmail OAuth**: Server-side OAuth 2.0 flow for `gmail.readonly` scope with connect/callback/status/disconnect/poll endpoints. <br> **Gmail Service**: Full rewrite of `gmail.py` — `build_gmail_service()` (refresh token → client), `fetch_recent_emails()` (date-filtered search with recruiter domain + subject pattern filtering), `classify_email()` (GPT-4o-mini classification returning status/confidence/company_name), `match_to_application()` (fuzzy Jaccard company-name matching). <br> **Background Scheduler**: APScheduler `BackgroundScheduler` polls all Gmail-connected users every 15 minutes via `poll_all_users()`. <br> **Status Priority**: Won't downgrade statuses (e.g., won't go from INTERVIEW_INVITED back to APPLIED), only updates when confidence ≥ 0.7. <br> **Onboarding**: New Step 3 "Connect Gmail" with privacy note (read-only), connect/skip buttons. Profile view shows Gmail badge + disconnect option. <br> **Frontend**: New `GmailService` (connect, status, disconnect, poll). <br> **Model**: Added `gmail_refresh_token` and `gmail_connected_at` columns to `User`. |
| 2026-02-18 | Goal 6: PostgreSQL Migration & Production Hardening | **Docker Compose**: Created `docker-compose.yml` with PostgreSQL 16 + pgvector (deferred until Docker installed). <br> **Dockerfile**: Backend Dockerfile with Python 3.12, system deps, Playwright chromium. <br> **Config**: `DATABASE_URL` env var as primary DB override; SQLite fallback preserved; `RATE_LIMIT_GLOBAL` + `RATE_LIMIT_PER_USER` settings; removed `SQLALCHEMY_DATABASE_URI`. <br> **Rate Limiting**: slowapi middleware — 30 req/min per-user (by IP), with `RateLimitExceeded` handler. <br> **File Validation**: Magic byte checks on resume uploads — verifies PDF (`%PDF`) and DOCX (`PK\x03\x04`) headers; rejects renamed files even if extension matches. <br> **Cosine-Similarity Ranking**: `rank_jobs_by_embedding()` using numpy — compares user's resume embedding against job description embeddings, returns jobs sorted by similarity. Works with both SQLite JSON and pgvector. <br> **Secrets Audit**: `.env` is sole source for all sensitive config; commented `DATABASE_URL` ready for Postgres switch. |
| 2026-02-24 | README Overhaul | Full restructure of `README.md`: moved Setup to top with prerequisites table, env var reference, and one-command quick start; updated Features to reflect all completed Phase 2 work; corrected Tech Stack to match actual dependencies (Angular 18, TheirStack, GPT-4o-mini, text-embedding-3-small); added Phase 2 progress overview table with completion statuses; condensed Frontend Development into a command table; trimmed Future Work to only remaining items; updated Original Requirements to reference TheirStack and Kanban dashboard. |
| 2026-03-09 | Frontend Visual Redesign | **Design System**: New CSS custom properties with indigo/violet palette, gradient tokens, shadow scale, animation utilities, global scrollbar styling. <br> **Navbar**: Glassmorphism sticky bar with `backdrop-filter`, mobile hamburger slide-in menu, SVG nav icons, pill-shaped active link indicators, gradient logo text, animated user dropdown with avatar. <br> **Landing Page**: Dark gradient hero (`--gradient-hero`) with animated badge, gradient heading text, 3-column glassmorphism feature cards with floating icon animation, responsive stacking. <br> **Login Page**: Dark gradient background with glassmorphism card, ⚡ logo, gradient-text branding, centered Google sign-in. <br> **Swipe Page**: Progress dots indicator, meta grid with emoji icons and bordered cells, gradient "Apply" button + outlined "Skip" with hover-fill, card entrance animation, polished empty state. <br> **Onboarding/Profile**: Visual 4-step progress bar (dots + connecting lines with active/completed states), 2-column form grid, section dividers with horizontal rule + label, drag-and-drop upload area, indigo-accented section groups, profile view with grid layout. <br> **Dashboard**: Summary stats bar with colored left-border cards above kanban, SVG search icon in pill-shaped input, refined kanban columns with hover borders, indigo-themed drag-and-drop placeholders, animated empty/loading states. <br> **Application Card**: Design-system CSS tokens, indigo hover glow on external link, pill-shaped status badges, consistent border-radius and transition timing. <br> **SEO**: Updated `<title>` and added meta description. |
| 2026-03-09 | Deployment Setup | **GitHub Pages**: GitHub Actions workflow (`.github/workflows/deploy-frontend.yml`) auto-builds Angular and deploys to `gh-pages` branch on push; copies `index.html` to `404.html` for SPA routing. <br> **Render Backend**: `render.yaml` blueprint for Docker-based backend deployment; secrets set in dashboard only. <br> **Environment Config**: Angular `environment.ts`/`environment.prod.ts` files with `fileReplacements` in `angular.json`; all 5 services (`auth`, `application`, `job`, `profile`, `gmail`) updated from hardcoded `localhost:8000` to `environment.apiUrl`. <br> **Backend Config**: Added `FRONTEND_URL`, `BACKEND_URL` settings; `cors_origins` property auto-includes frontend URL; `gmail_redirect_uri` property derives from `BACKEND_URL`; fixed `gmail.py` hardcoded redirect. |

## License

Proprietary.

## Contact

Nabeel Rahman - [nabeel.a.rahman64@gmail.com](mailto:nabeel.a.rahman64@gmail.com)
