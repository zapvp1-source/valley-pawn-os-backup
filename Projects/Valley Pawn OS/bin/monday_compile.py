#!/usr/bin/env python3
"""monday_compile.py [--render] [--pipeline-date D] [--post-date D] — native Monday ops posts.

Native counterpart of the Cowork task `monday-bravo-combined-compile` (2026-09-30), written so the Monday
reports keep publishing whatever happens to Cowork on 10/6. FORMAT PARITY IS BY CONSTRUCTION: every post
is the stdout of the same formatter the Cowork task already pasted "verbatim, byte for byte":
  #aged-inventory-review   Bravo Data Extraction/bin/format_aged_inventory.py  (posted as-is)
  #loan-review             comms_engine.py post --pub loan-review              (posts itself, bot)
  #layaway-review          comms_engine.py post --pub layaway-review
  #employee-performance    comms_engine.py post --pub employee-performance
  #first-payment-default   comms_engine.py post --pub first-payment-default
Every formatter enforces the all-5-stores completeness gate itself (exit 2 = withhold, post nothing).
Duplicate guard: comms_engine checks the channel itself; the aged post is skipped if a post with the
same header line already exists in the channel today (the bot can read posts made by either app).
NOT yet here: #store-performance store rankings (the Cowork task still does it) — see CHANGELOG.
Also: stashes the chekkit-inactives CSVs for the Tuesday task, and DMs Joshua a plain rollup.
"""
import datetime as dt
import glob
import os
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

AGENT = "monday-bravo-combined-compile"
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
BRAVO = os.path.expanduser("~/Documents/Claude/Projects/Bravo Data Extraction")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
AGED_CH = "C04NGH4FF35"
JOSHUA = "U03BB52MDSA"
PUBS = [("loan-review", "C0B08RS2BMK", "#loan-review"), ("layaway-review", "C04N24STDP1", "#layaway-review"),
        ("employee-performance", "C0ATTLPQHR8", "#employee-performance"),
        ("first-payment-default", "C0B17894S2Y", "#first-payment-default")]
PY = "/usr/bin/python3"


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def run(cmd, env=None):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    return p.returncode, p.stdout, p.stderr


def already_posted(channel, header, since):
    """True if a message starting with the same first line exists in the channel since `since`."""
    try:
        tok = vp_slack.token()
        import json, urllib.parse, urllib.request
        req = urllib.request.Request("https://slack.com/api/conversations.history?" + urllib.parse.urlencode(
            {"channel": channel, "oldest": str(since.timestamp()), "limit": "50"}), headers={"Authorization": "Bearer " + tok})
        r = json.load(urllib.request.urlopen(req, timeout=30))
        return any((m.get("text") or "").strip().splitlines()[:1] == [header] for m in r.get("messages", []))
    except Exception:
        return False


def main():
    render = "--render" in sys.argv
    now = dt.datetime.now(ET)
    post_date = arg("--post-date", now.date().isoformat())
    pipeline_date = arg("--pipeline-date", (dt.date.fromisoformat(post_date) - dt.timedelta(days=1)).isoformat())
    since = dt.datetime.combine(dt.date.fromisoformat(post_date), dt.time(0, 0), ET)
    lines, held = [], []

    # 1 — aged inventory (formatter prints; we post verbatim)
    rc, out, err = run([PY, os.path.join(BRAVO, "bin", "format_aged_inventory.py"),
                        "--pipeline-date", pipeline_date, "--post-date", post_date])
    if rc == 0 and out.strip():
        header = out.strip().splitlines()[0]
        if render:
            print("=== #aged-inventory-review (would post) ===\n" + out)
        elif already_posted(AGED_CH, header, since):
            lines.append("⏭️ Aged inventory — already posted today")
        else:
            env = dict(os.environ, VP_TASK=AGENT)
            tmp = "/tmp/monday_aged_%s.txt" % post_date
            open(tmp, "w").write(out)
            prc, _, perr = run([PY, os.path.join(BIN, "vp_slack.py"), "post", AGED_CH, "--file", tmp], env=env)
            lines.append("✅ Aged inventory — posted to #aged-inventory-review" if prc == 0 else "⚠️ Aged inventory — built but did not post")
    else:
        held.append("Aged inventory")
        if render:
            print("=== #aged-inventory-review WITHHELD (exit %d) ===\n%s" % (rc, err.strip()[-600:]))

    # 2 — comms_engine publications (they post themselves via the bot and self-dedupe)
    for pub, ch, name in PUBS:
        verb = "render" if render else "post"
        rc, out, err = run([PY, os.path.join(BIN, "comms_engine.py"), verb, "--pub", pub,
                            "--pipeline-date", pipeline_date, "--post-date", post_date], env=dict(os.environ, VP_TASK=AGENT))
        if render:
            print("=== %s %s (exit %d) ===\n%s%s" % (name, "would post" if rc == 0 else "WITHHELD", rc, out, err.strip()[-500:]))
            continue
        if rc == 0:
            lines.append("✅ %s — posted" % name)
        elif rc == 2:
            held.append(name)
        else:
            lines.append("⚠️ %s — did not post" % name)

    # 3 — chekkit-inactives stash for the Tuesday review-request task
    stash = os.path.expanduser("~/Documents/Claude/Scheduled/_shared-bravo-data/%s/chekkit-inactives" % post_date)
    found = 0
    for code in ("CUL", "HAR", "LEX", "ROA", "WAY"):
        c = sorted(glob.glob(os.path.join(BRAVO, "output", "%s*_%s_chekkit-inactives.csv" % (pipeline_date[:10], code))))
        if c:
            found += 1
            if not render:
                os.makedirs(stash, exist_ok=True)
                shutil.copyfile(c[-1], os.path.join(stash, "%s.csv" % code))
    if render:
        print("=== chekkit stash: %d/5 files would be copied to %s ===" % (found, stash))
        return 0

    # 4 — Joshua rollup (plain language, Rule 16)
    msg = ["✅ Monday reports — %s" % dt.date.fromisoformat(post_date).strftime("%a %b %-d")] + lines
    for h in held:
        msg.append("⏸️ %s — held until every store's data is complete" % h)
    msg.append("Store rankings — still posted by the Monday Claude task for now.")
    run([PY, os.path.join(BIN, "vp_slack.py"), "post", JOSHUA, "\n".join(msg)], env=dict(os.environ, VP_TASK=AGENT))
    if held:
        with open(LEDGER, "a") as fh:
            fh.write("| %s (native) | %s | Held for incomplete data: %s. | NEEDS_HUMAN: no | OPEN |\n"
                     % (now.strftime("%Y-%m-%d %H:%M ET"), AGENT, ", ".join(held)))
    print("\n".join(msg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
