You are a senior full-stack engineer and solution architect.
Your task is to design and implement an MVP for Jinder, a “Tinder for jobs” web application.

Jinder lets users:

Sign in with Google

Upload a resume

Answer a few questions to build a profile

Get suggested job categories and job listings

Swipe left/right on job cards:

Left = skip

Right = auto-apply using browser automation and an AI-generated cover letter

Track applications and statuses in a dashboard

Allow the system to read their Gmail (read-only) to automatically detect updates (thank-you emails, interview invites, rejections, follow-ups, etc.).

Your output should be:

A well-structured codebase

Infrastructure setup notes (or IaC if possible)

Clear documentation of APIs and flows

Focus on a working MVP first, but structure the code so premium features could be added later.

1. High-Level Requirements

User flow summary

User signs in via Google Sign-In.

On first login, user is asked to:

Upload one resume (PDF/DOCX). Only a single resume is supported in this MVP.

Answer profile questions: desired roles, locations, salary expectations, seniority, remote/on-site preference, etc.

System uses OpenAI embeddings to analyze the resume and build a semantic representation of the user’s skills, experience, and education.

System recommends job categories/fields first (e.g., “Backend developer”, “Data analyst”, “Product manager”) based on resume + profile.

User can:

Select categories they like.

Explicitly mark categories they don’t want (“not interested in sales roles,” etc.).

System pulls jobs from Indeed, ranks them using a hybrid scoring approach, and presents them as swipeable cards (desktop web).

User can filter jobs with a filter panel.

For each job:

Swipe left → skip.

Swipe right → automatically apply (no extra confirmation pop-up).

System generates a tailored cover letter using LLMs based on:

Job title

Job description

User’s resume

User’s profile preferences

System uses browser automation to fill application forms on the job’s external site.

System records the application in the database.

A dedicated dashboard page lets users see:

Which jobs they’ve applied to

Statuses and a status timeline per job

System requests read-only access to the user’s Gmail and periodically:

Reads new emails

Detects job-related messages (thank-you, interview invites, rejections, recruiter follow-ups, general status updates)

Updates the application status timeline accordingly

Sends notifications by email and SMS.

Non-goals (for MVP)

No mobile-native app yet (later).

No multi-resume support (MVP = single resume).

No complex monetization or premium tiers in MVP.

No support for non-Gmail providers in MVP.

2. Tech Stack Constraints

Frontend

Framework: Angular (desktop-first design, but responsive enough).

Style:

Color palette: sky blue, a complementary darker blue, and white as primary UI colors.

Clean, modern, card-based UI for job swiping.

Features:

Google Sign-In button and flow integration.

Resume upload UI (drag-and-drop or simple file input).

Profile wizard (step-by-step).

Job browsing/swiping UI (Tinder-style deck).

Applied jobs dashboard and status timeline view.

Filter panel for:

Salary range

Remote/hybrid/on-site

Job title keywords

Seniority level

Company size

Location

Backend

Language: Python.

Framework: Prefer FastAPI (you may optionally include a small Flask adapter or note, but FastAPI should be the main HTTP API).

Database: PostgreSQL (hosted on AWS RDS, or equivalent).

Hosting: AWS (you may choose between ECS Fargate, EC2, or Lambda + API Gateway; choose a practical option and document it).

Email integration: Gmail API with OAuth 2.0, read-only scope.

SMS provider: You can choose a reasonable provider (e.g., Twilio or AWS SNS with SMS), but keep it abstracted.

Resume and job embeddings: Use OpenAI embeddings. Choose a current, cost-effective embedding model and document it (e.g., text-embedding model).

Store embedding vectors either via pgvector in PostgreSQL or an equivalent vector store you set up.

Job Source

Use Indeed as the job source.

Design the job ingestion layer as a pluggable service so additional sources (LinkedIn, Greenhouse, etc.) could be added in the future.

For MVP, pull job listings by:

Location

Job title keywords

Category

Remote/on-site

Salary range (if available from API)

Browser Automation

Implement an application automation worker using a browser automation framework (e.g., Playwright or Selenium for Python).

This worker should:

Open the job application URL.

Fill in fields (name, email, phone, etc.) from the user profile.

Fill in a generated cover letter into a free-text field where appropriate.

Upload the resume file (the single resume).

Submit the form.

