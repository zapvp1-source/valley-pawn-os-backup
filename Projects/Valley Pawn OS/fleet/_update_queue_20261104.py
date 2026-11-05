import shutil, os

base = os.path.expanduser("~/mnt/Projects")
path = os.path.join(base, "Life OS", "HUMAN_QUEUE.md")
backup = path.replace(".md", ".md.bak-guardian-20261104-1245")
shutil.copy(path, backup)

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# bump Last-hit note on the Slack OAuth scope row (line index 55, 0-based)
marker = "See FAILURE_LEDGER.md 2026-11-03 07:35 ET conductwatch-report row. |\n"
idx = None
for i, l in enumerate(lines):
    if l.endswith(marker):
        idx = i
        break
if idx is not None:
    lines[idx] = lines[idx].rstrip("\n")[:-1].rstrip() + " recurred a 4th consecutive day 2026-11-04 (conductwatch-report 07:35 ET again, identical conversations.history: missing_scope) -- resurfaced (fleet-guardian 12:45 pass, SILENT); Last hit bumped to 2026-11-04. |\n"
else:
    print("WARNING: conductwatch marker row not found")

new_rows = [
    "| 2026-11-04 | [SIGN-IN] **Northwest Registered Agent -- sign back in once (northwestregisteredagent.com, ~1 min).** Recurred again: the 08:52 ET run hit the credentials login screen instead of an auto-authenticated session (same wall as 2026-10-24 and 2026-11-01, both previously resolved by signing in). Sign in once in an attended Claude session (or in Chrome directly) so the session persists for future automated runs. | northwest-registered-agent-daily-check | 2026-11-04 | OPEN [SIGN-IN] -- held for Login Day (first Monday of month = 2026-12-07), not surfaced today |\n",
    "| 2026-11-04 | **Ask Culpeper and Waynesboro to open their October 2026 gold buckets in Bravo (~2 min, Slack or call).** Both October Elemetal settlements have arrived (Gold Karat $28,473.30, Gold With Stones $31,961.87) and Harrisonburg/Lexington/Roanoke already have their October gold/gold-with-stones buckets open, but Culpeper and Waynesboro have not started theirs yet (confirmed live in Bravo 2026-11-04 09:57 ET -- zero October gold buckets of any kind at either store). The scrap manifest stage can't finish until those two buckets exist; day 4 of the 1st-5th retry window, escalates further on the 5th if still missing. | scrap-monthly-bravo-manifest-stage | 2026-11-04 | OPEN |\n",
]
lines.extend(new_rows)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("backup:", backup)
print("bumped conductwatch row:", idx is not None)
print("rows added:", len(new_rows))
