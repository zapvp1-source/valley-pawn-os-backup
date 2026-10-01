#!/usr/bin/env python3
"""texting_scorecard.py — one daily read on customer phone/text friction and response, all 5 stores.

WHY (Joshua, 2026-09-30): "harden what we have built and measure the customer friction and response".
Joins the sources we already own, read-only, no browser, no Chekkit login:
  * Zoom Phone call history (same S2S app as missed_call_text.py): inbound calls, answered, missed,
    open vs closed hours, and missed calls that got NO text (and why).
  * missed-call texts actually sent (fleet/receipts/missed-call-text.jsonl).
  * replies to those texts (fleet/missed_call_text_results.csv, filled by the missed-call-text-report task
    from Chekkit — lags a day, so the report shows the latest complete day).
  * Chekkit "Unanswered Message Alert" emails in Apple Mail: customer texts nobody answered within 10 min,
    split open-hours (staff friction) vs closed (demand while closed).
  * the AI text responder's own event log (fleet/ai_responder/events-*.jsonl): would-reply / silent / skip
    reasons, opt-out requests.
  * agent heartbeats (is the AI responder alive).

  texting_scorecard.py                  today so far -> fleet/texting_scorecard/<date>.md (+ .json)
  texting_scorecard.py --date 2026-09-29
  texting_scorecard.py --send           also queue a short DM to Joshua via the outbox (once per date)
No customer numbers or names are written anywhere. stdlib only.
"""
import argparse, csv, datetime as dt, glob, importlib.util, json, os, sys

OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
FLEET = os.path.join(OS_DIR, "fleet")
OUT_DIR = os.path.join(FLEET, "texting_scorecard")
JOSHUA = "U03BB52MDSA"
STORES = ["CUL", "WAY", "HAR", "LEX", "ROA"]


def load_mod(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, file))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


mct = load_mod("mct", "missed_call_text.py")
air = load_mod("air", "chekkit_ai_responder.py")
ET = mct.ET


def pct(a, b):
    return "%d%%" % round(100.0 * a / b) if b else "—"


def zoom_section(day, cfg, notes):
    """Per store: inbound, answered, missed (open/closed), texted-eligible. Returns dict."""
    out = {s: {"inbound": 0, "answered": 0, "missed_open": 0, "missed_closed": 0, "other": 0} for s in STORES}
    try:
        tok = mct.zoom_token(dt.datetime.now(dt.timezone.utc))
        if not tok:
            notes.append("Zoom call data unavailable (no credentials)"); return None
        calls = mct.zoom_calls(tok, day.isoformat(), day.isoformat())
    except Exception as e:
        notes.append("Zoom call data unavailable (%s)" % type(e).__name__); return None
    missed = {mct.norm(x) for x in cfg["missed_results"]}
    seen = set()
    for c in calls:
        if mct.norm(c.get("direction")) != "inbound" or mct.norm(c.get("connect_type")) == "internal":
            continue
        code = mct.store_for(c, cfg["stores"])
        cid = c.get("id") or c.get("call_id")
        if not code or cid in seen:
            continue
        seen.add(cid)
        t = mct.parse_ts(c.get("start_time"))
        if not t or t.astimezone(ET).date() != day:
            continue
        r = mct.norm(c.get("call_result")); o = out[code]
        o["inbound"] += 1
        if r in mct.ANSWERED:
            o["answered"] += 1
        elif r in missed:
            o["missed_open" if mct.during_hours(t.astimezone(ET), cfg["stores"][code]) else "missed_closed"] += 1
        else:
            o["other"] += 1
    return out


def receipts(day):
    n = {s: 0 for s in STORES}
    try:
        for line in open(os.path.join(FLEET, "receipts", "missed-call-text.jsonl")):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("ok") and str(r.get("ts", "")).startswith(day.isoformat()):
                code = str(r.get("target", "")).split(":")[-1]
                if code in n:
                    n[code] += 1
    except OSError:
        pass
    return n


def replies():
    """Latest complete day in the results CSV (filled by the report task from Chekkit)."""
    try:
        rows = list(csv.DictReader(open(os.path.join(FLEET, "missed_call_text_results.csv"))))
    except OSError:
        return None, {}
    if not rows:
        return None, {}
    last = max(r["date"] for r in rows)
    agg = {}
    for r in rows:
        if r["date"] != last:
            continue
        a = agg.setdefault(r["store"], {"texts": 0, "replied": 0, "optout": 0, "no_convo": 0, "store_min": []})
        a["texts"] += 1
        a["replied"] += r.get("replied") == "yes"
        a["optout"] += r.get("opt_out") == "yes"
        a["no_convo"] += "no chekkit conversation" in (r.get("outcome") or "").lower()
        if (r.get("store_reply_min") or "").strip().isdigit():
            a["store_min"].append(int(r["store_reply_min"]))
    return last, agg


