#!/usr/bin/env python3
"""vp_route.py — the ONE routing layer for every automated Slack post (Slack Restructure, 2026-11-09).

WHY: 136 publishers post to ~45 channels from ~100 scripts. Changing where/how each one posts by editing
each script is slow and dangerous. Instead every send already passes through vp_slack.post (and
comms_engine.cmd_post); this module sits inside that one chokepoint and applies rules from
fleet/slack_routes.json. Change the JSON, every publisher follows. Remove the row, it reverts.

ACTIONS (first matching rule wins; no rule = post unchanged):
  redirect  -> post to another channel (channel merges). `has()` dedupe/guardian checks follow too.
  quiet     -> an all-clear post is NOT sent; one line goes to fleet/quiet_ledger/YYYY-MM-DD.md and a
               receipt (surface slack-quiet) is written so the fleet knows the task ran and was clean.
  drop      -> never post this publication to a channel (ticker posts that belong on a canvas only).
               Ledger line + receipt, same as quiet.
  reply     -> post as a reply under the newest channel message containing reply_to_marker (e.g. the
               layaway yield report under the Monday layaway review). Not found -> top-level as before.
  thread    -> post as a reply under today's group parent in the channel (e.g. the three #basics
               morning checks under one "Morning checks — <date>" message). First post of the day
               creates the parent.
  headline  -> (Phase 1) body longer than max_lines: first max_lines lines + "Full table → <canvas>"
               go to the channel, full body is written to the channel's canvas section for this marker.
               Inactive until the rule carries a canvas id.

MATCHING per rule: channel (id) AND optional marker (substring, case-sensitive, anywhere in text)
AND optional task ($VP_TASK). `clean_any` = list of regexes; quiet fires only if at least one matches
AND none of `dirty_any` matches. All regexes are re.search with re.S|re.I.

SAFETY: fails OPEN. Any exception, missing config, or VP_ROUTE_OFF=1 -> the original post goes out
unchanged. `enabled: false` at the top of the JSON switches the whole layer off in one edit.
Python 3.9, stdlib only.
"""
import datetime as dt
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OS_DIR = os.path.dirname(HERE)
ROUTES = os.environ.get("VP_ROUTES_FILE") or os.path.join(OS_DIR, "fleet", "slack_routes.json")
LEDGER_DIR = os.path.join(OS_DIR, "fleet", "quiet_ledger")
THREAD_STATE = os.path.join(OS_DIR, "fleet", "state", "route_threads.json")


def _load():
    with open(ROUTES, encoding="utf-8") as fh:
        cfg = json.load(fh)
    if not cfg.get("enabled", True):
        return None
    return cfg


def _match(rule, channel, text, task):
    if rule.get("disabled"):
        return False
    if rule.get("channel") and rule["channel"] != channel:
        return False
    if rule.get("task") and rule["task"] != (task or ""):
        return False
    if rule.get("marker") and rule["marker"] not in text:
        return False
    if rule.get("only_days") and dt.date.today().strftime("%a") not in rule["only_days"]:
        return False
    return True


def _rx(pats, text):
    return any(re.search(p, text, re.S | re.I) for p in (pats or []))


def _is_clean(rule, text):
    if not _rx(rule.get("clean_any"), text):
        return False
    if _rx(rule.get("dirty_any"), text):
        return False
    return True


