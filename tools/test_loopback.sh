#!/usr/bin/env bash
set -euo pipefail

# Defaults (override with env vars)
: "${SPE_PORT:=COM15}"
: "${SPE_SENDER_PORT:=COM16}"
: "${SPE_BAUD:=115200}"
: "${SPE_BASE_URL:=http://127.0.0.1:8080}"

echo "[i] Repo: $(pwd)"
echo "[i] Target server port: $SPE_PORT @ $SPE_BAUD"
echo "[i] Sender port: $SPE_SENDER_PORT @ $SPE_BAUD"
echo "[i] Base URL: $SPE_BASE_URL"
echo

# Activate venv if present
if [[ -f ".venv/Scripts/activate" ]]; then
  source ".venv/Scripts/activate"   # Windows Git Bash
elif [[ -f ".venv/bin/activate" ]]; then
  source ".venv/bin/activate"       # macOS/Linux
else
  echo "[!] No .venv found. Create it first: python -m venv .venv"
  exit 2
fi

echo "[i] Python: $(python --version)"
echo

echo "[1/5] health"
curl -s "$SPE_BASE_URL/health" ; echo
echo

echo "[2/5] serial open"
curl -s -i -X POST "$SPE_BASE_URL/api/serial/open" | sed -n '1,15p'
echo

echo "[3/5] send loopback via sender port"
python tools/send_loopback.py "$SPE_SENDER_PORT" "$SPE_BAUD"
echo

echo "[4/5] recent"
RECENT_JSON="$(curl -s "$SPE_BASE_URL/api/serial/recent?n=20")"
echo "$RECENT_JSON"
echo

# PASS criteria: items non-empty (use python -c so stdin remains the JSON)
if echo "$RECENT_JSON" | python -c "import json,sys; obj=json.load(sys.stdin); items=obj.get('items') or []; sys.exit(0 if len(items)>0 else 1)"; then
  echo "[PASS] recent contains items ✅"
else
  echo "[FAIL] recent is empty ❌"
  exit 3
fi

echo
echo "[5/5] serial close"
curl -s -X POST "$SPE_BASE_URL/api/serial/close" ; echo
echo

echo "[i] debug snapshot (optional)"
curl -s "$SPE_BASE_URL/debug/get_log" ; echo
echo

echo "[DONE] Loopback test completed."
