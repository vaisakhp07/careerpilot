# Security gate implementation — maintainer-approved

This PR adds a *blocking* Security Gates workflow and Dependabot version-update configuration.
It does not change existing CI, CodeQL, branch rules or the autonomous agent's permissions.

## Gates in this phase
- Python dependency vulnerabilities: pip-audit (runtime dependencies)
- JavaScript dependencies: npm audit (including dev dependencies)
- Python high/critical static findings: Bandit
- Candidate hard-coded secrets: detect-secrets
- Existing: CodeQL (Python + JS/TS), CodeRabbit, unit tests, protected main
- Dependabot weekly update PRs: pip, npm, GitHub Actions

## Manual GitHub repository settings (one-time)
Repository Settings → Security and analysis / Advanced Security:
- Enable Dependabot alerts and Dependabot security updates
- Confirm secret scanning and push protection are enabled where available
- Keep CodeQL enabled (already working)

## Once this PR checks have actually run and pass
Add `security-gates` (GitHub Actions as source) to existing main ruleset.
Do NOT remove `validate`, `analyze (python)`, `analyze (javascript-typescript)`, `CodeRabbit`.

## Non-goals (must be built before real user data / monetization)
- User identity, authorization and session tests
- User data encryption, deletion/export, retention and consent
- Backups and tested restoration of user data
- Threat-model-driven dynamic API security tests and production penetration testing
- Artifact signing/provenance, SBOM publication, pinned-action SHAs and workflow lint
- Dedicated secure agent sandbox with no secrets or Docker socket
- Payment/advertising privacy and security review

Passing these checks NEVER proves the product is secure or safe for real resumes.
Security scanners may report false positives. Do not silence results automatically.
