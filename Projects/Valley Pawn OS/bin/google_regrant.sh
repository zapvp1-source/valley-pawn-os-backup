#!/bin/bash
# google_regrant.sh [dry-run|grant|verify] — ONE Google approval for the Mac fleet token (2026-10-14).
# dry-run (default): checks client + current token, prints the consent URL; opens nothing, writes nothing.
# grant: opens Google's consent page in the default browser; Joshua signs in as jdavis@fcfpawn.com and
#        clicks Allow once. Old token is backed up first; new one saved only if Sheets still works.
# verify: live check of the current token (one read call per Google service).
MODE="${1:-dry-run}"
PY=/usr/bin/python3
B="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/google_regrant.py"
case "$MODE" in
  dry-run) "$PY" "$B" --dry-run ;;
  verify)  "$PY" "$B" --verify ;;
  grant)
    "$PY" "$B" --grant; RC=$?
    if [ $RC -eq 0 ]; then MSG="Done. Google access approved for all six services. You can close this window."
    elif [ $RC -eq 3 ]; then MSG="Approved and saved. One or more Google services still need a setting turned on — Claude will see the details in the log."
    else MSG="Nothing changed (code $RC). Your existing Google access still works. Tell Claude and it will take it from here."; fi
    osascript -e "display dialog \"$MSG\" buttons {\"OK\"} with title \"Valley Pawn — Google access\" giving up after 600" >/dev/null 2>&1
    exit $RC ;;
  *) echo "usage: google_regrant.sh [dry-run|grant|verify]"; exit 2 ;;
esac
