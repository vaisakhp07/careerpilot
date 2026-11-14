#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v gh >/dev/null || { echo 'GitHub CLI gh required'; exit 1; }
gh auth status >/dev/null
if [ ! -d .git ]; then git init -b main; fi
if [ -f .env ]; then echo 'ERROR: remove .env before publishing; verify no secrets in files.'; exit 1; fi
if git remote get-url origin >/dev/null 2>&1; then echo 'Origin already exists. Refusing to publish automatically.'; exit 1; fi
printf 'Create public GitHub repo careerpilot under the current account? Type CREATE: '
read -r confirmation
[ "$confirmation" = 'CREATE' ] || { echo 'Cancelled'; exit 1; }
git add .
git commit -m 'feat: CareerPilot CP-001 local foundation' || true
gh repo create careerpilot --public --source=. --remote=origin --push
printf 'Next: connect CodeRabbit to this repository and configure protected main / required checks.
'
