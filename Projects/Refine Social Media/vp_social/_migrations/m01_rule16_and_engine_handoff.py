#!/usr/bin/env python3
"""
Migration 01 (2026-09-06) — social scheduled-task prompt sweep.

Two jobs:
  A. Rule 16 compliance. Every social task carries one or both of the pre-Rule-16
     failure blocks: the v2 "send Joshua ONE plain-language Slack DM ... did not
     complete" policy and the older "DO NOT POST TO SLACK ON FAILURE" policy. Rule 16
     (2026-08-24) supersedes both: failure notices never go to Slack at all, including
     Joshua's DM; technical detail goes to a status file. Twelve+ such DMs reached
     Joshua in the three weeks to 2026-09-05, several of them false alarms.
  B. Engine handoff. Point the reporting tasks at `python3 -m vp_social ...` so counts
     come from the ledger instead of ad-hoc Publer queries that silently undercounted
     5-6x, and record the routing/timing corrections the prompts had drifted away from.

Safety: frontmatter is never touched (everything above the second `---`). Every file is
backed up to SKILL.md.bak-pre-vpsocial-20260906 before writing. Idempotent — re-running
makes no further changes. Prints a per-file diffstat.
"""
from __future__ import annotations
import difflib
import re
import sys
from pathlib import Path

SCHED = Path.home() / "Documents/Claude/Scheduled"
BAK = ".bak-pre-vpsocial-20260906"
RSM = "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media"
STATUS = "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md"

RULE16 = (
    "> ⚠️ **FAILURE HANDLING (Rule 16, supersedes the 2026-07-22 v2 DM policy — updated 2026-09-06).** "
    "Failure notices NEVER go to Slack — not to a team channel, not to a store manager, and not to "
    f"Joshua's DM. If this run fails or cannot complete its core work, append one dated plain-language "
    f"line plus the technical detail to `{STATUS}` under a `## Run holds` heading and stop. The next "
    "session picks it up from there. Anything that does go to the field stays in plain everyday language "
    "— no error codes, no tool or file names. This replaces every 'DM Joshua that it did not complete' "
    "and every 'stay silent on Slack' instruction elsewhere in this file."
)

FAIL_V2 = re.compile(r"^>?\s*⚠️\s*\*{0,2}FAILURE ALERT POLICY.*$", re.M)
FAIL_OLD = re.compile(r"^>?\s*⚠️\s*\*{0,2}FAILURE POLICY\s*[—-]\s*DO NOT POST TO SLACK ON FAILURE.*$", re.M)

TASKS_RULE16 = [
    "weekly-social-media-recap", "vp-publer-analytics-friday", "vp-deals-social-wednesday",
    "vp-content-batch-weekly", "vp-content-batch-postflight", "vp-content-batch-preflight",
    "vp-casual-video-daily", "vp-deal-of-week-monday-prompt", "vp-deal-of-week-monday-pick",
    "vp-staff-video-chase", "vp-engagement-weekly", "vp-community-weekly",
    "vp-deal-reels-weekly", "vp-comedy-reel-weekly", "vp-follower-growth-monthly-check",
]


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    cut = text.find("\n", end + 1) + 1
    return text[:cut], text[cut:]


def apply_rule16(body: str) -> str:
    if "FAILURE HANDLING (Rule 16" in body:
        return body
    hits = list(FAIL_V2.finditer(body)) + list(FAIL_OLD.finditer(body))
    if not hits:
        return body
    first = min(hits, key=lambda m: m.start())
    body = body[:first.start()] + RULE16 + body[first.end():]
    body = FAIL_V2.sub("", body)
    body = FAIL_OLD.sub("", body)
    if "FAILURE HANDLING (Rule 16" not in body:          # first hit got swept by the global sub
        body = RULE16 + "\n\n" + body
    return re.sub(r"\n{4,}", "\n\n\n", body)


# --- per-file surgical edits ------------------------------------------------

RECAP_STEPS = f"""## Steps

1. Produce the recap with the deterministic formatter (osascript):
   `do shell script "cd '{RSM}' && python3 -m vp_social recap --days 7 2>/dev/null"`
   - **exit 0** — stdout IS the Slack message. Post it to `C0BMRC2LN3D` (#social-media) **verbatim**
     via `slack_send_message`. Do not reformat it, do not add a preamble, do not recompute a number.
   - **exit 2** — stdout is empty on purpose (Rule 18: withhold, don't caveat). Post NOTHING and append
     the stderr line to `{STATUS}` under `## Recap holds`.

2. That is the whole job. There is no marker extraction, no zero-post special case, and no fallback
   to hand-counting: a zero week is itself treated as a withhold condition by the formatter, because
   every real zero week to date has been a read failure, not an actual outage.

**WHY (2026-09-06):** the previous step ran `weekly_social_recap.py`, which called Publer's `/posts`
with no `from`/`to`. Publer silently returns a default slice, so the recap reported 15 posts for
Aug 24-31 when 88 had actually published, and 16 for Aug 17-24 when the real number was 47. The
August month-in-review inherited the error. `python3 -m vp_social recap` reads the local ledger,
which is synced from Publer with explicit date ranges and full pagination. `weekly_social_recap.py`
is left on disk but is no longer the source of the number.

**Timing note:** this task fires Monday 9:40 AM and covers the PRIOR seven days. The weekly content
batch fires later the same day (Mon 1:40 PM, postflight 4:40 PM), so this recap never includes
today's batch — that is intended, not a gap.
"""

