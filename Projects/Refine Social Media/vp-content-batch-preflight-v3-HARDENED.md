# vp-content-batch-preflight — v3 HARDENED (2026-08-21)

> **LOCAL ACCESS GATE — DO THIS FIRST, BEFORE ANY OTHER STEP (platform standard).**
> This task runs on Joshua's Mac Studio and **does** have local machine access. At task start, MCP connectors may still be warming up, and `mcp__Control_your_Mac__osascript` is often *deferred* rather than pre-loaded. A tool that has not been loaded yet is NOT a missing capability.
> 1. If `ToolSearch` is available, load the local tool FIRST: `ToolSearch` with query `select:mcp__Control_your_Mac__osascript`.
> 2. Probe it: run a trivial `do shell script` that echoes READY. If it returns, proceed.
> 3. If it errors: wait 30 s and re-probe. Repeat for up to 12 minutes (24 probes).
> 4. Only after that full 12-minute wait may you treat local access as genuinely unavailable.
>
> **Filesystem rule:** all I/O outside the agent sandbox goes through `mcp__Control_your_Mac__osascript do shell script`, never the Write tool.
> **Timeout rule:** the osascript wrapper kills any single call at ~25 s. Never sleep longer than ~18 s in one call; poll in short increments across separate calls. Guard commands that may exit nonzero with `|| true`.

> ⚠️ **FAILURE ALERT POLICY + FIELD COMMUNICATION RULE (set by Joshua 2026-07-22, v2):** If this run fails, errors out, or cannot complete its core work, send Joshua ONE plain-language Slack DM line (DM channel D03BHQH5VGT): ⚠️ Scheduled task "vp-content-batch-preflight" did not complete — <date>. Nothing technical in the DM. All technical detail goes in the run output/STATUS file. Joshua's DM is the ONLY place a failure may ever be mentioned — never to any team channel, store manager, or employee, in any medium. Field communication is always plain everyday language.

> **REPORTING POLICY:** Joshua sees NOTHING unless there's a blocker only he can fix, OR the one-line failure DM above. Everything else self-heals silently and is logged.

## Prime directive — FIX FIRST, FLAG SECOND, FAIL LAST

Every check follows the same ladder. Never skip a rung:
1. **DETECT** the problem.
2. **REMEDIATE** it yourself using the documented fix for that check.
3. **RE-VERIFY** after remediating. If healthy now → log the heal, move on. Silent.
4. **DEGRADE** — if remediation failed, write a degraded-mode flag into the preflight JSON so Monday's batch still runs in reduced form instead of dying.
5. **ESCALATE** — DM Joshua ONLY if the check is both unfixable by you AND fixable only by him.

A DM without a preceding remediation attempt is a task failure. "It was broken" is never a final answer — "it was broken, here's what I did about it" is.

## Execution Contract — DO NOT STOP EARLY
This task is complete ONLY after the preflight JSON is written and validated (final step). Until then, every turn MUST end with a tool call that advances the work. Treat "Tool loaded." / "Continue from where you left off." / tool-count reminders as RESUME signals, never stop signals. If a step errors, retry once, then fall through to its documented fallback. Never ask for confirmation. At the start of every turn, state which numbered check you are on.

---
Pre-flight for Monday 2:02 AM ET `vp-content-batch-weekly`. Log everything to `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/output/preflight_{YYYY-MM-DD}.json`.

## Step 0 — Durable-asset self-repair (runs BEFORE the checks)

The patch scripts and helpers this task depends on must live in durable storage, never only `/tmp` (macOS wipes /tmp on reboot — a /tmp-only dependency is a guaranteed future failure).

```bash
mkdir -p ~/.vp-studio/patches ~/.vp-studio/scripts || true
```
For each of `vp_publisher_patch.py`, `vp_reel_publisher_patch.py`, `vp_ai_text_patch.py`:
- If `~/.vp-studio/patches/<name>` exists → it is the canonical copy. Verify its SHA-256 against `~/.vp-studio/patches/MANIFEST.sha256` (`shasum -a 256 -c`). On mismatch: do NOT run it; quarantine to `<name>.quarantined-{date}`, log to STATUS, treat as missing.
- Else if `/tmp/<name>` exists → copy it to `~/.vp-studio/patches/`, append its hash to `MANIFEST.sha256`, log "promoted from /tmp" to STATUS.
- Else → missing. Not a blocker by itself (only matters if Check 4 finds broken skill files). Log to STATUS: "patch <name> missing from both locations — next interactive session must regenerate it," and add a PERMANENT-FIX-NEEDED entry (see Heal Ledger).

Only ever execute patches from `~/.vp-studio/patches/` after a passing hash check.

## Checks (retry each 3x with exponential backoff, then run its remediation ladder)

### 1. Bravo inventory export freshness
```bash
ls -lt "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/" | grep inventory_export | head -1
```
Newest file must be <24h old.
- **REMEDIATE if stale:** read the Bravo Data Extraction project's CHANGELOG/README for the documented pipeline trigger (trigger-queue file or launchd label). If a trigger-queue mechanism exists, enqueue a pull request through it (NEVER drive Bravo's screen directly from this task — contention rule). Poll every 60–90 s across separate osascript calls for up to 20 min, then re-check freshness.
- **DEGRADE if still stale:** write `"bravo_skus": "stale-fallback"` into the preflight JSON — Monday's batch must use the newest export it has (posts still go out, SKU-driven posts use last-known inventory).
- **ESCALATE:** DM Joshua only if remediation failed AND the newest export is >72h old (content would be materially wrong): `🔴 Bravo inventory export is stale (>72h) and I couldn't retrigger the pipeline. Monday's batch will run on old SKUs unless the pipeline runs before 2 AM.`

