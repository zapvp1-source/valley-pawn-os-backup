#!/usr/bin/env python3
"""blog_announce.py [--render] — every 30 min: announce new thevalleypawn.com articles in #blog-posts (2026-10-05).

Takes over Step 8 of `valley-pawn-blog-publisher` (which now only publishes through the WordPress connector) and the
job of `blog-publisher-watchdog`: reads the site's public REST listing, posts title + link for any post not
announced before (state: fleet/blog_announce_state.json), and on Mon/Thu after 10:00 ET writes ONE ledger line if
no post has appeared since the 03:00 run. First run seeds state silently (never re-announces old posts)."""
import datetime as dt
import html
import json
import os
import sys
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack  # noqa: E402

ET = ZoneInfo("America/New_York")
OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
STATE = os.path.join(OS_DIR, "fleet", "blog_announce_state.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
CH = "C0APY6TE604"
URL = "https://thevalleypawn.com/wp-json/wp/v2/posts?per_page=10&_fields=id,date,link,title,excerpt"


def main():
    render = "--render" in sys.argv
    now = dt.datetime.now(ET)
    posts = json.load(urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "ValleyPawnOps/1.0"}), timeout=30))
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    seen = set(st.get("seen", []))
    first = not seen
    new = [p for p in posts if p["id"] not in seen]
    for p in sorted(new, key=lambda p: p["date"]):
        title = html.unescape(p["title"]["rendered"])
        if render:
            print("WOULD ANNOUNCE" if not first else "SEED", p["date"][:10], title)
            continue
        if not first:
            os.environ["VP_TASK"] = "valley-pawn-blog-publisher"
            vp_slack.post(CH, ":newspaper: *New on the blog:* %s\n%s" % (title, p["link"]))
        seen.add(p["id"])
    # missed-run check: Mon/Thu, after 10:00, newest post older than today's 03:00 slot
    if now.weekday() in (0, 3) and now.hour >= 10 and posts:
        newest = dt.datetime.fromisoformat(posts[0]["date"]).replace(tzinfo=ET)
        key = now.date().isoformat()
        if newest < now.replace(hour=3, minute=0, second=0, microsecond=0) and st.get("missed_logged") != key and not render:
            with open(LEDGER, "a") as fh:
                fh.write("| %s (native) | valley-pawn-blog-publisher | No new blog post appeared from today's scheduled run (newest is %s). | NEEDS_HUMAN: no | OPEN |\n"
                         % (now.strftime("%Y-%m-%d %H:%M ET"), newest.date()))
            st["missed_logged"] = key
    if not render:
        st["seen"] = sorted(seen)
        json.dump(st, open(STATE, "w"), indent=1)
    print("posts %d, new %d%s" % (len(posts), len(new), " (seeded)" if first else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