Architecture:

Worker runs as a separate process/service from the main API, triggered via queue (SQS) or internal job scheduler if needed.

Application status should be updated when worker starts/completes with success/failure.

3. Core Functional Components & APIs

Design the backend and API in a modular way. At a minimum implement:

3.1 Authentication & Users

Google OAuth sign-in:

On first sign-in, create a user record in the database.

Store:

user_id

email

Google OAuth tokens/refresh tokens in a secure manner (for Gmail access).

Treat Google sign-in as email verification, but allow for a simple “Confirm account” UI step if needed.

3.2 User Profile & Resume

Models:

User

id

email

google_sub / provider_id

created_at

updated_at

UserProfile

user_id (FK)

name

desired_locations

desired_salary_range

desired_roles (array)

remote_preference (remote / hybrid / on-site)

seniority_preference

company_size_preferences

disallowed_categories (array: e.g., “sales”, “door-to-door”, etc.)

phone_number (for SMS)

other optional fields

Resume

user_id (FK)

file_path (S3 or similar)

raw_text

embedding_vector (via OpenAI embedding)

created_at

Endpoints:

POST /resume/upload

GET /profile

PUT /profile

Behavior:

On resume upload:

Store file securely (e.g., S3 with encryption).

Extract text from PDF/DOCX.

Call OpenAI embeddings API.

Store embedding vector in Postgres (with pgvector or equivalent).

Use embeddings later for job matching and cover letter generation.

3.3 Job Categories & Recommendations

Models:

JobCategory

id

name

description

UserCategoryPreference

user_id

category_id

liked (bool)

disliked (bool)

Endpoints:

GET /jobs/categories/recommendations

Use resume embedding + profile to suggest categories.

POST /jobs/categories/preferences

Accept likes/dislikes per category.

Logic:

Derive categories by matching resume embedding and profile to pre-defined category vectors or descriptions.

Allow user to mark categories as unwanted; filter those out in job searches.

3.4 Job Fetching & Matching

Models:

JobPosting

id

external_id (Indeed ID)

title

company_name

location

salary_range

description

employment_type (remote/hybrid/on-site)

seniority_level

company_size

url (application URL)

category_id

embedding_vector (optional; embedding of job description)

fetched_at

JobRecommendation

id

user_id

job_posting_id

match_score (float)

created_at

Logic (Hybrid scoring):

For each job:

Compute an LLM/embedding similarity between:

job description embedding

user resume embedding

Combine with rule-based constraints:

Required skills vs resume text

Location compatibility

Salary range vs desired salary

Remote/onsite preference

Match score = weighted combination of embedding similarity + rule checks.

Endpoints:

GET /jobs/recommendations

Supports filters: salary range, remote/hybrid/on-site, title keywords, seniority level, company size, location.

Returns a list of jobs ordered by match_score.

API should support a paginated “deck” of jobs to feed to the swipe UI.

3.5 Swiping & Applications

Models:

SwipeAction

id

user_id

job_posting_id

action (left/right)

created_at

Application

id

user_id

job_posting_id

resume_id

application_url

status (enum: PENDING_AUTOMATION, APPLIED, EMAIL_CONFIRMATION_RECEIVED, INTERVIEW_INVITED, REJECTED, FOLLOW_UP_RECEIVED, OTHER_UPDATE, FAILED)

created_at

updated_at

ApplicationStatusEvent

id

application_id

status

source (e.g., SYSTEM, GMAIL, USER)

message (optional human-readable note)

email_message_id (optional)

created_at

Endpoints:

POST /jobs/{job_id}/swipe

Payload: { "direction": "left" | "right" }

If right:

Create SwipeAction record.

Create Application with status PENDING_AUTOMATION.

Trigger automation worker to apply to the job.

GET /applications

Returns the list of applications for the user with:

job title

company

date applied

resume version used

application link

current status

GET /applications/{id}/timeline

Returns the ApplicationStatusEvents in chronological order.

3.6 Cover Letter Generation

Implement a service that, given:

Resume text

User profile data

Job title

Company name

Job description

Calls an OpenAI model to generate a concise, professional cover letter.

Return the generated text to the automation worker to paste into application forms.

3.7 Gmail Integration & Status Detection

Use Gmail API with OAuth 2.0, read-only scope.

