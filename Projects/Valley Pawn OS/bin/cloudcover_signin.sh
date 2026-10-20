#!/bin/bash
# cloudcover_signin.sh — RETIRED 2026-10-19: every native browser check now shares ONE automation profile
# (~/Library/Application Support/valleypawn/pw-vp) and ONE sign-in window. This name is kept only so older
# ledger rows / notes that point at it still work; it just runs bin/vp_signin_front.sh (4 tabs, in front).
exec /bin/bash "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_signin_front.sh" "$@"
