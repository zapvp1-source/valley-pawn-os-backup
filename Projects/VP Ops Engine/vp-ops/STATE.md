# VP Ops Engine — Cutover State

Per BUILD_SPEC.md §2/§8. One row per Phase-1 job. States: `not-started | shadow-manual | shadow-scheduled | verified | LIVE`.

| Job | State | Notes |
|---|---|---|
| A — job_store_rankings | **LIVE** | Posted for real to `#store-performance` 2026-07-26 21:35 ET using fresh 2026-07-25 EOM data. Joshua reviewed and approved cutover. Old Claude tasks this replaces (`monday-store-rankings` / `weekly-store-kpis`) — Joshua's call whether/when to disable them, not this project's (Rule #4). |
| B — job_aged_inventory | **LIVE** | Posted for real to `#aged-inventory-review` 2026-07-26 21:35 ET using fresh 2026-07-26 data. Replaces `weekly-aged-inventory-report`. |
| C — job_employee_rankings | **LIVE** | Posted for real to `#employee-performance` 2026-07-26 21:35 ET. **Caught and fixed a real bug before this went live**: fresh Bravo export had employee names in ALL CAPS ("PRESTON PETERS" not "Preston Peters"), which would have broken the case-sensitive Preston-exclusion check — a hard "NEVER publish Preston Peters" rule violation. Fixed to exclude by employee code (`PMONEY`, stable across casing) with a case-insensitive name check as backup; also normalized all names to title case for display. Replaces `weekly-employee-sales-rankings`. |
| D — job_loan_layaway_review | **LIVE** | Posted for real to `#loan-review` and `#layaway-review` 2026-07-26 21:35 ET. Replaces `weekly-loan-layaway-review`. |
| E — trigger_dropper | **verified working, one real bug fixed** | See "What actually happened with Job E" below — TL;DR: found and fixed a real timeout-handling bug in my own code, found and worked around a real bug in the pre-existing `bravo_health_gate.sh` (false-negative FAIL despite Bravo actually being healthy), and cleared a genuine one-off "Bravo is already running" dialog collision via computer-use. All 20 cells (4 cells x 5 stores) pulled successfully. Not yet proven on an actual unattended launchd firing (only run manually today) — first real unattended test is tomorrow 05:30 ET. |
| F — job_daily_loan_inv_text | **LIVE** | Ran for real 2026-07-26 14:21 ET — real Bravo pull, real iMessages confirmed delivered to Joshua and Preston. |
| G — watchdog | **LIVE (failure path still untested live)** | Verified against real heartbeats repeatedly today, always correctly silent when healthy. Never actually fired a real failure DM (no genuine miss has happened yet) — will get exercised organically whenever one does. |

## What actually happened with Job E (worth reading before touching this again)

1. First live attempt (~14:29 ET) failed: Bravo's VM had a stuck "Bravo is already running" dialog (mis-diagnosed by the existing `bravo_health_gate.sh` as a ClickOnce update wedge, since `dfsvc.exe` happened to be present too). My own code failed safe (no partial data, heartbeat + DM), correctly did not hammer retries.
2. Found and fixed a real bug in `vpops/bravo.py`'s `ensure_healthy()`: the original 300s timeout was shorter than a worst-case Bravo recovery cycle (6-9 min observed). `subprocess.run(timeout=...)` only kills the direct child on timeout, not grandchildren — so a timed-out health check left the ACTUAL recovery script running orphaned in the background, contributing to a second `Bravo.exe` instance. Fixed: 900s timeout + `start_new_session=True` + kill the whole process group on timeout.
3. With Joshua present, got `computer-use` access to look at the actual Parallels screen, found and dismissed two stacked "Bravo is already running" dialogs (one click each) — this was the real root cause, not a ClickOnce update. Bravo recovered cleanly to Dashboard.
4. Second live attempt: `bravo_health_gate.sh` recovered Bravo successfully FOUR times in its own log (`recover result='OK CUL'` x4, including auto-handling a real ClickOnce prompt correctly) — yet still reported the overall gate as `FAIL no-dashboard`. Screenshot confirmed Bravo was genuinely on a healthy Dashboard at that exact moment. **This is a bug in the existing `bravo_health_gate.sh`'s final verdict logic** (likely treating `dfsvc.exe`'s mere presence as an automatic fail even after a successful recovery/update) — not something to fix here (Rule #4, hardened infra), but worth flagging to whoever maintains that script.
5. Given visual confirmation Bravo was healthy, dropped the trigger directly (`bravo.drop_trigger()`), bypassing the buggy gate check for this one run. Watcher claimed it immediately; all 20 cells (aged-inventory-summary, employee-activity, loans-75-days-past-due, layaways x 5 stores) completed successfully over about 24 minutes, confirmed via the trigger's own `result.json` (`"status": "success"` for all 20).
6. Found a second real bug while verifying the fresh employee-activity data: `bravo.py`'s `locate_store_files()` assumes a single-date filename prefix, but `employee-activity`'s AHK handler names its output by the raw requested date RANGE (`2026-07-01..2026-07-25_CUL_employee-activity.csv`), unlike `end-of-month` which uses just the range's end date. The old file sat right next to the new one under a different name shape, silently invisible to date-prefix parsing. Fixed with a new `latest_store_files_by_mtime()` locator (ignores filename convention entirely, just picks the most recently modified match) and switched Job C to use it.

**Bottom line: none of Job E's failures today were "Bravo is fundamentally broken."** Two were real (small) bugs in this new code, one was a stuck dialog needing one human click, and one is a pre-existing bug in the hardened `bravo_health_gate.sh` script that's outside this project's scope to fix but worth reporting.

## launchd agents installed (2026-07-26)

All 7 `com.valleypawn.vpops.*.plist` in `~/Library/LaunchAgents/`, loaded via `launchctl load`. Jobs A-D's wrappers now point at `--live` (flipped after Joshua's review and approval, 2026-07-26 21:30 ET). E/F/G already pointed at `--live`.

