#!/usr/bin/env bash
set -euo pipefail

# Root del progetto
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Project root: $ROOT"
echo "Starting server in this terminal..."
echo

# Apri un nuovo TAB in Terminal.app per i test
osascript <<OSA
tell application "Terminal"
    activate
    tell application "System Events" to keystroke "t" using command down
    delay 0.3
    do script "cd '$ROOT'; source .venv/bin/activate; echo 'Client terminal ready (venv active)'" in front window
end tell
OSA

# Avvia il server nel terminale corrente
cd "$ROOT"
source .venv/bin/activate
exec python apps/speweb.py
