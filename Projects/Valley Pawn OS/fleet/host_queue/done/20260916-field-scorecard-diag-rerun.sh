#!/bin/bash
# HOST JOB — Phase 0.4 follow-up. The first field-scorecard run found most Slack entries came
# back "channel_not_found"/"not_in_channel" even for channels confirmed to exist and be active
# (verified via the Cowork Slack connector in-session). This job (1) identifies which Slack bot
# identity the native "vp-ops-slack-bot-token" belongs to, (2) re-runs field_scorecard.py with
# its new self-join fallback (auto-joins PUBLIC channels it can see but hasn't joined), and
# (3) reports which channels still fail after that, so those specific ones can be flagged to
# Joshua as a one-time manual /invite (private channels only — nothing else needed).
set +e
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
BIN="$OS/bin"
echo "=== field-scorecard diag/rerun start $(date) ==="

echo; echo "--- which bot does the native Keychain token belong to? ---"
TOK=$(security find-generic-password -s vp-ops-slack-bot-token -a "$(whoami)" -w 2>/dev/null)
if [ -n "$TOK" ]; then
  curl -s -H "Authorization: Bearer $TOK" https://slack.com/api/auth.test
  echo
else
  echo "NO TOKEN FOUND in Keychain under vp-ops-slack-bot-token"
fi

echo; echo "--- re-run field_scorecard.py (with self-join fallback) ---"
/usr/bin/python3 "$BIN/field_scorecard.py" 2>&1
echo "rc=$?"

echo; echo "--- entries still UNVERIFIED after self-join (need a one-time manual /invite, or a stale channel_id) ---"
grep "UNVERIFIED" "$OS/fleet/FIELD_SCORECARD.md" || echo "none — all Slack entries resolved"

echo "=== field-scorecard diag/rerun done $(date) ==="
