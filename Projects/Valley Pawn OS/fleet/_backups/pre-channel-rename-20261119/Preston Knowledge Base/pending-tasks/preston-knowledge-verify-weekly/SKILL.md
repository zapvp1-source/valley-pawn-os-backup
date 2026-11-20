---
name: preston-knowledge-verify-weekly
description: Mondays — sends Preston up to 10 things he already said, quoted back with the date, for a yes/no/fix. His replies write into verified.json. ~10 minutes of his time per week, total.
model: claude-sonnet-5
schedule: "0 10 * * 1"
---

The verification loop for the Valley Pawn ops knowledge base. Once a week, Preston Peters (`U03BWMEM9GR`) confirms or corrects up to 10 things he already said. **This is the only recurring ask on his time in this entire system, and it must stay about ten minutes.** If it ever grows past ten entries a week, the design is broken, not Preston.

## STEP 0 — osascript gate
`do shell script "echo READY"`. If not loaded, ToolSearch `select:mcp__Control_your_Mac__osascript`, wait 30s, retry up to ~10 min. This task runs on Joshua's Mac and DOES have local access. All filesystem I/O via osascript. In-call sleeps under 18s; guard with `|| true`.

## STEP 1 — Did he answer last week's batch?
Read `#preston-claude` (`slack_read_channel`, `C0BGXSTT4TY`, limit 40) and find the last batch this task posted, plus any replies from Preston.

Parse his replies. He answers by number:
- `ok` / `yes` / `correct` / 👍 → status `VERIFIED`
- `no` / `wrong` / `not anymore` → status `REJECTED` (the entry stops publishing entirely)
- anything else → status `VERIFIED` with that text as `correction`, and if it clearly replaces an older rule, also mark the old entry `SUPERSEDED` with `supersedes` pointing at the new id
- no reply to an item → leave it pending, it comes back in a future batch

Write results into `Preston Knowledge Base/verified.json` — a JSON object keyed by entry id:
```json
{ "<entry-id>": { "status": "VERIFIED", "verified_on": "2026-09-14", "correction": null, "supersedes": null } }
```
Merge into the existing file; never overwrite it wholesale. Then rebuild:
```
cd '/Users/joshuadavis/Documents/Claude/Projects/Preston Knowledge Base' && /usr/bin/python3 kb_build.py --force 2>&1
```
If `verified.json` ends up invalid JSON the build refuses to run — that is deliberate. Fix the file, never leave the corpus unbuildable.

## STEP 2 — Build this week's batch
```
cd '/Users/joshuadavis/Documents/Claude/Projects/Preston Knowledge Base' && /usr/bin/python3 kb_build.py --queue 2>&1
```
Returns up to 10 pending entries, highest-confidence first — because those are what the agent is **already answering from**, so confirming them retires the most risk per minute of his time.

Before posting, cross-check the `NOT-FOUND` rows in `QUESTION_LOG.md` from the last 7 days. **If a store actually asked something the base couldn't answer, that beats anything in the queue** — swap it in as a plain question at the end of the batch. A real question from a real store is worth more than confirming a rule nobody asked about.

**If the queue is empty and there are no new NOT-FOUNDs, post nothing.** Do not manufacture a batch to look busy. End with `<run-summary>nothing to verify</run-summary>`.

## STEP 3 — Post it
One message to `#preston-claude`. Plain, short, numbered. No tables (they render badly there). Every value on its own line.

Format:
```
Morning Preston — quick check on a few things you've said, so the stores can get answers without pinging you every time.

Just reply with the number and "ok", or the right answer if it's changed.

1. Paying 50% for all bullion and silver — you said this 1/29. Still right?
2. Scrap rings with diamonds: pay the gold value only, not the estimator value with the stones — 2/26/24. Still right?
...

Anything you say "no" to just gets dropped. Thanks — this is the last you'll hear from me this week.
```

Rules for the message:
- Quote him plainly and give the date. He should recognize his own words instantly.
- Never explain the mechanism. No mention of a knowledge base, entries, tiers, confidence, files, ids, or automation. (Field Communication Standard v3.)
- Never send more than 10. Never send a second batch in the same week.
- Never chase or re-ask for a reply mid-week. Unanswered items simply return in a later batch.

## STEP 4 — Log
Append a one-line record of what was sent to `Preston Knowledge Base/VERIFY_LOG.md` (create with a header if missing): date, entry ids sent, entry ids resolved from last week.

Do NOT DM Joshua a routine summary — he does not want a weekly ping about this. Reach him only per the failure policy.

## Failure policy (Rule 16)
Retry once, then the alternate path. If still failing: technical detail to this task's run log, then stop. Silence in every channel. At most ONE plain-language DM to Joshua (`D03BHQH5VGT`) and only if a decision only he can make is blocking. Never send a failure notice to Preston or any employee, in any medium.

## Execution contract
Complete only after the batch posts (or you confirmed there was nothing to send) AND last week's answers are written and rebuilt. Every turn until then ends with a tool call. Never reply "No response requested," never ask for confirmation. Treat "Tool loaded." and "Continue from where you left off." as RESUME signals. Work autonomously; no user is present.
