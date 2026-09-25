#!/usr/bin/env python3
"""missed_call_text.py — turn a missed store call into a text from that store's own number.

WHY (Joshua, 2026-09-23/24): 415 of 1,178 inbound calls went unanswered 1-23 Sep 2026 (35%).
A text back turns a dead call into a queued Chekkit conversation the store already works in.

HOW: poll Zoom Phone "Get account's call history" (GET /v2/phone/call_history, Server-to-Server
OAuth, scope phone:read:list_call_logs:admin) every 60 s from launchd. For each NEW inbound
external call to a store queue whose result is on the explicit "missed" allow-list — after a
2-minute grace, and only if the caller has not since been answered or called back — POST one
event to that store's Chekkit "Zoom Missed Call" webhook. Chekkit's own automation sends the
text FROM THE STORE NUMBER, so the customer's reply lands in the store's existing thread.
The event carries the finished message in "text" (built from config "messages" with the store
name and hours); each store's Chekkit automation is one rule — event == missed_call_text,
message ((text)), recipient caller_phone — so copy changes never need a Chekkit edit.

Deliberately NOT used: Zoom's phone.callee_missed webhook (inbound caller events fire
unreliably; queue-level abandons may never fire) and browser-reading the admin Calls log
(10-15 minute lag). The legacy /phone/call_logs API was retired by Zoom — do not switch to it.

  missed_call_text.py                      normal run (launchd, every 60 s)
  missed_call_text.py --render             do everything except POST and state writes; print
                                           what WOULD be sent and every call result value seen
  missed_call_text.py --render --hours 8   look further back (render only) to validate results
  missed_call_text.py --render --fixture calls.json --now 2026-09-24T15:00:00-04:00
                                           offline test against saved call-history rows

Safety rails:
  * texts ONLY on results in config "missed_results"; any other value is logged, never texted
  * send window 08:00-21:00 ET; never texts a call older than max_age_minutes (20)
  * never texts a store number or a listed staff number; one text per caller per cooldown (6 h)
  * skips the call if the same caller was answered afterwards or a store called them back
  * honours the fleet publish guard (fleet/DRY_RUN.json) — armed = send nothing
  * customer numbers are kept only as SHA-256 hashes in local (non-synced) state and logged
    only as last-4; nothing customer-identifying is written into the Drive-synced Projects tree
Credentials: the fleet's existing Zoom Server-to-Server app "Valley Pawn Ops Agent", read from
~/.vp_secrets/zoom_s2s.json — the same file the Zoom Call Pipeline uses (outside every synced
folder). Needs the read-only scope phone:read:list_call_logs:admin on that app.
stdlib only; /usr/bin/python3 (3.9+, zoneinfo).
"""
import argparse
import base64
import datetime as dt
import getpass
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

AGENT = "missed-call-text"
OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
CONFIG = os.path.join(OS_DIR, "fleet", "missed_call_text_config.json")
DRY_FLAG = os.path.join(OS_DIR, "fleet", "DRY_RUN.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
LOCAL = os.environ.get("VP_LOCAL_DIR") or os.path.expanduser("~/Library/Logs/valleypawn/missed_call_text")
STATE = os.path.join(LOCAL, "state.json")
TOKEN_CACHE = os.path.join(LOCAL, ".token.json")
HEARTBEAT = os.path.join(LOCAL, "heartbeat.json")
LOG = os.path.join(LOCAL, "run.log")
ET = ZoneInfo("America/New_York")
SECRETS_FILE = os.path.expanduser("~/.vp_secrets/zoom_s2s.json")
KC = {"account_id": "vp-zoom-s2s-account-id",
      "client_id": "vp-zoom-s2s-client-id",
      "client_secret": "vp-zoom-s2s-client-secret"}
ANSWERED = {"answered", "connected", "succeeded", "accepted"}


# ---------------------------------------------------------------- small helpers
def norm(s):
    return (s or "").strip().lower().replace(" ", "_").replace("-", "_")


def e164(num):
    """+1XXXXXXXXXX or None. Only US 10-digit numbers are textable here."""
    d = "".join(c for c in (num or "") if c.isdigit())
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return "+1" + d if len(d) == 10 else None


def last4(num):
    return "..." + (num or "")[-4:]


def h(num):
    return hashlib.sha256((num or "").encode()).hexdigest()[:24]


def parse_ts(s):
    if not s:
        return None
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def log(msg, render=False):
    line = "%s %s" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), msg)
    if render:
        print(line)
        return
    os.makedirs(LOCAL, exist_ok=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path, obj, mode=0o600):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def publish_guard_armed(now):
    d = load_json(DRY_FLAG, {})
    if not d.get("active"):
        return False
    try:
        return parse_ts(d["until"]) > now
    except Exception:
        return False


