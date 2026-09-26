---
name: roster-refresh
description: Daily 6:15 AM — rebuilds Valley Pawn OS/hr/ROSTER.json (active staff by store, phone, Slack ID) from Gusto + Slack. No messages sent.
model: claude-sonnet-5
---

Rebuild Valley Pawn's shared staff roster file. This file is read by other automations (the Chekkit unanswered-message alert uses it to decide which employees get store messages; the missed-call texting agent uses the phones so it never texts staff). Accuracy matters more than speed. SEND NO MESSAGES of any kind — this task only writes files.

On any failure follow FAILURE POLICY v3: append ONE row to ~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md — `| <YYYY-MM-DD HH:MM ET> | roster-refresh | <one plain sentence> | NEEDS_HUMAN: no | OPEN |` — and stop. Never write a partial roster; the previous ROSTER.json stays in place and consumers keep using it.

PATHS: the Valley Pawn OS folder is ~/Documents/Claude/Projects/Valley Pawn OS on the Mac; inside a sandbox shell it may be mounted at /sessions/*/mnt/Projects/Valley Pawn OS — find it with `ls -d /sessions/*/mnt/Projects/"Valley Pawn OS" "$HOME/Documents/Claude/Projects/Valley Pawn OS" 2>/dev/null`.

STEPS
1. Gusto connector: `list_employees` with `terminated: false`, `per: 100` (page until empty). These are the active employees. Use ONLY these fields: first/last name, preferred_first_name, department, the primary job's title, email, phone, uuid. Never copy pay, SSN, date of birth or anything else.
2. Read the current `hr/ROSTER.json` (if present) to get each person's existing slack_id by gusto_uuid.
3. For each active employee find their Slack user ID:
   a. `slack_search_users` with query = their Gusto email. Accept the single result whose email equals it.
   b. If no result and ROSTER.json already has a slack_id for this gusto_uuid, keep it after confirming with `slack_read_user_profile` that the profile exists and the name plausibly matches (Slack emails can differ from Gusto — e.g. Preston Peters U03BWMEM9GR).
   c. Otherwise try `slack_search_users` by "First Last"; accept only an unambiguous exact name match.
   d. Else slack_id = null (not on Slack).
4. Write the candidate to `hr/roster_candidate.json`:
   {"source": "gusto list_employees(terminated=false) <date> + slack email match", "employees": [{"name": "First Last", "preferred": preferred_first_name or first name, "department": Gusto department exactly, "title": primary job title, "email": Gusto email, "phone": Gusto phone (10 digits) or null, "gusto_uuid": uuid, "slack_id": "U…" or null}, …]}
   For Kennedy Davis and Audrey Davis (Corporate Support gold sorters) set phone to null.
5. Run: `python3 "<Valley Pawn OS>/bin/roster_write.py" "<Valley Pawn OS>/hr/roster_candidate.json"`. It validates and writes ROSTER.json, or prints REFUSED and writes nothing. If REFUSED, write the ledger row with its reason and stop.
6. Run `python3 "<Valley Pawn OS>/bin/roster_write.py" --check` and confirm it prints ok. Delete hr/roster_candidate.json.
7. Final output (for the run log only): employees count, how many on Slack, the names not on Slack, and the change line roster_write printed.