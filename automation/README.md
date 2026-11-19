# Embedded development automation
This directory is IN THE PRODUCT REPOSITORY. It is not a separate product.

## Current maturity
Existing `ai-dev-loop` + `pr_autofix_v3.py` proved partial Ollama → PR → CodeRabbit feedback → repair. They are **not hardened** for this full-stack app: host execution, mutating protected files, unresolved-thread lifecycle, review provenance, and durable retries remain risks.

## Planned trusted orchestrator (CP-AUTO-001)
- Local queue in SQLite with task id, claim lease, current PR SHA, attempts, last review/check IDs.
- Input is only approved issues or manifests; no raw email copying.
- Local Ollama outputs reviewed file changes restricted by task policy; run builds/tests inside rootless sandbox with no GH token, user files, or Docker socket.
- Separate push coordinator owns a narrowly scoped GitHub token and validates path allowlists before committing.
- Verify CI and CodeRabbit check runs for exact HEAD SHA, retrieve review threads and validate unresolved findings.
- Routine code PRs may auto-merge only after CI, security scans, branch rules and mandatory review gates succeed. Human-approved exceptions never silently allowed.
- PRs touching auth, security configuration, deployment, AI controller, payments, or data deletion remain manual.
- macOS launchd local agent; suspend on sleep or unavailable services; no cloud spend.

## IMPORTANT
No continuous agent is enabled in CP-001. Do not run an untrusted coding LLM with full shell/GitHub/AWS access on the primary macOS user session.

CodeRabbit integration verification.
