#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
.venv/bin/python -m compileall -q services tests
.venv/bin/python -m ruff check services tests --select E4,E7,E9,F
.venv/bin/python -m pytest tests -q
(cd apps/web && npm run build)
