#!/usr/bin/env python3
"""fleet_scorecard.py — the ONE daily "finish line" DM to Joshua (native, stdlib, 2026-10-14).

For every report that was due on a day (default: yesterday), checks the REAL output — the Slack
post (bot-readable channels) or the publication receipt (for DMs the bot cannot read, written by
vp_slack.py on every send), or a file's mtime — and grades it:

    ON TIME   landed once, by its deadline (scheduled time + grace_hours)
    LATE      landed, but after the deadline
    TWICE     landed more than once in its window ("Corrected:" reposts are not counted)
    MISSED    nothing landed before the next run was due (or before now)
    UNCHECKED the check itself failed (counts against a green day — silence is not proof)

Coverage = fleet/expected_outputs.json, filtered by its "scorecard" block (exclusions with reasons;
an entry marked "scorecard": true supersedes older entries for the same task). Reuses the Field
Scorecard's manifest and verification model (Rule 12: output, never lastRunAt) and the overnight
fleet doctor (bin/log_triage.py via fleet/doctor/<date>.md) + FLEET_HEALTH.md for one background-job
line. It REPLACES the separate scorecard/late-report DMs (field_scorecard "didn't post on time" and
fleet-event, fleet_doctor 02:10, fleet_health_sentinel, jewelry_pull_watchdog): those scripts check
"owns_dms" in fleet/state/fleet_scorecard.json and log instead of DMing.

    fleet_scorecard.py                  scheduled run: score yesterday, DM once (idempotent per date)
    fleet_scorecard.py --render [DATE]  print the DM for DATE (YYYY-MM-DD, default yesterday); no send
    fleet_scorecard.py --today          print today's partial (only items whose deadline has passed)
    fleet_scorecard.py --detail         with --render/--today: also print every item's grade + evidence
    fleet_scorecard.py --send DATE      score DATE and DM it once (refuses if already sent for DATE)

State: fleet/state/fleet_scorecard.json   Log: ~/Library/Logs/valleypawn/fleet-scorecard.log
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
MANIFEST = os.path.join(OS_DIR, "fleet/expected_outputs.json")
RECEIPTS = os.path.join(OS_DIR, "fleet/receipts")
STATE = os.path.join(OS_DIR, "fleet/state/fleet_scorecard.json")
DOCTOR_DIR = os.path.join(OS_DIR, "fleet/doctor")
FLEET_HEALTH = os.path.join(OS_DIR, "FLEET_HEALTH.md")
LOG = os.path.join(HOME, "Library/Logs/valleypawn/fleet-scorecard.log")
EARLY_H = 2.0          # a post up to 2 h before the scheduled time still counts for that instance
WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DETAIL = "--detail" in sys.argv

sys.path.insert(0, BIN)

# Plain names for entries without a "label" (Rule 16: no task ids in anything Joshua reads).
LABELS = {
    "pawn-walk": "Pawn walk", "sold-review": "Sold review", "discount-review": "Discount review",
    "daily-items-to-price": "Items to price", "chekkit-unanswered-alert": "Missed-message summary (morning)",
    "chekkit-unanswered-eod-followup": "Missed-message follow-up (evening)",
    "daily-cloudcover-check": "Cloud cover music check", "daily-funds-verification": "Funds verification",
    "jewelry-onhand-nightly-pull": "Jewelry count", "vp-website-shop-nightly": "Website shop refresh",
    "daily-unopened-email-eval": "Unopened mail brief", "health-records-intake": "Health records",
    "zoom-voicemail-eod-review": "Voicemail end-of-day review", "vp-staff-video-prompt": "Staff video ask",
    "vp-website-trend-daily-refresh": "Website visitor-trend page", "vp-deal-of-week-monday-pick": "Deal of the Week pick",
    "weekly-timekeeping-analysis": "Timekeeping summary", "review-obtained-last-week": "Google reviews ranking",
    "vp-presence-audit-weekly": "Online presence audit", "weekly-returns-summary": "Returns summary",
    "weekly-analytics-summary": "Website analytics", "weekly-social-media-recap": "Social recap",
    "nics-weekly-mtd-ranking": "FFL transfers (month to date)", "layaway-yield-weekly": "Layaway yield",
    "weekly-online-store-audit": "eBay store audit", "vp-ai-search-health-check": "AI-search health check",
    "vp-ai-visibility-metrics": "AI visibility metrics", "monday-bravo-postcheck": "Past-due loan review",
    "vp-website-deals-weekly": "Website deals refresh", "bonus-pace-monday": "Bonus pace",
    "weekly-markdown-verification-review": "Markdown check", "weekly-loan-layaway-manager-dms": "Loan & layaway manager notes",
    "weekly-loan-review-canvas-refresh": "Loan review card", "weekly-layaway-review-canvas-refresh": "Layaway review card",
    "weekly-employee-perf-canvas-refresh": "Employee performance card",
    "weekly-aged-inventory-canvas-refresh": "Aged inventory card", "weekly-store-perf-canvas-refresh": "Store performance card",
    "monthly-analytics-report": "Monthly business update", "monthly-employee-sales-rankings": "Monthly employee rankings",
    "monthly-scrap-rankings": "Scrap rankings", "nics-monthly-ranking": "FFL transfers (monthly)",
    "vp-new-customer-report": "New customers report", "monthly-ebay-ratings-sweep": "eBay ratings sweep",
    "monthly-gun-audit-report": "Gun audit summary", "monthly-we-buy-gold-silver-email": "Gold & silver email",
    "monthly-eom-recap": "Month in review", "monthly-gift-card-store-credit": "Gift cards & store credit",
    "monthly-mobilepawn-participation": "MobilePawn participation", "monthly-publication-audit": "Monthly publication audit",
}


def log(msg):
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a") as f:
            f.write(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S ") + msg + "\n")
    except Exception:
        pass


def load_json(p, default):
    try:
        v = json.load(open(p))
        return v if isinstance(v, type(default)) else default
    except Exception:
        return default


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w"), indent=2)
    os.replace(tmp, STATE)


# ------------------------------------------------------------------ cadence
def _hm(tok):
    tok = tok.replace("et", "")
    return int(tok[:2]), int(tok[2:4])


def fires_on(cadence, day):
    """datetime of this cadence's instance on `day` (a date), or None."""
    if not cadence or cadence.startswith(("retired", "quarterly")):
        return None
    p = cadence.split("-")
    try:
        k = p[0]
        if k == "daily":
            h, m = _hm(p[1])
        elif k in ("weekdays", "monsat", "tuesun"):
            ok = {"weekdays": day.weekday() < 5, "monsat": day.weekday() < 6, "tuesun": day.weekday() != 0}[k]
            if not ok:
                return None
            h, m = _hm(p[1])
        elif k == "weekly":
            if p[1] not in WEEKDAYS or WEEKDAYS.index(p[1]) != day.weekday():
                return None
            h, m = _hm(p[2])
        elif k == "monthly":
            n = int(re.sub(r"\D", "", p[1]) or "1")
            if day.day != n:
                return None
            h, m = _hm(p[2])
        else:
            return None
        return dt.datetime.combine(day, dt.time(h, m))
    except Exception:
        return None


