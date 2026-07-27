"""
common.py — shared helpers for the Valley Pawn Claude-independent job runner.

Copied verbatim from:
  Documents/Claude/Projects/Business Continuity/common.py
per BUILD_SPEC.md §1 (REUSE, don't rebuild). Do NOT edit the original — this
is the VP Ops Engine's own copy; changes here stay in this repo only.

Design goal: every job module in jobs/ is a thin wrapper around logic that
ALREADY EXISTS as a plain script somewhere in this Mac's Projects folder
(run_daily_intake.py, store_kpis_compile.py, brevo_preflight_watchdog.py,
etc.) or, for funds-verification, around the documented Bravo Data
Extraction trigger/result file contract. This file holds only the plumbing
that's identical across every job: Slack posting, logging, and locating the
Slack bot token — using the EXACT SAME token-resolution chain already used
by run_daily_intake.py, so no new secret needs to be configured.
"""

from __future__ import annotations
import json
import logging
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HOME = Path.home()
LOG_DIR = HOME / "Library" / "Logs" / "vp-continuity"

JOSHUA_SLACK_ID = "U03BB52MDSA"

# Real, confirmed channel IDs (looked up live via the Slack connector, not
# guessed from documentation — documentation drifts, the workspace doesn't).
CHANNELS = {
    "daily-funds-reconcilation": "C0B3R9B3S8H",
    "pawn-walks": "C0B8WR95N31",
    "store-performance": "C03CGTN3KN1",
    "email-campaigns": "C0APR5WUL2Z",   # channel is literally named #email-campiagns (typo in prod)
    "aged-inventory-review": "C04NGH4FF35",
    "employee-performance": "C0ATTLPQHR8",
    "loan-review": "C0B08RS2BMK",
    "layaway-review": "C04N24STDP1",
    "vp-ops-shadow": "C0BLQSABGGY",
}

BRAVO_ROOT = Path("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction")


# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

def setup_logging(job_name: str) -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d")
    log_path = LOG_DIR / f"{ts}-{job_name}.log"
    logger = logging.getLogger("vp-continuity")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(log_path)
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return log_path


log = logging.getLogger("vp-continuity")


# ---------------------------------------------------------------------
# Slack bot token — same fallback chain as run_daily_intake.py
# (env var -> Bravo Data Extraction/slack_config.json -> ~/.vp_slack_config.json
#  -> shell profile). Reusing this means no new secret setup for Joshua:
#  if the existing pipeline can already post to Slack, so can this.
# ---------------------------------------------------------------------

KEYCHAIN_SERVICE = "vp-ops-slack-bot-token"


def _keychain_lookup(service: str) -> str | None:
    """BUILD_SPEC.md Hard Rule #6: new secrets go in macOS Keychain only.
    Checked first, ahead of the legacy env-var/config-file chain below
    (which BUILD_SPEC assumed already had a token in it — verified
    2026-07-26 that none of those locations actually did)."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-a", os.environ.get("USER", ""), "-s", service, "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            tok = result.stdout.strip()
            if tok.startswith("xoxb-"):
                return tok
    except Exception:
        pass
    return None


def get_slack_token() -> str | None:
    tok = _keychain_lookup(KEYCHAIN_SERVICE)
    if tok:
        return tok

    tok = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if tok.startswith("xoxb-"):
        return tok

    for cpath in [
        BRAVO_ROOT / "slack_config.json",
        HOME / ".vp_slack_config.json",
    ]:
        try:
            d = json.loads(cpath.read_text())
            t = (d.get("SLACK_BOT_TOKEN") or d.get("slack_bot_token") or "").strip()
            if t.startswith("xoxb-"):
                return t
        except Exception:
            pass

    for profile in [HOME / ".bash_profile", HOME / ".zshenv", HOME / ".profile"]:
        try:
            txt = profile.read_text()
            m = re.search(r'(?:export\s+)?SLACK_BOT_TOKEN=["\']?(xoxb-[^\s"\']+)', txt)
            if m:
                return m.group(1).rstrip("\"'")
        except Exception:
            pass

    return None


def _slack_api(method: str, payload: dict) -> dict:
    token = get_slack_token()
    if not token:
        log.error(f"No Slack token found anywhere in the known fallback chain. Cannot call {method}.")
        return {"ok": False, "error": "no_token"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        log.error(f"Slack network error calling {method}: {e}")
        return {"ok": False, "error": str(e)}
    if not body.get("ok"):
        log.error(f"Slack API error on {method}: {body.get('error')}")
    return body


def _slack_api_get(method: str, params: dict) -> dict:
    token = get_slack_token()
    if not token:
        return {"ok": False, "error": "no_token"}
    qs = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"https://slack.com/api/{method}?{qs}",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        log.error(f"Slack network error calling {method}: {e}")
        return {"ok": False, "error": str(e)}


def slack_post(channel: str, text: str, dry_run: bool = False, thread_ts: str | None = None) -> str | None:
    """Posts a message. Returns the message ts (for threading a reply) or None."""
    if dry_run:
        log.info(f"[DRY-RUN] Would post to {channel} (thread_ts={thread_ts}):\n{text}")
        return "dryrun-ts"
    payload = {"channel": channel, "text": text, "mrkdwn": True}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    resp = _slack_api("chat.postMessage", payload)
    return resp.get("ts") if resp.get("ok") else None


def slack_dm(user_id: str, text: str, dry_run: bool = False):
    if dry_run:
        log.info(f"[DRY-RUN] Would DM {user_id}:\n{text}")
        return
    opened = _slack_api("conversations.open", {"users": user_id})
    dm_channel = opened.get("channel", {}).get("id") if opened.get("ok") else None
    if not dm_channel:
        log.error(f"Could not open DM with {user_id}; falling back to funds channel alert")
        _slack_api("chat.postMessage", {"channel": CHANNELS["daily-funds-reconcilation"], "text": f"@here (DM to Joshua failed) {text}"})
        return
    _slack_api("chat.postMessage", {"channel": dm_channel, "text": text, "mrkdwn": True})


def slack_read_history(channel: str, oldest_ts: float) -> list:
    resp = _slack_api_get("conversations.history", {"channel": channel, "oldest": str(oldest_ts), "limit": "200"})
    if not resp.get("ok"):
        return []
    return resp.get("messages", [])


def report_crash(job_name: str, exc: BaseException, dry_run: bool = False):
    import traceback
    # Python 3.9's traceback.format_exception() needs the 3-arg
    # (etype, value, tb) form -- the original common.py's single-exception
    # call only works on 3.10+. Found by testing 2026-07-26.
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    log.error(f"UNHANDLED EXCEPTION in {job_name}:\n{tb}")
    try:
        slack_dm(JOSHUA_SLACK_ID, f"\U0001F6D1 vp-continuity job '{job_name}' crashed:\n```{tb[-1500:]}```", dry_run=dry_run)
    except Exception:
        log.error("Also failed to DM Joshua about the crash — check the log file directly.")


def missed_run_dm(job_name: str, date_str: str, dry_run: bool = False):
    """Rule #3 (BUILD_SPEC): the ONE allowed failure-alert format, plain language only."""
    slack_dm(JOSHUA_SLACK_ID, f"⚠️ VP Ops job \"{job_name}\" did not complete — {date_str}.", dry_run=dry_run)
