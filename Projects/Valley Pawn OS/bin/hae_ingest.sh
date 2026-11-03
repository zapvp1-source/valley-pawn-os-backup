#!/bin/bash
# hae_ingest.sh — native fleet agent `com.valleypawn.hae-ingest` (Apple Health auto-export ingest).
#
# WHAT (2026-11-02, Joshua: "set up the auto export"): the Health Auto Export iPhone app drops a JSON
# of Apple Health / Apple Watch data into iCloud every morning; this parses it into tidy CSVs under
# ~/Library/Application Support/HealthOS/apple_health/ (see Health Optimization/apple_health/README.md).
# Twice daily (08:40 / 20:40). Self-installing: the runtime is synced from the project source copy
# on every run, so editing the source is the whole deploy. Publishes nothing on success; ONE ledger
# row on a parse error (Failure Policy v3). "No export files yet" is NOT a fault — it is the state
# until the iPhone app is installed. Domain 3 — personal. Nothing here touches Valley Pawn.
AGENT="hae-ingest"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 30
H="$HOME/Library/Application Support/HealthOS"
SRC="$HOME/Documents/Claude/Projects/Health Optimization/apple_health"
mkdir -p "$H/bin" "$H/logs" "$H/hae_inbox"

# Step 0 — sync runtime (source copy wins when it differs; guard: never install an unparsable file)
if [ -f "$SRC/hae_ingest.py" ] && ! cmp -s "$SRC/hae_ingest.py" "$H/bin/hae_ingest.py"; then
  if "$PY" -m py_compile "$SRC/hae_ingest.py" 2>/dev/null; then
    cp "$SRC/hae_ingest.py" "$H/bin/hae_ingest.py" && vlog "runtime synced from source copy"
  else
    ledger "$AGENT" "apple_health/hae_ingest.py source copy does not compile — kept the installed runtime." "yes, fix the source file"
  fi
fi
[ -f "$H/bin/hae_ingest.py" ] || { ledger "$AGENT" "hae_ingest.py missing from both source and runtime." "yes, restore Health Optimization/apple_health/hae_ingest.py"; exit 1; }

# Step 1 — ingest
OUT="$H/logs/hae_ingest.log"
echo "=== hae-ingest $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUT"
"$PY" "$H/bin/hae_ingest.py" >> "$OUT" 2>&1; RC=$?
[ "$(wc -l < "$OUT")" -gt 5000 ] && { tail -n 2000 "$OUT" > "$OUT.tmp" && mv "$OUT.tmp" "$OUT"; }

# Step 2 — verify against the output, not the exit code (Rule 12)
SUMMARY=$("$PY" - "$H/apple_health/hae_latest.json" <<'PY' 2>/dev/null
import json,sys
try: d=json.load(open(sys.argv[1]))
except Exception as e: print("NOJSON"); sys.exit(0)
print(f"files={d.get('export_files_seen',0)} new={d.get('new_points_this_run',0)} total={d.get('total_points',0)} latest={d.get('latest_sample') or '-'} errors={len(d.get('errors') or [])}")
PY
)
vlog "rc=$RC $SUMMARY"
if [ $RENDER -eq 1 ]; then echo "=== RENDER ONLY ==="; echo "rc=$RC $SUMMARY"; tail -8 "$OUT"; exit 0; fi

case "$SUMMARY" in
  NOJSON) ledger "$AGENT" "hae_ingest.py ran (exit $RC) but wrote no hae_latest.json: $(tail -1 "$OUT" | cut -c1-160)" "no"; exit 1 ;;
  *errors=0*) ;;
  *) ledger "$AGENT" "Apple Health export parse errors: $(tail -1 "$OUT" | cut -c1-160)" "no"; exit 1 ;;
esac
# The mirror into the synced project folder is attempted inside hae_ingest.py (vp-runner can write there).
"$PY" "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "$H/apple_health/hae_latest.json" >/dev/null 2>&1
exit 0
