#!/usr/bin/env bash
# Bravo Pipeline ISLAND Preflight
# Verifies the island is self-contained and fully reachable from this session.
# Unlike bravo-preflight.sh (which is tolerant of an unmounted parent Projects/),
# this script FAILS LOUD if any island path is missing.
#
# See island/ISLAND.md for the contract.

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PIPELINE_PROJECT="$( dirname "$SCRIPT_DIR" )"     # .../Bravo Pipeline

ISLAND_ROOT="$PIPELINE_PROJECT/island"
ISLAND_SRC="$ISLAND_ROOT/source"
ISLAND_OUT="$ISLAND_ROOT/output"
ISLAND_SCHED="$ISLAND_ROOT/scheduled"
ISLAND_POC="$ISLAND_ROOT/proof-of-concept"
ISLAND_DOC="$ISLAND_ROOT/ISLAND.md"
ISLAND_REG="$ISLAND_ROOT/island-registry.md"

FAIL=0

echo "===================================================="
echo " BRAVO PIPELINE — ISLAND PREFLIGHT"
echo " $(date)"
echo "===================================================="

# --- Required paths -----------------------------------------------------------
check_dir() {
  local label="$1" path="$2"
  if [ -d "$path" ]; then
    echo "[OK]   $label: $path"
  else
    echo "[FAIL] $label MISSING: $path"
    FAIL=1
  fi
}

check_file() {
  local label="$1" path="$2"
  if [ -f "$path" ]; then
    echo "[OK]   $label: $path"
  else
    echo "[FAIL] $label MISSING: $path"
    FAIL=1
  fi
}

echo ""
check_dir  "Island root"         "$ISLAND_ROOT"
check_file "Island contract"     "$ISLAND_DOC"
check_file "Island registry"     "$ISLAND_REG"
check_dir  "Island source"       "$ISLAND_SRC"
check_dir  "Island output"       "$ISLAND_OUT"
check_dir  "Island scheduled"    "$ISLAND_SCHED"
check_dir  "Island PoC"          "$ISLAND_POC"

# --- Isolation check: nothing in island/ should reference prod paths ---------
echo ""
echo "--- Isolation: any references to prod paths from inside island/ ---"
LEAKS=$(grep -r --include='*.sh' --include='*.ahk' --include='*.py' --include='*.md' \
  -l "Bravo Data Extraction" "$ISLAND_ROOT" 2>/dev/null \
  | grep -v "ISLAND.md" \
  | grep -v "island-registry.md" || true)
if [ -z "$LEAKS" ]; then
  echo "[OK]   No leaks into prod paths from island code files."
else
  echo "[WARN] These files reference prod paths — confirm they are doc-only:"
  echo "$LEAKS" | sed 's/^/       /'
fi

# --- Island inventory ---------------------------------------------------------
echo ""
echo "--- Island inventory ---"
SRC_COUNT=$(find "$ISLAND_SRC" -maxdepth 1 -type f ! -name 'README.md' 2>/dev/null | wc -l | tr -d ' ')
OUT_COUNT=$(find "$ISLAND_OUT" -maxdepth 1 -type f -name '*.csv' 2>/dev/null | wc -l | tr -d ' ')
SCHED_COUNT=$(find "$ISLAND_SCHED" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
echo "Handlers in source/:      $SRC_COUNT"
echo "CSVs in output/:          $OUT_COUNT"
echo "Tasks in scheduled/:      $SCHED_COUNT"

# --- Registry freshness -------------------------------------------------------
echo ""
if stat -f %m "$ISLAND_REG" >/dev/null 2>&1; then
  REG_MTIME=$(stat -f %m "$ISLAND_REG")
else
  REG_MTIME=$(stat -c %Y "$ISLAND_REG")
fi
REG_AGE_DAYS=$(( ($(date +%s) - REG_MTIME) / 86400 ))
echo "Island registry updated $REG_AGE_DAYS days ago."
if [ "$REG_AGE_DAYS" -gt 14 ]; then
  echo "[WARN] Island registry is older than 14 days — re-audit it."
fi

# --- Final verdict ------------------------------------------------------------
echo ""
echo "===================================================="
if [ "$FAIL" -eq 0 ]; then
  echo " ISLAND PREFLIGHT: PASS"
  echo ""
  echo " Next step — read the island contract + registry:"
  echo "   cat \"$ISLAND_DOC\""
  echo "   cat \"$ISLAND_REG\""
  echo "===================================================="
  exit 0
else
  echo " ISLAND PREFLIGHT: FAIL"
  echo " Fix the missing paths above before island work."
  echo "===================================================="
  exit 1
fi
