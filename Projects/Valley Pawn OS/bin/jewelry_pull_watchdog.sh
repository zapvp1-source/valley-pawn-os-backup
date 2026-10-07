#!/bin/bash
# Native replacement for jewelry-pull-watchdog — 2026-09-17. One plain DM only when last night's pull produced nothing.
AGENT=jewelry-pull-watchdog; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
# 2026-10-06: the Monday skip now logs a line. It used to exit silently, so every Tuesday 02:10 the
# fleet doctor saw a 41h+ gap on a daily agent and called it "gone quiet" (stores closed Sunday = no pull).
Y=$(date -v-1d +%Y-%m-%d); [ "$(date -v-1d +%u)" = "7" ] && { vlog "skip: $Y was a Sunday (stores closed, no pull to check)"; exit 0; }
ls "$BRAVO/output/" | grep -q "^${Y}_.*jewelry-case-counts" && { vlog "ok: $Y counts on disk"; exit 0; }
slack dm "Heads up — last night's jewelry count pull didn't run (no data for $Y). It will try again at the next 8:30 PM run." && vlog "DM sent"
