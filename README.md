# CareerPilot — India-first jobs MVP (CP-001)

**Status:** local, synthetic-data-only prototype. Not production-ready; don't upload real resumes or expose publicly.

## What actually works
- React + TypeScript job search UI; title, city, work mode, and skills filters.
- FastAPI `/api/jobs` and `/api/health` with validated parameters, page bounds, CORS allowlist and security headers.
- Local demo job dataset explicitly labeled *DEMO* (no fake claim of live job availability).
- SQLite for effortless local start or PostgreSQL via Compose; data model includes provenance, timestamps, duplicate source IDs.
- Basic parameterized search tests, GitHub Actions checks, CodeRabbit config, feature backlog, read-only Greenhouse adapter skeleton.
- **Not yet verified:** frontend dependency install/build in this environment (package registry network unavailable); Mac bootstrap is the first full integration test.
- Existing AI-loop code is **not promoted to trusted execution**. Separate local agent runner integration is an approval-gated task.

## Single-command Mac setup
Prerequisites: Python >=3.11, Node >=20, npm, git. Ollama and gh already installed for the user.

Extract ZIP, then from a terminal:

```bash
cd ~/Documents/careerpilot
bash scripts/bootstrap.sh
```

This command creates Python venv, installs API/frontend dependencies, runs tests, starts the local API and Vite UI in the background, and prints both URLs. It **does not** use AWS, create a repository, open public network access, or contact a coding LLM. For source publication, explicit opt-in:

```bash
bash scripts/publish.sh
```

Publish checks GitHub auth, initializes Git when needed, and creates a **public** GitHub repo `careerpilot` if available. Inspect `.env.example` and verify no secrets before publishing; **never** put personal data in a public repo.

Stop local servers: `bash scripts/stop.sh`. Run validation: `bash scripts/check.sh`.

## Runtime choices
Local bootstrap defaults to SQLite for low RAM. PostgreSQL is recommended before testing real data; use `docker compose -f infra/local/compose.yaml up -d db`, then set `DATABASE_URL` from `.env.example` locally (don't commit `.env`). `scripts/bootstrap.sh` loads `.env` only when present. Avoid running Ollama model at the same time as resource-heavy E2E tests on 8 GB RAM.

## Security boundaries / non-goals
This MVP is **anonymous, read-only jobs search**. No login, resume upload, user profiles, payment, ads, or exposure to friends until those features have been implemented and security tested. Sample postings are synthetic and have no application links. All sensitive features are explicitly deferred; there is no claim of ASVS certification or zero risk.

`automation/` contains product backlog, approval rules, and integration plan. Do not run legacy local AI-generated tests on a Mac with secrets or unrestricted developer credentials. The permanent agent requires isolated execution, fail-closed PR gating, review-thread lifecycle tests, and manual approval before it can merge. See `automation/README.md`.

## Deployment and recovery
GitHub maintains code, not live database/resumes. `scripts/backup.sh` produces a local SQLite snapshot and a git bundle (if git is initialized). Do not treat this as a complete off-site or encrypted backup. Production DB/files backups need an independently verified encrypted export and restore drill. No AWS spend is enabled by default.
