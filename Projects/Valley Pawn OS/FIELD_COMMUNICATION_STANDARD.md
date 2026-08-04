# Valley Pawn — Field Communication Standard (v3)

Set by Joshua, 2026-08-03. Supersedes the v2 "FAILURE ALERT POLICY + FIELD COMMUNICATION RULE"
paragraph as the source of truth for what any automation is allowed to post to a channel or DM
that store employees read. v2 is preserved below as the failure-routing rule — it still applies,
unchanged. v3 adds the missing piece: a routing test and a content standard for the successful,
everyday posts, not just failures.

This file is the one place to change this standard going forward. Task files should point here,
not restate it, so it never drifts out of sync across 27+ files again.

---

## 1. The routing test — apply BEFORE writing a single word of the post

Ask: **is this something a store clerk or manager needs to know or act on today?**

- If yes → post it to the team channel, following the content rules below.
- If no — it's an audit trail, a pipeline status, a methodology note, a data-quality caveat, a
  file/lock/CSV problem, a "verified against," a "supersedes the prior format," a run count, a
  tool name, a doc ID — it does **not** go to a team channel or a store-employee DM, ever.
  Route it to: Joshua's DM (`D03BHQH5VGT`), a STATUS/log file, or nowhere (silent success).

**Internal audit/compliance-sync tasks are internal by default.** A task whose job is to check
whether OTHER documents/policies are in sync (e.g. the monthly HR/policy sync) is talking to
Joshua and to a master document — not to the floor. Only the underlying policy itself, once
confirmed real and staff-relevant, goes to a team channel, and it goes as the policy, not as an
audit report about the policy.

## 2. Content rules for anything that passes the routing test

- **Plain everyday language.** No technical jargon, no error codes, no tool/system/pipeline
  names (never say Bravo, Cowork, Chekkit, Gusto, Brevo, QBO, Publer, "the pipeline," "the API,"
  "handler," "watchdog," "scheduled task," "sync," "audit script," "CSV," "export").
- **No file paths, file names, doc IDs, task IDs, or spreadsheet column references** in the
  posted message. A single "full details" link is fine if the audience actually needs to click
  through — the surrounding sentence still has to stand alone in plain English.
- **No meta-commentary about the automation itself.** No "reviewed X against Y," "auto-appended,"
  "verified to the penny," "supersedes the prior format," "this is a mid-week manual run to
  test...," "pulled automatically from," "source: X pipeline." If a number needs a caveat, give
  the plain-English version of the caveat, not the process explanation for it.
- **Lead with the one-line takeaway.** The single most important fact or number comes first, in
  the first sentence. Everything else is supporting detail, and supporting detail belongs behind
  a link, not in a stacked table in the message body.
- **Length cap: ~100 words for a routine post.** If a message needs more than that to say
  something a clerk can act on, that's a sign the detail belongs in a linked doc/sheet, not in
  the channel.
- **No signature footers.** Do not append "Sent using Claude," an automation-run timestamp, or
  any "— <task-name> · <file>" credit line. The team channel is a business channel, not a build
  log.
- **Failures, errors, and pipeline problems never appear in a team channel or employee DM** —
  this is the existing v2 rule, unchanged and still binding: one plain-language line to Joshua's
  DM only, full technical detail to the run log/STATUS file. If a v2 header in a task file
  conflicts with an instruction later in the same file, v2/v3 win — always.

## 3. Two working examples (copy this bar)

**Good — #google-reviews:**
> Nice job Team Culpeper! You just got a new 5 star review from Maurice Linder! ⭐

**Good — #items-to-price:**
> Culpeper: 14 items, $2,340. Waynesboro: 9 items, $1,180. Harrisonburg: 6 items, $890.
> Total: 29 items, $4,410 ready to price today.

**Bad — do not do this (real example, before the fix):**
> _Bravo pull: FAILED for all 5 stores... Every cell hit the same error: "Grid never rendered
> after 2 attempts (~3 min)"... Logged to STATUS.md and BRAVO_KNOWN_ISSUES.md for follow-up._

## 4. Scope

Applies to every scheduled task, native launchd agent, and one-off post that touches a channel
or DM read by store employees or store managers. Does not restrict what Joshua's own DMs,
STATUS files, run logs, or Joshua-only channels contain — those can and should stay as detailed
and technical as needed.

## 5. Enforcement

A monthly comms-drift check (`vp-comms-drift-monthly-check`) reads the team-facing channels and
DMs Joshua a one-line digest of anything that violates this standard, so drift gets caught
inside 30 days instead of accumulating for months.

## 6. Change log

- **2026-08-03** — v3 created. Audit found 27 team-facing tasks; 1 missing the v2 header
  entirely (`jewelry-count-reconciliation`), 4 with body instructions that directly contradicted
  their own v2 header (posting failures to a team channel anyway), and roughly a dozen with
  system names, file paths, or audit-report framing baked into the "successful" post template.
  Worst offenders by verbatim content: `#jewlery-counts`, `#weekly-returns-summary`,
  `#company-performance`, `#layaway-review`. Cleanest models found and kept as-is:
  `#google-reviews`, `#items-to-price`, `#deal-of-the-week`.