Check status: `launchctl list | grep vpops`. Remove one: `launchctl unload ~/Library/LaunchAgents/com.valleypawn.vpops.<job>.plist && rm ~/Library/LaunchAgents/com.valleypawn.vpops.<job>.plist`.

## Slack bot setup (one-time, done 2026-07-26)
- App: "VP Ops Engine" (`vp_ops_engine`, bot user ID U0BLQTHLUTA, app team Valley Pawn T03BL4W1DCL)
- Bot Token Scopes: `chat:write`, `im:write`, `users:read`
- Token stored in macOS Keychain: service `vp-ops-slack-bot-token`, account `$USER` — never in a repo file (Hard Rule #6)
- `vpops/common.py` checks Keychain first via `_keychain_lookup()`, before falling back to the legacy env-var/config-file chain (which had nothing in it on this Mac — the "existing token chain" BUILD_SPEC assumed was already populated was actually empty)
- Bot is now a member of all channels it needs: `#vp-ops-shadow`, `#store-performance`, `#aged-inventory-review`, `#employee-performance`, `#loan-review`, `#layaway-review`.

## Known deviations from BUILD_SPEC's assumptions (found during Phase 1 build)
- No Slack bot token existed anywhere on the Mac — the biggest gap between BUILD_SPEC's assumptions and reality (see above).
- Job A: the actual live poster differs in format from both `store_kpis_compile.py`'s own output and `monday-store-rankings/SKILL.md`'s documented example — neither uses the real format (italic + Slack emoji shortcodes). Renderer built to match real Slack history instead.
- Job B: real Slack history for #aged-inventory-review shows 5+ inconsistent format variants, none matching the CLAUDE.md canonical spec exactly. Built against CLAUDE.md directly.
- Job C: fresh Bravo exports can come back ALL CAPS instead of title case — a real, hard-rule-relevant bug, now fixed (see above).
- `employee-activity`'s output filename convention (full date range, not single end-date) differs from `end-of-month`'s — now handled via mtime-based file lookup instead of filename parsing.
- `bravo_health_gate.sh` (pre-existing, not modified) has a bug where it can report FAIL even after its own recovery logic reports 4 consecutive successes — worth flagging to whoever maintains it, not fixed here.
- Store-rankings and aged-inventory Slack evidence in BUILD_SPEC §4 ("store rankings last posted 3/23") does not match live channel history (real posts found through 2026-07-20) — worth a note back to the design session, doesn't change what was built.

## Phase 2 — dashboard (BUILD_SPEC.md §5) — complete, 2026-07-26

1. **`vpops/store.py`** — SQLite (`kpis(store,metric,value,as_of,period,source)` + `runs(job,ts,status,detail)`, exact schema per spec) + `data/latest.json` export. Wired into all 8 jobs (`write_run()` on every heartbeat; `write_kpis_bulk()` in Jobs A, B, D — the store-shaped ones). `write_run()` always regenerates `latest.json`, not just the KPI-writing jobs, so the export never goes stale relative to any single job's run (found and fixed a bug where it only reflected whichever of A/B ran last).
2. **Command Center KPI page** — new `/vpops` route + `/api/vpops-kpis` endpoint in `command_center.py` (backed up first: `command_center.py.bak-pre-vpops-kpi-page-2026-07-26`), plus one new link on the existing page. Verified both the existing `/` page and the new `/vpops` page render correctly after restarting the LaunchAgent.
3. **`publish_dashboard.py`** — renders vp-ops' SQLite data into the *existing* `Business Dashboard Website/site/data/kpis.json` schema (pastDue, pastDueTotal, companyLoanBalance, layaway, layawayTotal, dates.loans/layaway, and the 3 feed "Last Run" dates it owns) — every other field (funds, watch, daily.*, bravoDaily, other feeds) preserved untouched. Deployed live via `wrangler pages deploy`; verified on the real site with a cache-busted request (first check hit a stale CDN edge cache, don't be fooled by that — always cache-bust when verifying a fresh deploy).
4. Scheduled `com.valleypawn.vpops.publish_dashboard` — Mon 09:45 ET (15 min after Job D, the last of the Monday jobs to produce fresh loan/layaway data).