# ------------------------------------------------------------------ coverage
def scored_entries(man):
    sc = man.get("scorecard", {}) or {}
    excl = sc.get("exclude", {}) or {}
    entries = man.get("entries", [])
    superseding = {e.get("task") for e in entries if e.get("scorecard")}
    out = []
    for e in entries:
        t = e.get("task", "")
        if t in excl:
            continue
        if t in superseding and not e.get("scorecard"):
            continue
        o = e.get("output", "")
        ch = e.get("channel_id", "") or ""
        if o.startswith("slack-canvas"):
            continue
        if o.startswith(("slack:", "slack-dm:")):
            if not ch.startswith("C"):
                continue      # a DM channel: the bot cannot read it — DM reports are scored by receipt entries
        elif o == "file":
            if "{PREV" in e.get("path", ""):
                continue
        elif o != "receipt":
            continue
        out.append(e)
    return out


def label_of(e):
    return e.get("label") or LABELS.get(e["task"]) or e["task"].replace("-", " ").capitalize()


# ------------------------------------------------------------------ evidence
_hist_cache = {}


def channel_messages(ch, start, end):
    """Top-level messages in [start, end). No `oldest` param (vp_slack.has 2026-10-05: oldest-bounded
    reads came back empty at random) — page back from `latest` until older than start."""
    key = (ch, start, end)
    if key in _hist_cache:
        return _hist_cache[key]
    import vp_slack
    msgs, cursor = [], None
    for _ in range(15):
        p = {"channel": ch, "latest": str(end.timestamp()), "limit": 200}
        if cursor:
            p["cursor"] = cursor
        try:
            r = vp_slack.call("conversations.history", params=p)
        except SystemExit as ex:          # vp_slack exits when there is no token
            raise RuntimeError(str(ex))
        if not r.get("ok") and r.get("error") == "not_in_channel":
            try:
                vp_slack.call("conversations.join", {"channel": ch})
                r = vp_slack.call("conversations.history", params=p)
            except Exception:
                pass
        if not r.get("ok"):
            raise RuntimeError(r.get("error", "?"))
        batch = r.get("messages", [])
        msgs += batch
        if not batch or float(batch[-1]["ts"]) < start.timestamp():
            break
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not r.get("has_more") or not cursor:
            break
    msgs = [m for m in msgs if start.timestamp() <= float(m.get("ts", 0)) < end.timestamp()]
    _hist_cache[key] = msgs
    return msgs


