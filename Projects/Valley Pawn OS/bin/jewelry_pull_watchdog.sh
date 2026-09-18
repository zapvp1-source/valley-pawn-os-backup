#!/bin/bash
# Native replacement for jewelry-pull-watchdog — 2026-09-17. One plain DM only when last night's pull produced nothing.
AGENT=jewelry-pull-watchdog; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
Y=$(date -v-1d +%Y-%m-%d); [ "$(date -v-1d +%u)" = "7" ] && exit 0
ls "$BRAVO/output/" | grep -q "^${Y}_.*jewelry-case-counts" && { vlog "ok: $Y counts on disk"; exit 0; }
slack dm "Heads up — last night's jewelry count pull didn't run (no data for $Y). It will try again at the next 8:30 PM run." && vlog "DM sent"