Also fixed while wiring this in (real bugs, found by actually testing, not by inspection):
- `store` module name was shadowed by a `for store, path in files.items()` loop variable in three job files (A, B, C) — silent `AttributeError` at the exact line that mattered. Renamed loop vars to `store_code` throughout.
- `common.report_crash()`'s `traceback.format_exception(exc)` single-arg call only works on Python 3.10+; this Mac runs 3.9. Fixed to the 3-arg form.

## Git structure correction (2026-07-26)

`~/Documents/Claude` is already a single git repo backed up nightly to `github.com/zapvp1-source/valley-pawn-os-backup` (task `vp-os-github-nightly-backup`) — it is NOT per-project. `git init` was mistakenly run inside `vp-ops/` itself first (creating a nested repo, which would have made this folder invisible to the parent backup as an untracked gitlink); corrected by removing that nested `.git` and instead extending `~/Documents/Claude/.gitignore`'s whitelist additively (new section, scoped to `Projects/VP Ops Engine/vp-ops/**` only — not a global extension whitelist, to avoid pulling in unrelated data files elsewhere) to cover `.json` (heartbeats, `latest.json`), `.plist` (launchd configs), and `.txt` (golden-test fixtures) — `.py`/`.sh`/`.md` were already covered. Verified via `git add -A -n` that every vp-ops file is now correctly staged. Did not commit myself — the nightly-backup task owns that step (it runs its own secret scan before committing, which I don't want to bypass).

## Next steps
1. Confirm tomorrow (2026-07-27, Monday) that ALL 8 launchd-scheduled firings succeed fully unattended (05:30/08:30/09:00/09:15/09:30/09:45 ET) — first real unattended test, today's runs were all manual/hands-on.
2. Old Claude-side tasks (`monday-store-rankings`/`weekly-store-kpis`, `weekly-aged-inventory-report`, `weekly-employee-sales-rankings`, `weekly-loan-layaway-review`, `monday-bravo-combined-compile`) were confirmed NOT auto-scheduled via CCR triggers (they're "T (manual)" per BUSINESS_OS.md, matching what `RemoteTrigger` list showed live) — no duplicate-posting risk, nothing to disable. If Joshua ever DOES want them gone, that's still his call in the scheduler UI (Rule #4), not this project's.
3. Consider reporting the `bravo_health_gate.sh` false-negative bug (recovers successfully 4x in its own log, still reports overall FAIL) to whoever maintains the Bravo Data Extraction pipeline.
4. Watch `vp-dashboard.pages.dev` and Command Center's `/vpops` page after Monday's real cycle to confirm they pick up fresh data automatically.
5. Acceptance criteria (BUILD_SPEC.md §9) status: Phase-1 jobs live ✅ (1 manual cycle done, needs 2 consecutive *scheduled* cycles); dashboard+Command Center showing current KPIs ✅; watchdog's real failure-DM path still unexercised (no genuine miss has happened yet); `vp-ops/` correctly whitelisted for the nightly backup ✅ (not yet committed — rides tonight's run); kill test conceptually passed today (Monday's reports + daily text did publish with Claude idle) but not yet proven on the real unattended schedule.
