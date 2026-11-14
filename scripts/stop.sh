#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for name in web api; do
 if [ -f ".run/$name.pid" ]; then
   pid=$(cat ".run/$name.pid")
   if [[ "$pid" =~ ^[0-9]+$ ]]; then kill "$pid" 2>/dev/null || true; fi
   rm -f ".run/$name.pid"
 fi
done
echo 'Stop signals sent; check ports if child processes remain.'