Store tokens securely; implement token refresh.

Implement a background worker that:

Polls Gmail for new emails for each user on a schedule (e.g., every X minutes; design as cron/CloudWatch or queue-based).

Detects job-related emails via:

Sender domains (from job boards, company ATS).

Subject patterns (e.g., “Application received”, “Interview”, “We regret”, etc.).

Use an LLM classification step on email subject/body to label each email as one of:

APPLICATION_CONFIRMATION

INTERVIEW_INVITE

REJECTION

FOLLOW_UP

STATUS_UPDATE_OTHER

Maps emails back to a specific Application (e.g., using job title, company name, links inside the email, or metadata).

Creates ApplicationStatusEvent records and updates Application.status.

On status changes:

Send notification via:

Email

SMS

4. Frontend UX Requirements

Desktop-first Angular application

Pages:

Landing page

Branding for Jinder (sky blue / dark blue / white theme).

Short tagline and a “Sign in with Google” button.

Onboarding flow

Step 1: Google sign-in.

Step 2: Upload resume.

Step 3: Profile questions (roles, locations, salary, remote preference, etc.).

Step 4: Suggested categories; let user select preferred and mark some as “not interested.”

Job browsing / swipe page

Shows one main job card at a time (Tinder-style).

Card includes:

Company name

Job title

Location

Salary (if available)

Short description snippet

Match percentage (e.g., “87% match”)

“Show more” button that expands:

Full description

Additional metadata

Controls:

Swipe left/right (use buttons and/or drag gestures for desktop).

Filters panel (salary, location, remote/hybrid/on-site, seniority, company size, job title search).

Applications dashboard

Tabular or card view listing:

Job title

Company

Date applied

Resume version used (single resume for now)

Application link

Current status (human-readable)

Clicking into an application shows:

Full job details

Status timeline (ApplicationStatusEvents in order).

Settings / account page

View/update profile preferences.

Reconnect Gmail if needed.

View or re-upload resume (still single resume restriction).

Phone number for SMS notifications.

Legal pages

Privacy Policy page.

Terms of Use page.

Cookie consent banner and settings.

5. Security, Privacy, and Compliance

Use HTTPS everywhere.

Store PII and resume files securely:

Encrypted S3 bucket for resumes.

Encrypted RDS for PostgreSQL.

Store OAuth tokens and API keys in a secure secrets manager (e.g., AWS Secrets Manager or Parameter Store).

Implement role-based access at least at “user can only see their own data”.

Only request read-only Gmail scopes.

Implement a mechanism for:

User revoking Gmail access.

User deleting their account & associated data (at least basic handling).

Add visible links to Privacy Policy, Terms of Use, and Cookie policy on relevant pages.

6. Implementation Guidance & Deliverables

Core deliverables:

Backend code (FastAPI-based) with:

Auth endpoints & Google OAuth flow.

Profile/resume/job/application APIs.

Embedding and cover letter generation modules.

Gmail polling & classification module.

Job scraping/fetching module for Indeed.

Application automation worker module.

Frontend code (Angular) with:

All described pages and components.

The swipe deck UI and filters.

Dashboard and timeline.

Database schema (PostgreSQL) including:

Users, UserProfile, Resume, JobCategory, UserCategoryPreference, JobPosting, JobRecommendation, SwipeAction, Application, ApplicationStatusEvent (and any helper tables).

Basic infra/deployment notes on AWS:

How to deploy backend (e.g., ECS Fargate + ALB, or API Gateway + Lambda).

How to deploy Angular frontend (e.g., S3 + CloudFront).

How to provision PostgreSQL (RDS).

How to schedule workers (e.g., ECS scheduled tasks or Lambda for Gmail polling).

Documentation:

README with setup instructions.

API documentation (OpenAPI/Swagger for FastAPI).

Notes for environment variables and secrets.

Focus on bare-bones but real: the system should actually:

Let a test user sign in with Google.

Upload a resume.

Get basic category recommendations.

See some real job listings pulled from Indeed.

Swipe right/left.

Trigger at least a basic “fake” or test-mode automation for job application (full robust automation can be iterative).

Show an application dashboard with statuses and a timeline.

Use this spec as the source of truth. If any ambiguity remains (e.g., exact Indeed or Gmail API details), choose reasonable defaults and document your decisions clearly in the README.