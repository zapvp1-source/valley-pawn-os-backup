# VP Ops Engine

Claude-independent replacement for Valley Pawn's recurring Slack analytics. Plain Python, stdlib only, no LLM in the runtime path. See `../BUILD_SPEC.md` for the full spec and `STATE.md` for per-job cutover status.

## Layout

```
vpops/          shared library (common.py, xlsxmin.py, bravo.py, formats.py, watchdog.py)
jobs/           one job_*.py per Phase-1 job — each runnable standalone
tests/          golden tests, verified against real historical Slack posts / CSVs
launchd/        plist templates (not yet installed)
data/heartbeats/  written by every job run, read by job_watchdog.py
```

## Running a job

Every job defaults to `--dry-run` (render only, print to stdout, no Slack post):

```bash
python3 jobs/job_store_rankings.py            # dry-run
python3 jobs/job_store_rankings.py --shadow   # post to #vp-ops-shadow
python3 jobs/job_store_rankings.py --live     # post to production
```

Run the test suite:

```bash
for t in tests/test_*.py; do python3 "$t"; done
```

## Slack bot

Token lives in macOS Keychain (`security find-generic-password -a "$USER" -s vp-ops-slack-bot-token -w`), never in this repo. `common.py` checks Keychain first before falling back to env var / config file. The bot (`vp_ops_engine` in the Valley Pawn workspace) must be invited to any channel before it can post there — see `STATE.md` for which channels are done.

## Status

Jobs A (store rankings), B (aged inventory), C (employee rankings), D (loan/layaway review), and G (watchdog) are built, golden-tested against real production data, and live-verified in `#vp-ops-shadow`. Jobs E (Bravo trigger dropper) and F (daily loan/inventory text) are held pending a go-ahead — both have real-world side effects (a live Bravo pull; real iMessages) beyond this project's own test channel. See `STATE.md` for detail.
