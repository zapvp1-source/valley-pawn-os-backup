#!/usr/bin/env python3
"""zoom_call_path.py — resolve Zoom Phone calls that enter through an Auto Receptionist (IVR).

WHY (2026-11-09, Joshua): every store number now answers with a phone menu
("press 1 for hours, press 2 for the payment-app link, press 3 for a team member").
Zoom's GET /phone/call_history list shows only the FIRST hop of a call. Once a store number
lands on an Auto Receptionist, the list row says callee_ext_type=auto_receptionist and a
top-level result for the menu, not for the store queue. Every consumer that counts missed /
answered calls (missed_call_text.py, zoom_missed_alert.py, texting_scorecard.py) would then
see the wrong result. This module reads the call path (GET /phone/call_history/{id},
scope phone:read:call_log:admin) once per AR call and rewrites the row so it looks exactly like
the pre-IVR rows those scripts already understand:

  * reached a store queue  -> callee_ext_number/type = the queue, call_result = the queue outcome
                              (answered / no_answer / abandoned / voicemail ...)
  * pressed 1 (hours) and never reached the queue  -> call_result = "ivr_hours"
  * pressed 2 (app link) and never reached the queue -> call_result = "ivr_app_link"
  * hung up in the menu with no key                -> call_result = "abandoned"
  * path unreadable -> row left as-is, flagged _path_error (caller decides)
Added fields on every resolved row: ivr_key ("" if none), ivr_ar_ext, _resolved=True.
Non-AR rows pass through untouched, so behaviour is identical until a number sits on an AR.

Cache: resolved rows keyed by call-history id in ~/Library/Logs/valleypawn/zoom_call_path/cache.json
(local, non-synced; only finished calls are cached). stdlib only.

  zoom_call_path.py --probe            read-only: token + scope check on today's first call
  zoom_call_path.py --show <id>        read-only: print the resolved row for one call id
"""
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOCAL = os.path.expanduser("~/Library/Logs/valleypawn/zoom_call_path")
CACHE = os.path.join(LOCAL, "cache.json")
ANSWERED = {"answered", "connected", "succeeded", "accepted"}
VM_WORDS = ("voicemail", "voice_mail")


def _norm(s):
    return (s or "").strip().lower().replace(" ", "_").replace("-", "_")


def _load():
    try:
        with open(CACHE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save(c):
    os.makedirs(LOCAL, exist_ok=True)
    # keep 4 days
    cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=4)).isoformat()
    c = {k: v for k, v in c.items() if v.get("_cached", "") > cut}
    tmp = CACHE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(c, f)
    os.chmod(tmp, 0o600)
    os.replace(tmp, CACHE)


def _keys():
    """Menu key meanings live in fleet/ivr_config.json (changed 2026-11-12)."""
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fleet", "ivr_config.json")) as f:
            c = json.load(f)
        return {"hours_key": str(c.get("hours_key", "1")), "app_link_key": str(c.get("app_link_key", "2"))}
    except (OSError, ValueError):
        return {"hours_key": "1", "app_link_key": "2"}


