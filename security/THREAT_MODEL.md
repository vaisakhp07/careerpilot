# CP-001 threat model (draft)
**Assets:** public job listings, source registry, future profiles/resumes, service credentials, Github PR authority. **Trust boundaries:** browser↔API, API↔DB, ingestion↔external ATS, CI↔GitHub, LLM↔generated files and review text.

## Current controls
- Anonymous read-only API; NO private user endpoints or uploads exist.
- SQLite/SQLAlchemy parameters, bounded pagination, validated mode, explicit CORS origins, local bind.
- Demo-only postings marked; no unsanctioned fetching during local bootstrap.
- Secret files excluded from Git, workflow has read-only content permission.

## Open / blocking before public users
- Use managed authentication or audited sessions, per-user access checks, CSRF, abuse controls; no direct public launch before tests.
- Dedicated isolated ingestion worker, allowlisted URLs and blocked cross-origin redirects.
- Resume scanning, document-parser sandbox, content limits and private object store.
- SQL migrations, encryption/key management, observability without PII, rate limits, user deletion/export.
- Trusted agent separated from build-test sandbox, protected-policy changes require approval.
- Dependency lockfiles + auditing, CodeQL, secret scan and security regression suite.
- Real backup encryption, offsite replica, and restore drill.

No promise of perfect security or current ASVS L2 compliance.
