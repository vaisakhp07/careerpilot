# CP-AUTO-001 — Phase 1: read-only trust verification

This phase provides a **read-only** CLI using the authenticated GitHub CLI (`gh`).
It checks the protected `main` ruleset and obtains check-run statuses from the
**exact PR HEAD commit**, checking the expected GitHub App identity. It will not
merge, push, run generated code, resolve CodeRabbit threads, or call Ollama.

Run from CareerPilot root:

```bash
python3 -m automation.controller.cli doctor
python3 -m automation.controller.cli pr-status 2
python3 -m unittest discover -s tests -p 'test_controller_phase1.py' -v
```

The next stages need a sandboxed, credential-free worker and explicit human
review for any security, GitHub workflow, authentication, or billing changes.
Never treat green checks as evidence that review conversations are resolved.

## Limits

- Assumes repo name `vaisakhp07/careerpilot` and current configured required checks.
- `gh api` calls require network/GitHub auth, but the controller does not read or
  print token values.
- Does not yet implement job queue, generation, review repair, or unattended merges.