def msg_text(m):
    t = m.get("text") or ""
    if m.get("blocks"):
        t += " " + json.dumps(m["blocks"], ensure_ascii=False)
    return t


def slack_hits(e, ws, we):
    msgs = channel_messages(e["channel_id"], ws, we)
    mk = e.get("marker") or ""
    ci = bool(e.get("marker_ci"))
    hits = []
    for m in msgs:
        if m.get("subtype") in ("thread_broadcast", "channel_join", "channel_leave"):
            continue
        t = msg_text(m)
        if (mk.lower() in t.lower()) if ci else (mk in t):
            first = (m.get("text") or "").strip()
            hits.append({"ts": dt.datetime.fromtimestamp(float(m["ts"])),
                         "corrected": first.lower().startswith("corrected"), "id": m["ts"]})
    hits.sort(key=lambda h: h["ts"])
    return hits


def receipt_hits(e, ws, we):
    rp = os.path.join(RECEIPTS, e["task"] + ".jsonl")
    if not os.path.isfile(rp):
        raise RuntimeError("no receipts file")
    hits = []
    for line in open(rp, errors="replace"):
        try:
            r = json.loads(line)
            if not r.get("ok", True):
                continue
            ts = dt.datetime.fromisoformat(r["ts"]).replace(tzinfo=None)
        except Exception:
            continue
        if ws <= ts < we:
            hits.append({"ts": ts, "corrected": False, "id": r.get("note", "")[:40]})
    hits.sort(key=lambda h: h["ts"])
    # receipts are per send (a report + its DM + its xlsx = several rows), so they prove "landed",
    # not "how many times": collapse rows within 15 minutes of each other into one delivery.
    out = []
    for h in hits:
        if out and (h["ts"] - out[-1]["ts"]).total_seconds() < 900:
            continue
        out.append(h)
    return out


def file_hits(e, inst, ws, we):
    p = e.get("path", "").replace("{YYYY-MM-DD}", inst.strftime("%Y-%m-%d")).replace("{YYYY-MM}", inst.strftime("%Y-%m"))
    ms = glob.glob(p) if "*" in p else ([p] if os.path.exists(p) else [])
    if not ms:
        if not os.access(os.path.dirname(p) or "/", os.R_OK):
            raise RuntimeError("cannot read the folder")
        return []
    hits = []
    for x in ms:
        t = dt.datetime.fromtimestamp(os.path.getmtime(x))
        if "{" in e.get("path", "") or ws <= t < we:
            hits.append({"ts": t, "corrected": False, "id": os.path.basename(x)})
    return sorted(hits, key=lambda h: h["ts"])[-1:]   # a file is rewritten in place: one delivery


