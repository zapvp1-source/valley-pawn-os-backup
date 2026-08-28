---
name: vp-creative-refresh-quarterly
description: Quarterly (1st of Jan/Apr/Jul/Oct, 7:40 AM) — retire proven-weak formats, rest fatigued ones, INVENT 8-12 genuinely new content formats seeded by season + local calendar + performance, gate them for novelty, and write the creative ledger.
---

---
model: claude-opus-5
---

# vp-creative-refresh-quarterly — where genuinely new ideas come from

**Why this exists.** Joshua, 2026-08-22: *"this also needs to shift and move with creative genius
over time, season and year... a self-iterating, with new drift for content, all run by you."*

A content system left alone either **freezes** (the audit found one caption run 21 times across 5
accounts, and another run four times on the *same* page) or **converges on noise** (the Friday loop
was moving the mix ±5% on n=8 posts with single-digit engagement). The weekly lanes handle
selection. This task is the only thing in the system that creates material that did not exist
before — without it, the registry slowly empties and every lane starts under-filling.

**Read first:** `~/Documents/Claude/Projects/Refine Social Media/CREATIVE_DRIFT.md` (this task
implements its §3), `CITY_COMMUNITY_KB.md`, `PILLAR_OVERLAY.md`, `vp-brand-studio`,
`valley-pawn-context`.

Model is pinned to **opus** deliberately — this is the one genuinely creative job in the fleet, it
runs four times a year, and cheaping out on it is how the whole system goes stale.

---

## Step 0 — File access
File tools first; on failure fall back to `mcp__Control_your_Mac__osascript` → `do shell script`.
Never call `request_cowork_directory` — this fires at 7:40 AM unattended.
Working dir: `~/Documents/Claude/Projects/Refine Social Media`

## Step 1 — Read the state of the registry
    /usr/bin/python3 creative_drift.py status
    /usr/bin/python3 creative_drift.py refresh

`refresh` does the mechanical part: retires anything past the signal threshold that has been
bottom-quintile for **two** consecutive quarters (one weak quarter is variance, not a verdict),
rests anything more than 40% off its own peak, and reports `candidates_needed`.

## Step 2 — Pull the real evidence (Rule 12: output, not run records)
Pull the last quarter of **actual published output and engagement from the Publer API** — not from
manifests. Two API facts that have already caused false conclusions twice:
- `GET /posts` **silently caps at ~15 results** unless you pass explicit `from`/`to` params.
- `/analytics/{id}/post_insights` pagination is **zero-indexed** — starting a loop at `page=1`
  silently drops records 11–20 for every account.

Also read: `weekly-adjustments.json` (the Friday loop's output — treat as *evidence*, never as
authority), the last quarter of `#social-media` and `#vp-studio-queue`, and any comment threads
that actually happened.

## Step 3 — Retire honestly
Confirm the engine's retirements make sense and archive them **with their numbers**. Never delete a
retired format — a forgotten bad idea gets reinvented and re-fails. Write each retirement into
`CREATIVE_LEDGER.md` with what it was, what it scored, and your read on *why* it died. That "why"
is the most valuable thing this task produces.

## Step 4 — INVENT (the point of the whole task)
Generate **8–12 new candidate formats** for the coming quarter. Seed them from:
- what actually performed **above the 30-post signal threshold** (ignore everything below it)
- the **incoming season skin** (`CREATIVE_DRIFT.md` §2 — palette, hook register, subject drift)
- the next quarter's **`[C26]` dated local events** per town from `CITY_COMMUNITY_KB.md`
- real **Bravo inventory categories** moving that quarter
- the **`untried_territory`** list in `creative_state.json` — things the brand has never tried

Write each candidate as a real format record: `id`, `lane`, `pillar`, `title`, `template`,
`seasons`, `hook_key`. The `template` must be specific enough that a Monday lane task can execute
it without inventing the concept from scratch.

**Bias toward formats that invite a reply.** The brand's structural problem is not reach, it is
that 485 measured posts produced 18 comments. A format nobody can respond to is worth less than one
that is slightly weaker but asks something.

## Step 5 — Gate every candidate for novelty
    engine.add_candidate(fmt)   # runs is_novel() automatically

A candidate is rejected if it shares an opening with an active format, matches an existing template,
or repeats pillar + subject + hook verb. **When a candidate is rejected, rewrite it into genuinely
new territory — do not weaken the gate.** This step is the entire defence against the standard
self-prompting failure mode: regenerating the same five ideas each quarter with new adjectives.

If you cannot get to 8 accepted candidates, that means the brand's territory is genuinely
exhausted in that direction — go somewhere it has never been (a new medium, a new subject, a new
voice, a new length) rather than lowering the bar.

## Step 6 — Annual pass (only when the quarter has a same-season predecessor a year back)
Detect formats that ran at this point last year and **force a transformation, not a repeat**: same
slot, same season, deliberately different medium / angle / opening / subject. Log the
transformation so the following year can transform it again rather than reverting.

## Step 7 — Write the ledger
Append a dated section to `CREATIVE_LEDGER.md`: what was retired and why · what was rested · every
candidate invented, with its seed reasoning · which pillars grew · which towns responded to what ·
which humor registers landed · what the quarter taught. This ledger seeds the next exploration
list, so year two starts smarter than year one instead of starting over.

## Step 8 — Report to Joshua
DM Joshua (`D03BHQH5VGT`) **one plain-language paragraph** — no jargon, no format IDs: what's
working, what we're retiring, what we're trying next quarter, and one honest sentence on whether
the engagement needle is actually moving. This is one of the few DMs in the fleet that fires on
success, because it is the quarterly creative review and he should see it.

Also post a short version to `#social-media` (C0BMRC2LN3D) so the team sees the direction.

## Step 9 — Verify
Re-run `creative_drift.py status` and confirm the registry has at least 20 active-or-candidate
formats across the lanes. If any lane is thin for the incoming season, that lane will under-fill
every week for 13 weeks — fix it now, in this run. Do not defer it.

Append a dated entry to `~/Documents/Claude/Projects/Valley Pawn OS/CHANGELOG.md` and log a row in
`Life OS/OPEN_ITEMS_REGISTER.md` for anything left pending.
