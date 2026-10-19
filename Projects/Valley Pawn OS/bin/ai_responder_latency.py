#!/usr/bin/env python3
"""ai_responder_latency.py [--days N] — READ-ONLY: how long customers wait for the AI reply, and where the time goes.

Joins Chekkit per-message emails (Apple Mail Envelope Index, read-only) to the AI responder's event log
(fleet/ai_responder/events-*.jsonl) by store + nearest later reply within 10 min. Also prints Apple Mail's
fetch setting (defaults read com.apple.mail PollTime: -1 = Automatically/push, else minutes) and the
responder agent's launchd interval. Added 2026-10-18 (Joshua: "can we make this faster?").
"""
import datetime as dt, glob, json, os, sqlite3, subprocess, sys
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
days = int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7
STORES = {"culpeper": "CUL", "waynesboro": "WAY", "harrisonburg": "HAR", "lexington": "LEX", "roanoke": "ROA"}

env = glob.glob(os.path.expanduser("~/Library/Mail/V*/MailData/Envelope Index"))[0]
c = sqlite3.connect("file:%s?mode=ro" % env.replace(" ", "%20"), uri=True)
cutoff = int((dt.datetime.now() - dt.timedelta(days=days)).timestamp())
rows = list(c.execute(
    "select s.subject, m.date_received, m.date_sent from messages m left join subjects s on s.ROWID=m.subject "
    "left join addresses a on a.ROWID=m.sender where lower(a.address) like '%support@chekkit.io%' "
    "and s.subject like '%: message via %' and m.date_received >= ? group by coalesce(m.global_message_id, m.ROWID) order by m.date_received", (cutoff,)))
emails = [(dt.datetime.fromtimestamp(r[1], ET), dt.datetime.fromtimestamp(r[2], ET) if r[2] else None) for r in rows]

events = []
for p in glob.glob(os.path.join(OS_DIR, "fleet", "ai_responder", "events-*.jsonl")):
    for line in open(p):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("action") == "reply":
            events.append(dt.datetime.fromisoformat(e["ts"]))
events.sort()

lat, fetch_lag = [], []
for recv, sent in emails:
    nxt = [t for t in events if 0 <= (t - recv).total_seconds() <= 600]
    if nxt:
        lat.append((nxt[0] - recv).total_seconds())
    if sent:
        fetch_lag.append((recv - sent).total_seconds())

def stats(xs):
    if not xs:
        return "no data"
    xs = sorted(xs)
    return "n=%d  median %.0fs  p90 %.0fs  min %.0fs  max %.0fs" % (len(xs), xs[len(xs)//2], xs[int(len(xs)*0.9)], xs[0], xs[-1])

print("Per-message emails last %d days: %d; matched to an AI reply: %d" % (days, len(emails), len(lat)))
print("Chekkit email -> AI reply sent:        ", stats(lat))
print("Email sent (Chekkit) -> received (Mail):", stats(fetch_lag), " (Mail fetch lag; sent time per header)")
try:
    pt = subprocess.run(["defaults", "read", "com.apple.mail", "PollTime"], capture_output=True, text=True, timeout=5).stdout.strip()
except Exception:
    pt = "?"
print("Apple Mail PollTime:", pt or "(default)", "  (-1 = Automatically/push; otherwise minutes between checks)")
try:
    pl = open(os.path.expanduser("~/Library/LaunchAgents/com.valleypawn.chekkit-ai-responder.plist")).read()
    import re
    m = re.search(r"StartInterval</key>\s*<integer>(\d+)", pl)
    print("Responder agent interval:", m.group(1) + "s" if m else "?")
except Exception as e:
    print("Responder plist:", e)
