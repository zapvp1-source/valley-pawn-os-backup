#!/bin/bash
# Native replacement for unified-search-verify — 2026-09-17 (deterministic branch; a FAILED log is ledgered, not "fixed" blind).
AGENT=usearch-verify; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
U="$HOME/Documents/Claude/Projects/Unified Search"; TODAY=$(date +%Y-%m-%d); ST="UNKNOWN"
L=$(tail -c 1500 "$U/refresh_hardened.log" 2>/dev/null | tr '\r' '\n')
if echo "$L" | grep -q "=== hardened success on attempt" && [ "$(stat -f %Sm -t %Y-%m-%d "$U/stats.txt" 2>/dev/null)" = "$TODAY" ]; then ST=SUCCESS
elif pgrep -f refresh_hardened.sh >/dev/null; then ST=RUNNING
elif echo "$L" | grep -q "=== hardened FAILED after"; then ST=FAILED
else ( bash "$U/refresh_hardened.sh" ) > /tmp/usearch_task_run.log 2>&1 < /dev/null & sleep 15; pgrep -f refresh_hardened.sh >/dev/null && ST=RELAUNCHED || ST=FAILED; fi
PH="N/A"; PL=$(tail -8 "$U/photosindex_documents.log" 2>/dev/null | grep "DOCUMENT PHOTOS INDEX DONE" | tail -1)
[ -n "$PL" ] && { echo "$PL" | grep -q "$TODAY" && PH=SUCCESS || PH=STALE; }
echo "$(date +%Y-%m-%dT%H:%M:%S%z) usearch=$ST photos=$PH (native)" >> "$U/verify_runs.log"; vlog "usearch=$ST photos=$PH"
[ "$ST" = "FAILED" ] && ledger "unified-search-verify" "The overnight search index rebuild finished FAILED after 3 attempts — last lines: $(echo "$L" | tail -3 | tr '\n' ' ' | cut -c1-160)" "no"

# ---- STALENESS GATE (added 2026-09-20) -------------------------------------------------
# Why: the index silently rotted for 8 days and this verifier never once ledgered it. Its only
# alarm was the literal "hardened FAILED after 3 attempts" marker, which the wrapper can only
# write if it SURVIVES all 3 attempts. On 9/18 and 9/19 the wrapper was SIGTERM'd mid-attempt-1,
# so the status stayed RELAUNCHED, no row was ever written, and two nights of total failure looked
# identical to a healthy relaunch. A verifier whose alarm depends on the thing it is verifying
# finishing cleanly is not a verifier. This gate asks the only question that actually matters —
# HOW OLD IS THE INDEX — and is independent of how or why any run died.
# Age is measured from stats.txt, the file that is only written when a full chain succeeds.
ST_MTIME=$(stat -f %m "$U/stats.txt" 2>/dev/null || echo 0)
case "$ST_MTIME" in ''|*[!0-9]*) ST_MTIME=0 ;; esac
if [ "$ST_MTIME" -eq 0 ]; then
  AGE_DAYS=999; AGE_TEXT="has never finished a rebuild"; LAST_GOOD="never"
else
  AGE_DAYS=$(( ( $(date +%s) - ST_MTIME ) / 86400 ))
  AGE_TEXT="has not refreshed in $AGE_DAYS days"; LAST_GOOD=$(date -r "$ST_MTIME" '+%b %-d' 2>/dev/null)