def unanswered(day, mcfg):
    out = {s: {"open": 0, "closed": 0, "enders": 0} for s in STORES}
    start = dt.datetime.combine(day, dt.time(0), ET)
    minutes = int((dt.datetime.now(ET) - start).total_seconds() // 60) + 5
    try:
        alerts = air.read_alerts(max(minutes, 60))
    except Exception:
        return None
    for a in alerts:
        rec = dt.datetime.fromisoformat(a["received"])
        if rec.date() != day:
            continue
        msg_t = rec - dt.timedelta(minutes=10)
        o = out[a["store"]]
        if air.is_ender(a["text"]):
            o["enders"] += 1
        elif mct.during_hours(msg_t, mcfg["stores"][a["store"]]):
            o["open"] += 1
        else:
            o["closed"] += 1
    return out


def ai_events(day):
    ev = []
    try:
        for line in open(os.path.join(FLEET, "ai_responder", "events-%s.jsonl" % day.isoformat())):
            try:
                ev.append(json.loads(line))
            except ValueError:
                pass
    except OSError:
        pass
    agg = {"reply": 0, "silent": 0, "skip": 0, "optout": 0, "reasons": {}}
    for e in ev:
        agg[e["action"]] = agg.get(e["action"], 0) + 1
        if "opt-out" in (e.get("reason") or ""):
            agg["optout"] += 1
        if e["action"] != "reply":
            k = (e.get("reason") or "")[:40]
            agg["reasons"][k] = agg["reasons"].get(k, 0) + 1
    return agg


def heartbeat_age(path):
    d = mct.load_json(os.path.expanduser(path), {})
    try:
        return (dt.datetime.now(ET) - dt.datetime.fromisoformat(d["ts"])).total_seconds() / 60
    except Exception:
        return None


def build(day):
    mcfg = mct.load_json(mct.CONFIG, None)
    notes = []
    z = zoom_section(day, mcfg, notes)
    tx = receipts(day)
    rday, rep = replies()
    ua = unanswered(day, mcfg)
    ai = ai_events(day)
    hb = heartbeat_age("~/Library/Logs/valleypawn/chekkit_ai_responder/heartbeat.json")
    closed_today = [s for s in STORES if day.weekday() not in mcfg["stores"][s]["days"]]

    L = ["# Texting & phone scorecard — %s" % day.strftime("%a %b %-d, %Y"), ""]
    if closed_today:
        L.append("Closed today: %s." % ", ".join(closed_today))
    L += ["", "## Calls → texts", "| Store | Inbound calls | Answered | Missed (open hrs) | Missed (closed) | Texts sent |", "|---|---|---|---|---|---|"]
    tot = {"inbound": 0, "answered": 0, "mo": 0, "mc": 0, "tx": 0}
    for s in STORES:
        zz = (z or {}).get(s, {})
        L.append("| %s | %s | %s | %s | %s | %d |" % (s, zz.get("inbound", "?"), "%s (%s)" % (zz.get("answered", "?"), pct(zz.get("answered", 0), zz.get("inbound", 0))) if z else "?",
                                                    zz.get("missed_open", "?"), zz.get("missed_closed", "?"), tx[s]))
        if z:
            tot["inbound"] += zz["inbound"]; tot["answered"] += zz["answered"]; tot["mo"] += zz["missed_open"]; tot["mc"] += zz["missed_closed"]
        tot["tx"] += tx[s]
    if z:
        L.append("| **All** | **%d** | **%d (%s)** | **%d** | **%d** | **%d** |" % (tot["inbound"], tot["answered"], pct(tot["answered"], tot["inbound"]), tot["mo"], tot["mc"], tot["tx"]))
        gap = tot["mo"] + tot["mc"] - tot["tx"]
        L.append("")
        L.append("Missed calls with no text: %d (caller got through later, store called back, repeat caller, blocked/no number, or outside 8am–9pm)." % max(gap, 0))
    L += ["", "## Customer replies to missed-call texts (latest complete day: %s)" % (rday or "none yet"),
          "| Store | Texts | Replied | Opted out | No Chekkit thread | Median staff reply (min) |", "|---|---|---|---|---|---|"]
    for s in STORES:
        a = rep.get(s)
        if not a:
            L.append("| %s | 0 | — | — | — | — |" % s); continue
        m = sorted(a["store_min"]); med = m[len(m) // 2] if m else "—"
        L.append("| %s | %d | %d (%s) | %d | %d | %s |" % (s, a["texts"], a["replied"], pct(a["replied"], a["texts"]), a["optout"], a["no_convo"], med))
    L += ["", "## Customer texts nobody answered in 10 min (Chekkit alerts)", "| Store | During open hours | While closed | Sign-offs (ignored) |", "|---|---|---|---|"]
    for s in STORES:
        u = (ua or {}).get(s, {})
        L.append("| %s | %s | %s | %s |" % (s, u.get("open", "?"), u.get("closed", "?"), u.get("enders", "?")))
    L += ["", "## AI text responder (%s)" % ("alive, last run %d min ago" % hb if hb is not None and hb < 10 else "NOT RUNNING" if hb is not None else "no heartbeat yet"),
          "Would reply: %d · Stayed silent: %d · Skipped: %d · Opt-out requests (staff must unsubscribe): %d" % (ai["reply"], ai["silent"], ai["skip"], ai["optout"])]
    for k, v in sorted(ai["reasons"].items(), key=lambda x: -x[1])[:6]:
        L.append("- %s: %d" % (k, v))
    if notes:
        L += ["", "Notes: " + "; ".join(notes)]
    data = {"date": day.isoformat(), "zoom": z, "texts_sent": tx, "reply_day": rday, "replies": {k: {kk: vv for kk, vv in v.items() if kk != "store_min"} for k, v in rep.items()},
            "unanswered": ua, "ai": ai, "ai_heartbeat_min": hb, "notes": notes}
    return "\n".join(L) + "\n", data, tot if z else None, ua, ai, rday, rep


def dm_text(day, tot, ua, ai, rday, rep, hb_ok):
    lines = ["*Texting scorecard — %s*" % day.strftime("%a %-m/%-d")]
    if tot:
        lines.append("Calls: %d in, %d answered (%s). Missed %d open hours + %d closed. %d got a text." % (
            tot["inbound"], tot["answered"], pct(tot["answered"], tot["inbound"]), tot["mo"], tot["mc"], tot["tx"]))
    if ua:
        o = sum(v["open"] for v in ua.values()); c = sum(v["closed"] for v in ua.values())
        worst = max(ua.items(), key=lambda x: x[1]["open"])
        lines.append("Texts left 10+ min: %d while open%s, %d while closed." % (o, " (most: %s %d)" % (worst[0], worst[1]["open"]) if o else "", c))
    if rep:
        t = sum(v["texts"] for v in rep.values()); r = sum(v["replied"] for v in rep.values())
        lines.append("Replies to missed-call texts (%s): %d of %d (%s)." % (rday, r, t, pct(r, t)))
    lines.append("AI drafts: %d would reply, %d silent%s.%s" % (ai["reply"], ai["silent"], ", %d opt-out requests to unsubscribe" % ai["optout"] if ai["optout"] else "", "" if hb_ok else " AI responder not running."))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--date"); ap.add_argument("--send", action="store_true")
    a = ap.parse_args()
    day = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(ET).date()
    md, data, tot, ua, ai, rday, rep = build(day)
    os.makedirs(OUT_DIR, exist_ok=True)
    open(os.path.join(OUT_DIR, "%s.md" % day), "w").write(md)
    json.dump(data, open(os.path.join(OUT_DIR, "%s.json" % day), "w"), indent=1, default=str)
    print(md)
    if a.send:
        flag = os.path.join(OUT_DIR, ".sent-%s" % day)
        if os.path.exists(flag):
            print("already sent for", day); return 0
        hb = data["ai_heartbeat_min"]
        stamp = dt.datetime.now(ET).strftime("%Y%m%d-%H%M%S")
        txt = os.path.join(FLEET, "outbox", "texting-scorecard-%s.txt" % stamp)
        os.makedirs(os.path.dirname(txt), exist_ok=True)
        open(txt, "w").write(dm_text(day, tot, ua, ai, rday, rep, hb is not None and hb < 10))
        json.dump({"channel": JOSHUA, "file": txt}, open(txt[:-4] + ".json", "w"))
        open(flag, "w").write(stamp)
        print("queued DM to Joshua")
    return 0


if __name__ == "__main__":
    sys.exit(main())
