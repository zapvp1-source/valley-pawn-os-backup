#!/bin/bash
# social_recap.sh — native replacement for Cowork `weekly-social-media-recap` (Mon 09:40, 2026-09-29).
# The SKILL's whole job: run the deterministic formatter; exit 0 -> post stdout VERBATIM to #social-media;
# exit 2 -> post nothing, append the reason to Valley Pawn Studios/STATUS.md under "## Recap holds".
AGENT="weekly-social-media-recap"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 20
SM="$HOME/Documents/Claude/Projects/Refine Social Media"; OUT=/tmp/social_recap_out.txt; ERR=/tmp/social_recap_err.txt
( cd "$SM" && $PY -m vp_social recap --days 7 ) > "$OUT" 2> "$ERR"; RC=$?
if [ $RENDER -eq 1 ]; then echo "=== RENDER ONLY (exit $RC) ==="; cat "$OUT"; tail -3 "$ERR"; exit 0; fi
if [ $RC -eq 0 ] && [ -s "$OUT" ]; then
  VP_TASK="$AGENT" $PY "$BIN/vp_slack.py" post C0BMRC2LN3D --file "$OUT" >/dev/null && vlog "recap posted" \
    || ledger "$AGENT" "This week's social media recap was built but did not post." "no"
elif [ $RC -eq 2 ]; then
  printf -- '- %s (native) %s\n' "$(date '+%Y-%m-%d %H:%M')" "$(tail -1 "$ERR")" >> "$HOME/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md"
  $PY "$BIN/vp_receipt.py" write "$AGENT" --surface file --target "Valley Pawn Studios/STATUS.md" --note "held (formatter exit 2)" >/dev/null 2>&1
  vlog "recap held: $(tail -1 "$ERR")"
else
  ledger "$AGENT" "This week's social media recap could not be built (formatter exit $RC)." "no"; exit 1
fi