def ledger(rule, channel, text, task, action):
    if os.environ.get("VP_ROUTE_DRY") == "1":
        return
    try:
        os.makedirs(LEDGER_DIR, exist_ok=True)
        now = dt.datetime.now()
        line = "- %s · %s · %s · %s · #%s · %s\n" % (
            now.strftime("%H:%M"), action, rule.get("id", "?"), task or "-", rule.get("channel_name", channel),
            re.sub(r"\s+", " ", text.strip())[:300])
        with open(os.path.join(LEDGER_DIR, now.strftime("%Y-%m-%d") + ".md"), "a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass


def resolve_channel(channel):
    """Redirect only — used by has() so dedupe + guardian checks look where the post actually went."""
    try:
        cfg = _load()
        if not cfg:
            return channel
        for rule in cfg.get("rules", []):
            if rule.get("action") == "redirect" and not rule.get("disabled") and rule.get("channel") == channel \
                    and not rule.get("marker") and not rule.get("task"):
                return rule["to"]
    except Exception:
        pass
    return channel


def apply(channel, text, task=None):
    """Returns (action, channel, text, rule). action in post|redirect|quiet|drop|thread|headline."""
    if os.environ.get("VP_ROUTE_OFF") == "1":
        return "post", channel, text, None
    try:
        cfg = _load()
        if not cfg:
            return "post", channel, text, None
        task = task if task is not None else os.environ.get("VP_TASK", "").strip()
        # pass 1 — redirects (channel merges). Resolved first so the action rules below are judged
        # against the channel the post will actually land in. One hop only.
        redirected = None
        for rule in cfg.get("rules", []):
            if rule.get("action") == "redirect" and _match(rule, channel, text, task):
                channel, redirected = rule["to"], rule
                break
        for rule in cfg.get("rules", []):
            if rule.get("action") == "redirect" or not _match(rule, channel, text, task):
                continue
            act = rule.get("action")
            if act == "drop":
                ledger(rule, channel, text, task, "drop")
                return "drop", channel, text, rule
            if act == "quiet":
                if _is_clean(rule, text):
                    ledger(rule, channel, text, task, "quiet")
                    return "quiet", channel, text, rule
                continue                                # not clean -> the exception posts; later rules may still shape it
            if act == "thread":
                return "thread", channel, text, rule
            if act == "reply":
                return "reply", channel, text, rule
            if act == "headline":
                if rule.get("canvas") and len(text.strip().splitlines()) > int(rule.get("max_lines", 5)):
                    return "headline", channel, text, rule
                return "post", channel, text, rule
            return "post", channel, text, rule
        if redirected:
            return "redirect", channel, text, redirected
    except Exception as exc:  # fail open, always
        sys.stderr.write("vp_route: %s — posting unchanged\n" % exc)
    return "post", channel, text, None


# ---------------------------------------------------------------- thread parents
def _load_threads():
    try:
        with open(THREAD_STATE, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_threads(st):
    try:
        os.makedirs(os.path.dirname(THREAD_STATE), exist_ok=True)
        tmp = THREAD_STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(st, fh, indent=1)
        os.replace(tmp, THREAD_STATE)
    except Exception:
        pass


def _period(rule):
    """'day' (default) -> 2026-11-09 ; 'week' -> 2026-W46 (Mon-Sun) ; 'month' -> 2026-11."""
    today = dt.date.today()
    k = rule.get("thread_key", "day")
    if k == "week":
        y, w, _ = today.isocalendar()
        return "%d-W%02d" % (y, w)
    if k == "month":
        return today.strftime("%Y-%m")
    return today.isoformat()


def _current_periods():
    today = dt.date.today()
    y, w, _ = today.isocalendar()
    return {today.isoformat(), "%d-W%02d" % (y, w), today.strftime("%Y-%m")}


def thread_parent(call, channel, rule):
    """Return the ts of the current period's parent for this rule's group, creating it if needed."""
    group = rule.get("thread_group", rule.get("id"))
    period = _period(rule)
    key = "%s|%s|%s" % (channel, group, period)
    st = _load_threads()
    if st.get(key):
        return st[key]
    today = dt.date.today()
    monday = today - dt.timedelta(days=today.weekday())
    title = (rule.get("thread_title") or "*%s — {date}*" % group)
    title = title.replace("{date}", today.strftime("%A, %B %-d")).replace(
        "{week}", "week of %s" % monday.strftime("%b %-d")).replace("{month}", today.strftime("%B %Y"))
    r = call("chat.postMessage", {"channel": channel, "text": title, "unfurl_links": False, "_routed": True})
    if not r.get("ok"):
        return None
    cur = _current_periods()
    st = {k: v for k, v in st.items() if k.rsplit("|", 1)[-1] in cur}   # drop stale periods
    st[key] = r["ts"]
    _save_threads(st)
    return r["ts"]


def todays_parents(channel):
    """ts of every live thread parent this router created in `channel` (today / this week / this month).
    Dedupe checks need it: replies are not in conversations.history."""
    cur = _current_periods()
    return [v for k, v in _load_threads().items()
            if k.startswith(channel + "|") and k.rsplit("|", 1)[-1] in cur]

def reply_parent(call, channel, rule):
    """ts of the newest top-level message in `channel` containing rule['reply_to_marker'] within
    reply_within_hours (default 24). None -> caller posts top-level."""
    import time
    marker = rule.get("reply_to_marker") or ""
    cutoff = time.time() - float(rule.get("reply_within_hours", 24)) * 3600
    r = call("conversations.history", params={"channel": channel, "limit": 50})
    for m in r.get("messages", []):
        if float(m.get("ts", 0)) < cutoff:
            break
        if marker and marker in (m.get("text") or ""):
            return m["ts"]
    return None


def headline_split(text, rule):
    """(headline, full_body). Headline = the lines BEFORE the first table / code fence / bullet wall,
    capped at max_lines (default 5), plus one line pointing at the canvas. The first non-empty line
    (the report title) is always kept."""
    lines = text.strip().splitlines()
    n = int(rule.get("max_lines", 5))
    head = []
    for l in lines:
        st = l.strip()
        if not st:
            continue
        if head and (st.startswith("|") or st.startswith("```") or st.startswith("•") or st.startswith("- ")):
            break
        head.append(l.rstrip())
        if len(head) >= n:
            break
    url = rule.get("canvas_url") or ""
    if not url and rule.get("canvas"):
        try:
            import vp_canvas_section
            url = vp_canvas_section.url_for(rule["canvas"])
        except Exception:
            url = ""
    tail = "Full report → %s" % (("<%s|canvas>" % url) if url else "the canvas pinned in this channel")
    return "\n".join(head + [tail]), text


if __name__ == "__main__":
    # vp_route.py test <channel_id> <file-or-text> [task]   -> prints the decision, posts nothing
    a = sys.argv[1:]
    if a and a[0] == "test":
        txt = open(a[2], encoding="utf-8").read() if os.path.exists(a[2]) else a[2]
        act, ch, t, rule = apply(a[1], txt, a[3] if len(a) > 3 else "")
        print(act, ch, (rule or {}).get("id"))
    else:
        print(__doc__)
