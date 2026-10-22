#!/bin/bash
# launchd wrapper — com.valleypawn.online-store-audit, Sunday 08:00 (native, 2026-10-05; was Cowork weekly-online-store-audit).
AGENT="weekly-online-store-audit"; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
vp_lock "$AGENT" 120
"$PY" "$BIN/online_store_audit.py" "$@" >> "$VLOG/$AGENT.log" 2>&1
# 2026-10-21 (online-store audit): keep Rule 2 enforced every week — Best Offer OFF on video games, including the
# listings skipped because a buyer offer was pending. Until 2026-11-15 also retries the August Culpeper revert
# (Joshua yes 9/17) for listings that had a pending offer on 10/21. Script can only ever write BestOfferEnabled=false.
BO_ARGS="--video-games"
[ "$(date +%Y%m%d)" -lt 20261115 ] && BO_ARGS="--video-games --august"
/bin/bash "$BIN/ebay_bestoffer_off.sh" $BO_ARGS --apply >> "$VLOG/$AGENT.bestoffer_off.log" 2>&1 || true
