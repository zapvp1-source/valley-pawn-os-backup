#!/bin/bash
# ceo_brief_deliver.sh — native (no-Claude) delivery of the Weekly CEO Brief PDF:
#   (1) emailed as an attachment via Apple Mail (account jdavis@fcfpawn.com -> Joshua's two addresses)
#   (2) uploaded into Joshua's Slack DM as a file attachment (vp_slack.py, bot token from Keychain)
# Added 2026-10-09 (additive). Invoked by a one-line fleet/host_queue job that the CEO Weekly Brief task drops
# after it writes outbox/READY.pdf (+ READY.subject, READY.body). Each leg is independent and idempotent: a leg
# that succeeded leaves a marker so a retry never double-sends; READY.pdf moves to sent/ only when BOTH are done.
# Rule 16: nothing technical is ever posted to Slack; status lives in outbox/LAST_DELIVERY.txt and the vp log.
OS="$HOME/Documents/Claude/Projects"
BIN="$OS/Valley Pawn OS/bin"
D="$OS/Communcations/ceo-scorecard/outbox"
mkdir -p "$D/sent"
PDF="$D/READY.pdf"
[ -f "$PDF" ] || { echo "no READY.pdf — nothing to deliver"; exit 0; }
SUBJ="Valley Pawn — Weekly CEO Brief"; [ -s "$D/READY.subject" ] && SUBJ="$(head -1 "$D/READY.subject")"
BODY="Your weekly CEO brief is attached (one page)."; [ -s "$D/READY.body" ] && BODY="$(cat "$D/READY.body")"
STAMP="$(date +%Y%m%d-%H%M%S)"
SHA="$(/usr/bin/shasum "$PDF" | cut -c1-8)"
# attach/upload under a readable name (not READY.pdf): outbox/READY.name may hold it, else dated default
NICE="Valley-Pawn-Weekly-CEO-Brief-$(date +%Y-%m-%d).pdf"; [ -s "$D/READY.name" ] && NICE="$(head -1 "$D/READY.name")"
ATT="$D/sent/$NICE"; cp -p "$PDF" "$ATT"   # markers are per-PDF so a stale marker can never suppress next week's send
RC=0

# --- leg 1: email via Apple Mail ---
if [ ! -f "$D/.emailed-$SHA" ]; then
  /usr/bin/osascript - "$SUBJ" "$BODY" "$ATT" <<'OSA'
on run argv
  set theSubject to item 1 of argv
  set theBody to item 2 of argv
  set thePath to item 3 of argv
  tell application "Mail"
    set msg to make new outgoing message with properties {subject:theSubject, content:theBody & return & return, sender:"jdavis@fcfpawn.com", visible:false}
    tell msg
      make new to recipient at end of to recipients with properties {address:"jdavis@fcfpawn.com"}
      make new to recipient at end of to recipients with properties {address:"zapvp1@me.com"}
      make new attachment with properties {file name:(POSIX file thePath as alias)} at after the last paragraph
    end tell
    delay 3
    send msg
  end tell
end run
OSA
  if [ $? -eq 0 ]; then touch "$D/.emailed-$SHA"; echo "EMAIL ok $STAMP"; else echo "EMAIL failed $STAMP"; RC=1; fi
else echo "EMAIL already sent"; fi

# --- leg 2: Slack DM file upload ---
if [ ! -f "$D/.slacked-$SHA" ]; then
  if /usr/bin/python3 "$BIN/vp_slack.py" upload U03BB52MDSA "$ATT" "$SUBJ"; then touch "$D/.slacked-$SHA"; echo "SLACK ok $STAMP"
  else echo "SLACK failed $STAMP"; RC=1; fi
else echo "SLACK already sent"; fi

# Archive the PDF whenever the EMAIL leg is done so a stuck Slack leg can never block the next week's run.
# Slack-upload problems (e.g. the bot token missing the files:write scope) are handed to the cloud task, which
# finishes the DM leg through the Slack connector (brief text + Drive link) and records it.
if [ -f "$D/.emailed-$SHA" ]; then
  mv "$PDF" "$D/sent/CEO-BRIEF-$STAMP.pdf"
  if [ -f "$D/.slacked-$SHA" ]; then
    echo "DELIVERED both legs $STAMP" > "$D/LAST_DELIVERY.txt"
  else
    echo "EMAIL delivered; SLACK-FILE pending $STAMP (sent/CEO-BRIEF-$STAMP.pdf) - cloud task completes the DM leg" > "$D/LAST_DELIVERY.txt"
  fi
  rm -f "$D/.emailed-$SHA" "$D/.slacked-$SHA" "$D/READY.subject" "$D/READY.body" "$D/READY.name"
else
  echo "EMAIL NOT DELIVERED $STAMP - READY.pdf kept for retry" > "$D/LAST_DELIVERY.txt"
fi
cat "$D/LAST_DELIVERY.txt"
exit $RC
