#!/usr/bin/env python3
"""install_receipt_step.py — append the publication-receipt step to every scheduled task whose
manifest entry is scored by receipt (output == "receipt").

WHY: those tasks publish to a Slack DM or a Slack canvas. Neither has message history the audit bot
can read, so for as long as they have existed "it ran and delivered" and "it never ran" have looked
identical from outside. The receipt is the evidence. It only exists if the task writes it, so the
instruction has to live in the task's own SKILL.md.

SAFE BY CONSTRUCTION: idempotent (a SKILL that already mentions vp_receipt.py is skipped), additive
(appends at the end, never edits existing steps), backed up before every write, and it reports every
task it could not find instead of guessing. Run it again any time a new receipt entry is added.

    install_receipt_step.py            # dry run — prints exactly what it WOULD do
    install_receipt_step.py --apply
"""
import datetime as dt
import json
import os
import sys

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
MANIFEST = os.path.join(OS_DIR, "fleet/expected_outputs.json")
SCHEDULED = os.path.join(HOME, "Documents/Claude/Scheduled")
RECEIPT = os.path.join(OS_DIR, "bin/vp_receipt.py")

BLOCK = """

## Final step (MANDATORY) — write the publication receipt

This task publishes to a surface with no readable history (a DM or a Slack canvas), so this receipt
is the ONLY evidence the task ran and delivered. Without it, a healthy run and a dead task are
indistinguishable in the fleet audit, and this task will read as AWAITING RECEIPTS forever.

Run this as the LAST action of the task, only after the publication actually succeeded:

```bash
python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_receipt.py" write {task} \\
  --surface {surface} --target "{target}" --note "<first line of what you published>"
```

Rules:
- Write it ONLY on a real, confirmed send. Never write a receipt for something you did not publish.
- If the task is silent by design this run (nothing to report), still write the receipt, with
  `--note "checked, nothing to report"`. Recording the look is what makes the silence trustworthy.
- If the publication FAILED, write it with `--ok false` and the reason in `--note`. Do not post the
  failure to Slack (Rule 16).
"""


def main():
    apply = "--apply" in sys.argv
    entries = [e for e in json.load(open(MANIFEST))["entries"] if e.get("output") == "receipt"]
    if not entries:
        print("no receipt-scored entries in the manifest — nothing to do")
        return 0
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    done = skipped = missing = 0
    for e in sorted(entries, key=lambda x: x["task"]):
        task = e["task"]
        former = (e.get("_former_output") or "")
        surface = "canvas" if "canvas" in task or "canvas" in former else \
                  ("slack-dm" if "dm" in former else "slack-dm")
        target = e.get("_former_canvas_id") or e.get("_former_channel_id") or "D03BHQH5VGT"
        path = os.path.join(SCHEDULED, task, "SKILL.md")
        if not os.path.isfile(path):
            print("MISSING  %-38s no SKILL.md at Scheduled/%s/" % (task, task))
            missing += 1
            continue
        body = open(path, encoding="utf-8").read()
        if "vp_receipt.py" in body:
            print("already  %-38s receipt step present" % task)
            skipped += 1
            continue
        block = BLOCK.format(task=task, surface=surface, target=target)
        if not apply:
            print("WOULD ADD %-37s surface=%s target=%s" % (task, surface, target))
            done += 1
            continue
        with open(path + ".bak-" + stamp, "w", encoding="utf-8") as f:
            f.write(body)
        with open(path, "a", encoding="utf-8") as f:
            f.write(block)
        print("ADDED    %-38s surface=%s target=%s" % (task, surface, target))
        done += 1
    print("\n%s: %d written, %d already had it, %d SKILL.md not found"
          % ("APPLIED" if apply else "DRY RUN", done, skipped, missing))
    if missing:
        print("A missing SKILL.md means the task name in the manifest does not match the Scheduled/ "
              "folder name. Fix the manifest — do NOT create a folder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
