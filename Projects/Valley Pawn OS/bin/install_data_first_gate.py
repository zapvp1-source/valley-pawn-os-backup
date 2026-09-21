#!/usr/bin/env python3
"""install_data_first_gate.py — unblock the Monday chain without rewriting it.

THE PROBLEM (confirmed 2026-09-20). The `Control_your_Mac` connector was REMOVED — Joshua checked
his settings, it is not listed, and `list_connectors` is empty. There is no toggle to flip. Eleven
of the twelve weekly Monday tasks gate on it at step 0, so they fire every Monday, hit a tool that
does not exist, and publish nothing. Three Mondays lost that way.

WHY NOT JUST CONVERT THEM. The three daily reports were convertible because their analysis lives in
standalone scripts (run_daily_intake.py and friends) that a native agent can call. The Monday
reports have no such scripts — the analysis lives inside the SKILLs themselves. Converting them
means REWRITING that analysis, which is not honest work to attempt in one night against a Monday
deadline, and a rushed rewrite of a report people act on is worse than a late report.

THE ACTUAL INSIGHT. That step-0 gate exists to PULL DATA. As of today the data arrives by another
route: `com.valleypawn.monday-pull`, a native agent that owes nothing to the dead connector, puts
the CSVs on disk every Sunday. So the gate is asking for permission to do something already done.
This prepends an override telling each task to look on disk FIRST and proceed if the data is there.

This is a bridge, not the destination. It restores the reports now; converting the analysis to
native scripts remains the durable fix, and the override says so in the file so no one mistakes it
for finished work.

Idempotent, backs up every file, and reports any task whose name does not match a Scheduled/ folder
rather than inventing one.

    install_data_first_gate.py            # dry run
    install_data_first_gate.py --apply
"""
import datetime as dt
import os
import sys

HOME = os.path.expanduser("~")
SCHED = os.path.join(HOME, "Documents/Claude/Scheduled")
MARK = "DATA-FIRST GATE OVERRIDE"

# The 11 flagged by dep_scan.py. weekly-timekeeping-analysis is excluded — it has no host-shell
# dependency and does not need this.
TASKS = ["monday-bravo-combined-run", "monday-bravo-combined-compile", "monday-bravo-postcheck",
         "monday-bravo-cell-gapfill", "weekly-store-kpis", "weekly-returns-summary",
         "nics-weekly-mtd-ranking", "layaway-yield-weekly", "review-obtained-last-week",
         "weekly-markdown-verification-pull", "weekly-markdown-verification-review"]

BLOCK = """

---

# %s (2026-09-20) — READ THIS BEFORE STEP 0

**The `Control_your_Mac` / `osascript` connector no longer exists.** It was removed, not disabled —
Joshua confirmed on 2026-09-20 that it is not in his connector list. Any step in this file that
waits for it will wait forever. That is why this task fired on 9/14 and 9/21-eve and published
nothing three Mondays running.

**The data it was going to fetch is already on disk.** A native agent
(`com.valleypawn.monday-pull`, Sundays 16:30) pulls it and owes nothing to that connector.

So, replacing step 0:

1. **Look on disk first.** Check `Bravo Data Extraction/output/` for today's or yesterday's CSVs
   for the reports you need — `aged-inventory-summary`, `loans-75-days-past-due`, `layaways`,
   `employee-activity`, `chekkit-inactives`. Filenames look like
   `2026-09-20..2026-09-20_CUL_aged-inventory-summary.csv` or `2026-09-20_CUL_employee-activity.csv`.
2. **If the data is there, PROCEED.** Do not look for `osascript`, do not check for
   `Control_your_Mac`, do not stop because a pull step is unavailable. The pull already happened.
3. **Check the certificate** at `Bravo Data Extraction/logs/_monday_pull_status_<date>.txt`. It says
   `ALL CLEAN` or names which reports came back incomplete.
4. **If data for a store you need is MISSING, do not publish a partial picture.** The all-or-nothing
   rule still stands. Write one row to `fleet/FAILURE_LEDGER.md` naming exactly which store and
   report are missing, post nothing, and stop. A missing store is a real gap, not a formatting
   problem.
5. **Never drive Bravo directly from this task.** Not through computer-use, not through Parallels.
   The pull is a native agent's job and two things driving that VM at once is how it wedges.

If you genuinely need a pull that has not happened, drop a job in
`Valley Pawn OS/fleet/host_queue/` — a native runner picks it up within about two minutes. That is
the sanctioned host path now. It is allow-listed, so only vetted scripts in `bin/` will run.

**This is a bridge, not the finished fix.** The durable repair is moving this report's analysis into
a script a native agent can run, the way the daily pawn-walk / sold / discount reports work. Until
that happens this task still depends on a Cowork session firing — it just no longer depends on a
connector that does not exist.
""" % MARK


def main():
    apply = "--apply" in sys.argv
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    done = skipped = missing = 0
    for task in TASKS:
        path = os.path.join(SCHED, task, "SKILL.md")
        if not os.path.isfile(path):
            print("MISSING  %-38s no SKILL.md" % task)
            missing += 1
            continue
        body = open(path, encoding="utf-8").read()
        if MARK in body:
            print("already  %-38s override present" % task)
            skipped += 1
            continue
        if not apply:
            print("WOULD ADD %-37s" % task)
            done += 1
            continue
        with open(path + ".bak-datafirst-" + stamp, "w", encoding="utf-8") as f:
            f.write(body)
        with open(path, "a", encoding="utf-8") as f:
            f.write(BLOCK)
        print("ADDED    %-38s" % task)
        done += 1
    print("\n%s: %d written, %d already had it, %d not found"
          % ("APPLIED" if apply else "DRY RUN", done, skipped, missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
