#!/bin/bash
# gift_credit_run.sh [YYYY-MM] [--render] — native replacement for Cowork `monthly-gift-card-store-credit`
# (2nd of month 02:30, 2026-10-02). The SKILL's own steps, nothing re-derived:
#   1 reuse the 10 CSVs if already on disk, else pull credit-balance (single date = month END) and
#     credit-journal (START..END) for all 5 stores via bravo_pull.sh
#   2 gift_credit_monthly.py — exit 0 = its stdout is the post; exit 2 = HOLD, publish nothing (Rule 18)
#   3 post that text VERBATIM (Goldilocks) to #company-performance AND DM Preston (Joshua 2026-09-29)
#   4 archive the xlsx (customer names, internal only) to the Drive reports folder
AGENT="monthly-gift-card-store-credit"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; YM=""; for a in "$@"; do case "$a" in --render) RENDER=1;; 20*) YM="$a";; esac; done
[ -z "$YM" ] && YM=$(date -v-1m +%Y-%m)
START="$YM-01"; END=$(/usr/bin/python3 -c "import calendar,sys;y,m=map(int,'$YM'.split('-'));print('%04d-%02d-%02d'%(y,m,calendar.monthrange(y,m)[1]))")
B="$HOME/Documents/Claude/Projects/Bravo Data Extraction"; GC="$HOME/Documents/Claude/Projects/Gift Card & Store Credit"
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 120
have=0; for s in CUL HAR LEX ROA WAY; do for r in credit-balance credit-journal; do [ -s "$B/output/${END}_${s}_${r}.csv" ] && have=$((have+1)); done; done
vlog "$YM: $have/10 input CSVs on disk"
if [ $have -lt 10 ] && [ $RENDER -eq 0 ]; then
  bash "$BIN/bravo_pull.sh" credit-balance "$END" CUL,HAR,LEX,ROA,WAY "giftcredit-bal-$YM-$(date +%s)" >> "$VLOG/$AGENT.log" 2>&1
  bash "$BIN/bravo_pull.sh" credit-journal "$START..$END" CUL,HAR,LEX,ROA,WAY "giftcredit-jrn-$YM-$(date +%s)" >> "$VLOG/$AGENT.log" 2>&1
fi
OUT="$GC/out/$YM"; mkdir -p "$OUT"
"$PY" "$BIN/gift_credit_monthly.py" "$YM" "$B/output" "$OUT" > /tmp/gc_post_$YM.txt 2> /tmp/gc_err_$YM.txt; RC=$?
if [ $RENDER -eq 1 ]; then echo "=== RENDER ONLY (formatter exit $RC) ==="; cat /tmp/gc_post_$YM.txt; tail -5 /tmp/gc_err_$YM.txt; exit 0; fi
if [ $RC -ne 0 ]; then
  ledger "$AGENT" "Gift card / store credit report for $YM held — Bravo numbers did not reconcile or an input was missing." "no"; exit 1
fi
VP_TASK="$AGENT" "$PY" "$BIN/vp_slack.py" post C0B26GD8D2R --file /tmp/gc_post_$YM.txt >/dev/null || { ledger "$AGENT" "Gift card / store credit report for $YM was built but did not post." "no"; exit 1; }
VP_TASK="$AGENT" "$PY" "$BIN/vp_slack.py" post U03BWMEM9GR --file /tmp/gc_post_$YM.txt >/dev/null || ledger "$AGENT" "Gift card / store credit report posted, but Preston's copy did not send." "no"
D="$HOME/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/01 Business/Full Circle Finance (Valley Pawn)/08 Reports & Analysis/Gift Card & Store Credit"
[ -d "$D" ] && cp "$OUT/gift_credit_$YM.xlsx" "$D/" 2>/dev/null && vlog "archived xlsx to Drive" || vlog "Drive archive folder not reachable — xlsx kept at $OUT"
vlog "$YM posted"
