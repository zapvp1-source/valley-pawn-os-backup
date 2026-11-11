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
        elif key == "1":
            out["call_result"] = "ivr_hours"
        elif key == "2":
            out["call_result"] = "ivr_app_link"
        elif key:
            out["call_result"] = "ivr_key_" + key
        else:
            out["call_result"] = "abandoned"
    out["ivr_key"] = key
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
