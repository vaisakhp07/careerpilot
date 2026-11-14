#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .backups
umask 077
stamp=$(date -u +%Y%m%dT%H%M%SZ)
if [ -f careerpilot.sqlite3 ]; then .venv/bin/python -c 'import sqlite3,sys; s=sqlite3.connect(sys.argv[1]); t=sqlite3.connect(sys.argv[2]); s.backup(t);t.close();s.close()' careerpilot.sqlite3 ".backups/db-$stamp.sqlite3"; fi
if [ -d .git ]; then git bundle create ".backups/source-$stamp.bundle" --all; fi
printf 'Created LOCAL backups under .backups/. Not encrypted, offsite, or suitable for real user data.
'
