#!/bin/bash
# monday_pull.sh — native Sunday-evening pull of the data the Monday reports need.
#
# WHY (2026-09-20). The 9/12-9/17 outage had ONE cause: the osascript/Control_your_Mac connector
# disappeared from scheduled sessions. On 9/17 that was fixed for ELEVEN DAILY tasks by converting
# them to native launchd agents — and the WEEKLY Monday chain was never converted. Proof, not
# inference: the registry shows all 12 weekly tasks FIRED on 9/14 and published nothing, they are
# all enabled with correct next-run times, and a scan of their SKILLs shows 11 of 12 still gate on
# that connector at step 0. It is still absent today. So Monday 9/21 fails exactly like 9/14 unless
# the DATA is already on disk before those tasks wake up.
#
# This is the same shape as morning_pull.sh, which has been working since 9/18: drop triggers into
# the Bravo queue, poll for results, gate on integrity, write an honest certificate. No Claude
# session, no osascript, no computer-use.
#
# It does NOT publish anything. Its only job is to put CSVs on disk so the Monday compile steps
# have something real to read. Publishing stays where it is until each report is converted too.
#
# RUNS TWICE: Sunday 16:30 AND Monday 05:30. That is not belt-and-braces, it is a correctness fix.
# The Sunday-only schedule (my first version) stamped every CSV with SUNDAY's date, and the Monday
# tasks look for TODAY's date — so monday-bravo-combined-compile reported on 2026-09-21 that "today's
# data pull did not include that report at all for any store" while all 25 files sat on disk under
# 2026-09-20. The Sunday run still matters for the Sunday-evening tasks (markdown-pull 19:00,
# cell-gapfill 20:30); the Monday 05:30 run is what the Monday reports actually read.
AGENT="monday-pull"
. "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
RENDER=0; for a in "$@"; do [ "$a" = "--render" ] && RENDER=1; done
[ $RENDER -eq 0 ] && vp_lock "$AGENT" 90

TODAY=$(date +%Y-%m-%d)
CERT="$BRAVO/logs/_monday_pull_status_${TODAY}.txt"

