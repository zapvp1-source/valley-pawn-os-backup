#!/usr/bin/env bash
# Bravo Pipeline Preflight
# MANDATORY first step for any Bravo-touching Cowork session.
# See SESSION_PROTOCOL.md for the contract.

set -uo pipefail

# Self-locating: resolve every path relative to this script's own location,
# so the preflight works whether invoked from the user's Mac
# (/Users/joshuadavis/...) or from a Cowork sandbox mount
# (/sessions/<id>/mnt/...).
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PIPELINE_PROJECT="$( dirname "$SCRIPT_DIR" )"     # .../Bravo Pipeline
PROJECTS_PARENT="$( dirname "$PIPELINE_PROJECT" )" # .../Projects  (or sandbox mnt)

PIPELINE_ROOT="$PROJECTS_PARENT/Bravo Data Extraction"
PIPELINE_OUT="$PIPELINE_ROOT/output"
REGISTRY="$PIPELINE_PROJECT/bravo-pipeline-registry.md"
PROTOCOL="$PIPELINE_PROJECT/SESSION_PROTOCOL.md"

echo "===================================================="
echo " BRAVO PIPELINE PREFLIGHT"
echo " $(date)"
echo "===================================================="

# --- Visibility check ---------------------------------------------------------
echo ""
if [ -d "$PIPELINE_ROOT" ]; then
  echo "[OK] Pipeline source visible: $PIPELINE_ROOT"
else
  echo "[WARN] Pipeline source NOT visible at: $PIPELINE_ROOT"
  echo "       This session does not have the parent Projects/ folder mounted."
  echo "       Skill-level absolute-path triggers will still work."
  echo "       Pipeline DEV (editing handlers) requires mounting parent Projects/."
fi

# --- Registry check -----------------------------------------------------------
echo ""
if [ -f "$REGISTRY" ]; then
  if stat -f %m "$REGISTRY" >/dev/null 2>&1; then
    REG_MTIME=$(stat -f %m "$REGISTRY")
  else
    REG_MTIME=$(stat -c %Y "$REGISTRY")
  fi
  REG_AGE_DAYS=$(( ($(date +%s) - REG_MTIME) / 86400 ))
  echo "[OK] Registry: $REGISTRY"
  echo "     Updated $REG_AGE_DAYS days ago."
  if [ "$REG_AGE_DAYS" -gt 30 ]; then
    echo "     [WARN] Registry is older than 30 days — schedule a re-audit."
  fi
else
  echo "[FAIL] Registry NOT found at: $REGISTRY"
  echo "       Cannot proceed safely. Stop and surface to Joshua."
  exit 1
fi

# --- CSV freshness ------------------------------------------------------------
if [ -d "$PIPELINE_OUT" ]; then
  echo ""
  echo "--- Fresh CSVs (last 7 days) ---"
  find "$PIPELINE_OUT" -maxdepth 1 -name "*.csv" -mtime -7 -type f 2>/dev/null \
    | sort \
    | while read -r f; do
        if stat -f "%Sm %N" -t "%Y-%m-%d" "$f" >/dev/null 2>&1; then
          stat -f "%Sm  %N" -t "%Y-%m-%d" "$f"
        else
          stat -c "%y  %n" "$f" | cut -c1-10,20-
        fi
      done

  FRESH=$(find "$PIPELINE_OUT" -maxdepth 1 -name "*.csv" -mtime -7 -type f 2>/dev/null | wc -l | tr -d ' ')
  STALE=$(find "$PIPELINE_OUT" -maxdepth 1 -name "*.csv" -mtime +30 -type f 2>/dev/null | wc -l | tr -d ' ')
  TOTAL=$(find "$PIPELINE_OUT" -maxdepth 1 -name "*.csv" -type f 2>/dev/null | wc -l | tr -d ' ')
  echo ""
  echo "Counts:  fresh (<7d) = $FRESH   stale (>30d) = $STALE   total = $TOTAL"
else
  echo ""
  echo "[WARN] Output folder not visible — CSV freshness check skipped."
fi

# --- Next step ----------------------------------------------------------------
echo ""
echo "===================================================="
echo " NEXT STEP — Read the registry before proposing work:"
echo "   cat \"$REGISTRY\""
echo ""
echo " Then follow the protocol:"
echo "   cat \"$PROTOCOL\""
echo "===================================================="
