#!/bin/bash
# mail_brief.sh — native replacement for daily-unopened-email-eval (worst task in the fleet, 1/7 days).
#
# WHY: that task drove Mail.app through the Control_your_Mac connector, which is permanently absent
# from scheduled sessions (probe, 2026-09-21). It reads Apple Mail's own Envelope Index instead —
# proven readable by vp-runner on 2026-09-21, contradicting the Full Disk Access theory that had
# been blamed for 9 days.
#
# No Claude session, no osascript, no computer-use. Gets the publish guard and the publication
# receipt for free by going through vp_slack.py.
AGENT="daily-unopened-email-eval"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 20

OUT="/tmp/mail_brief_$(date +%Y%m%d).txt"
$PY "$BIN/mail_unread.py" --hours 24 > "$OUT" 2>/dev/null || {
  ledger "$AGENT" "Could not read the mail index for today's unopened-email check." "no"; exit 1; }

N=$(grep -oE '^\*\*[0-9]+ unopened' "$OUT" | grep -oE '[0-9]+' | head -1)
[ -z "$N" ] && { ledger "$AGENT" "Mail index read but the unopened count could not be parsed — not posting a number I cannot stand behind." "no"; exit 1; }

# Build the message. Plain language, no task ids, no jargon (Rule 16).
MSG="/tmp/mail_brief_msg_$(date +%Y%m%d).txt"
{
  printf ':mailbox_with_mail: *Unopened mail — last 24 hours*\n\n'
  printf '*%s* unopened.\n\n' "$N"
  grep '^- ' "$OUT" | head -15
  printf '\n_Read straight from Apple Mail. Senders and subjects only — no message bodies._\n'
} > "$MSG"

if [ $RENDER -eq 1 ]; then
  echo "=== RENDER ONLY — nothing published ==="; cat "$MSG"; exit 0
fi

# Silent when there is nothing to say: a zero-unopened day needs no DM (Rule 16 — no noise).
if [ "$N" -eq 0 ]; then vlog "0 unopened — staying quiet"; exit 0; fi

slack dm "$(cat "$MSG")" >/dev/null && vlog "brief sent ($N unopened)" \
  || { ledger "$AGENT" "Unopened-mail brief compiled ($N) but Slack refused the DM." "no"; exit 1; }
vlog "=== mail brief done ==="
