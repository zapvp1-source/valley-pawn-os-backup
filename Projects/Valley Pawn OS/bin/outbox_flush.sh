#!/bin/bash
# outbox_flush.sh — post anything a Cowork task left in fleet/outbox/, through the ops bot.
#
# WHY (2026-09-22): chekkit-unanswered-eod-followup did every step of its job on 9/21 and then its
# final Slack post was "declined automatically because no one was available to approve it during
# this scheduled run." The morning Chekkit alert posts fine because its send was approved once by a
# human and that approval is stored on the task; the EOD one never got that click, and Joshua reports
# the "Run now" button that would have provided it no longer exists. So there is no path to grant it.
#
# This removes the human from the loop instead of hunting for the button: a task writes what it wants
# to say into fleet/outbox/<name>.json ({"channel": "C0...", "file": "/abs/path/to/message.txt"}) and
# this posts it through vp_slack.py — the ops bot, a token, which never asks anyone. Same fix that
# revived compliance_brief. It runs every ~2 min from the same hook as the host job queue.
#
# Rule 16 lives in the CALLER: this posts exactly the file it is handed.
OS_DIR="$HOME/Documents/Claude/Projects/Valley Pawn OS"
BOX="$OS_DIR/fleet/outbox"; SENT="$BOX/sent"; FAIL="$BOX/failed"
mkdir -p "$BOX" "$SENT" "$FAIL"
LOCK="$BOX/.lock"
mkdir "$LOCK" 2>/dev/null || exit 0
trap 'rmdir "$LOCK" 2>/dev/null' EXIT
shopt -s nullglob
for j in "$BOX"/*.json; do
  name="$(basename "$j" .json)"
  ch="$(/usr/bin/python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("channel",""))' "$j" 2>/dev/null)"
  f="$(/usr/bin/python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("file",""))' "$j" 2>/dev/null)"
  if [ -z "$ch" ] || [ ! -s "$f" ]; then
    mv "$j" "$FAIL/$name.json"; echo "$(date '+%F %T') $name: bad envelope (channel=$ch file=$f)" >> "$BOX/outbox.log"; continue
  fi
  case "$ch" in C*|D*|U*) ;; *) mv "$j" "$FAIL/$name.json"; echo "$(date '+%F %T') $name: refused channel '$ch'" >> "$BOX/outbox.log"; continue ;; esac
  # 2026-09-25: D03BHQH5VGT is the Cowork app's DM with Joshua — a different app; the ops bot cannot
  # post there (channel_not_found; jewelry 9/24 lost its DM this way). Any SKILL that still writes
  # that id means "DM Joshua" — deliver to him by user id, which the bot CAN do.
  [ "$ch" = "D03BHQH5VGT" ] && ch="U03BB52MDSA"
  # VP_TASK -> the receipt is written under the ORIGINATING task's name, so the audit credits it.
  # Names are <task>[-<suffix>]-<YYYYMMDD-HHMMSS>; a suffix (-main, -joshua-dm, -cul-manager) must
  # not fork the receipt file, so strip trailing words until the name matches a real task folder.
  task="${name%%-20*}"
  while [ -n "$task" ] && [ ! -d "$HOME/Documents/Claude/Scheduled/$task" ] && [[ "$task" == *-* ]]; do task="${task%-*}"; done
  [ -d "$HOME/Documents/Claude/Scheduled/$task" ] || task="${name%%-20*}"
  if VP_TASK="$task" /usr/bin/python3 "$OS_DIR/bin/vp_slack.py" post "$ch" --file "$f" >/dev/null 2>>"$BOX/outbox.log"; then
    mv "$j" "$SENT/$name.json"; echo "$(date '+%F %T') $name: posted to $ch" >> "$BOX/outbox.log"
  else
    mv "$j" "$FAIL/$name.json"; echo "$(date '+%F %T') $name: vp_slack refused" >> "$BOX/outbox.log"
  fi
done
exit 0