def fetch_path(token, cid):
    req = urllib.request.Request("https://api.zoom.us/v2/phone/call_history/" + cid,
                                 headers={"Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def resolve_detail(row, detail):
    """Pure: list row + call-path detail -> resolved row (copy)."""
    out = dict(row)
    hops = detail.get("call_path") or []
    keys = [str(hp.get("press_key")) for hp in hops
            if hp.get("press_key") not in (None, "") and _norm(hp.get("callee_ext_type")) == "auto_receptionist"]
    key = keys[-1] if keys else ""
    ar_ext = row.get("callee_ext_number") or ""
    queue_hops = [hp for hp in hops if _norm(hp.get("callee_ext_type")) == "call_queue"]
    # who actually picked up: member legs decide when present (a queue hop can read "answered"
    # in Zoom's own example even though the answer came from a member leg)
    member = [hp for hp in hops if _norm(hp.get("callee_ext_type")) in ("user", "common_area", "shared_line_group")]
    if member:
        answered = any(_norm(hp.get("result")) == "answered" for hp in member)
    else:
        answered = any(_norm(hp.get("result")) == "answered" and _norm(hp.get("callee_ext_type")) == "call_queue" for hp in hops)
    vm = any(any(w in _norm(hp.get("result")) or w in _norm(hp.get("event")) or w in _norm(hp.get("callee_ext_type")) for w in VM_WORDS)
             for hp in hops)
    if queue_hops:
        q = queue_hops[-1]
        out["callee_ext_number"] = q.get("callee_ext_number") or out.get("callee_ext_number")
        out["callee_ext_type"] = "call_queue"
        out["callee_name"] = q.get("callee_name") or out.get("callee_name")
        out["callee_ext_id"] = q.get("callee_ext_id") or out.get("callee_ext_id")
        if answered:
            res = "answered"
        elif vm:
            res = "voicemail"
        else:
            qr = _norm(q.get("result"))
            top = _norm(row.get("call_result"))
            if qr and qr not in ANSWERED:
                res = qr
            elif top and top not in ANSWERED and top not in ("succeeded",):
                res = top
            else:
                res = "abandoned"
        out["call_result"] = res
    else:
        if answered:
            out["call_result"] = "answered"
        elif vm:
            out["call_result"] = "voicemail"
        elif key == _keys().get("hours_key", "1"):
            out["call_result"] = "ivr_hours"
        elif key == _keys().get("app_link_key", "2"):
            out["call_result"] = "ivr_app_link"
        elif key:
            out["call_result"] = "ivr_key_" + key
        else:
            out["call_result"] = "abandoned"
    out["ivr_key"] = key
    out["ivr_keys"] = keys
    out["ivr_ar_ext"] = ar_ext
    out["ivr_top_result"] = row.get("call_result")
    out["_resolved"] = True
    return out


def resolve_rows(rows, token=None, now=None, log=None, fetch=None):
    """Resolve every inbound auto_receptionist row. Returns (rows, errors).
    fetch(cid) -> detail dict may be passed by callers with their own Zoom client."""
    fetch = fetch or (lambda cid: fetch_path(token, cid))
    now = now or dt.datetime.now(dt.timezone.utc)
    cache = _load()
    out, errors, dirty = [], 0, False
    for r in rows:
        if _norm(r.get("direction")) != "inbound" or _norm(r.get("callee_ext_type")) != "auto_receptionist":
            out.append(r)
            continue
        cid = r.get("id") or ""
        if cid in cache:
            c = dict(cache[cid]); c.pop("_cached", None)
            out.append(c)
            continue
        try:
            d = fetch(cid)
            res = resolve_detail(r, d)
            end = r.get("end_time")
            done = end and dt.datetime.fromisoformat(end.replace("Z", "+00:00")) < now - dt.timedelta(minutes=3)
            if done:
                cache[cid] = dict(res, _cached=now.isoformat()); dirty = True
            out.append(res)
        except Exception as e:  # noqa: BLE001
            errors += 1
            if isinstance(e, urllib.error.HTTPError) and e.code in (400, 401):
                # a token minted before a scope was added lacks it until expiry: drop the shared
                # cached token so the next run mints a fresh one (self-heal, 2026-11-09)
                try:
                    os.remove(os.path.expanduser("~/Library/Logs/valleypawn/missed_call_text/.token.json"))
                except OSError:
                    pass
            rr = dict(r, _path_error=("HTTP %s" % e.code) if isinstance(e, urllib.error.HTTPError) else type(e).__name__)
            out.append(rr)
            if log:
                log("call path fetch failed for %s: %s" % (cid[-8:], rr["_path_error"]))
    if dirty:
        try:
            _save(cache)
        except OSError:
            pass
    return out, errors


def _main():
    import missed_call_text as mct
    now = dt.datetime.now(dt.timezone.utc)
    tok = mct.zoom_token(now)
    if not tok:
        print("no token"); return 1
    if len(sys.argv) > 1 and sys.argv[1] == "--answer":
        # read-only: answer rate per period, same definitions as Call Analysis/deck_2026-11/COMM_STATS.md section A
        # usage: --answer FROM:TO [FROM:TO ...]
        cfg = mct.load_json(mct.CONFIG, {})
        stores = cfg.get("stores", {})
        UN = ("no_answer", "abandoned", "voicemail", "missed", "overflowed", "ring_timeout", "busy", "timeout", "rejected")
        for span in sys.argv[2:]:
            f, t = span.split(":")
            rows = [r for r in mct.zoom_calls_raw(tok, f, t) if _norm(r.get("direction")) == "inbound"
                    and _norm(r.get("connect_type")) != "internal" and mct.store_for(r, stores)]
            res, _ = resolve_rows(rows, tok)
            tot = len(res); un = 0; self_served = 0; op = 0; opm = 0; per = {}
            for r in res:
                cr = _norm(r.get("call_result"))
                st = mct.store_for(r, stores)
                isopen = mct.during_hours(mct.parse_ts(r["start_time"]).astimezone(mct.ET), stores[st])
                p = per.setdefault(st, [0, 0, 0, 0])
                p[0] += 1
                if cr in ("ivr_hours", "ivr_app_link"):
                    self_served += 1
                    continue
                miss = cr in UN
                un += miss; p[1] += miss
                if isopen:
                    op += 1; opm += miss; p[2] += 1; p[3] += miss
            pc = lambda a, b: "%d/%d (%d%%)" % (a, b, round(100.0 * a / b)) if b else "-"
            print("%s..%s  inbound %d  unanswered %s  self-served by menu %d  missed while open %s" % (f, t, tot, pc(un, tot), self_served, pc(opm, op)))
            for st in sorted(per):
                p = per[st]
                print("    %s inbound %d  unanswered %s  missed while open %s" % (st, p[0], pc(p[1], p[0]), pc(p[3], p[2])))
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "--spam":
        # read-only: how many quick hang-ups look like spam/robocalls. Prints counts only (no names, last-4 only).
        # usage: --spam <menu_since> <baseline_from> <baseline_to> <history_from>
        msince, bfrom, bto, hfrom = sys.argv[2:6]
        cfg = mct.load_json(mct.CONFIG, {})
        stores = cfg.get("stores", {})
        today = now.astimezone(mct.ET).date().isoformat()
        dids = {mct.e164(x.get("did")) for x in stores.values()}
        hist = [r for r in mct.zoom_calls_raw(tok, hfrom, today) if _norm(r.get("direction")) == "inbound"]
        hist += [r for r in mct.zoom_calls_raw(tok, msince, today) if _norm(r.get("direction")) == "inbound"]
        seen_ids, H = set(), []
        for r in hist:
            if r.get("id") not in seen_ids:
                seen_ids.add(r.get("id")); H.append(r)
        out_rows = [r for r in mct.zoom_calls_raw(tok, hfrom, today) if _norm(r.get("direction")) == "outbound"]
        by_num, stores_by_num = {}, {}
        for r in H:
            n = mct.e164(r.get("caller_did_number"))
            if not n: continue
            by_num.setdefault(n, []).append(r)
            stores_by_num.setdefault(n, set()).add(mct.store_for(r, stores) or "?")
        called_back = {mct.e164(r.get("callee_did_number")) for r in out_rows if _norm(r.get("call_result")) in ANSWERED}
        SPAMWORDS = ("spam", "scam", "telemarket", "robo", "fraud", "potential", "unknown", "unavailable", "private", "toll free")
        def dur(r):
            a, b = mct.parse_ts(r.get("start_time")), mct.parse_ts(r.get("end_time"))
            return (b - a).total_seconds() if a and b else 0
        def classify(r):
            n = mct.e164(r.get("caller_did_number"))
            name = (r.get("caller_name") or "").lower()
            sig = []
            if r.get("spam") not in (None, "", False, "no", "not_spam", 0):
                sig.append("zoom-spam-flag:%s" % r.get("spam"))
            if any(w in name for w in SPAMWORDS):
                sig.append("spam-like caller ID")
            if not n or r.get("hide_caller_id"):
                sig.append("no caller number")
            d = r.get("caller_did_number") or ""
            if n and n[2:5] in ("800", "833", "844", "855", "866", "877", "888"):
                sig.append("toll-free")
            st = mct.store_for(r, stores)
            sd = mct.e164(stores.get(st, {}).get("did")) if st else None
            if n and sd and n[:8] == sd[:8]:
                sig.append("same prefix as store (neighbor spoof)")
            if n and len(stores_by_num.get(n, set()) - {"?"}) >= 3:
                sig.append("called %d stores" % len(stores_by_num[n] - {"?"}))
            calls = by_num.get(n, [])
            ok = [c for c in calls if _norm(c.get("call_result")) in ANSWERED and c.get("id") != r.get("id")]
            known = bool(ok) or (n in called_back)
            if known:
                verdict = "real customer (talked to a store before/after)"
            elif any(x.startswith("zoom-spam") or x.startswith("spam-like") or x.startswith("called") for x in sig):
                verdict = "likely spam"
            elif sig or dur(r) <= 3:
                verdict = "possible spam"
            else:
                verdict = "unknown caller (never reached a store)"
            return verdict, sig, len(calls)
        def report(label, rows):
            tally = {}
            print("%s: %d calls" % (label, len(rows)))
            for r in rows:
                v, sig, nc = classify(r)
                tally[v] = tally.get(v, 0) + 1
                print("   ...%s %s %-4s %3ds  calls-from-number:%d  %s | %s" % (
                    (r.get("caller_did_number") or "")[-4:], mct.parse_ts(r["start_time"]).astimezone(mct.ET).strftime("%m-%d %I:%M%p"),
                    mct.store_for(r, stores) or "?", dur(r), nc, v, ", ".join(sig) or "-"))
            print("   TOTALS: %s" % json.dumps(tally, sort_keys=True))
        # menu hang-ups during open hours (no key, never reached the queue)
        raw = [r for r in mct.zoom_calls_raw(tok, msince, today) if _norm(r.get("direction")) == "inbound" and _norm(r.get("callee_ext_type")) == "auto_receptionist"]
        mh = []
        for r in raw:
            try:
                d = resolve_detail(r, fetch_path(tok, r["id"]))
            except Exception:
                continue
            st = mct.store_for(r, stores)
            if st and mct.during_hours(mct.parse_ts(r["start_time"]).astimezone(mct.ET), stores[st]) and not d["ivr_keys"] \
                    and d.get("callee_ext_type") == "auto_receptionist" and d["call_result"] == "abandoned":
                mh.append(r)
        report("MENU hang-ups before pressing anything, open hours, since %s" % msince, mh)
        base = [r for r in mct.zoom_calls_raw(tok, bfrom, bto) if _norm(r.get("direction")) == "inbound" and mct.store_for(r, stores)
                and _norm(r.get("call_result")) in ("abandoned", "no_answer", "missed") and dur(r) <= 15
                and mct.during_hours(mct.parse_ts(r["start_time"]).astimezone(mct.ET), stores[mct.store_for(r, stores)])]
        report("BASELINE hang-ups within 15s, open hours, %s..%s (no menu)" % (bfrom, bto), base)
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "--hangups":
        # read-only friction check: menu calls that hung up before pressing anything vs the pre-menu baseline
        # usage: --hangups <menu_since> <baseline_from> <baseline_to>
        msince, bfrom, bto = sys.argv[2], sys.argv[3], sys.argv[4]
        cfg = mct.load_json(mct.CONFIG, {})
        stores = cfg.get("stores", {})
        today = now.astimezone(mct.ET).date().isoformat()
        def dur(r):
            a, b = mct.parse_ts(r.get("start_time")), mct.parse_ts(r.get("end_time"))
            return (b - a).total_seconds() if a and b else 0
        def inb(rows):
            return [r for r in rows if _norm(r.get("direction")) == "inbound" and _norm(r.get("connect_type")) != "internal"]
        # ---- baseline: straight to the store queue (no menu)
        base = [r for r in inb(mct.zoom_calls_raw(tok, bfrom, bto)) if mct.store_for(r, stores)]
        bopen = [r for r in base if mct.during_hours(mct.parse_ts(r["start_time"]).astimezone(mct.ET), stores[mct.store_for(r, stores)])]
        def quick_ab(rows, secs):
            return [r for r in rows if _norm(r.get("call_result")) in ("abandoned", "no_answer", "missed") and dur(r) <= secs]
        # ---- menu period
        raw = inb(mct.zoom_calls_raw(tok, msince, today))
        menu = [r for r in raw if _norm(r.get("callee_ext_type")) == "auto_receptionist"]
        res, errs = [], 0
        for r in menu:
            try:
                d = resolve_detail(r, fetch_path(tok, r["id"]))
            except Exception:
                errs += 1; continue
            st = mct.store_for(r, stores)
            t = mct.parse_ts(r["start_time"])
            d["_open"] = bool(st) and mct.during_hours(t.astimezone(mct.ET), stores[st])
            d["_st"] = st or "?"
            d["_dur"] = dur(r)
            d["_menu_hangup"] = (not d["ivr_keys"]) and d.get("callee_ext_type") == "auto_receptionist" and d["call_result"] == "abandoned"
            res.append(d)
        # did a menu hang-up get through later that day (any answered call from same number)?
        answered = {}
        for d in res:
            if d["call_result"] == "answered":
                answered.setdefault(mct.e164(d.get("caller_did_number")), []).append(mct.parse_ts(d["start_time"]))
        for r in raw:
            if _norm(r.get("callee_ext_type")) != "auto_receptionist" and _norm(r.get("call_result")) in ANSWERED:
                answered.setdefault(mct.e164(r.get("caller_did_number")), []).append(mct.parse_ts(r["start_time"]))
        def pct(a, b):
            return "%d of %d (%.1f%%)" % (a, b, 100.0 * a / b) if b else "0 of 0"
        hang = [d for d in res if d["_menu_hangup"]]
        hang_open = [d for d in hang if d["_open"]]
        menu_open = [d for d in res if d["_open"]]
        print("MENU PERIOD since %s: %d menu calls (%d during open hours), path errors %d" % (msince, len(res), len(menu_open), errs))
        print("hung up in the menu before pressing anything: %s overall; %s during open hours" % (pct(len(hang), len(res)), pct(len(hang_open), len(menu_open))))
        b = sorted(d["_dur"] for d in hang_open)
        if b:
            print("  open-hours menu hang-ups, seconds on the line: %s" % b)
        later = [d for d in hang_open if any(t > mct.parse_ts(d["start_time"]) and t.date() == mct.parse_ts(d["start_time"]).date() for t in answered.get(mct.e164(d.get("caller_did_number")), []))]
        print("  of open-hours menu hang-ups, reached the store later the same day: %d" % len(later))
        by = {}
        for d in hang_open:
            by[d["_st"]] = by.get(d["_st"], 0) + 1
        print("  open-hours menu hang-ups by store: %s" % json.dumps(by, sort_keys=True))
        reached = [d for d in menu_open if d["call_result"] in ANSWERED]
        print("open-hours menu calls answered by the store: %s" % pct(len(reached), len(menu_open)))
        print("BASELINE %s..%s (no menu): %d inbound to stores, %d during open hours" % (bfrom, bto, len(base), len(bopen)))
        for secs in (15, 20, 30):
            print("  hung up within %ds without being answered (open hours): %s" % (secs, pct(len(quick_ab(bopen, secs)), len(bopen))))
        print("  answered (open hours): %s" % pct(len([r for r in bopen if _norm(r.get("call_result")) in ANSWERED]), len(bopen)))
        return 0
    if len(sys.argv) > 2 and sys.argv[1] == "--dump":
        # read-only: one JSON line per inbound menu call since a date (store, ET time, keys, result, last4, duration)
        since = sys.argv[2]
        until = sys.argv[3] if len(sys.argv) > 3 else now.astimezone(mct.ET).date().isoformat()
        cfg = mct.load_json(mct.CONFIG, {})
        stores = cfg.get("stores", {})
        rows = mct.zoom_calls_raw(tok, since, until)
        n = errs = 0
        for r in rows:
            if _norm(r.get("direction")) != "inbound" or _norm(r.get("connect_type")) == "internal":
                continue
            st = mct.store_for(r, stores) or "?"
            t = mct.parse_ts(r.get("start_time"))
            out = {"id": r.get("id"), "store": st, "et": t.astimezone(mct.ET).strftime("%Y-%m-%d %H:%M:%S") if t else None,
                   "callee_type": r.get("callee_ext_type"), "raw_result": r.get("call_result"),
                   "caller4": (mct.e164(r.get("caller_did_number")) or "")[-4:],
                   "open": bool(st in stores and t and mct.during_hours(t.astimezone(mct.ET), stores[st]))}
            a, b = t, mct.parse_ts(r.get("end_time"))
            out["dur"] = (b - a).total_seconds() if a and b else None
            if _norm(r.get("callee_ext_type")) == "auto_receptionist":
                try:
                    d = resolve_detail(r, fetch_path(tok, r["id"]))
                    out["keys"] = d["ivr_keys"]; out["result"] = d["call_result"]
                except Exception as e:
                    errs += 1; out["err"] = str(e)[:80]
            print(json.dumps(out)); n += 1
        print("#DONE rows=%d path_errors=%d" % (n, errs))
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "--keys":
        # read-only: every key pressed on the store menus since a date (fresh call paths, no cache)
        since = sys.argv[2] if len(sys.argv) > 2 else now.astimezone(mct.ET).date().isoformat()
        cfg = mct.load_json(mct.CONFIG, {})
        rows = mct.zoom_calls_raw(tok, since, now.astimezone(mct.ET).date().isoformat())
        menu = [r for r in rows if _norm(r.get("direction")) == "inbound" and _norm(r.get("callee_ext_type")) == "auto_receptionist"]
        tally, ones, errs = {}, {}, 0
        for r in menu:
            try:
                d = resolve_detail(r, fetch_path(tok, r["id"]))
            except Exception:
                errs += 1; continue
            st = mct.store_for(r, cfg.get("stores", {})) or "?"
            ks = d["ivr_keys"]
            for k in set(ks):
                tally.setdefault(st, {}).setdefault(k, 0); tally[st][k] += 1
            if _keys()["hours_key"] in ks:
                then = "hung up" if d["call_result"] in ("ivr_hours",) else ("then reached store: " + d["call_result"])
                ones.setdefault(st, []).append("%s %s" % (mct.parse_ts(r["start_time"]).astimezone(mct.ET).strftime("%m-%d %I:%M %p"), then))
        print("menu calls since %s: %d (path errors %d)" % (since, len(menu), errs))
        print("calls per store that pressed each key: %s" % json.dumps(tally, sort_keys=True))
        for st, lst in sorted(ones.items()):
            print("PRESSED 1 %s: %d" % (st, len(lst)))
            for x in lst:
                print("   " + x)
        return 0
    if len(sys.argv) > 2 and sys.argv[1] == "--show":
        rows = mct.zoom_calls_raw(tok, (now - dt.timedelta(days=2)).date().isoformat(), now.date().isoformat())
        r = [x for x in rows if x.get("id") == sys.argv[2]]
        if not r:
            print("id not found"); return 1
        d = fetch_path(tok, sys.argv[2])
        print(json.dumps(d, indent=1)[:6000])
        print(json.dumps(resolve_detail(r[0], d), indent=1))
        return 0
    today = now.astimezone(mct.ET).date().isoformat()
    rows = mct.zoom_calls_raw(tok, today, today)
    print("list rows today: %d" % len(rows))
    types = {}
    for x in rows:
        k = "%s/%s/%s" % (x.get("direction"), x.get("callee_ext_type"), x.get("call_result"))
        types[k] = types.get(k, 0) + 1
    print("types: %s" % types)
    if not rows:
        return 0
    try:
        d = fetch_path(tok, rows[0]["id"])
        print("call path OK: %d hops; keys %s" % (len(d.get("call_path") or []), sorted((d.get("call_path") or [{}])[0].keys())))
    except urllib.error.HTTPError as e:
        print("call path FAILED: HTTP %s %s" % (e.code, e.read()[:300]))
        return 1
    ar = [x for x in rows if x.get("callee_ext_type") == "auto_receptionist"]
    for x in ar[:15]:
        rr, _ = resolve_rows([x], tok, now)
        r0 = rr[0]
        print("AR %s ...%s key=%r top=%s -> %s %s" % (x.get("start_time"), (x.get("caller_did_number") or "")[-4:],
              r0.get("ivr_key"), x.get("call_result"), r0.get("callee_ext_number"), r0.get("call_result")))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