fi
STAMP="$U/.stale_ledgered_on"
if [ "$AGE_DAYS" -ge 2 ] && [ "$(cat "$STAMP" 2>/dev/null)" != "$TODAY" ]; then
  echo "$TODAY" > "$STAMP"
  # Plain language only, no jargon (Rule 16). One row per calendar day, never a per-run burst.
  # 2026-09-30: was reading .refresh_attempt.log, which refresh_hardened.sh TRUNCATES (`: > "$ATT"`)
  # at the start of every attempt. By 04:50 the fresh attempt had usually blanked it, so this test
  # was false and the row fell through to the vague wording on the one night it actually mattered
  # (2026-09-25 read "starting but never finishing" instead of naming the permission problem).
  # refresh_hardened.log is append-only, so read the guard state from there instead — but scoped to
  # the MOST RECENT attempt block only. A plain tail would keep matching guard trips from nights
  # already recovered from, and would send the wrong branch for an unrelated future staleness.
  if awk '/hardened attempt/{buf=""} {buf=buf $0 "\n"} END{printf "%s", buf}' \
       "$U/refresh_hardened.log" 2>/dev/null | grep -q "SHRINK GUARD TRIPPED"; then
    # CORRECTED 2026-09-30. A comment here previously claimed Full Disk Access "was never the
    # problem" and told sessions NOT to ask for it. That was wrong, and it was wrong in a
    # specific, instructive way: it tested access at 10:34 on 2026-09-21 — AFTER Joshua granted
    # FDA that same morning — and read post-grant success as proof the grant had never been
    # needed. The CHANGELOG for 2026-09-21 settles it ("FULL DISK ACCESS GRANTED AND PROVEN on
    # all three surfaces"): the 04:50 run logged `found 0 messages`, a hand-run at 10:34 logged
    # `found 349468 messages`, same script and machine six hours apart, and `tmutil latestbackup`
    # plus chat.db's `authorization denied` flipped at the same moment. FDA WAS the cause.
    # So: a TCC grant CAN be silently lost (a macOS update is the likely trigger — that is what
    # happened before 9/18), and if this guard trips on mail or msgs, permissions are the FIRST
    # thing to check, not the last. Check it by straddling: run the indexer by hand and compare
    # to the scheduled run — never by testing access after someone has already changed something.
    ledger "unified-search-verify" \
      "Joshua's mail/text/file search $AGE_TEXT — nothing newer than $LAST_GOOD is findable. The nightly rebuild stopped itself rather than risk damaging the existing index, which is the safe behaviour, but it means the search is going stale. No data has been lost." \
      "possibly — the last time this happened (2026-09-18 to 09-21) the Mac had stopped allowing the overnight job to read Apple Mail and Messages, and one permission change fixed it. Check that first: System Settings > Privacy & Security > Full Disk Access, ~/bin/vp-runner. See CHANGELOG 2026-09-21 and the unified-search skill."
  else
    ledger "unified-search-verify" \
      "Joshua's mail/text/file search $AGE_TEXT. The nightly rebuild is starting but never finishing." \
      "yes — see CHANGELOG 2026-09-18/09-20 and the Open Items Register."
  fi
fi

# ---- EROSION SENSOR (added 2026-09-30) ------------------------------------------------
# Why: on 2026-09-30 ~15,045 .emlx files disappeared from disk in one night (the nightly scan
# went 351,949 -> 336,904). The shrink guard correctly did NOT fire — its floor is 50% and this
# was 4%. The guard's job is stopping a WIPE; nothing was watching for slow EROSION. Worse, the
# drop could not be attributed afterwards, because nothing retained a per-night history to diff
# against: by the time anyone looked, the "before" state had already been overwritten by the
# rebuild. So this appends one line per night and compares to the previous one.
# Deliberately CHEAP: counts come from the `meta` table (instant, no scan) and from the log line
# the mail indexer already prints, which reports DISK. No full-table scan runs here — a per-account
# breakdown costs ~50s and is only worth paying once drift has actually fired (see below).
HIST="$U/index_history.tsv"
[ -f "$HIST" ] || printf 'date\tdisk_found\tmail\tfiles\tmsgs\tnotes\treminders\tgdrive\tphotos\n' > "$HIST"
m() { /usr/bin/sqlite3 "file:$U/index.db?mode=ro" \
        "select coalesce((select v from meta where k='$1'),0);" 2>/dev/null || echo 0; }
DISK=$(grep -oE 'found [0-9]+ messages' "$U/refresh_hardened.log" 2>/dev/null | tail -1 | tr -dc 0-9)
[ -n "$DISK" ] || DISK=0
H_MAIL=$(m mail_count)
if [ "${H_MAIL:-0}" -gt 0 ] && [ "$(cut -f1 "$HIST" | tail -1)" != "$TODAY" ]; then
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$TODAY" "$DISK" "$H_MAIL" \
    "$(m files_count)" "$(m msgs_count)" "$(m notes_count)" "$(m reminders_count)" \
    "$(m gdrive_count)" "$(m photos_count)" >> "$HIST"

  # Compare against the previous night. Alarm on a drop the guard is designed to let through:
  # more than 3% or more than 5,000 messages. One row per day, plain language, ledger only.
  PREV=$(grep -v "^$TODAY" "$HIST" | tail -1 | cut -f3)
  case "$PREV" in ''|*[!0-9]*) PREV=0 ;; esac
  if [ "$PREV" -gt 0 ]; then
    LOST=$(( PREV - H_MAIL ))
    if [ "$LOST" -gt 5000 ] || { [ "$LOST" -gt 0 ] && [ $(( LOST * 100 / PREV )) -ge 3 ]; }; then
      ledger "unified-search-erosion" \
        "Joshua's searchable mail dropped by $LOST messages overnight ($PREV to $H_MAIL) — that is real mail leaving the Mac, not a search problem, and it is too small a drop for the existing safety check to stop. Nothing is broken; the older mail is simply no longer findable." \
        "no — but worth someone establishing WHY before it repeats. Per-account breakdown: see the erosion-sensor note in the unified-search skill. History: Unified Search/index_history.tsv."
    fi
  fi
fi
exit 0
