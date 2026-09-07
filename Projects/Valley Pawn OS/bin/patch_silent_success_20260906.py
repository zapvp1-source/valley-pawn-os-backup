#!/usr/bin/env python3
"""
2026-09-06 — silent-success routing for routine "all clear" posts (Field Communication Standard
v3 §1: an all-clear is an audit trail, not something the team must act on today).

brevo-preflight-watchdog posted a green "Email watchdog: N upcoming send(s) checked..." line into
#email-campiagns EVERY morning (verified 8/25–9/5, daily 07:02). That buries the one weekly post
in that channel that actually carries a decision. Red alerts, seed auto-repairs and the
API-unreachable warning STAY in the channel — only the green line moves to Joshua's DM.

The fleet-guardian marker moves with it (expected_outputs entry re-pointed to the DM), so the
watchdog is still verified against real output, just in the right place.

Idempotent. Backs up both files.
"""
import datetime as dt
import json
import os
import shutil
import sys

SKILL = os.path.expanduser("~/Documents/Claude/Scheduled/brevo-preflight-watchdog/SKILL.md")
MANIFEST = "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/expected_outputs.json"
TODAY = dt.date.today().isoformat()
STAMP = dt.date.today().strftime("%Y%m%d")
MARK = "silent-success 2026-09-06"

OLD = ("- If `failed` == 0 AND `seed_fixes` == 0 AND `seed_hard_fails` == 0 AND `checked` > 0 "
       "→ post a brief green confirmation: `:white_check_mark: Email watchdog: <checked> "
       "upcoming send(s) checked, all carry full Call/Text + UTM instrumentation and the "
       "standing recipient list.`")

NEW = ("- If `failed` == 0 AND `seed_fixes` == 0 AND `seed_hard_fails` == 0 AND `checked` > 0 "
       "→ **SILENT SUCCESS (" + MARK + ").** Post NOTHING to C0APR5WUL2Z. Send the green line "
       "to Joshua's DM (`D03BHQH5VGT`) instead: `:white_check_mark: Email watchdog: <checked> "
       "upcoming send(s) checked, all carry full Call/Text + UTM instrumentation and the standing "
       "recipient list.` A routine all-clear is an audit trail, not something the team must act on "
       "today (Field Communication Standard v3 §1) — daily green lines were burying the one "
       "weekly post in #email-campiagns that carries a decision. Keep the marker text `Email "
       "watchdog:` EXACTLY as written: the fleet-guardian verifies this task by that string, now "
       "in the DM. Everything above this line (red alerts, seed auto-repair confirmations) still "
       "goes to the channel — those are exceptions, and exceptions are what the channel is for.")

README_NOTE = ("2026-09-06 comms review: routine all-clear posts moved off team channels to "
               "Joshua's DM (Field Communication Standard v3 §1). When an entry's output moves, "
               "re-point output/channel_id here in the same change and add a _corrected note — "
               "never leave the guardian verifying a surface the task no longer writes to.")


def patch_skill():
    with open(SKILL, encoding="utf-8") as fh:
        text = fh.read()
    if MARK in text:
        print("skill already patched")
        return False
    if OLD not in text:
        raise SystemExit("green-confirmation line not found verbatim — skill changed; patch by hand")
    shutil.copy2(SKILL, SKILL + ".bak-pre-silent-success-" + STAMP)
    text = text.replace(OLD, NEW)
    text = text.replace(
        "=== STEP 2 — Report to Slack (#email-campaigns, channel ID C0APR5WUL2Z) ===",
        "=== STEP 2 — Report (exceptions → #email-campiagns C0APR5WUL2Z; routine all-clear → Joshua DM D03BHQH5VGT) ===")
    with open(SKILL, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("skill patched")
    return True


def patch_manifest():
    with open(MANIFEST, encoding="utf-8") as fh:
        d = json.load(fh)
    hit = [e for e in d["entries"] if e["task"] == "brevo-preflight-watchdog"]
    if not hit:
        raise SystemExit("manifest entry not found")
    e = hit[0]
    if e.get("channel_id") == "D03BHQH5VGT":
        print("manifest already re-pointed")
        return False
    shutil.copy2(MANIFEST, MANIFEST + ".bak-" + STAMP + "-silentsuccess")
    e["output"] = "slack-dm:Joshua"
    e["channel_id"] = "D03BHQH5VGT"
    e["_corrected"] = (TODAY + " — the routine green 'Email watchdog:' line moved from "
                       "#email-campiagns to Joshua's DM (silent-success, Field Communication "
                       "Standard v3 §1). Same marker string, new surface. Red alerts and seed "
                       "auto-repairs still post to C0APR5WUL2Z; absence of the marker in the DM "
                       "on a day with scheduled sends is the real miss signal. Days with zero "
                       "scheduled sends are silent by design and were always exempt.")
    if isinstance(d.get("_readme"), list) and README_NOTE not in d["_readme"]:
        d["_readme"].append(README_NOTE)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("manifest re-pointed")
    return True


if __name__ == "__main__":
    patch_skill()
    patch_manifest()
    sys.exit(0)
