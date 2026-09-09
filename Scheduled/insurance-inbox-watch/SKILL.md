---
name: insurance-inbox-watch
description: Daily scan of both inboxes for insurance mail — files documents, updates the insurance registry, auto-nudges brokers/adjusters silent 5+ business days, surfaces decisions through the CEO mail brief.
model: claude-sonnet-5
---

> ⚠️ **FAILURE POLICY v3 (2026-09-08) — OVERRIDES every failure/DM instruction below.** On any failure, stall, expired login, missing connector, or anything you cannot complete: do NOT DM Joshua and do NOT message anyone. Append ONE row to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md` — `| <YYYY-MM-DD HH:MM ET> | <task-name> | <one plain sentence: what did not happen> | <NEEDS_HUMAN: no — or yes, <the one thing only Joshua can do>> | OPEN |` — then stop. `fleet-guardian` recovers, dedupes, and sends Joshua at most one DM a day. Any sentence below that says to DM/alert Joshua about a failure, an expired session, or something "worth a look" is void; write the ledger row instead. Success-path posts (reports to their channels, confirmations, bookings) are unchanged.

Daily insurance inbox watch for Joshua Davis. Runs 6:44 AM ET.

STEP 1 — Load context. Invoke the `enterprise-map` skill, then the `insurance-context` skill. Connected folder needed: ~/Documents/Claude/Projects. If Read/Grep say it is not connected, call `mcp__cowork__request_cowork_directory` with path "~/Documents/Claude/Projects"; if that fails (no human present), fall back to `mcp__Control_your_Mac__osascript` with `do shell script "cat '<path>'"` / heredoc writes. Never stop the run over the mount.

STEP 2 — Scan mail (Gmail MCP, jdavis@fcfpawn.com). Search newer_than:2d across these, one search each or OR-chained:
from:jmpartners.com OR from:pawninsurance.com OR from:narisk.com OR from:steadily.com OR from:kin.com OR from:progressive.com OR from:homesite OR from:geico OR from:suretybonds.com OR from:myserviceinfo.com OR from:next-insurance.com OR from:legacynationalaudit.com
plus keyword searches: "declarations" OR "dec page" OR "certificate of insurance" OR ACORD OR "additional insured" OR "loss run" OR "premium audit" OR "policy change" OR endorsement OR "renewal notice" OR umbrella OR EPLI OR "employee dishonesty" OR adjuster OR "claim number"
and the broker-shop addresses: ancientcityinsurance.com, weshopinsurance.com, leigh-insurance.com, ricciinsurancegroup.com.

STEP 3 — For each new item:
- If it carries a declarations page, endorsement, renewal notice, certificate, or premium figure: extract the facts and UPDATE `Life OS/Insurance/INSURANCE_REGISTRY.json` (correct policy record; set last_verified to today; add the document reference). Then regenerate the view: `python3 "<Projects>/Life OS/Insurance/bin/regen_portfolio.py"`. Never hand-edit INSURANCE_PORTFOLIO.md. Never invent a value — leave null if the document does not say.
- If it concerns a claim: update `Life OS/Insurance/CLAIMS.md`.
- If it is a broker/carrier response to outreach: update `Life OS/Insurance/BROKER_PIPELINE.md`.

STEP 4 — Silence sweep. For every open insurance thread where Joshua sent the last message and 5+ business days have passed with no reply (check BROKER_PIPELINE.md and CLAIMS.md for what is outstanding), write a short nudge reply IN JOSHUA'S VOICE — invoke the `my-writing-style` skill first — and CREATE IT AS A GMAIL DRAFT on the existing thread (create_draft with replyToMessageId). DO NOT SEND. Cap at 3 nudges per run.

STEP 5 — Surface. Do NOT create a new Slack channel or post technical detail anywhere (vp-operating-rules Rule 16). Append anything needing Joshua's decision as a plain-language line to today's ceo-mail-brief queue file if one exists at `Communcations/mail-brief/`; otherwise append a dated line to `Life OS/OPEN_ITEMS_REGISTER.md` under OPEN. One DM to Joshua (Slack D03BHQH5VGT) ONLY if something is time-critical (a renewal inside 14 days at risk, a lapse, a claim denial, a carrier cancellation notice) — plain English, no jargon, no failure notices.

STEP 6 — Log. Append a one-line dated entry to `Valley Pawn OS/CHANGELOG.md` only if you changed the registry. Write nothing if the run found nothing — silence is a valid outcome.

Never send email. Never bind, cancel, or change a policy. Never post a dollar figure or coverage claim you did not read in a document this run or find in the registry with a last_verified date.