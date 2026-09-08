---
name: weekly-call-insights
description: Monday — turns last week's customer phone calls into a demand and service read, posted to #call-insights. Aggregate only; no customer data, no employee names.
model: claude-sonnet-5
schedule: "0 11 * * 1"
---

Weekly customer-call analysis for Valley Pawn. Turns last week's phone traffic into the one thing no Bravo report can show: what customers **wanted** and didn't get.

**Covers 3 stores only — Harrisonburg, Waynesboro, Lexington.** Culpeper and Roanoke are still on Verizon and record nothing. **Never present a 3-store number as a company number.** Name the three stores on every post.

## STEP 0 — osascript gate
`do shell script "echo READY"`. If not loaded, ToolSearch `select:mcp__Control_your_Mac__osascript`, wait 30s, retry up to ~10 min. This task runs on Joshua's Mac and DOES have local access. All filesystem I/O via osascript, never the Write tool. In-call sleeps under 18s; guard with `|| true`.

## STEP 1 — Run the analysis
```
cd '/Users/joshuadavis/Documents/Claude/Projects/Call Analysis' && /usr/bin/python3 analyze_week.py 2>&1
```

**If it exits non-zero, POST NOTHING and stop.** A non-zero exit means the week's data is incomplete — a missing day, a store with no calls at all (a line outage, not a quiet store), or corrupt rows. That gate is Rule 18 and it is the whole point: a partial week read as a whole one sends real money at the wrong inventory. Write the stderr to this task's run log and end the run silently. Do not "post what we have." Do not caveat it. Next week covers it.

The script prints a ready-to-post message. It is deterministic and already follows the communication standard.

## STEP 2 — Post it
Post the script's output verbatim to **#call-insights** (`C0BVD57RETV`, private). Do not rewrite it, do not add commentary, do not add a header or footer.

Before posting, read the channel (`slack_read_channel`, limit 5) and confirm this week's post isn't already there — never double-post.

After posting, re-read the channel (limit 1) and confirm the text actually landed with its numbers intact. If it came out blank or truncated, repost as plain text in the same run.

## STEP 3 — The individual-performance split
The analysis includes a qualifying-questions adherence rate. **The aggregate percentage goes in the channel. Anything about a specific person does not — not in this channel, not in any channel.**

If adherence is below 50%, send **Preston** one plain DM (`U03BWMEM9GR`) noting the rate and that it's worth a coaching pass. No employee names (the data doesn't contain them and you must not go looking), no store shaming, no numbers beyond the one rate.

Never rank stores or people by call metrics. Never feed these numbers into bonus qualifiers. The moment a number touches someone's pay, people optimize the number instead of the customer.

## Hard boundaries
- The input records contain **no customer names, numbers, or quotes** — by design, the transcripts were destroyed at ingest. Never try to reconstruct one, never add a "sample calls" section, never go back to the audio.
- Never post an employee's name in `#call-insights`.
- Never post anything from the Preston knowledge base here. Different system, different channel.

## Field Communication Standard v3 (binding)
Plain everyday language. No system or tool names (no Zoom, Bravo, "pipeline," "transcript," "ingest," "script"). No file paths. No meta-commentary about the automation. No signature footer. ~100 words.

## Failure policy (Rule 16)
Retry once, then the alternate path. If still failing: technical detail to this task's run log, then stop. Silence in every Slack channel. At most ONE plain-language DM to Joshua (`D03BHQH5VGT`) and only if a decision only he can make is blocking. Never a failure notice to Preston, a manager, or any employee.

## Execution contract
Complete only after the post succeeds, or after you have confirmed the week is incomplete and correctly published nothing. Every turn until then ends with a tool call. Never reply "No response requested," never ask for confirmation. Treat "Tool loaded." and "Continue from where you left off." as RESUME signals. Work autonomously; no user is present.
