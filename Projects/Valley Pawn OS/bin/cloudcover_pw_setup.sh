#!/bin/bash
# cloudcover_pw_setup.sh — one-time, idempotent: make sure /usr/bin/python3 can import Playwright
# (native daily-cloudcover-check, 2026-10-14). Uses the installed Google Chrome (channel="chrome"), so
# NO Playwright browser download is needed. Creates the dedicated automation profile dir (empty).
# Safe to re-run: if playwright already imports it only prints the version.
set +e
PY=/usr/bin/python3
PROFILE="$HOME/Library/Application Support/valleypawn/pw-cloudcover"
mkdir -p "$PROFILE"; chmod 700 "$PROFILE"
if "$PY" -c "import playwright" 2>/dev/null; then
  echo "playwright already installed"
else
  "$PY" -m pip install --user --break-system-packages playwright 2>&1 | tail -5
  "$PY" -c "import playwright" 2>/dev/null || "$PY" -m pip install --user playwright 2>&1 | tail -5
fi
"$PY" - <<'PY'
try:
    from importlib.metadata import version
    import playwright.sync_api  # noqa
    print("playwright OK", version("playwright"))
except Exception as e:
    print("playwright STILL MISSING", type(e).__name__, e)
PY
ls -ld "$PROFILE"
