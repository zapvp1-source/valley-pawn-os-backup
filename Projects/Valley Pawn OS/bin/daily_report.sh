#!/bin/bash
# daily_report.sh <pawn|sold|discount> [YYYY-MM-DD]
# Native replacement (2026-09-17) for the Cowork tasks pawn-walk (07:15), sold-review (07:45) and
# discount-review (08:25). Each one: wait for the morning pull's CSVs (fall back to its own pull),
# run the existing compile script, read its summary JSON, and post `slack_message` VERBATIM —
# exactly the gate the SKILL.md files describe. Nothing here composes text.
#   pawn     -> Pawn Walks/run_daily_intake.py           -> #pawn-walks       C0B8WR95N31
#   sold     -> Sold Margin Review/run_daily_sold_review.py -> #sold-review     C0BK802MP43
#   discount -> Discount Outlier Review/run_daily_discount_review.py -> #discount-review C0BQ6JA27MX
# --render : compile and show EXACTLY what would be posted, publish NOTHING. Isolation testing
# (Joshua 2026-09-18: "test everything and see if it's working in isolation without publishing a
# bunch of bullshit to Slack"). Output goes to fleet/test_output/<task>-<date>.txt.
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
AGENT="daily-report-$1"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 60
KIND="$1"; Y="${2:-$(date -v-1d +%Y-%m-%d)}"; TODAY=$(date +%Y-%m-%d)
case "$Y" in --render) Y=$(date -v-1d +%Y-%m-%d);; esac
case "$KIND" in
  pawn)     REPORT=intake-detail;        PROJ="$HOME/Documents/Claude/Projects/Pawn Walks";              SCRIPT=run_daily_intake.py;          SUM="daily/${Y}_intake_margin_summary.json";  CH=C0B8WR95N31; TASK=pawn-walk; LABEL="Pawn walk" ;;
  sold)     REPORT=sold-discount-detail; PROJ="$HOME/Documents/Claude/Projects/Sold Margin Review";      SCRIPT=run_daily_sold_review.py;     SUM="daily/${Y}_sold_review_summary.json";    CH=C0BK802MP43; TASK=sold-review; LABEL="Sold review" ;;
  discount) REPORT=sold-discount-detail; PROJ="$HOME/Documents/Claude/Projects/Discount Outlier Review"; SCRIPT=run_daily_discount_review.py; SUM="daily/${Y}_discount_review_summary.json"; CH=C0BQ6JA27MX; TASK=discount-review; LABEL="Discount review" ;;
  *) echo "usage: daily_report.sh <pawn|sold|discount> [date]"; exit 2 ;;
esac
OPEN=$(open_stores "$Y"); [ -z "$OPEN" ] && { vlog "$Y was a Sunday — nothing to review"; exit 0; }
vlog "=== $TASK for $Y (open: $OPEN) ==="

# ---- 1. data: wait up to 25 min for the morning pull, then fall back to our own pull ----
have_all() { for s in $OPEN; do [ -f "$BRAVO/output/${Y}_to_${Y}_${s}_${REPORT}.csv" ] || return 1; done; return 0; }
t0=$(date +%s)
while ! have_all && [ $(( $(date +%s) - t0 )) -lt 1500 ]; do sleep 30; done
if ! have_all; then
  MISSING=""; for s in $OPEN; do [ -f "$BRAVO/output/${Y}_to_${Y}_${s}_${REPORT}.csv" ] || MISSING="$MISSING $s"; done
  vlog "morning pull did not deliver ($REPORT for$MISSING) — own pull"
  health_gate 600 >/dev/null
  bravo_run "${TASK}-$(date +%Y-%m-%dT%H-%M-%S)" "{\"name\":\"$REPORT\",\"stores\":[$(stores_json "$MISSING")],\"date\":\"$Y..$Y\"}" 1800
  have_all || { ledger "$TASK" "$LABEL for $Y is on hold — Bravo did not return data for$MISSING and I didn't want to post half a picture." "no"; exit 1; }
fi

