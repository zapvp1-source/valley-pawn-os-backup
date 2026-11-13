#!/usr/bin/env python3
"""ivr_app_link_text.py — "press 2" on the store phone menu texts the caller the MobilePawn app link.

WHY (Joshua, 2026-11-09): cut non-essential calls to the stores. The store numbers answer with a
Zoom Auto Receptionist: 1 = hours, 2 = "we're texting you the link to pay in the app",
3 = a team member. Zoom's IVR cannot send a text itself, so this agent (launchd, every 10 s (Joshua 2026-11-10: 'ultra fast', or they call back))
reads Zoom call history, resolves menu calls through the call path (bin/zoom_call_path.py),
and for every finished call whose key press was 2 POSTs the finished message to that store's
existing Chekkit webhook (same rule as missed-call-text: event == missed_call_text,
message ((text)), recipient caller_phone) — the text goes FROM the store number, so any reply
lands in the store's normal Chekkit thread.

  ivr_app_link_text.py            normal run
  ivr_app_link_text.py --render   show what would be sent (looks back --hours, default 8)
Rails: send window 07:00-22:00 ET; never older than max_age_minutes; one text per caller per
cooldown; never a store number; honours fleet/DRY_RUN.json; numbers hashed in local state,
logged as last-4 only. Failures -> one FAILURE_LEDGER row per day per kind, never Slack.
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import missed_call_text as mct  # noqa: E402

AGENT = "ivr-app-link-text"
CFG = os.path.join(mct.OS_DIR, "fleet", "ivr_config.json")
LOCAL = os.path.expanduser("~/Library/Logs/valleypawn/ivr_app_link_text")
STATE = os.path.join(LOCAL, "state.json")
LOG = os.path.join(LOCAL, "run.log")
HEARTBEAT = os.path.join(LOCAL, "heartbeat.json")


def log(msg, render=False):
    line = "%s %s" % (dt.datetime.now(mct.ET).strftime("%Y-%m-%d %H:%M:%S"), msg)
    if render:
        print(line); return
    os.makedirs(LOCAL, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def ledger_once(state, key, sentence, needs_human="no"):
    today = dt.date.today().isoformat()
    if state.setdefault("ledgered", {}).get(key) == today:
        return
    state["ledgered"][key] = today
    row = "| %s | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (
        dt.datetime.now(mct.ET).strftime("%Y-%m-%d %H:%M ET") + " (native)", AGENT, sentence, needs_human)
    try:
        with open(mct.LEDGER, "a") as f:
            f.write(row)
    except OSError:
        pass
    log("LEDGER: " + sentence)


def decide(calls, mcfg, icfg, state, now, lookback_min):
    stores = mcfg["stores"]
    dids = {mct.e164(s.get("did")) for s in stores.values()}
    oldest = now - dt.timedelta(minutes=lookback_min)
    cool = dt.timedelta(minutes=icfg.get("cooldown_minutes", 30))
    out, batch = [], set()
    for c in calls:
        if mct.norm(c.get("direction")) != "inbound" or str(c.get("ivr_key") or "") != str(icfg.get("app_link_key", "2")):
            continue
        code = mct.store_for(c, stores)
        cid = c.get("id") or c.get("call_id")
        end = mct.parse_ts(c.get("end_time")) or mct.parse_ts(c.get("start_time"))
        caller = mct.e164(c.get("caller_did_number"))
        if not (code and cid and end) or cid in state["processed"]:
            continue
        rec = lambda d, r: out.append((d, r, c, code, caller))  # noqa: E731
        if end < oldest:
            rec("SKIP", "older than lookback"); continue
        if not caller:
            rec("SKIP", "no textable caller number"); continue
        if caller in dids:
            rec("SKIP", "store number"); continue
        last = state["texted"].get(mct.h(caller))
        if (last and mct.parse_ts(last) > now - cool) or caller in batch:
            rec("SKIP", "already sent the link within cooldown"); continue
        if not stores[code].get("webhook"):
            rec("SKIP", "no Chekkit webhook for %s" % code); continue
        batch.add(caller)
        rec("SEND", "pressed app-link key")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--hours", type=float, default=8)
    a = ap.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    now_et = now.astimezone(mct.ET)
    mcfg = mct.load_json(mct.CONFIG, None)
    icfg = mct.load_json(CFG, None)
    if not (mcfg and icfg):
        print("config missing"); return 2
    state = mct.load_json(STATE, {"processed": {}, "texted": {}})
    w0, w1 = icfg.get("send_window", ["07:00", "22:00"])
    if not a.render and not (dt.time.fromisoformat(w0) <= now_et.time() < dt.time.fromisoformat(w1)):
        return 0
    lookback = a.hours * 60 if a.render else icfg.get("max_age_minutes", 30)
    try:
        tok = mct.zoom_token(now)
    except Exception as e:  # noqa: BLE001
        if a.render:
            print("token failed: %s" % e); return 1
        ledger_once(state, "token", "Could not get a Zoom API token; press-2 app-link texts paused.", "yes, check the Zoom app")
        mct.save_json(STATE, state); return 1
    if not tok:
        if a.render:
            print("no Zoom credentials"); return 1
        ledger_once(state, "creds", "Zoom credentials missing; press-2 app-link texts cannot run.", "no")
        mct.save_json(STATE, state); return 1
    day_from = (now_et - dt.timedelta(minutes=lookback)).date().isoformat()
    try:
        calls = mct.zoom_calls(tok, day_from, now_et.date().isoformat())
    except Exception as e:  # noqa: BLE001
        log("fetch error %s" % e, a.render); return 1
    if mct.LAST_PATH_ERRORS and not a.render:
        ledger_once(state, "callpath", "Zoom call-path lookups failed for %d menu calls; press-2 texts may be missed." % mct.LAST_PATH_ERRORS,
                    "yes, check the Zoom app has scope phone:read:call_log:admin")
    decisions = decide(calls, mcfg, icfg, state, now, lookback)
    dry = mct.publish_guard_armed(now)
    if a.render:
        menu = [c for c in calls if c.get("_resolved")]
        print("=== RENDER ONLY === now %s | calls %d | menu calls %d | path errors %d | guard %s"
              % (now_et.strftime("%a %m-%d %H:%M"), len(calls), len(menu), mct.LAST_PATH_ERRORS, "ARMED" if dry else "off"))
        keys = {}
        for c in menu:
            k = "%s:key=%s->%s" % (mct.store_for(c, mcfg["stores"]), c.get("ivr_key") or "-", c.get("call_result"))
            keys[k] = keys.get(k, 0) + 1
        print("menu outcomes: %s" % keys)
        for d, r, c, code, caller in decisions:
            print("%-4s %s %s %s %s" % (d, mct.parse_ts(c["start_time"]).astimezone(mct.ET).strftime("%m-%d %H:%M"),
                                        code, mct.last4(caller), r))
            if d == "SEND":
                print("     text: " + icfg["app_link_text"].format(store=mcfg["stores"][code]["name"]))
        return 0
    sent = 0
    for d, r, c, code, caller in decisions:
        cid = c.get("id") or c.get("call_id")
        if d == "SKIP":
            state["processed"][cid] = now.isoformat(); log("skip %s %s: %s" % (code, mct.last4(caller), r)); continue
        if dry:
            log("publish guard ARMED - would send link %s %s" % (code, mct.last4(caller))); continue
        s = mcfg["stores"][code]
        payload = {"event": "missed_call_text", "text": icfg["app_link_text"].format(store=s["name"]),
                   "store": s["name"], "caller_phone": caller, "call_result": "ivr_app_link",
                   "queue": "phone menu", "during_hours": mct.during_hours(now_et, s), "call_time": c.get("start_time")}
        try:
            ok = mct.post_event(s["webhook"], payload)
        except Exception as e:  # noqa: BLE001
            ok = False; log("POST failed %s %s: %s" % (code, mct.last4(caller), e))
        if ok:
            state["processed"][cid] = now.isoformat(); state["texted"][mct.h(caller)] = now.isoformat(); sent += 1
            lag = int((now - (mct.parse_ts(c.get("end_time")) or now)).total_seconds())
            log("SENT app link %s %s (%ds after hang-up)" % (code, mct.last4(caller), lag))
        else:
            state.setdefault("post_fail", {}); state["post_fail"][code] = state["post_fail"].get(code, 0) + 1
            if state["post_fail"][code] >= 3:
                ledger_once(state, "post" + code, "Chekkit webhook for %s rejected press-2 app-link texts 3 times." % code)
    cut = now - dt.timedelta(days=3)
    state["processed"] = {k: v for k, v in state["processed"].items() if mct.parse_ts(v) > cut}
    state["texted"] = {k: v for k, v in state["texted"].items() if mct.parse_ts(v) > cut}
    os.makedirs(LOCAL, exist_ok=True)
    mct.save_json(STATE, state)
    mct.save_json(HEARTBEAT, {"ts": now.isoformat(), "calls": len(calls), "sent": sent, "guard": dry}, 0o644)
    return 0


if __name__ == "__main__":
    sys.exit(main())
