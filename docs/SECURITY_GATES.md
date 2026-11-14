# Security and privacy gates (blocking by default)
Reference: OWASP ASVS 5.0, risk-based L2 as a working target (not certification), OWASP Top 10, India DPDP Act and applicable phased 2025 Rules. Obtain professional security/legal review before a public service handling real personal data or accepting payment.

## Zero-trust developer agent
- No production accounts, payment credentials or private user data accessible to coding agent.
- Hard file scope for ordinary work; controller, security policy, CI, authentication, authorization, IaC and billing require human-reviewed PR.
- Three maximum repair cycles; stop on repeated unchanged findings, missing reviewer signal, new unknown commits, and security check failures.
- Never auto-resolve CodeRabbit threads just because the check run is green; require evidence that a finding was addressed.
- Restrict GitHub token scope and protect main with required checks, conversation resolution and non-bypassable policy for normal agent credentials.

## Application controls
- Anonymous read-only search; account required for user data.
- Secure, preferably managed authentication when public; password hashing Argon2id if passwords managed internally; HttpOnly Secure SameSite cookies, CSRF protection, MFA for admin, rate limits, session expiry and rotation.
- Tenant/user authorization on every private object and API; mandatory object-level access tests.
- Parameterized SQL, output encoding, HTML sanitation for job description, security headers, CSP and input schema validation.
- Resume PDF MIME/size limits, malware scan where available, no macros/scripts execution, sandboxed parser, no public URLs, deletion controls.
- Encryption in transit; encrypted disks/backups and protected keys; no secrets in repository, logs, analytics or third-party AI.
- SSRF defenses for ingestion; allowlisted source domains, redirect/timeouts/size limits, safe outbound fetch; respect provider terms and rate limits.
- No profile/ad targeting by default. Any future ads/payment requires new consent/data flow/security review and separate, isolated integration.
- Audit login, administrative changes, deletion requests and security events without logging sensitive content.

## CI gates
1. Python + TypeScript lint and formatting, static type checks.
2. Unit/integration tests + actual unittest/pytest discovery assertion.
3. API authorization isolation tests, injection cases, file upload security tests.
4. Dependency audit and license review; secret scanning; CodeQL for public repo; gitleaks; Semgrep (where compatible).
5. Container scanning (Trivy) when containers used; SAST results not ignored.
6. Build/reproducibility, migration smoke test, E2E test on synthetic user accounts.
7. CodeRabbit review complete for exact HEAD and threads resolved with evidence; branch rules enforce checks.

## Release gates
- Local friend testing only with synthetic data until authorization and privacy gates pass.
- Real-user public beta only after backup/restore drill, abuse controls, privacy notice, deletion/export functionality and independent human threat review.
- Payments or ads not in MVP. PCI scope should be minimized with external hosted checkout if ever introduced; never store full card details.
- No honest engineering process can guarantee '200/100' security; defects remain possible. The release threshold is demonstrable controls, tests and independent review, not a numeric promise.
