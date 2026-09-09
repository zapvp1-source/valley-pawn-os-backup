---
name: scheduled-task-model-audit-weekly
description: Weekly audit of every Cowork scheduled task's AI-model pin against the Haiku/Sonnet/Opus tier framework; fixes mis-tiered/unpinned/Fable pins and logs the results.
model: claude-sonnet-5
---

You are running the WEEKLY SCHEDULED-TASK MODEL AUDIT for Full Circle Finance Inc DBA Valley Pawn (Joshua's 5-VA-pawn-store business). This is a recurring Monday 5:00 AM task with no memory of any prior run — reconstruct everything from scratch below. Run fully autonomously, no clarifying questions, no check-ins. This is routine maintenance — do NOT post anything to Slack (per Rule 16 — no routine notifications) and do NOT DM Joshua about it.

## Background

Cowork scheduled tasks run on whatever AI model the app defaults to UNLESS the task's own SKILL.md frontmatter has a `model:` line, which overrides the default for that task. Task files live at `~/Documents/Claude/Scheduled/<task-id>/SKILL.md` on the real Mac filesystem (NOT the sandboxed bash tool's filesystem — use `mcp__Control_your_Mac__osascript` with `do shell script` to read/grep/edit these files; load that tool via ToolSearch with query "select:mcp__Control_your_Mac__osascript" if it's deferred).

If a skill named "scheduled-task-models" is available in your skills list, load it via the Skill tool first for full mechanism details and any helper scripts (audit_task_models.py, set_task_model.py, apply_standard_tiers.py) — locate its real host-filesystem path (try `mdfind -name scheduled-task-models` via osascript, or check `~/Library/Application Support/Claude/local-agent-mode-sessions/**/skills/scheduled-task-models`) so you can call `set_task_model.py <task-id> <model-id>` for a safe, backed-up edit instead of hand-editing frontmatter. If you can't find/run it, edit the frontmatter directly via osascript heredoc/sed — replace or insert the single `model:` line between the two `---` delimiters, leaving everything else (especially the task body below the second `---`) byte-for-byte unchanged, and back up the file first (copy to `<file>.bak-model-<timestamp>`).

## Tier framework

- **Haiku** — token pings, health/threshold watchdogs, mechanical file/artifact/Canvas refreshes, simple detect-and-notify. No narrative or judgment.
- **Sonnet** — DEFAULT for the bulk. Data pulls, reports, scans, KPI compiles, templated Slack/email posts, lightweight orchestration, pipeline/watchdog work.
- **Opus** — customer-facing copy, brand voice, long-form content (e.g. blog posts), multi-asset creative orchestration (e.g. comedy/story video scripts), high-stakes HR/legal/financial judgment (e.g. compliance reviews, bonus/termination decisions).
- **Fable** — NEVER use for scheduled tasks. If you find any task pinned to Fable, treat it as urgent and fix it immediately regardless of anything else.

## Steps

1. Before writing any `model:` value, discover the currently valid model ID convention: grep existing `model:` lines across several live task SKILL.md files (e.g. `grep -r '^model:' ~/Documents/Claude/Scheduled/*/SKILL.md | sort | uniq -c` via osascript) and use whatever the dominant, well-formed convention is (as of the 2026-08-27 baseline audit this was `claude-haiku-4-5`, `claude-sonnet-5`, `claude-opus-4-8`; Fable was `claude-fable-5` but must never be assigned). Do not blindly assume these strings are still current — confirm against what's actually deployed this week, since Anthropic model names change over time.
2. Call `mcp__scheduled-tasks__list_scheduled_tasks` to get every current task: taskId, description, schedule, enabled state.
3. For every ENABLED task (skip disabled ones — not worth the audit effort, just note count skipped), read its SKILL.md frontmatter via osascript to see its current `model:` pin (or "unpinned").
4. Classify each task against the tier framework using its description (and a skim of the prompt body if the description is ambiguous). Compare to its current pin.
5. Fix any task that is: unpinned, pinned to a malformed/non-standard model string, pinned to Fable, or clearly mis-tiered relative to the framework (e.g. a brand-voice/creative-writing task sitting on Sonnet when it should be Opus, or a purely mechanical refresh sitting on Sonnet when it should be Haiku). Use `set_task_model.py` if found, else edit frontmatter directly with a backup as described above. When in doubt between two adjacent tiers, prefer the cheaper one (Sonnet default) rather than guessing upward — only move to Opus when the task clearly involves brand voice, customer-facing copy, or high-stakes HR/legal/financial judgment.
6. Keep a running tally: task id → old model → new model (or "no change"), plus which tasks you left alone because you weren't confident in the classification (and why).
7. Append ONE new row to the Open Items Register at `~/Documents/Claude/Projects/Life OS/OPEN_ITEMS_REGISTER.md` (this path is a normal file, reachable directly, not via osascript) under the "OPEN (unresolved or status unconfirmed)" table, following the existing row format (Date logged | Domain | Item | Status | Next action). Domain = "1 — Valley Pawn". Summarize: total tasks audited, how many changed (with the id → old → new list), how many left unchanged because already correctly tiered, and any left unclassified with reasons. Use today's actual date for "Date logged" (compute it — never hardcode a date from this prompt template).
8. If you can locate the scheduled-task-models skill's `reference/model-policy.md` at a writable real host path (some plugin cache locations are read-only — if a write is refused, skip this step, it is a nice-to-have not critical), update it with the current Haiku/Sonnet/Opus assignment lists and today's date.
9. Do NOT post to Slack. Do NOT DM Joshua. Do NOT ask any clarifying questions. This task's only outputs are: the SKILL.md frontmatter edits (with backups), the Open Items Register row, and optionally the model-policy.md refresh. End the run once step 7 is complete.

This task replicates a full manual audit Joshua's agent ran on 2026-08-27 (28 tasks changed then). The goal is to catch drift — new unpinned tasks, broken model strings, or tasks that quietly slid back to the wrong tier — before it costs meaningful compute.