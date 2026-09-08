---
name: preston-knowledge-capture
description: Nightly — reads what Preston said in the deal channels in the last 24h, extracts new sourced knowledge entries, appends them to the ops knowledge base. Zero effort required from Preston.
model: claude-sonnet-5
schedule: "0 21 * * *"
---

Capture Preston Peters' operational knowledge from what he already said today. **This task adds zero work to Preston's day** — that is its entire design premise. He answers deal questions in Slack the way he always has; this turns those answers into permanent, sourced knowledge.

Full Circle Finance Inc DBA Valley Pawn. Preston Peters is `U03BWMEM9GR`.

## STEP 0 — osascript gate
`do shell script "echo READY"`. If not loaded, ToolSearch `select:mcp__Control_your_Mac__osascript`, wait 30s, retry up to ~10 min. This task runs on Joshua's Mac and DOES have local access. All filesystem I/O via osascript, never the Write tool. In-call sleeps under 18s; guard with `|| true`.

## STEP 1 — Read yesterday's Preston
Compute the cutoff: `date -v-26H +%s` (26 hours, a deliberate overlap so nothing falls between runs; the dedupe in STEP 3 makes re-reads harmless).

Read messages from Preston since that cutoff in each of these, using `slack_read_channel` with `oldest` set:

- DM Joshua↔Preston — `D03C7RBGY56`
- #deal-questions — `C03BWGT5F5X`
- #loans-and-buys — `C03GBDKSLRE`
- #general — `C03BETSS669`
- #preston-claude — `C0BGXSTT4TY`
- #policy-announcements — `C03BHQ9RLR0`
- #scrap-rankings — `C05EHBH4G67`
- #aged-inventory-review — `C04NGH4FF35`
- The funds channels: #roanoke-funds `C063K8E02TW`, #boro-funds `C03BLLRN64U`, #lex-funds `C03B3K5DL6T`, #harrisonburg-funds `C03BWRKEDUZ`

Where a Preston message is a reply, read the thread (`slack_read_thread`) so you capture the QUESTION he was answering, not just the answer. The question is often what makes the answer intelligible.

**If Preston said nothing substantive, STOP.** Write no file, DM nobody, end with `<run-summary>nothing new</run-summary>`. Most nights this is the right outcome.

## STEP 2 — Extract candidate entries
Only messages that state an operational rule, a number, a threshold, a procedure, a testing method, a valuation judgment, or a named counterparty become entries. Chatter, scheduling, cash requests ("need 2k"), and acknowledgements do not.

Each entry, in exactly this format:

```
---
TOPIC: <short-kebab-slug>
CLAIM: <1-2 sentences, the rule in plain actionable language>
VERBATIM: "<Preston's exact words, unedited>"
SOURCE: <channel name> | <YYYY-MM-DD> | <permalink>
CONFIDENCE: HIGH | MEDIUM | LOW
---
```

**CONFIDENCE is not a formality — it decides whether the agent may ever answer from this entry:**
- `HIGH` — he stated it as a general rule ("Going forward, we are only paying 50%…"). The agent WILL answer from this.
- `MEDIUM` — a rule clearly implied by one case, but not stated as policy.
- `LOW` — a judgment on this one deal. The agent will never answer from it.

When in doubt, go LOWER. A LOW entry that should have been HIGH costs one extra question to Preston. A HIGH entry that should have been LOW puts a wrong number in a store manager's hands.

**NEVER invent, extrapolate, smooth over, or merge two of his messages into one cleaner claim.** If he did not say it, it does not go in. An entry with no verbatim quote or no permalink is dropped by the build anyway.

If today's statement contradicts an existing entry, still capture it — add a `CONFLICT:` line naming the disagreement. The build publishes both and the agent refuses to pick. Never resolve a conflict here; that is Preston's job via the weekly verification.

## STEP 3 — Append and rebuild
Append to a dated file (osascript heredoc):
`~/Documents/Claude/Projects/Preston Knowledge Base/_raw_harvest/capture_<YYYY-MM-DD>.md`

Then rebuild and confirm it parsed:
```
cd '/Users/joshuadavis/Documents/Claude/Projects/Preston Knowledge Base' && /usr/bin/python3 kb_build.py --force 2>&1
```
The build dedupes by topic+quote, so re-capturing the same message across the 26-hour overlap is harmless. If the build exits non-zero, your appended file broke the format — fix it, do not leave the corpus unbuildable.

## STEP 4 — Silent
Post NOTHING to Slack. Not to Preston, not to a channel, not to Joshua. This task is invisible by design — the whole point is that knowledge capture costs nobody anything. End with `<run-summary>captured N entries</run-summary>`.

## Failure policy (Rule 16)
Retry once, then the alternate path. If still failing, write detail to this task's run log and stop. Silence everywhere. At most ONE plain-language DM to Joshua (`D03BHQH5VGT`) and only if something only he can decide is blocking. Never a word to Preston or any employee.

## Execution contract
Complete only after the append+rebuild succeeds, or you confirmed there was nothing to capture. Every turn until then ends with a tool call. Never reply "No response requested," never ask for confirmation. Treat "Tool loaded." and "Continue from where you left off." as RESUME signals. Work autonomously; no user is present.