def ledger_once(state, key, sentence, needs_human="no"):
    """Failure Policy v3: one FAILURE_LEDGER row, at most once per day per key. No DM."""
    today = dt.date.today().isoformat()
    if state.setdefault("ledgered", {}).get(key) == today:
        return
    state["ledgered"][key] = today
    row = "| %s | %s | %s | NEEDS_HUMAN: %s | OPEN |\n" % (
        dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET") + " (native)", AGENT, sentence, needs_human)
    try:
        with open(LEDGER, "a") as f:
            f.write(row)
    except OSError:
        pass
    log("LEDGER: " + sentence)


# ---------------------------------------------------------------- Zoom
def keychain(svc):
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", svc, "-a", getpass.getuser(), "-w"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


def zoom_creds():
    """The fleet's existing Zoom S2S app ("Valley Pawn Ops Agent") — the same credential file the
    Zoom Call Pipeline already uses, outside every synced folder. Keychain is a fallback only."""
    f = load_json(SECRETS_FILE, {})
    creds = {k: f.get(k) for k in ("account_id", "client_id", "client_secret")}
    if all(creds.values()):
        return creds
    creds = {k: keychain(v) for k, v in KC.items()}
    return creds if all(creds.values()) else None


def zoom_token(now):
    cached = load_json(TOKEN_CACHE, {})
    if cached.get("token") and cached.get("exp", 0) > now.timestamp() + 120:
        return cached["token"]
    creds = zoom_creds()
    if not creds:
        return None
    basic = base64.b64encode(("%s:%s" % (creds["client_id"], creds["client_secret"])).encode()).decode()
    url = "https://zoom.us/oauth/token?" + urllib.parse.urlencode(
        {"grant_type": "account_credentials", "account_id": creds["account_id"]})
    req = urllib.request.Request(url, data=b"", method="POST", headers={"Authorization": "Basic " + basic})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    save_json(TOKEN_CACHE, {"token": d["access_token"], "exp": now.timestamp() + int(d.get("expires_in", 3600))})
    return d["access_token"]


def zoom_calls(token, day_from, day_to):
    rows, npt = [], ""
    for _ in range(20):  # hard page cap
        q = {"from": day_from, "to": day_to, "page_size": 300}
        if npt:
            q["next_page_token"] = npt
        req = urllib.request.Request("https://api.zoom.us/v2/phone/call_history?" + urllib.parse.urlencode(q),
                                     headers={"Authorization": "Bearer " + token})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        rows.extend(d.get("call_logs") or [])
        npt = d.get("next_page_token") or ""
        if not npt:
            break
    return rows


# ---------------------------------------------------------------- logic
def store_for(call, stores):
    ext = str(call.get("callee_ext_number") or "")
    did = e164(call.get("callee_did_number"))
    name = norm(call.get("callee_name"))
    for code, s in stores.items():
        if ext and ext == str(s.get("queue_ext", "")):
            return code
        if did and did == s.get("did"):
            return code
        if name and name == norm(s.get("name", "") + " Store Queue"):
            return code
    return None


def during_hours(ts_et, s):
    if ts_et.weekday() not in s.get("days", []):
        return False
    o = dt.time.fromisoformat(s.get("open", "10:00"))
    c = dt.time.fromisoformat(s.get("close", "18:00"))
    return o <= ts_et.time() < c


def in_window(now_et, cfg):
    a, b = cfg.get("send_window", ["08:00", "21:00"])
    return dt.time.fromisoformat(a) <= now_et.time() < dt.time.fromisoformat(b)


def decide(calls, cfg, state, now, lookback_min, render):
    """Return list of (decision, reason, call, store_code, caller, during) — pure, testable."""
    stores = cfg["stores"]
    missed = {norm(x) for x in cfg["missed_results"]}
    exclude = {e164(x) for x in cfg.get("exclude_numbers", []) + [s.get("did") for s in stores.values()]}
    exclude.discard(None)
    grace = dt.timedelta(seconds=cfg.get("grace_seconds", 120))
    oldest = now - dt.timedelta(minutes=lookback_min)
    cooldown = dt.timedelta(hours=cfg.get("cooldown_hours", 6))
    processed = state.get("processed", {})
    texted = state.get("texted", {})
    out, unknown = [], {}

    # index later activity per caller number for reconnect / call-back suppression
    answered_in, called_out = {}, {}
    for c in calls:
        t = parse_ts(c.get("start_time"))
        if not t:
            continue
        if norm(c.get("direction")) == "inbound" and norm(c.get("call_result")) in ANSWERED:
            n = e164(c.get("caller_did_number"))
            if n:
                answered_in.setdefault(n, []).append(t)
        if norm(c.get("direction")) == "outbound":
            n = e164(c.get("callee_did_number"))
            if n:
                called_out.setdefault(n, []).append(t)

    for c in calls:
        if norm(c.get("direction")) != "inbound":
            continue
        code = store_for(c, stores)
        if not code:
            continue
        res = norm(c.get("call_result"))
        if res in ANSWERED:
            continue
        cid = c.get("id") or c.get("call_id")
        start = parse_ts(c.get("start_time"))
        end = parse_ts(c.get("end_time")) or start
        if not (cid and start):
            continue
        if res not in missed:
            unknown[res or "(blank)"] = unknown.get(res or "(blank)", 0) + 1
            continue
        caller = e164(c.get("caller_did_number"))
        s = stores[code]
        dur = during_hours(start.astimezone(ET), s)

        def rec(decision, reason):
            out.append((decision, reason, c, code, caller, dur))

        if cid in processed:
            continue
        if end < oldest:
            rec("SKIP", "older than lookback")
            continue
        if end > now - grace:
            rec("WAIT", "inside %ds grace" % grace.seconds)
            continue
        if norm(c.get("connect_type")) == "internal":
            rec("SKIP", "internal call")
            continue
        if not caller:
            rec("SKIP", "no textable caller number")
            continue
        if caller in exclude:
            rec("SKIP", "store or staff number")
            continue
        if any(t > start for t in answered_in.get(caller, [])):
            rec("SKIP", "caller got through on a later call")
            continue
        if any(t > start for t in called_out.get(caller, [])):
            rec("SKIP", "store already called them back")
            continue
        last = texted.get(h(caller))
        if last and parse_ts(last) > now - cooldown:
            rec("SKIP", "already texted within cooldown")
            continue
        if not s.get("webhook"):
            rec("SKIP", "no Chekkit webhook configured for %s" % code)
            continue
        rec("SEND", "missed (%s)" % res)
    return out, unknown


def render_text(cfg, s, open_now):
    """The finished customer text. Copy lives in config 'messages' so wording changes are a
    config edit, never a Chekkit wizard edit (Chekkit just sends ((text)) verbatim)."""
    tpl = cfg["messages"]["open" if open_now else "closed"]
    return tpl.format(store=s["name"], hours=s.get("hours_text", ""))


def post_event(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return 200 <= r.status < 300


def receipt(store_code):
    try:
        subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_receipt.py"), "write", AGENT,
                        "--surface", "file", "--target", "chekkit-webhook:%s" % store_code],
                       capture_output=True, timeout=15)
    except Exception:
        pass


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--hours", type=float, default=0)
    ap.add_argument("--fixture")
    ap.add_argument("--now")
    a = ap.parse_args()
    render = a.render

    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    now_et = now.astimezone(ET)
    cfg = load_json(CONFIG, None)
    if not cfg:
        print("config missing: " + CONFIG)
        return 2
    state = load_json(STATE, {"processed": {}, "texted": {}})

    if not render and not in_window(now_et, cfg):
        return 0
    lookback = a.hours * 60 if (render and a.hours) else cfg.get("max_age_minutes", 20)

    if a.fixture:
        calls = load_json(a.fixture, {})
        calls = calls.get("call_logs", calls) if isinstance(calls, dict) else calls
    else:
        try:
            tok = zoom_token(now)
        except Exception as e:
            if render:
                print("Zoom token request failed: %s" % e)
                return 1
            ledger_once(state, "token", "Could not get a Zoom API token (%s); missed-call texts paused." % type(e).__name__,
                        "yes, check the Zoom Server-to-Server app is still activated")
            save_json(STATE, state)
            return 1
        if not tok:
            if render:
                print("Zoom credentials not found at ~/.vp_secrets/zoom_s2s.json.")
                return 1
            ledger_once(state, "creds", "Zoom API credentials not found at ~/.vp_secrets/zoom_s2s.json; missed-call texts cannot run.",
                        "no, the Zoom Call Pipeline uses the same file; check it still exists")
            save_json(STATE, state)
            return 1
        day_from = (now_et - dt.timedelta(minutes=lookback)).date().isoformat()
        try:
            calls = zoom_calls(tok, day_from, now_et.date().isoformat())
        except urllib.error.HTTPError as e:
            if render:
                print("Zoom call history request failed: HTTP %s %s" % (e.code, e.read()[:300]))
                return 1
            ledger_once(state, "api%s" % e.code, "Zoom call-history API returned HTTP %s; missed-call texts paused." % e.code,
                        "yes, check the app's scopes include phone:read:list_call_logs:admin" if e.code in (400, 401, 403) else "no")
            save_json(STATE, state)
            return 1
        except Exception as e:
            log("fetch error %s" % e)
            return 1

    dry = publish_guard_armed(now)
    decisions, unknown = decide(calls, cfg, state, now, lookback, render)

    if render:
        print("=== RENDER ONLY — nothing sent, no state written ===")
        print("now %s ET | lookback %d min | calls fetched %d | publish guard %s"
              % (now_et.strftime("%a %Y-%m-%d %H:%M"), lookback, len(calls), "ARMED" if dry else "off"))
        seen = {}
        for c in calls:
            k = "%s/%s" % (norm(c.get("direction")), norm(c.get("call_result")) or "(blank)")
            seen[k] = seen.get(k, 0) + 1
        print("result values seen: " + ", ".join("%s=%d" % kv for kv in sorted(seen.items())))
        if unknown:
            print("NOT on the missed allow-list (never texted, review these): "
                  + ", ".join("%s=%d" % kv for kv in sorted(unknown.items())))
        for dec, reason, c, code, caller, dur in decisions:
            print("%-4s %s %-3s %-12s %s %-7s %s" % (
                dec, parse_ts(c["start_time"]).astimezone(ET).strftime("%m-%d %H:%M"), code,
                norm(c.get("call_result")), last4(caller), "open" if dur else "closed", reason))
            if dec == "SEND":
                print("      would text from %s: %s" % (cfg["stores"][code]["name"],
                                                         render_text(cfg, cfg["stores"][code], dur)))
        return 0

    sent = 0
    for dec, reason, c, code, caller, dur in decisions:
        cid = c.get("id") or c.get("call_id")
        if dec == "WAIT":
            continue
        if dec == "SKIP":
            state["processed"][cid] = now.isoformat()
            log("skip %s %s %s: %s" % (code, last4(caller), norm(c.get("call_result")), reason))
            continue
        if dry:
            log("publish guard ARMED — would text %s %s" % (code, last4(caller)))
            continue
        s = cfg["stores"][code]
        payload = {"event": "missed_call_text", "text": render_text(cfg, s, dur), "store": s["name"],
                   "caller_phone": caller, "call_result": norm(c.get("call_result")),
                   "queue": c.get("callee_name") or "", "during_hours": dur, "call_time": c.get("start_time")}
        try:
            ok = post_event(s["webhook"], payload)
        except Exception as e:
            ok = False
            log("POST failed %s %s: %s" % (code, last4(caller), e))
        if ok:
            state["processed"][cid] = now.isoformat()
            state["texted"][h(caller)] = now.isoformat()
            sent += 1
            log("SENT %s %s (%s, %s)" % (code, last4(caller), norm(c.get("call_result")), "open" if dur else "closed"))
            receipt(code)
        else:
            state.setdefault("post_fail", {})
            state["post_fail"][code] = state["post_fail"].get(code, 0) + 1
            if state["post_fail"][code] >= 3:
                ledger_once(state, "post%s" % code, "Chekkit webhook for %s rejected missed-call events 3 times." % code, "no")

    # prune state: processed 3 days, texted 2 days
    cut = now - dt.timedelta(days=3)
    state["processed"] = {k: v for k, v in state["processed"].items() if parse_ts(v) > cut}
    cut2 = now - dt.timedelta(days=2)
    state["texted"] = {k: v for k, v in state["texted"].items() if parse_ts(v) > cut2}
    if unknown:
        state["unknown_results"] = unknown
    save_json(STATE, state)
    save_json(HEARTBEAT, {"ts": now.isoformat(), "calls": len(calls), "sent": sent, "guard": dry}, 0o644)
    return 0


if __name__ == "__main__":
    sys.exit(main())
