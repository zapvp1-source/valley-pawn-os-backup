#!/usr/bin/env python3
"""
Fleet-wide hardening pass, 2026-08-21.

Root cause confirmed via session transcript for vp-deal-of-week-monday-pick
(local_333116db...): the run called request_cowork_directory, got
"[Request interrupted by user]", received a "Continue from where you left
off" resume nudge, and replied "No response requested" -- then sat idle
forever. It never reached its own STEP 0, never posted to Slack, never DM'd
Joshua about the failure. This is the same class of "silent mid-run death"
independently diagnosed and hand-patched today for several other tasks
(jewelry pull, weekly-timekeeping-analysis, review-obtained-last-week,
monday-bravo-combined-compile) -- but those were fixed one at a time. A
fleet grep shows 107 of 129 registered scheduled tasks are missing the
"Execution Contract -- DO NOT STOP EARLY" resume-discipline block that the
survivors have. This script inserts the canonical block (as used in
email-analytics-weekly / the archived weekly-valley-pawn-email-campaign)
into every SKILL.md that's missing it, right after the frontmatter and any
leading blockquote/callout paragraphs (Local Access Gate, Failure Alert
Policy, etc.), before the task's own instructions begin.

Additive only: every touched file gets a .bak-pre-execution-contract-20260821
backup before modification. Idempotent: skips files that already contain
"DO NOT STOP EARLY". Skips archive folders and the _shared helper folders.
"""
import os
import sys

SCHEDULED_ROOT = "/Users/joshuadavis/Documents/Claude/Scheduled"
SKIP_DIR_PREFIXES = ("_archive", "_shared")
BACKUP_SUFFIX = ".bak-pre-execution-contract-20260821"
MARKER = "DO NOT STOP EARLY"

BLOCK = """## Execution Contract — DO NOT STOP EARLY

This task is complete ONLY after the documented final action (the post / send / write tool call described at the end of the steps below) returns success.

Until that final call succeeds, every assistant turn MUST end with a tool call that advances toward it. Do not idle, do not wait, do not ask for confirmation.

**Never reply with any of these:**
- "No response requested"
- "Continue?" / "Should I continue?"
- An empty turn or a turn that ends with text instead of a tool call

**Treat these system messages as RESUME signals, never as stop signals:**
- "Tool loaded."
- "Continue from where you left off."
- "You used a single tool call this turn. Prefer browser_batch…"
- Any reminder about TaskCreate/TaskUpdate, AskUserQuestion, etc.

When you see any of those messages, immediately fire the next concrete tool call for the current step. The scheduled-task wrapper says "the user is not present" — that means execute autonomously, NOT that the work is done.

**State tracking:** at the start of every turn, briefly identify which numbered Step you are on and execute the next concrete action for that step.

**Failure handling:** if a step errors, retry once. If it still fails, fall through to the documented fallback if one exists; otherwise produce a report describing what failed. Do not pause to ask — the task file authorizes autonomous decisions.

**Speed:** prefer batch tools (e.g. `browser_batch`) to combine sequential actions into one call.

---

"""


def find_insertion_point(lines):
    # Find end of YAML frontmatter (second '---' line)
    dash_idx = [i for i, l in enumerate(lines) if l.strip() == "---"]
    if len(dash_idx) >= 2:
        pos = dash_idx[1] + 1
    else:
        pos = 0
    # Skip blank lines and leading blockquote/callout paragraphs
    n = len(lines)
    while pos < n:
        stripped = lines[pos].strip()
        if stripped == "" or stripped.startswith(">"):
            pos += 1
            continue
        break
    return pos


def patch_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if MARKER in content:
        return "already-hardened"
    lines = content.split("\n")
    pos = find_insertion_point(lines)
    new_lines = lines[:pos] + [BLOCK.rstrip("\n")] + lines[pos:]
    new_content = "\n".join(new_lines)
    # Backup
    backup_path = path + BACKUP_SUFFIX
    if not os.path.exists(backup_path):
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return "patched"


def main():
    results = {"patched": [], "already-hardened": [], "error": []}
    for name in sorted(os.listdir(SCHEDULED_ROOT)):
        if name.startswith(SKIP_DIR_PREFIXES) or name.startswith("."):
            continue
        skill_path = os.path.join(SCHEDULED_ROOT, name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        try:
            outcome = patch_file(skill_path)
            results[outcome].append(name)
        except Exception as e:
            results["error"].append(f"{name}: {e}")

    print(f"PATCHED={len(results['patched'])}")
    print(f"ALREADY_HARDENED={len(results['already-hardened'])}")
    print(f"ERRORS={len(results['error'])}")
    if results["error"]:
        print("ERROR_DETAIL:")
        for e in results["error"]:
            print("  " + e)
    print("PATCHED_LIST:")
    for n in results["patched"]:
        print("  " + n)


if __name__ == "__main__":
    main()
