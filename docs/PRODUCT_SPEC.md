# CareerPilot — Product specification v0.1
Date: 2026-11-14
Status: design, not deployed
Audience: India-based technology job seekers, starting with entry-level to mid-career roles.

## Product promise
Find genuine jobs from verifiable employer career pages and permitted feeds, understand why each matches a resume, and track applications, without a mandatory paid subscription.

## MVP user journeys
1. Browse jobs without creating an account; filter by India city, hybrid/remote/on-site, role, experience, date, source, and known salary.
2. Open a result with company, original job URL, source, last-verified time, and clearly labeled known/unknown fields.
3. Create an account only to save jobs, manage application status, and store a resume.
4. Upload PDF resume with explicit consent, parse in an isolated process, display extracted profile for correction, delete original uploaded file after processing unless retention was explicitly chosen.
5. See transparent rule-based match score with evidence, missing skills and uncertainties; no invented salary or 'guaranteed ATS score'.
6. Track application status manually: saved, applied, screening, interview, offer, rejected/withdrawn.
7. Export all user profile, saved jobs and application records; delete user account and associated data.

## MVP exclusions
No auto-applying; no unapproved scraping, CAPTCHA circumvention, bulk recruiter messaging, payments, advertisements, or cloud-hosted user resume AI processing. No universal coverage claim.

## Functional modules
- Jobs: source registry, ingestion, normalization, deduplication, expiration, original application URLs.
- Search: PostgreSQL text search with indexed structured filters, pagination and sorting.
- Identity: user registration and secure session management; anonymous browse.
- Resumes: private upload, text extraction, editable candidate skills, versioning and export.
- Matching: explainable weighted matching with versioned scoring rules and explicit uncertainty.
- Tracker: user-scoped records, notes and status history.
- Admin: trusted source approvals, ingestion health, abuse reports, audit events.

## Core acceptance examples
- A user cannot read or modify another user's resume, job tracker or private notes even if IDs are guessed.
- A source failure does not erase previously verified jobs or make expired jobs appear current.
- Missing compensation is represented as `unknown`; it is not treated as zero or estimated without a label.
- Deletion removes personal files and database associations from live systems; backup retention is disclosed and enforced.
- Jobs always link to the originating employer posting when available.
- Baseline search, save, match and tracker work with AI services disabled.

## Success metrics (targets for pilot, not claims)
- 25 verified India-targeted employer source configurations.
- >= 95% of displayed jobs point to a retrievable original URL during spot checks.
- 0 confirmed cross-user data access in automated isolation tests.
- 5 friends successfully search, track and export their own data.
- No paid infrastructure required during local prototype.
