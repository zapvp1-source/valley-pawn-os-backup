#!/usr/bin/env python3
"""Phase 0 hygiene patches — Email Dept plan 2026-09-05 (file 19).
Additive/corrective edits to three scheduled-task SKILL.md files, each backed up first.
Run on the Mac: python3 <this file>
"""
import os, shutil, re, sys, datetime

S = os.path.expanduser("~/Documents/Claude/Scheduled")
STAMP = "20260905-phase0"
log = []

def backup(p):
    b = f"{p}.bak-pre-{STAMP}"
    if not os.path.exists(b):
        shutil.copy2(p, b)
    return b

def patch(path, fn, label):
    p = os.path.join(S, path)
    src = open(p, encoding="utf-8").read()
    new = fn(src)
    if new == src:
        log.append(f"NOCHANGE {label}")
        return
    backup(p)
    open(p, "w", encoding="utf-8").write(new)
    log.append(f"PATCHED  {label}")

# ---- 1. vp-deal-of-week-monday-pick: kill the dead /v3/media step, pin Step 8 channel ID
def fix_pick(s):
    old5 = re.search(r"STEP 5 — DOWNLOAD EVERY QUALIFYING PHOTO AND UPLOAD TO BREVO MEDIA LIBRARY.*?(?=\nSTEP 6)", s, re.S)
    if old5 and "/v3/media` (multipart form)" in old5.group(0):
        new5 = (
            "STEP 5 — DOWNLOAD EVERY QUALIFYING PHOTO AND HOST IT (PROVEN PATH ONLY)\n"
            "- **Do NOT use Brevo `POST /v3/media` — that endpoint does not exist** (returns not_found; it silently killed W10–W12 in Jul/Aug 2026).\n"
            "- Use the PROVEN PATH in the HARDENING ADDENDUM (2026-08-21) at the bottom of this file, RULE 1: Slack file → Chrome download → `sips -Z 1200` → localhost:8787 (with Access-Control-Allow-Private-Network) → authenticated fetch to `https://thevalleypawn.com/wp-json/wp/v2/media` → use the public WP URL in the email. Optionally import that public URL into the Brevo gallery via `POST /v3/emailCampaigns/images` (`{\"imageUrl\": ...}`).\n"
            "- Faster alternative when it exists: the website deal-image mirror (`thevalleypawn.com/wp-content/...` referenced by `deal_store.json`) — if the photo is already hosted there from a prior week, reuse that URL, no upload needed.\n"
            "- If a single photo retrieval fails after both paths, fall back to the vp-hero-image skill to generate a cinematic-premium product render from that item's description. If even that fails for one submission, drop only that submission (skip its block) — do not abort the whole run.\n"
            "- Record the final public image URL for each submission before moving on.\n"
        )
        s = s.replace(old5.group(0), new5)
    # Step 8: the public confirmation post has silently failed since 7/27 — the step named the channel
    # but not its ID. Pin the ID (verified: #deal-of-the-week = C0AVCANK7E3, same as the Thursday watchdog).
    s = s.replace(
        "STEP 8 — POST CONFIRMATION TO SLACK AND DM JOSHUA\nPost in `#deal-of-the-week`:",
        "STEP 8 — POST CONFIRMATION TO SLACK AND DM JOSHUA\nPost in `#deal-of-the-week` — **use channel_id `C0AVCANK7E3`** (never the bare name; the name-only call has failed silently every Monday since 2026-07-27 while the send itself succeeded). After posting, re-read the channel and confirm your message is the newest — if it is not, retry once with the ID.:",
    )
    return s

patch("vp-deal-of-week-monday-pick/SKILL.md", fix_pick, "pick: STEP 5 proven photo path + STEP 8 channel ID")

# ---- 2. brevo-weekly-efficiency-audit: runway floor 4 -> 8 weeks
def fix_audit(s):
    s = s.replace(
        "If fewer than 4 weeks of runway remain, that is your top-priority fix this run (see Step 4).",
        "If fewer than 8 weeks of runway remain, that is your top-priority fix this run (see Step 4). (Floor raised 4→8 on 2026-09-05: the primary stager is now the quarterly `brevo-stage-next-quarter` task — this audit is the safety net, and 8 weeks gives two full months to notice a stall.)",
    )
    s = s.replace(
        "- Draft calendar running low (<4 weeks) → stage more weeks",
        "- Draft calendar running low (<8 weeks) → stage more weeks",
    )
    return s

patch("brevo-weekly-efficiency-audit/SKILL.md", fix_audit, "audit: runway floor 4→8 weeks")

# ---- 3. brevo-weekly-draft-guard: point the Dec-31 warning at the new stager
def fix_guard(s):
    return s.replace(
        "After Dec 31 2026 the calendar runs out — from mid-December, include in your Slack report: `Weekly email calendar ends Dec 31 — next quarter needs staging.`",
        "The quarterly `brevo-stage-next-quarter` task (Dec 1 / Mar 1 / Jun 1 / Sep 1) stages the following quarter's 13 drafts. If you find fewer than 8 future-dated weekly drafts on ANY run, say so in your Slack report in plain language (`Weekly email calendar has N weeks left — staging is behind`) — that is the signal the stager missed its run.",
    )

patch("brevo-weekly-draft-guard/SKILL.md", fix_guard, "guard: Dec-31 warning → runway-floor check tied to stager")

print("\n".join(log))
