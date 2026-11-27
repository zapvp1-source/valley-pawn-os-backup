import re

path = "fleet/FAILURE_LEDGER.md"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

updates = {
    "| 2026-11-26 02:10 ET (native) | fleet-doctor |": (
        "COVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- 48 quiet jobs is a new high but close to "
        "the established routine range (1-44 observed since late Sept per 11/24-11/25 passes); 6 "
        "errored-this-week jobs also in the normal noise band. No single new broken agent identified "
        "beyond today's other tracked rows (supply-approvals/deliveries, sign-in walls). Watching for "
        "further growth; not escalated."
    ),
    "| 2026-11-26 02:35 ET (native) | instock-nightly |": (
        "QUEUED 2026-11-26 (fleet-guardian 12:45 ET pass) -- verified locally (Rule 12): all 5 store "
        "captures and the merged 2026-11-25_ALL_instock.csv (12,259 items) completed in Bravo Data "
        "Extraction/output/, but fleet/state/instock/status_latest.json still shows 2026-11-24 -- the "
        "Drive-copy step after the local merge appears to have thrown before writing status (same "
        "Drive-mount 'Resource deadlock' class seen on shop-refresh 11/25). Rerun-safe by HARDENING_STANDARD "
        "classification (internal Drive report, duplicate-guarded all-or-nothing, no external messaging/money) "
        "but was unlisted in rerun_manifest.json -- added it (additive) and queued a host-queue retry "
        "(bin/instock_merge.py 2026-11-25, already allow-listed) since the Drive destination is outside "
        "this session's device-bridge mount; result pending next pass."
    ),
    "| 2026-11-26 08:30 ET (native) | oura-daily-import |": (
        "UNRECOVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- recurring phone-app-sync item (10/21, "
        "11/6, 11/7, 11/23, 11/24, 11/25), not rerun-safe (needs a physical ring sync); Life OS/HUMAN_QUEUE.md "
        "row bumped to today. 12:45 pass is silent by design regardless."
    ),
    "| 2026-11-26 10:15 ET (native) | valley-pawn-blog-publisher |": (
        "COVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- FALSE ALARM, verified via "
        "fleet/receipts/valley-pawn-blog-publisher.jsonl (Rule 12): a post was published and Slack-announced "
        "at 02:15:21 ET today (\"Sinking Funds: The Easy Fix for Big Yearly Bills\", #C0APY6TE604, ok=true). "
        "Same recurring timezone/window-check bug as 10/26, 11/2, 11/9, 11/12, 11/19, 11/23 (watchdog checks "
        "before its own early-AM post lands). No action needed; underlying timing-check bug remains an open dev item."
    ),
    "| 2026-11-26 10:25 ET (native) | daily-cloudcover-check |": (
        "QUEUED 2026-11-26 (fleet-guardian 12:45 ET pass) -- [SIGN-IN] wall, same recurring Cloud Cover item "
        "already on Life OS/HUMAN_QUEUE.md (bumped). Per Sign-In Batching rule, held for Login Day 2026-12-01 "
        "(not a payment/legal deadline in the next 3 days)."
    ),
    "| 2026-11-26 10:28 ET | fb-inbox-replies |": (
        "COVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- no receipts file exists for this task to verify "
        "against, but the task's own message already confirms store inboxes were read directly and had no "
        "unanswered customer threads in the window -- no customer impact despite the Chekkit cross-check gap. "
        "Verify-only regardless; no rerun."
    ),
    "| 2026-11-26 10:30 ET (native) | daily-dress-code-check |": (
        "QUEUED 2026-11-26 (fleet-guardian 12:45 ET pass) -- [SIGN-IN] wall, same recurring Google Home item "
        "already on Life OS/HUMAN_QUEUE.md (bumped). Held for Login Day 2026-12-01 per the Sign-In Batching rule."
    ),
    "| 2026-11-26 10:31 ET (native) | daily-dress-code-check | The dress code check could not open any store's camera page, so nothing was posted. | NEEDS_HUMAN: no | OPEN |": None,  # handled by generic dress-code rule below but needs its own text
    "| 2026-11-26 11:10 ET (native) | supply-approvals |": (
        "UNRECOVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- verify-only (unlisted in rerun_manifest.json, "
        "purchasing-adjacent, hard limit regardless). Same multi-day REPEAT FAILURE class as 11/24-11/25 "
        "(DM'd 11/24 21:45), not re-run. Candidate for tonight's digest if still unresolved at 21:45."
    ),
    "| 2026-11-26 11:10 ET (native) | supply-deliveries |": (
        "UNRECOVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- same class as supply-approvals above. "
        "Candidate for tonight's digest if still unresolved at 21:45."
    ),
    "| 2026-11-26 12:01 ET (native) | daily-dress-code-check |": (
        "COVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- continuation of today's Google Home sign-in "
        "wall (10:30 ET row above), not a separate action."
    ),
}

# Special-case the two daily-dress-code-check rows separately since they share a prefix with the 10:30 sign-in one.
dress_code_downstream = (
    "COVERED 2026-11-26 (fleet-guardian 12:45 ET pass) -- downstream symptom of the 10:30 ET Google Home "
    "sign-in wall above, same row, not a separate action."
)

changed = 0
for i, line in enumerate(lines):
    if not line.startswith("| 2026-11-26"):
        continue
    if "| OPEN |\n" not in line and not line.rstrip("\n").endswith("| OPEN |"):
        continue
    for prefix, disposition in updates.items():
        if disposition is None:
            continue
        if line.startswith(prefix):
            # the 10:31 and 12:01 dress-code rows share no distinct prefix with the 10:30 one except full text;
            # guard: only match if this is the sign-in-wall row (contains "Google Home needs" or "CloudCover needs" etc.)
            if prefix.startswith("| 2026-11-26 10:30 ET (native) | daily-dress-code-check |") and "camera page" in line:
                continue
            newline = line.rstrip("\n")
            assert newline.endswith("| OPEN |"), repr(newline)
            newline = newline[: -len("OPEN |")] + disposition + " |\n"
            lines[i] = newline
            changed += 1
            break

# Now handle the two "could not open any store's camera page" rows (10:31 and 12:01) explicitly
for i, line in enumerate(lines):
    if line.startswith("| 2026-11-26 10:31 ET (native) | daily-dress-code-check |") and "camera page" in line and line.rstrip("\n").endswith("| OPEN |"):
        newline = line.rstrip("\n")
        newline = newline[: -len("OPEN |")] + dress_code_downstream + " |\n"
        lines[i] = newline
        changed += 1
    if line.startswith("| 2026-11-26 12:01 ET (native) | daily-dress-code-check |") and "camera page" in line and line.rstrip("\n").endswith("| OPEN |"):
        newline = line.rstrip("\n")
        newline = newline[: -len("OPEN |")] + dress_code_downstream + " |\n"
        lines[i] = newline
        changed += 1

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("rows changed:", changed)
