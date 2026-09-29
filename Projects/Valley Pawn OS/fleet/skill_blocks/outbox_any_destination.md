# OUTBOX SEND (MANDATORY) — every Slack send, any destination (added 2026-09-28)

**Do NOT call `slack_send_message` in this task — for ANY post or DM.** This task has no stored approval
for it, so in a scheduled run the send is declined automatically and the whole run's work is lost (this
is how jewelry counts, chekkit follow-ups and Northwest lost their posts 9/21–9/26). Every send goes
through the outbox instead; a native agent delivers it via the ops bot within about two minutes, with
no approval step.

For EACH message the steps above tell you to send (a channel post, a DM to Joshua, a DM to anyone):
1. Write the complete, final message text (exactly as it should appear, Slack mrkdwn, plain language —
   Rule 16) to
   `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/outbox/<this-task-id>-<label>-<YYYYMMDD-HHMMSS>.txt`
   where `<label>` is a short word naming the destination (e.g. `main`, `joshua`, `bonusgoals`).
2. Write the envelope, same base name, `.json`:
   `{"channel": "<the SAME channel or user id the step names>", "file": "<absolute path of the .txt>"}`
   A DM to Joshua may use `U03BB52MDSA` (or the old `D03BHQH5VGT` — the flusher maps it to Joshua).
3. Always write the `.txt` BEFORE the `.json`, and always use the `/Users/joshuadavis/...` path shown
   above — never the `/sessions/...` path your sandbox shows.
4. Do not wait, do not verify it in Slack, do not post a "sent via outbox" note. Receipts are written
   under this task's name automatically.

Every "all-or-nothing", "silent when nothing to report" and Rule 16 instruction above still stands —
this changes only HOW a send happens, never WHETHER or WHAT.
