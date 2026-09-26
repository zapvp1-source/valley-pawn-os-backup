#!/usr/bin/env python3
"""zoom_missed_alert.py — native replacement for the Cowork tasks `zoom-voicemail-alert`
(every 20 min, 09:00–19:59 Mon–Sat) and `zoom-voicemail-eod-review` (17:45 daily).

WHY (2026-09-25): the Cowork version drove the Zoom admin web UI — 33 Claude sessions a day, and it
died the moment the zoom.us browser session expired (9/25). The fleet already reads the SAME data
natively: missed_call_text.py polls Zoom Phone's call history over the Server-to-Server API every
60 s (creds ~/.vp_secrets/zoom_s2s.json, scope phone:read:list_call_logs:admin). This reuses its
client, its store/queue map and its resolution rules, and publishes what the SKILL published:

  alert  — ONE compact message to #voicemails-calls-missed (C0BP4M3B99R), one line per still-
           unresolved missed call / voicemail that has not been alerted before. Silent when none.
  eod    — at close: every missed call from today that STILL has no callback and no reconnect,
           one line each, to the same channel. Silent when the day is clean.

Rules carried over from the SKILL, not invented: 2-minute grace so an in-progress call is not
flagged; "resolved" = a later Connected outbound from the store to that number OR a later Answered
inbound from that number; dedupe by Zoom call id in fleet/zoom_alert_state.json; never alert on a
store or staff number; the format `📞 Store — (540) 555-1234, 9:34 AM — missed (no VM) / 🔴 VM left,
call back ASAP`. Publishes through vp_slack (receipt + publish guard). Ledger row on API failure.

  zoom_missed_alert.py alert [--render]
  zoom_missed_alert.py eod   [--render]
"""
import datetime as dt
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import missed_call_text as mct  # noqa: E402  (same-dir module; stdlib only)

AGENT_ALERT = "zoom-voicemail-alert"
AGENT_EOD = "zoom-voicemail-eod-review"
CHANNEL = "C0BP4M3B99R"          # #voicemails-calls-missed (SKILL NOTES 2026-08-13)
STATE = os.path.join(mct.OS_DIR, "fleet", "zoom_alert_state.json")
ET = mct.ET
ANSWERED = mct.ANSWERED


def fmt_num(n):
    d = "".join(ch for ch in (n or "") if ch.isdigit())
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    return "(%s) %s-%s" % (d[:3], d[3:6], d[6:]) if len(d) == 10 else (n or "unknown")


def fmt_time(t):
    return t.astimezone(ET).strftime("%-I:%M %p")


def candidates(calls, cfg, now):
    """Unresolved missed inbound calls to store queues today. Mirrors the SKILL's Step 2/3.5."""
    stores = cfg["stores"]
    missed = {mct.norm(x) for x in cfg["missed_results"]}
    exclude = {mct.e164(x) for x in cfg.get("exclude_numbers", []) + [s.get("did") for s in stores.values()]}
    exclude.discard(None)
    grace = dt.timedelta(seconds=cfg.get("grace_seconds", 120))
    answered_in, called_out = {}, {}
    for c in calls:
        t = mct.parse_ts(c.get("start_time"))
        if not t:
            continue
        if mct.norm(c.get("direction")) == "inbound" and mct.norm(c.get("call_result")) in ANSWERED:
            n = mct.e164(c.get("caller_did_number"))
            if n:
                answered_in.setdefault(n, []).append(t)
        if mct.norm(c.get("direction")) == "outbound" and mct.norm(c.get("call_result")) in ANSWERED:
            n = mct.e164(c.get("callee_did_number"))
            if n:
                called_out.setdefault(n, []).append(t)
    out = []
    for c in calls:
        if mct.norm(c.get("direction")) != "inbound":
            continue
        code = mct.store_for(c, stores)
        if not code:
            continue
        res = mct.norm(c.get("call_result"))
        if res in ANSWERED:
            continue
        cid = c.get("id") or c.get("call_id")
        start = mct.parse_ts(c.get("start_time"))
        end = mct.parse_ts(c.get("end_time")) or start
        if not (cid and start):
            continue
        vm = bool(c.get("has_voicemail")) or "voicemail" in res
        if res not in missed and not vm:
            continue
        if end > now - grace:
            continue
        if mct.norm(c.get("connect_type")) == "internal":
            continue
        caller = mct.e164(c.get("caller_did_number"))
        if not caller or caller in exclude:
            continue
        if any(t > start for t in answered_in.get(caller, [])):
            continue
        if any(t > start for t in called_out.get(caller, [])):
            continue
        out.append({"id": str(cid), "store": stores[code]["name"], "code": code, "caller": caller,
                    "start": start, "vm": vm, "result": res})
    out.sort(key=lambda r: r["start"])
    return out