# ------------------------------------------------------------------ scoring
def score_day(day, now, partial=False):
    man = load_json(MANIFEST, {})
    entries = scored_entries(man)
    groups = {}
    for e in entries:
        key = (e["task"], e.get("output"), e.get("channel_id", ""), e.get("marker", ""), e.get("path", ""))
        groups.setdefault(key, []).append(e)
    items = []
    for key, es in groups.items():
        # every instance of this report across the group, for the day before .. day after
        inst_all = []
        for e in es:
            for off in (-1, 0, 1, 2):
                i = fires_on(e.get("cadence", ""), day + dt.timedelta(days=off))
                if i:
                    inst_all.append((i, e))
        inst_all.sort(key=lambda x: x[0])
        for idx, (inst, e) in enumerate(inst_all):
            if inst.date() != day:
                continue
            prev_i = inst_all[idx - 1][0] if idx > 0 else inst - dt.timedelta(days=7)
            next_i = inst_all[idx + 1][0] if idx + 1 < len(inst_all) else inst + dt.timedelta(days=7)
            early = min(EARLY_H, (inst - prev_i).total_seconds() / 7200.0)
            ws = inst - dt.timedelta(hours=early)
            deadline = inst + dt.timedelta(hours=float(e.get("grace_hours", 4)))
            we = min(next_i - dt.timedelta(hours=min(EARLY_H, (next_i - inst).total_seconds() / 7200.0)), now)
            it = {"task": e["task"], "label": label_of(e), "inst": inst, "deadline": deadline,
                  "kind": e.get("output"), "channel": e.get("channel_id", "")}
            if now < deadline:
                if partial:
                    continue
                it.update(grade="PENDING", note="deadline %s not reached" % deadline.strftime("%m/%d %H:%M"))
                items.append(it)
                continue
            try:
                o = e.get("output", "")
                if o == "receipt":
                    hits = receipt_hits(e, ws, we)
                elif o == "file":
                    hits = file_hits(e, inst, ws, we)
                else:
                    hits = slack_hits(e, ws, we)
            except Exception as ex:
                it.update(grade="UNCHECKED", note=str(ex)[:120])
                items.append(it)
                continue
            real = [h for h in hits if not h["corrected"]]
            it["hits"] = [h["ts"].strftime("%m/%d %H:%M:%S") + (" (corrected)" if h["corrected"] else "") for h in hits]
            if not hits:
                it.update(grade="MISSED", note="nothing between %s and %s" % (ws.strftime("%m/%d %H:%M"), we.strftime("%m/%d %H:%M")))
            elif len(real) >= 2:
                it.update(grade="TWICE", note="%d posts" % len(real), first=hits[0]["ts"])
            elif hits[0]["ts"] > deadline:
                it.update(grade="LATE", note="first at %s, due by %s" % (hits[0]["ts"].strftime("%m/%d %H:%M"),
                                                                    deadline.strftime("%H:%M")), first=hits[0]["ts"])
            else:
                it.update(grade="ON TIME", note="", first=hits[0]["ts"])
            items.append(it)
    items.sort(key=lambda i: i["inst"])
    seen = {}
    for i in items:
        seen[i["label"]] = seen.get(i["label"], 0) + 1
    for i in items:
        if seen[i["label"]] > 1:
            i["label"] += " (%s)" % t12(i["inst"])
    return items


def t12(t):
    return t.strftime("%-I:%M %p")


def exception_line(it):
    g = it["grade"]
    if g == "MISSED":
        return "%s — didn't post" % it["label"]
    if g == "TWICE":
        late = " (and late)" if it.get("first") and it["first"] > it["deadline"] else ""
        return "%s — posted twice%s" % (it["label"], late)
    if g == "LATE":
        same = it["first"].date() == it["inst"].date()
        when = t12(it["first"]) if same else it["first"].strftime("%a ") + t12(it["first"])
        return "%s — posted late (%s, due by %s)" % (it["label"], when, t12(it["deadline"]))
    if g == "UNCHECKED":
        return "%s — couldn't check" % it["label"]
    return None


def background_line(day):
    """One plain line from the overnight check (fleet doctor -> log_triage) and FLEET_HEALTH.md."""
    parts = []
    rep = os.path.join(DOCTOR_DIR, (day + dt.timedelta(days=1)).isoformat() + ".md")
    try:
        s = open(rep, errors="replace").read()
        sf = re.search(r"still_failing=(\d+)", s)
        st = re.search(r"SUMMARY still_failing=\d+ resolved=\d+ stale=(\d+)", s)
        if sf and int(sf.group(1)):
            parts.append("%s logged errors this week" % sf.group(1))
        if st and int(st.group(1)):
            parts.append("%s went quiet" % st.group(1))
        if not re.search(r"RESULT: .* 0 failed", s):
            parts.append("the overnight self-test didn't come back clean")
    except Exception:
        pass
    try:
        top = open(FLEET_HEALTH, errors="replace").read().split("\n## ")[1]
        hdr = top.splitlines()[0]
        when = dt.datetime.strptime(hdr[:16], "%Y-%m-%d %H:%M")
        if "ISSUES" in hdr and dt.datetime.now() - when < dt.timedelta(hours=20):
            n = sum(1 for l in top.splitlines() if l.startswith("- "))
            if n:
                parts.append("%d ended their last run with an error" % n)
    except Exception:
        pass
    return ("Background jobs: " + "; ".join(parts) + ".") if parts else None


def streak_after(st, day, green):
    hist = st.setdefault("history", {})
    hist[day.isoformat()] = dict(hist.get(day.isoformat(), {}), green=green)
    n, d = 0, day
    while hist.get(d.isoformat(), {}).get("green"):
        n += 1
        d -= dt.timedelta(days=1)
    return n