# The reports the Monday chain consumes, under the names the PIPELINE actually knows. These were
# read out of the pipeline's own docs and output history — never guessed. A wrong name does not
# error, it returns nothing, which is the silent-success failure this whole effort exists to kill.
REPORTS="aged-inventory-summary loans-75-days-past-due layaways employee-activity chekkit-inactives"
# --only <report>: validate ONE report name against the live pipeline before trusting all five.
# A wrong name returns nothing rather than erroring, so the names have to be proven, not assumed —
# and proving them at 01:00 Sunday is free, while discovering them wrong at 16:30 costs the Monday.
for i in $(seq 1 $#); do
  [ "${!i}" = "--only" ] && { j=$((i+1)); REPORTS="${!j}"; }
done

OPEN=$(open_stores "$TODAY")
# Sunday is closed, but this job RUNS on Sunday to prepare Monday — pull for all five stores, since
# Monday is a normal trading day. Using open_stores("$TODAY") here would return nothing and the job
# would silently do nothing at all, which is exactly the class of bug being fixed.
STORES="CUL HAR LEX ROA WAY"
vlog "=== monday pull for $TODAY (stores: $STORES) ==="

if [ $RENDER -eq 1 ]; then
  echo "=== RENDER ONLY — no Bravo contact, nothing pulled, nothing published ==="
  echo "would pull, for stores [$STORES]:"
  for r in $REPORTS; do echo "  - $r"; done
  echo "would write certificate -> $CERT"
  exit 0
fi

health_gate 900 >/dev/null || { ledger "$AGENT" "Sunday prep pull could not start — Bravo did not come up healthy, so Monday's reports will have no fresh data." "yes"; exit 1; }

# Count today's CSVs for a report. Dated-filename match only — an old file from a previous week
# must never be read as today's success.
have() {  # have <report> ; echo count
  local r="$1" n=0 s
  for s in $STORES; do
    ls "$BRAVO/output/${TODAY}"*"_${s}_${r}.csv" >/dev/null 2>&1 && n=$((n+1))
  done
  echo $n
}

# Poll for the CSVs themselves, NOT for a result.json.
#
# CORRECTED 2026-09-20 — the first version of this comment was wrong and is kept honest here rather
# than quietly deleted. I saw a probe write four CSVs with no results/<id>.result.json and concluded
# "these handlers don't emit one". They DO — it is written at the END, after every store finishes.
# I had simply looked while the run was still going.
#
# Polling the CSVs is still the right call, for reasons that survive the correction:
#   * per-store progress is visible (4/5 vs 0/5), where the result file is all-or-nothing at the end;
#   * a partial pull can be retried for just the stragglers instead of re-running all five stores;
#   * the CSV is the actual deliverable the Monday reports read, and Rule 12 says verify against
#     output, not against a run record — a result file is a run record.
pull() {  # pull <report> <timeout_s> ; echoes how many of the 5 stores landed
  # EVERY log line in here goes to stderr. vlog tees to stdout, so a single unredirected vlog
  # makes $(pull ...) return log text instead of a number — which it did on the first live run,
  # turning a genuine 5/5 into '[: integer expression expected' and a pointless retry.
  local r="$1" tmo="$2" id t0 n healed=0 unclaimed
  id="monday-${r}-$(date +%Y-%m-%dT%H-%M-%S)"
  # same trigger envelope bravo_run writes — written directly so completion can be judged by the
  # CSVs rather than by a result.json these handlers do not always emit
  printf '{"id":"%s","requested_at":"%s","reports":[%s]}' \
    "$id" "$(date +%Y-%m-%dT%H:%M:%S%z)" \
    "{\"name\":\"$r\",\"stores\":[$(stores_json "$STORES")],\"date\":\"$TODAY..$TODAY\"}" \
    > "$BRAVO/triggers/$id.json"
  vlog "trigger written: $id" >&2
  t0=$(date +%s)
  while [ $(( $(date +%s) - t0 )) -lt "$tmo" ]; do
    n=$(have "$r")
    [ "$n" -eq 5 ] && { vlog "$r complete: 5/5" >&2; echo 5; return 0; }
    sleep 20
    # one self-heal if the watcher never even claimed the trigger (same rule bravo_run uses)
    unclaimed=0; [ -f "$BRAVO/triggers/$id.json" ] && unclaimed=1
    if [ $healed -eq 0 ] && [ $unclaimed -eq 1 ] && [ $(( $(date +%s) - t0 )) -gt 180 ]; then
      vlog "self-heal: $id still unclaimed after 3 min" >&2
      if bravo_procs | grep -q Bravo.exe; then watcher_restart; else bravo_relaunch; fi
      healed=1; sleep 120
    fi
  done
  have "$r"
}

RESULTS=""
FAILED=""
for r in $REPORTS; do
  vlog "--- pulling $r ---"
  n=$(pull "$r" 1500)
  if [ "$n" -eq 5 ]; then
    RESULTS="$RESULTS $r:CLEAN"
  else
    vlog "$r came back $n/5 — one retry for the stragglers"
    n=$(pull "$r" 900)
    if [ "$n" -eq 5 ]; then RESULTS="$RESULTS $r:CLEAN(retry)"
    else RESULTS="$RESULTS $r:PARTIAL($n/5)"; FAILED="$FAILED $r"; fi
  fi
  vlog "$r -> $n/5"
done

{
  echo "monday pull $TODAY $(date +%H:%M)"
  echo "stores: $STORES"
  for x in $RESULTS; do echo "  $x"; done
  [ -n "$FAILED" ] && echo "INCOMPLETE:$FAILED" || echo "ALL CLEAN"
} > "$CERT"
vlog "certificate: $(tr '\n' ' ' < "$CERT")"

if [ -n "$FAILED" ]; then
  # Rule 16: no jargon to a team channel. One ledger row; the Monday tasks will see the certificate
  # and can decide for themselves rather than publishing half a picture.
  ledger "$AGENT" "Sunday prep pull for Monday's reports came back incomplete ($FAILED). Monday's affected reports will hold rather than post partial numbers." "no"
  exit 1
fi
vlog "=== monday pull done — all reports on disk ==="
