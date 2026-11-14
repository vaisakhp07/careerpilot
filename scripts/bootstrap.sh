#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo 'Python 3 required'; exit 1; }
command -v npm >/dev/null || { echo 'npm required'; exit 1; }
if [ -f .env ]; then set -a; source .env; set +a; fi
python3 -m venv .venv
.venv/bin/python -m pip install -r services/api/requirements-dev.txt
(cd apps/web && npm install --no-audit --no-fund)
bash scripts/check.sh
mkdir -p .run
if [ -f .run/api.pid ] || [ -f .run/web.pid ]; then echo 'Existing PID files found; run bash scripts/stop.sh first'; exit 1; fi
nohup .venv/bin/python -m uvicorn services.api.main:app --host 127.0.0.1 --port 8000 > .run/api.log 2>&1 < /dev/null & echo $! > .run/api.pid
(cd apps/web; nohup npm run dev -- --host 127.0.0.1 > ../../.run/web.log 2>&1 < /dev/null & echo $! > ../../.run/web.pid)
echo 'CareerPilot local services started:'
echo 'Web: http://127.0.0.1:5173'
echo 'API: http://127.0.0.1:8000/api/health'
echo 'Stop: bash scripts/stop.sh'