DEALS_WED_STEP0 = f"""## Step 0 — MANDATORY duplicate check before anything else

The Monday batch (`vp-content-batch-weekly`) and the deal reels lane already publish this week's
Deal of the Week items. On 2026-09-02 this task re-posted all five deals a second time; Culpeper's
tiller landed on the same page three times in three days.

1. `do shell script "cd '{RSM}' && python3 -m vp_social sync --back 7 --forward 14"`
2. For each store, check the ledger before staging anything:
   `sqlite3 '{RSM}/state/social_ledger.sqlite' "select account_key, scheduled_date, substr(text,1,60) from posts where account_key in ('<Store>','GBP_<Store>') and scheduled_date >= date('now','-2 day') and state in ('scheduled','published')"`
3. If that store's page already has a post for the same product this week, **skip that store entirely**.
   Only fill genuine gaps. Never publish the same deal photo twice to one page.

**Routing (2026-08-04 redesign):** store deal items go to that store's Facebook Page + that store's
Google Business Profile ONLY. Brand IG is not a store-local target — do not add it.

**Submission cutoff is Monday 12:00 PM ET** (not end-of-day Tuesday).
"""

BATCH_ADDENDUM = f"""
## ADDENDUM 2026-09-06 — engine handoff (read this BEFORE Step 11)

1. **Publish through the engine's client, never a bare `PublerClient`.** Any Python this run writes
   must do `sys.path.insert(0, "{RSM}")` then `from vp_social.publish import Publisher` and use
   `Publisher()`. It carries the browser User-Agent (Cloudflare 1010), refuses the bulk
   `DELETE /posts` that wiped 63 queued posts on 2026-08-22, and accepts Publer's `"complete"` job
   status — the base client only accepts `"completed"`, which is why every batch since August logged
   5 phantom `JOB_timeout` entries for items that had actually published.

2. **De-duplicate against the ledger before scheduling.**
   `cd '{RSM}' && python3 -m vp_social sync --back 7 --forward 14`
   then skip any (item, page) pair that already has a post that week. Three lanes were independently
   picking the same Deal of the Week.

3. **Do NOT generate Community or Humor items.** `vp-community-weekly` owns community and
   `vp-comedy-reel-weekly` owns humor, each with its own cooldown state in `creative_state.json`.
   Generating them here as well breached the 1-humor-per-week cap and doubled community volume.

4. **Timing (corrected):** this task fires **Monday 1:40 PM ET**; preflight 11:00 AM; postflight
   4:40 PM. Any text in this file that says 2:02 AM, "90 minutes later", or 3:30 AM is stale.

5. **Routing (corrected, 2026-08-04):** Brand items → Brand FB + Brand IG + Brand X.
   Store-local items → that store's FB + that store's GBP only (no IG, no X).
"""

POSTFLIGHT_ADDENDUM = f"""
## ADDENDUM 2026-09-06 — correct routing, correct timing, ledger verification

- **Schedule:** this task fires **Monday 4:40 PM ET (cron `40 16 * * 1`)**, verifying the 1:40 PM
  batch. Any "3:30 AM" / `0 30 3 * * 1` text above is stale.
- **Routing to verify against (2026-08-04 redesign, supersedes anything above):**
  Brand items → Brand FB + Brand IG + Brand X. Store-local items → that store's FB + that store's
  GBP **only**. Store items no longer touch Brand IG, so a missing store-IG leg is correct behaviour,
  not a silent drop — do not "self-heal" one.
- **Preferred verification:** if `{RSM}/state/plans/plan_<week>.json` exists, run
  `cd '{RSM}' && python3 -m vp_social postflight plan_<week>` — it reconciles every planned placement
  against the ledger and withholds (exit 2) rather than reporting a half-verified run. Otherwise run
  `python3 -m vp_social sync` first and verify against the ledger, never against the manifest.
- Unchanged: publishing a brand-new replacement post still needs Joshua's explicit go-ahead.
"""

PREFLIGHT_ADDENDUM = f"""
## ADDENDUM 2026-09-06 — corrected checks

- **Schedule:** fires **Monday 11:00 AM ET** for the **1:40 PM** batch. Every "Sunday 9 PM",
  "2:02 AM", or "before 2 AM" reference above is stale — read them as "before 1:40 PM today".
- **Check 1 (Bravo freshness):** look for the files the batch actually reads —
  `_items-to-price.csv` and `_aged-inventory-summary.csv` in `Bravo Data Extraction/output/`.
  `inventory_export` is a filename that never existed; that check has been passing vacuously.
- **Check 2 (Publer):** the `~/.vp-studio/publer-session.json` restore file was never created, so this
  check has been a hard gate on something that does not exist. Replace it with a reachability probe:
  `cd '{RSM}' && python3 -m vp_social sync --back 1 --forward 7` — a clean exit means the API key and
  workspace are live, which is what the batch actually needs. Only a non-zero exit is a real blocker.
"""


