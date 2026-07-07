---
name: daily-funds-verification
description: Daily verification that funds Joshua sent to each store made it into the store's Safe via Bravo's Safe Register Journal — runs at 6 PM ET every day. Zero computer-use; reads CSVs produced by the Bravo Data Extraction pipeline via osascript shell.
---

You are running Joshua Davis's daily funds verification for Valley Pawn / Full Circle Finance Inc. The goal: verify that the cash Joshua sent to each store today was actually entered into Bravo the same day.

**How this task works:** the verification no longer drives Bravo's UI. The Bravo Data Extraction pipeline runs inside a Windows VM and produces a Safe Register Journal CSV per store on demand. This task drops one trigger file (via the Mac shell since the pipeline folder isn't in the agent's sandbox), waits for the CSVs, then reconciles them against Slack. No Parallels grant required.

⚠️ **CRITICAL — DO NOT use the Write tool to drop the trigger file.** The Bravo Data Extraction folder (`/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`) is OUTSIDE this task's sandbox. The Write tool cannot reach it. Use `mcp__Control_your_Mac__osascript` to run shell commands instead. The pattern is illustrated in Step 2.

# Step 1 — Slack scan (fast, ~5 tool calls)

For each of the 5 store funds channels, pull TODAY's messages (oldest = midnight local). Capture each store's request and Joshua's "sent X" reply (amounts like "1k", "2k", "800", "$1,000"). Track cancellations — if a store later says "don't need it", that send was NOT entered.

| Channel | Channel ID | Store code | Store name |
|---|---|---|---|
| #pepper-funds | C03BLHFJ3KN | CUL | Culpeper (Joshua calls it "Pepper") |
| #lex-funds | C03B3K5DL6T | LEX | Lexington |
| #boro-funds | C03BLLRN64U | WAY | Waynesboro (Joshua calls it "Boro") |
| #roanoke-funds | C063K8E02TW | ROA | Roanoke |
| #harrisonburg-funds | C03BWRKEDUZ | HAR | Harrisonburg |

Use `slack_read_channel` with `oldest=<today_midnight_unix>` and `response_format=concise`. Send all 5 reads in a single message for parallelism. Build a per-store ledger:

```
{ store: "WAY",
  amounts_sent: [{amount: 1000, time: "12:13", text: "sent 1k"}],
  cancellations: [],
  net_expected: 1000 }
```

Cancellations subtract from `net_expected`. If a store has zero sends, `net_expected` is 0 and it's still part of the report.

# Step 2 — Drop the Bravo trigger via osascript

Build the trigger JSON in memory, then write it to disk via `mcp__Control_your_Mac__osascript` shell escape. The Bravo Data Extraction folder is at `/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/`.

**2a. Generate a trigger ID:**
```
daily-funds-verification-YYYY-MM-DDTHH-MM-SS
```

**2b. Build the trigger JSON string:**
```json
{
  "id": "daily-funds-verification-2026-05-12T18-03-00",
  "requested_at": "2026-05-12T18:03:00-04:00",
  "reports": [
    {
      "name": "safe-register-journal",
      "stores": ["CUL", "HAR", "LEX", "ROA", "WAY"],
      "date": "2026-05-12"
    }
  ]
}
```

**2c. Write via osascript.** Use this exact pattern (substitute the JSON and id):

```applescript
set triggerId to "daily-funds-verification-2026-05-12T18-03-00"
set triggerJson to "{\"id\": \"" & triggerId & "\", \"requested_at\": \"2026-05-12T18:03:00-04:00\", \"reports\": [{\"name\": \"safe-register-journal\", \"stores\": [\"CUL\",\"HAR\",\"LEX\",\"ROA\",\"WAY\"], \"date\": \"2026-05-12\"}]}"
set triggerPath to "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/triggers/" & triggerId & ".json"
do shell script "echo " & quoted form of triggerJson & " > " & quoted form of triggerPath
return "dropped " & triggerPath
```

**2d. Poll for completion via osascript.** The watcher polls `triggers/` every 30s. The full 5-store cycle takes ~4-5 minutes. Poll every 30 seconds via:

```applescript
do shell script "test -f '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/" & triggerId & ".result.json' && echo READY || echo PENDING"
```

Loop with a small delay between polls. Time out at 10 minutes (20 polls).

**2e. Read the result JSON via osascript:**

```applescript
do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/results/" & triggerId & ".result.json'"
```

Parse the returned JSON. For each cell with `status="success"`, the `output_path` field points to the CSV.

If a cell's `status` is anything other than `success`, treat that store as `❓ Could not verify`. If the timeout fires with no result JSON, DM Joshua the failure and stop.

# Step 3 — Read and parse each CSV via osascript

For each successful cell, read its CSV via:

```applescript
do shell script "cat '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/2026-05-12_WAY_safe-register-journal.csv'"
```

Columns: `Txn Num, Date & Time, , Txn Type, Till Number, Associate, Comments, , Tender Type, , Amt Coll`.

**Signature for funds Joshua sent:**
- `Txn Type` = `TENDER TRANSFER`
- `Till Number` = `BANK`
- `Amt Coll` is the negative leg (e.g. `"($2,000.00)"`)

Parse amounts by stripping `$`, `(`, `)`, `,` and converting to a positive float. Sum per store.

# Step 4 — Reconcile and report

For each store:
- `✓ Matched` — totals within $1 (or both zero)
- `⚠ Discrepancy` — differ by more than $1
- `❓ Could not verify` — pipeline cell failed

**Save the report via osascript** at `/Users/joshuadavis/Documents/Claude/Projects/Daily Funds Verification/<YYYY-MM-DD> Funds Verification.md`. Use heredoc through osascript:

```applescript
do shell script "cat > '/Users/joshuadavis/Documents/Claude/Projects/Daily Funds Verification/" & today & " Funds Verification.md' <<'EOF'
# Daily Funds Verification — " & today & "

... report body ...
EOF"
```

Post a Slack DM to Joshua (`U03BB52MDSA`) leading with the bottom line. Use a markdown table.

# If something goes wrong

- **Watcher not running** (no result JSON and no CSVs after 10 min): DM Joshua the failure with the trigger ID and stop. He'll restart the watcher.
- **Some cells succeeded, others didn't**: report what you have, mark the rest `❓ Could not verify`.
- **No activity today** (Slack ledgers empty AND CSVs only SAFE OPEN-BALANCE): post "No funds activity today — all clear" one-liner DM.
- **Sandbox write fails despite osascript**: DM Joshua to manually deploy. Don't keep trying.

# Background

This SKILL was rewritten 2026-05-12 to use the Bravo Data Extraction pipeline. The Bravo Data Extraction folder is OUTSIDE the scheduled-task agent's sandbox, so all filesystem I/O against that folder MUST go through `mcp__Control_your_Mac__osascript do shell script` (not the Write/Read tools). Without this, the agent gets stuck trying to `request_cowork_directory` which Joshua won't approve mid-cron.

The 2026-05-12 first run failed exactly that way — agent built the Slack ledger then hit the sandbox wall trying to Write the trigger file. The fix is this osascript pattern, baked into every filesystem touch.