def line(r):
    status = "🔴 VM left" if r["vm"] else "missed (no VM)"
    return "📞 %s — %s, %s — %s, call back ASAP" % (r["store"], fmt_num(r["caller"]), fmt_time(r["start"]), status)


def post(agent, text):
    env = dict(os.environ, VP_TASK=agent)
    p = subprocess.run(["/usr/bin/python3", os.path.join(mct.BIN, "vp_slack.py"), "post", CHANNEL, text],
                       capture_output=True, text=True, timeout=60, env=env)
    return p.returncode == 0, (p.stderr or p.stdout).strip()[:200]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "alert"
    render = "--render" in sys.argv
    agent = AGENT_EOD if mode == "eod" else AGENT_ALERT
    cfg = mct.load_json(mct.CONFIG, None)
    if not cfg:
        mct.log("no config at %s" % mct.CONFIG)
        return 1
    now = dt.datetime.now(dt.timezone.utc)
    today = now.astimezone(ET).date().isoformat()
    state = mct.load_json(STATE, {"alerted": {}})
    try:
        tok = mct.zoom_token(now)
        # Zoom's from/to are UTC dates; ask for yesterday+today and keep only calls that started
        # TODAY in Eastern time (the SKILL's "today"), so last night's 8:49 PM call is not re-raised.
        yday = (now.astimezone(ET).date() - dt.timedelta(days=1)).isoformat()
        calls = [c for c in mct.zoom_calls(tok, yday, today)
                 if (mct.parse_ts(c.get("start_time")) or now).astimezone(ET).date().isoformat() == today]
    except Exception as e:  # API/auth failure: one plain ledger row, nothing to Slack (Rule 16)
        mct.log("zoom api failed: %s" % e)
        if not render:
            mct.ledger_once(state, "api-" + today, "The Zoom missed-call check could not read today's call log (%s)."
                            % type(e).__name__, "no")
            mct.save_json(STATE, state)
        return 1
    cands = candidates(calls, cfg, now)
    if mode == "alert":
        new = [r for r in cands if r["id"] not in state["alerted"]]
    else:
        new = cands  # EOD: everything still unresolved, alerted before or not
    print("%s: %d calls today, %d unresolved, %d to publish" % (mode, len(calls), len(cands), len(new)))
    if render:
        print("=== RENDER ONLY ===")
        for r in new:
            print(line(r))
        return 0
    if not new:
        mct.log("%s: nothing to post" % mode)
        # a quiet run still leaves a receipt so the audit can tell "checked, clean" from "dark"
        subprocess.run(["/usr/bin/python3", os.path.join(mct.BIN, "vp_receipt.py"), "write", agent,
                        "--surface", "file", "--target", STATE], capture_output=True, timeout=15)
        return 0
    text = "\n".join(line(r) for r in new)
    if mode == "eod":
        text = "🕠 Still no callback today:\n" + text
    ok, err = post(agent, text)
    if ok:
        if mode == "alert":
            for r in new:
                state["alerted"][r["id"]] = r["start"].isoformat()
            # keep the state small: drop ids older than 3 days
            cutoff = (now - dt.timedelta(days=3)).isoformat()
            state["alerted"] = {k: v for k, v in state["alerted"].items() if v >= cutoff}
            mct.save_json(STATE, state)
        mct.log("%s: posted %d line(s)" % (mode, len(new)))
        return 0
    mct.log("%s: post failed: %s" % (mode, err))
    if "guard" not in err.lower() and "dry" not in err.lower():
        mct.ledger_once(state, "post-" + today, "The missed-call alert had %d call(s) to report but the Slack post did not go through." % len(new), "no")
        mct.save_json(STATE, state)
    return 1


if __name__ == "__main__":
    sys.exit(main())
