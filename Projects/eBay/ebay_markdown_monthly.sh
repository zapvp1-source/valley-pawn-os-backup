#!/bin/bash
# Valley Pawn — monthly eBay auto-markdown (10% per month, cap 30% off). Runs 1st of each month.
LOG="$HOME/ebay_markdown_monthly.log"
echo "=== monthly markdown $(date) ===" > "$LOG"
for s in Roanoke Culpeper Harrisonburg Lexington Waynesboro; do
  echo "--- $s ---" >> "$LOG"
  /usr/bin/python3 "$HOME/ebay_markdown_engine.py" "$s" --apply >> "$LOG" 2>&1
done
APPLIED=$(grep -oE 'APPLIED [0-9]+' "$LOG" | awk '{s+=$2} END{print s+0}')
FAILED=$(grep -oE 'failed [0-9]+' "$LOG" | awk '{s+=$2} END{print s+0}')
curl -s -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"🏷️ *eBay Monthly Markdown* — applied a 10% cut to *${APPLIED}* aged listings (each stops at 30% off). Failures: ${FAILED}. Items already at 30% are left alone.\"}" \
  "$(cat "$HOME/.vp_secrets/slack_webhook_ebay_markdown" 2>/dev/null)" > /dev/null