def edit_recap(body: str) -> str:
    if "python3 -m vp_social recap" in body:
        return body
    i = body.find("## Steps")
    return (body[:i] + RECAP_STEPS) if i != -1 else body + "\n" + RECAP_STEPS


def edit_digest(body: str) -> str:
    if "python3 -m vp_social digest" in body:
        return body
    block = f"""
## ADDENDUM 2026-09-06 — the DM text comes from the engine

Keep running `publer_weekly_digest.py` (it still writes `friday_digests/`, `weekly-adjustments.json`,
`adjustments_log.jsonl` and `~/.vp-studio/lessons.md`, which the Monday planner reads).

Then, before DMing Joshua:
`do shell script "cd '{RSM}' && python3 -m vp_social digest --days 7 2>/dev/null"`
- exit 0 → that stdout **is** the DM. Send it verbatim.
- exit 2 → send no DM; append the reason to `{STATUS}`.

**WHY:** the old digest counted posts the same broken way the recap did — it reported 57 posts for
Aug 29-Sep 4 when 89 published, and 64 vs 93 the week before. The engine's counts come from the
ledger; the engagement figures still come from Publer's insights endpoint.
"""
    return body + "\n" + block


def edit_deals_wed(body: str) -> str:
    if "MANDATORY duplicate check" in body:
        return body
    i = body.find("## Step 1")
    body = (body[:i] + DEALS_WED_STEP0 + "\n" + body[i:]) if i != -1 else body + "\n" + DEALS_WED_STEP0
    return body


def edit_engagement(body: str) -> str:
    if "REVEAL IS MANDATORY" in body:
        return body
    return body + f"""
## HARD RULE 2026-09-06 — REVEAL IS MANDATORY

If this lane posts a Guess-the-Price, "answer tomorrow", poll, or any format that promises the
audience a follow-up, the reveal post is **mandatory** the next evening on the **same accounts**, and
must contain the real number. Schedule the reveal in the same run as the question — never leave it to
a later session. Log both in `{RSM}/engagement_lane/RUN_LOG.md`.

This exists because the 2026-09-01 Guess-the-Price went out on Brand FB, Brand IG and X saying "the
real number goes in the comments tomorrow evening," the 8/31 run died before logging, and the reveal
was never posted. An open promise to customers is a brand problem, not a scheduling detail.
"""


def edit_comedy(body: str) -> str:
    if "reply sweep owns comments" in body:
        return body
    body = re.sub(r"(?m)^.*reel-comment-alert.*$",
                  "**Comments: the reply sweep owns comments.** Do NOT schedule a `reel-comment-alert` "
                  "one-shot — that skill reads the Meta Graph API, whose Page tokens have been dead since "
                  "2026-08-21, so it cannot run. Comment replies are handled by the engagement lane's "
                  "reply sweep through the Business Suite session.", body)
    return body


EDITS = {
    "weekly-social-media-recap": edit_recap,
    "vp-publer-analytics-friday": edit_digest,
    "vp-deals-social-wednesday": edit_deals_wed,
    "vp-content-batch-weekly": lambda b: b if "ADDENDUM 2026-09-06" in b else b + BATCH_ADDENDUM,
    "vp-content-batch-postflight": lambda b: b if "ADDENDUM 2026-09-06" in b else b + POSTFLIGHT_ADDENDUM,
    "vp-content-batch-preflight": lambda b: b if "ADDENDUM 2026-09-06" in b else b + PREFLIGHT_ADDENDUM,
    "vp-engagement-weekly": edit_engagement,
    "vp-comedy-reel-weekly": edit_comedy,
}


def main() -> int:
    changed = []
    for task in TASKS_RULE16:
        path = SCHED / task / "SKILL.md"
        if not path.exists():
            print(f"MISSING  {task}")
            continue
        original = path.read_text()
        fm, body = split_frontmatter(original)
        new = apply_rule16(body)
        if task in EDITS:
            new = EDITS[task](new)
        if new == body:
            print(f"nochange {task}")
            continue
        bak = path.with_suffix(".md" + BAK)
        if not bak.exists():
            bak.write_text(original)
        path.write_text(fm + new)
        added = sum(1 for l in difflib.ndiff(body.splitlines(), new.splitlines()) if l.startswith("+ "))
        removed = sum(1 for l in difflib.ndiff(body.splitlines(), new.splitlines()) if l.startswith("- "))
        assert path.read_text().startswith(fm), f"frontmatter damaged in {task}"
        changed.append(task)
        print(f"EDITED   {task}  +{added}/-{removed}")
    print(f"\n{len(changed)} files changed: {', '.join(changed) or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