def render(day, items, st, partial=False, record=False):
    scored = [i for i in items if i["grade"] != "PENDING"]
    ok = sum(1 for i in scored if i["grade"] == "ON TIME")
    tot = len(scored)
    green = tot > 0 and ok == tot
    head = "Fleet %s (%s %s): %d/%d on time%s" % (
        "today so far" if partial else "yesterday", day.strftime("%a"), day.strftime("%-m/%-d"), ok, tot,
        " ✓" if green else "")
    lines = [head]
    unchecked = [i for i in scored if i["grade"] == "UNCHECKED"]
    if len(unchecked) > 3:      # one shared cause (Slack read down, no token) — one line, not N
        lines += [exception_line(i) for i in scored if exception_line(i) and i["grade"] != "UNCHECKED"]
        lines.append("%d reports couldn't be checked (the checker couldn't read Slack)" % len(unchecked))
    else:
        lines += [exception_line(i) for i in scored if exception_line(i)]
    if not partial:
        bl = background_line(day)
        if bl:
            lines.append(bl)
        if record:
            n = streak_after(st, day, green)
        else:
            tmp = json.loads(json.dumps(st))
            n = streak_after(tmp, day, green)
        lines.append("Streak: %d green day%s (goal 7)" % (n, "" if n == 1 else "s"))
    return "\n".join(lines), green, ok, tot


def detail(items):
    out = []
    for i in items:
        out.append("  %-9s %-34s %s  %s %s %s" % (i["grade"], i["label"][:34], i["inst"].strftime("%a %H:%M"),
                   i.get("kind", ""), i.get("channel", ""), (i.get("note") or "") + ("  hits=" + ",".join(i.get("hits", [])) if i.get("hits") else "")))
    return "\n".join(out)


def send_dm(text):
    env = dict(os.environ, VP_TASK="fleet-scorecard")
    r = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "dm", text],
                       capture_output=True, text=True, timeout=60, env=env)
    return r.returncode == 0, (r.stdout.strip() or r.stderr.strip())


def main(a):
    now = dt.datetime.now()
    st = load_json(STATE, {})
    yday = now.date() - dt.timedelta(days=1)
    if "--today" in a:
        items = score_day(now.date(), now, partial=True)
        txt, *_ = render(now.date(), items, st, partial=True)
        print(txt)
        if DETAIL:
            print("\n" + detail(items))
        return 0
    if "--render" in a:
        i = a.index("--render")
        day = dt.date.fromisoformat(a[i + 1]) if len(a) > i + 1 and re.match(r"\d{4}-\d\d-\d\d", a[i + 1]) else yday
        items = score_day(day, now)
        txt, *_ = render(day, items, st)
        print(txt)
        if DETAIL:
            print("\n" + detail(items))
        return 0
    day = yday
    if "--send" in a:
        i = a.index("--send")
        day = dt.date.fromisoformat(a[i + 1])
    if st.get("sent", {}).get(day.isoformat()):
        log("already sent for %s at %s — nothing to do" % (day, st["sent"][day.isoformat()]))
        print("already sent for %s" % day)
        return 0
    items = score_day(day, now)
    if any(i["grade"] == "PENDING" for i in items):
        log("WARNING: %d item(s) for %s still inside their grace window at send time"
            % (sum(1 for i in items if i["grade"] == "PENDING"), day))
    txt, green, ok, tot = render(day, items, st, record=True)
    good, info = send_dm(txt)
    st.setdefault("history", {})[day.isoformat()].update(
        ontime=ok, total=tot, exceptions=[exception_line(i) for i in items if exception_line(i)],
        items=[{"label": i["label"], "grade": i["grade"], "inst": i["inst"].isoformat(), "note": i.get("note", "")} for i in items])
    if good:
        st.setdefault("sent", {})[day.isoformat()] = now.isoformat(timespec="seconds")
        st["owns_dms"] = True
        log("sent %s: %d/%d on time, green=%s (ts %s)" % (day, ok, tot, green, info))
    else:
        log("DM FAILED for %s: %s" % (day, info))
        try:
            with open(os.path.join(OS_DIR, "fleet/FAILURE_LEDGER.md"), "a") as f:
                f.write("| %s ET (native) | fleet-scorecard | The morning fleet scorecard for %s did not send (%s). | NEEDS_HUMAN: no | OPEN |\n"
                        % (now.strftime("%Y-%m-%d %H:%M"), day, info[:120]))
        except Exception:
            pass
    save_state(st)
    print(txt)
    return 0 if good else 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:
        import traceback
        log("CRASH: %s | %s" % (e, traceback.format_exc().replace("\n", " | ")))
        raise
