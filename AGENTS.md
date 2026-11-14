# CareerPilot coding rules (untrusted-code boundary)
- No production data, credentials, real resumes, paid APIs, unauthorized job scraping, or billing changes.
- Before introducing auth, payment, ads, resumes, or cloud access: HUMAN APPROVAL REQUIRED.
- Never edit `.github/`, `automation/policies/`, `AGENTS.md`, `.coderabbit.yaml`, `infra/cloud/`, or security gates from ordinary automated tasks.
- Tests must assert behavior and be actually discovered by CI. No pretending a test passed.
- Implement one small approved task at a time. Fail closed on ambiguous security impact.
- Never auto-resolve outstanding review threads without objective verified evidence and maintainer permission.
- Agent generated code/tests must execute in sandbox without host secrets, Docker socket, or live GH/AWS tokens. Current bootstrap DOES NOT run an autonomous agent for this reason.