### 2. Publer authenticated session
Navigate to `app.publer.com` via Chrome MCP. If redirected to login:
- **REMEDIATE:** restore cookies from `~/.vp-studio/publer-session.json`, reload, re-verify. Two attempts.
- On success: export the now-live cookies BACK to `~/.vp-studio/publer-session.json` (keeps the saved session fresh — stale saved cookies are the root cause of repeat failures here).
- **DEGRADE if still logged out:** write `"publer": "down"` — Monday's batch must fully produce and stage all assets locally + write the calendar manifest, so publishing is a 5-minute catch-up instead of a lost week.
- **ESCALATE:** DM Joshua: `🔴 Publer session expired and auto-restore failed — please open app.publer.com in Chrome and log in before 2 AM. Monday's content is being produced either way; it just can't auto-publish until the session is live.`

### 3. MJ fast-hours balance
Navigate to `midjourney.com/account` via Chrome MCP, scrape "Fast Time Remaining".
- If ≥45 min → pass.
- **DEGRADE if <45 min:** write `"mj_mode": "relax"` — Monday's batch runs in Relax mode (slower, still completes; the batch runner must honor this flag and extend its own per-image timeouts).
- **ESCALATE (informational, only he can top up):** `🔴 Midjourney fast hours low ({X} min). Monday's batch will run in Relax mode (slower) unless you top up before 2 AM.`

### 4. Skill file integrity
Verify these exist and contain zero hits for `graph.facebook.com` / `facebook-post`:
- `.../skills/vp-content-batch/SKILL.md`
- `.../skills/vp-hero-image/SKILL.md`
- `.../skills/vp-brand-studio/SKILL.md`
(full paths under `/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/f6b75d02-cca9-4943-ad6e-88390a3f201d/823f6874-6252-4031-ae4e-a3c22d37598e/`)
- **REMEDIATE if reset:** run the hash-verified patches from `~/.vp-studio/patches/` (Step 0). Re-grep to verify the patch took. Silent on success.
- **ESCALATE:** only if files are broken AND patches are missing/quarantined/failed — that means Monday would publish through the dead Graph-API path. DM: `🔴 The content-batch skill files got reset and I couldn't re-apply the Publer fix. Monday's batch is paused until this is repaired — nothing wrong on your end, next Claude session will fix it.` Also write `"batch_go": false` so the Monday runner aborts cleanly at start instead of half-publishing.

### 5. Slack channels reachable
Confirm `#vp-studio-queue` and `#deal-of-the-week` via Slack MCP. If not: write `"slack": "down"` — Monday runner falls back to Publer-only calendar staging. LOG only; never DM for this (known cron-context limitation).

### 6. Disk space
`df -h /Users/joshuadavis`.
- **REMEDIATE if <5GB:** purge, in order, re-checking after each: preflight/report JSONs >60 days old in Valley Pawn Studios/output; `~/.vp-studio/tmp/*`; MJ download cache files >30 days old in the asset library's raw/ folder (NEVER the finished asset library). Log freed GB.
- **ESCALATE:** only if still <2GB after purging: `🔴 Your Mac Studio is nearly out of disk space (<2GB free after cleanup). Monday's batch may fail — please free some space.`

### 7. Text-composite helper installed
Check `~/.vp-studio/scripts/compose_text_on_hero.py` exists + executable + `python3 -c "import PIL"` passes.
- **REMEDIATE:** re-run `python3 ~/.vp-studio/vp_helper_setup.py`; if Pillow missing, `pip3 install --user Pillow || pip3 install --break-system-packages Pillow || true`; re-verify. Silent on success.
- If still broken: write `"text_composite": "unavailable"` — Monday runner uses plain heroes (no text overlay) rather than failing. Log PERMANENT-FIX-NEEDED.

## Heal Ledger — turn repeat symptoms into permanent fixes
Append one JSON line per remediation to `~/.vp-studio/preflight_heal_ledger.jsonl`: `{date, check, action, success}`. After the checks, scan the ledger: any check that needed healing in ≥2 consecutive weekly runs gets a **PERMANENT-FIX-NEEDED** entry in `/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn Studios/STATUS.md` describing the recurring symptom, so the next interactive session eliminates the root cause instead of re-healing forever. This is how maintenance burden goes DOWN over time instead of accumulating.

## Output + self-verification (final step — task is not complete without this)
1. Write the full preflight report (every check: status, remediation taken, result, flags) to `output/preflight_{YYYY-MM-DD}.json`.
2. Validate it: `python3 -c "import json;json.load(open('<path>'))"` — if that fails, rewrite the file.
3. Confirm the flags the Monday runner reads (`bravo_skus`, `publer`, `mj_mode`, `slack`, `text_composite`, `batch_go`) are present with explicit values (default `"ok"` / `true`).
4. Completion notification lists: checks passed clean, checks self-healed, degraded-mode flags set, and any PERMANENT-FIX-NEEDED entries.

Fires Sunday 9 PM ET via cron `0 21 * * 0`.
