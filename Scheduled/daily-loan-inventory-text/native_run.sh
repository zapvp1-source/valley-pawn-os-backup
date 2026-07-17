#!/bin/bash
# Mac-native driver for daily-loan-inventory-text. Runs on the Mac via launchd
# with NO dependency on a cloud session: runs the EOM pull, then texts both
# recipients directly through Messages.
TASK="/Users/joshuadavis/Documents/Claude/Scheduled/daily-loan-inventory-text"
LOG="$TASK/native.log"
NUMS="+18049304221 +15408364200"
echo "=== native run $(date) ===" >> "$LOG"
/bin/bash "$TASK/daily_run.sh" >> "$LOG" 2>&1
ST=$(cat "$TASK/latest_status.txt" 2>/dev/null)
echo "pull status: $ST" >> "$LOG"
if [ "$ST" = "OK" ]; then
  BODY=$(cat "$TASK/latest_message.txt")
else
  BODY="Valley Pawn daily numbers: couldn't pull Bravo this morning ($ST). Will retry tomorrow."
fi
for N in $NUMS; do
  R=$(/usr/bin/osascript "$TASK/send_imsg.applescript" "$N" "$BODY" 2>&1)
  echo "send $N -> $R" >> "$LOG"
done
echo "=== native run done $(date) ===" >> "$LOG"
