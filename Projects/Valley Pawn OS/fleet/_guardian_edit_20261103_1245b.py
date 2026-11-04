import io
path = "../Life OS/HUMAN_QUEUE.md"
with io.open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

idx = 55  # line 56, 0-based
old = lines[idx]
marker = "blocked by a session permission classifier)) |\n"
assert old.endswith(marker), repr(old[-60:])
addition = (" resurfaced 2026-11-03 (fleet-guardian 12:45 pass, SILENT) -- a SECOND scope gap "
    "found on the same bot app: conductwatch-report has failed 3 straight days (11/1-11/3) on "
    "`conversations.history: missing_scope` (its duplicate-guard read, a different API call than "
    "this row's files:write/getUploadURLExternal gap). Same fix location -- while on "
    "api.slack.com/apps for this row, also add channels:history (and/or groups:history/im:history, "
    "whichever covers the bot's own DM-history read) and Reinstall to Workspace once more; covers "
    "both gaps in one visit. See FAILURE_LEDGER.md 2026-11-03 07:35 ET conductwatch-report row. |")
new = old[:-len(marker)] + marker.rstrip("\n") + addition + "\n"
lines[idx] = new
with io.open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("done, new tail:", repr(lines[idx][-200:]))
