# Architecture and single-repository layout

```text
careerpilot/
  apps/web/                     # React + TypeScript + Vite client
  services/api/                 # FastAPI HTTP endpoints
  services/ingestion/           # scheduled job-source adapters
  packages/contracts/          # OpenAPI and typed schemas
  packages/matching/           # deterministic scoring
  db/migrations/               # Alembic migrations
  infra/local/                 # Docker Compose, local DB
  infra/cloud/                 # portable IaC (later, opt-in)
  automation/controller/       # trusted local orchestration service
  automation/policies/         # file allowlist, PR classifications, approval gates
  automation/tasks/            # structured task definitions
  .github/workflows/           # CI + security workflows
  security/                    # threat model, requirements, test fixtures
  tests/                       # API, integration, security, E2E tests
  docs/                        # product specification and runbooks
  scripts/                     # bootstrap, test, backup/restore
  .env.example                 # names only, never credentials
```

## Runtime
Browser -> React client -> FastAPI -> PostgreSQL. Separate ingestion worker -> approved ATS feeds -> PostgreSQL. Private resume documents remain on local encrypted filesystem for development, or later private object storage with access policies. Ollama is a *developer-side* local service, outside the application request path.

## Local development
MacBook M2 8 GB: start DB + API + web first. Stop heavy browser test processes before running local Qwen coding models. Docker Compose for DB, lightweight native processes if RAM tight. Use synthetic accounts and resumes for friend testing until private-user security gates pass.

## AI workflow inside same repository
Task (GitHub Issue with approved label or local task manifest) -> LaunchAgent polls -> claim task with persistent SQLite state -> local Ollama generates changes in disposable Git worktree -> static lint, type check, unit/security tests in isolated runner -> push feature branch -> PR -> CodeRabbit and GitHub Actions -> retrieve check runs and unresolved review threads for exact current HEAD -> model repairs under bounded 3 retries -> revalidate -> eligible merge. Controller/security/CI/IaC/auth/payments changes require human approval. Application functionality PRs may become eligible for auto-merge only after policy validation, tested review-thread lifecycle, and explicit opt-in.

## Isolation rules
Agent never gets production secrets, cloud credentials, arbitrary internet write access, or permission to change its own guardrails. Test runner is isolated from host files and host socket. No privileged Docker or writable Docker socket. Treat job content, reviews and repository text as untrusted data, not instructions.

## Portability
Source and IaC in GitHub plus a local clone and git bundle; database via encrypted versioned `pg_dump` exports and restore drills; user uploads backed up separately and encrypted. Keep independent backup outside AWS, with separate access credentials and checksum manifest. No live personal data in Git.
