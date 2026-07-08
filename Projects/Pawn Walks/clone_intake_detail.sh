#!/bin/bash
# Clone BuysFromPublic.ahk -> IntakeDetail.ahk, pointed at saved report "Claude Pawn Walks".
# Self-contained: every function/global defined in the file is renamed so it never
# collides with the original (which stays byte-identical and keeps powering Deep KPI).
set -e
R="/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/reports"
SRC="$R/BuysFromPublic.ahk"
DST="$R/IntakeDetail.ahk"

# never overwrite an existing clone without a backup
if [ -f "$DST" ]; then cp "$DST" "$DST.bak-$(date +%Y%m%dT%H%M%S)"; fi
cp "$SRC" "$DST"

# global renames (def + all call sites move together because they're in one file)
sed -i '' \
  -e 's/Claude Buy Reviews/Claude Pawn Walks/g' \
  -e 's/BUYS_ELEMENTS/INTAKE_ELEMENTS/g' \
  -e 's/PullBuysFromPublic/PullIntakeDetail/g' \
  -e 's/WriteBuysGridToCsv/WriteIntakeDetailGrid/g' \
  -e 's/JoinCsvRow/JoinIntakeCsvRow/g' \
  -e 's/WaitForBravoWindowExists/WaitForIntakeBravoWin/g' \
  -e 's/_buys-from-public\.csv/_intake-detail.csv/g' \
  -e 's/"buys-from-public"/"intake-detail"/g' \
  -e 's/BuysFromPublic/IntakeDetail/g' \
  "$DST"

echo "=== VERIFY: key lines in the clone ==="
grep -n 'saved_report_value\|INTAKE_ELEMENTS :=\|^PullIntakeDetail(\|outputFileName :=\|"report",' "$DST" | head -20
echo "=== sanity: no leftover 'Claude Buy Reviews' or 'PullBuysFromPublic' in clone ==="
grep -c 'Claude Buy Reviews\|PullBuysFromPublic' "$DST" || true
echo "=== original untouched? (should still say Claude Buy Reviews) ==="
grep -c 'Claude Buy Reviews' "$SRC"
echo "=== function defs in clone (all should be *Intake* names) ==="
grep -nE '^[A-Za-z_][A-Za-z0-9_]*\(' "$DST"