# ---- 2. compile (the existing script; it writes the summary JSON and the xlsx) ----
# never compile while the pipeline is still writing CSVs (a re-pull resets a file before rewriting it)
for i in $(seq 1 40); do bravo_busy 2 || break; [ $i -eq 1 ] && vlog "pipeline busy — waiting before compile"; sleep 30; done
if [ "$KIND" = "sold" ]; then   # fair-value lookup first, single-flight, as the SKILL does
  if ! pgrep -f "fair_value.py --lookup-all" >/dev/null; then ( cd "$PROJ" && nohup $PY fair_value.py --lookup-all "$Y" > /tmp/fv_lookup.log 2>&1 < /dev/null & ); fi
  for i in $(seq 1 32); do pgrep -f "fair_value.py --lookup-all" >/dev/null || break; sleep 15; done
fi
( cd "$PROJ" && $PY "$SCRIPT" "$Y" > "/tmp/${TASK}_compile_${Y//-/}.log" 2>&1 ); rc=$?
vlog "compile rc=$rc :: $(tail -1 "/tmp/${TASK}_compile_${Y//-/}.log" | cut -c1-160)"
[ -f "$PROJ/$SUM" ] || { ledger "$TASK" "$LABEL for $Y did not compile (no summary written, exit $rc)." "no"; exit 1; }

# ---- 3. gate + post verbatim ----
read -r MSG_OK MISSING_N FLAGS XLSX INFO <<EOF
$($PY - "$PROJ/$SUM" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
msg=d.get("slack_message") or ""
print(("1" if msg.strip() else "0"), len(d.get("missing_stores") or []), d.get("flags",0), (d.get("excel_path") or "-").replace(" ","\\ "), (d.get("info") or "-").replace(" ","_")[:80])
open(sys.argv[1]+".msg","w").write(msg)
PY
)
EOF
if [ "$MSG_OK" != "1" ] || [ "$MISSING_N" != "0" ]; then
  ledger "$TASK" "$LABEL for $Y is on hold — ${INFO//_/ } (missing stores: $MISSING_N). Detail is saved for the next look." "no"; exit 1
fi
if [ $RENDER -eq 1 ]; then
  OUT="$OS_DIR/fleet/test_output"; mkdir -p "$OUT"
  cp "$PROJ/$SUM.msg" "$OUT/${TASK}-${Y}.txt"
  echo "=== RENDER ONLY — nothing was published ==="
  echo "task=$TASK date=$Y open_stores=[$OPEN] flags=$FLAGS missing=$MISSING_N xlsx=$XLSX"
  echo "would post to $CH ($(wc -c < "$PROJ/$SUM.msg" | tr -d ' ') bytes):"
  echo "---------------------------------------------"
  cat "$PROJ/$SUM.msg"
  echo "---------------------------------------------"
  echo "saved -> fleet/test_output/${TASK}-${Y}.txt"
  exit 0
fi
TITLE=$(head -1 "$PROJ/$SUM.msg" | sed 's/^[[:space:]:_*a-z]*//' | cut -c1-60)   # first line = report title incl. the date
if [ -n "$TITLE" ] && slack has "$CH" "$TITLE" 20 2>/dev/null; then vlog "already posted today — skip"; exit 0; fi
if [ "$KIND" = "pawn" ]; then
  # the SKILL's one line-substitution: the spreadsheet goes to Joshua, not to the channel
  sed -i '' 's/^📎 _Spreadsheet:.*$/📎 _Detailed item-level spreadsheet sent to Joshua._/' "$PROJ/$SUM.msg"
fi
slack post "$CH" --file "$PROJ/$SUM.msg" >/dev/null && vlog "posted to $CH" || { ledger "$TASK" "$LABEL for $Y compiled but Slack refused the post to $CH." "no"; exit 1; }
XLSX="${XLSX//\\ / }"
[ "$XLSX" != "-" ] && [ -f "$XLSX" ] && slack upload U03BB52MDSA "$XLSX" "$LABEL $Y" >/dev/null && vlog "xlsx sent to Joshua"
if [ "${FLAGS:-0}" -gt 0 ] 2>/dev/null; then
  case "$KIND" in
    pawn)     slack dm "⚑ PAWN WALK flags $Y: $FLAGS item(s) below 30% margin. Spreadsheet is in this DM." ;;
    sold)     slack dm "SOLD REVIEW flags $Y: $FLAGS item(s) sold below the margin floor. Spreadsheet is in this DM." ;;
    discount) slack dm "DISCOUNT REVIEW flags $Y: $FLAGS item(s) discounted ≥20% or ≥\$50 off ticket. Spreadsheet is in this DM." ;;
  esac >/dev/null
fi
vlog "=== $TASK done ==="
