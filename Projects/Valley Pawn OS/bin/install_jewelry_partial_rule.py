#!/usr/bin/env python3
"""install_jewelry_partial_rule.py — Joshua's 2026-09-22 rule for the nightly jewelry count.

"On the jewelry counts only we should post the completed stores since it was an employee error not
a Claude error, and then send the store manager the error message."

Until now the task held the ENTIRE post when one store's paper count sheet was not filled in
(Waynesboro, 9/19 and 9/21). That punished four stores that did their job and told the fifth
nothing. This replaces the all-or-nothing rule for THIS task only, and routes both the channel post
and the manager DM through fleet/outbox/ so neither dies on an unattended approval.
"""
import datetime as dt, os, sys
SCHED = os.path.expanduser("~/Documents/Claude/Scheduled")
TASK = "jewelry-onhand-nightly-pull"
MARK = "PARTIAL-POST RULE (Joshua 2026-09-22)"
BLOCK = """

---

# %s — REPLACES the all-or-nothing rule for this task

Joshua, 2026-09-22: *"On the jewelry counts only we should post the completed stores since it was an
employee error not a Claude error, and then send the store manager the error message."*

So, when the Bravo pull succeeded but a store's paper PM count sheet is missing, unfilled for
tonight's date, or does not sum:

1. **Post the stores that completed.** Build the normal jewelry-count post for every store whose
   Bravo pull AND PM sheet are both good. Add one plain line at the end naming the store(s) left out
   and why in five words or fewer ("Waynesboro — count sheet not filled in").
2. **Send that store's manager the specific problem**, as a DM, plain language, no task ids:
   what was missing (which date block, or which total did not match), and that tonight's company
   post went out without their store. Managers:
   Culpeper `U04C5DL5EKH` (Sandi Cole) · Harrisonburg `U09UTFT4P7X` (Walker Tapley — the roster
   in valley-pawn-context still says Andrew Clark; he is no longer with the company) ·
   Lexington `U09H9ES2LKA` (Uriah Tiglao) · Roanoke `U0631AECK4K` (Benjie Moore) ·
   Waynesboro `U04U136MF6V` (Chadd McClintic).
3. **Both messages go through the outbox, never `slack_send_message`** — in a scheduled run there
   is no one to approve a send and it is declined. For each message: write the text to
   `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/outbox/{task}-<what>-<YYYYMMDD-HHMMSS>.txt`,
   then the envelope `{{"channel": "<channel or user id>", "file": "<that .txt's absolute path>"}}`
   as `.json` with the same base name. Write the `.txt` first. Then stop — do not wait or verify.
4. **Still hold everything** only if the BRAVO side failed (no CSV for a store, or a store's pull
   errored) — that is a Claude/pipeline problem, not an employee one, and half a Bravo picture must
   not be published. Ledger row as before.
5. Nothing about this changes what you compare or how; it changes only what is published when a
   store's people did not do their part.
"""
p = os.path.join(SCHED, TASK, "SKILL.md")
if not os.path.isfile(p):
    print("MISSING SKILL.md"); sys.exit(1)
body = open(p, encoding="utf-8").read()
if MARK in body:
    print("already present"); sys.exit(0)
if "--apply" not in sys.argv:
    print("WOULD ADD partial-post rule to %s" % TASK); sys.exit(0)
stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
open(p + ".bak-partial-" + stamp, "w", encoding="utf-8").write(body)
open(p, "a", encoding="utf-8").write(BLOCK.format(task=TASK) % MARK)
print("ADDED to %s (backup .bak-partial-%s)" % (TASK, stamp))
