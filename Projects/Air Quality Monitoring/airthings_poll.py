#!/usr/bin/env python3
"""
Airthings air-quality poller + alerter + daily digest (Domain 3 — Personal).

Runs natively via launchd (no Claude in the loop):
  com.personal.airthings-poll    every 15 min   -> python3 airthings_poll.py
  com.personal.airthings-digest  07:30 daily    -> python3 airthings_poll.py --digest

Data path (all in this folder):
  secrets.json   {"client_id": "...", "client_secret": "..."}   chmod 600
  readings.csv   one row per device per poll (append-only history)
  latest.json    most recent values per device
  state.json     alert cooldowns + cached account id
  poll.log       plain-text log (technical detail lives HERE, never in Slack)

API: Airthings for Consumer API (OAuth2 client_credentials)
  POST https://accounts-api.airthings.com/v1/token
  GET  https://consumer-api.airthings.com/v1/accounts
  GET  https://consumer-api.airthings.com/v1/accounts/{id}/devices
  GET  https://consumer-api.airthings.com/v1/accounts/{id}/sensors?unit=imperial[&sn=...]
  Rate limit ~120 req/hour -> 15-min polling uses ~12/hour.

Alerts: iMessage text to Joshua's phone via Messages.app (his call 2026-09-05 — text, not Slack).
Plain language, no jargon, never a failure notice (Rule 16).
"""
import base64, csv, json, os, sys, time, datetime, subprocess, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
SECRETS = os.path.join(HERE, "secrets.json")
READINGS = os.path.join(HERE, "readings.csv")
LATEST = os.path.join(HERE, "latest.json")
STATE = os.path.join(HERE, "state.json")
LOG = os.path.join(HERE, "poll.log")

TOKEN_URL = "https://accounts-api.airthings.com/v1/token"
API = "https://consumer-api.airthings.com/v1"

ALERT_COOLDOWN_S = 6 * 3600

# Thresholds (imperial units from the API: radon pCi/L, temp F, pm ug/m3, voc ppb, co2 ppm, humidity %)
# Each: (sensor_type, low, high, plain-language label, unit)
THRESHOLDS = {
    "radonShortTermAvg": (None, 4.0, "Radon", "pCi/L"),
    "co2":               (None, 1000, "CO2", "ppm"),
    "pm25":              (None, 35, "Fine particles (PM2.5)", "µg/m³"),
    "pm1":               (None, 35, "Fine particles (PM1)", "µg/m³"),
    "voc":               (None, 2000, "Airborne chemicals (VOC)", "ppb"),
    "humidity":          (30, 65, "Humidity", "%"),   # 60 would fire 27% of the time (year baseline); 65 = real problem
    "temp":              (60, 85, "Temperature", "°F"),
}

CSV_COLS = ["ts_utc", "ts_local", "serial", "device_name", "location", "sensor", "value", "unit"]


def log(msg):
    line = "%s %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    try:
        with open(LOG, "a") as f:
            f.write(line)
    except Exception:
        pass


def load_json(p, default):
    try:
        with open(p) as f:
            return json.load(f)
    except Exception:
        return default


def save_json(p, obj):
    tmp = p + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1)
    os.replace(tmp, p)


def http(url, headers=None, data=None, timeout=25):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


def get_token(sec):
    basic = base64.b64encode(("%s:%s" % (sec["client_id"], sec["client_secret"])).encode()).decode()
    body = json.dumps({"grant_type": "client_credentials"}).encode()
    tok, _ = http(TOKEN_URL, {"Authorization": "Basic " + basic, "Content-Type": "application/json"}, body)
    return tok["access_token"]


def api_get(token, path):
    return http(API + path, {"Authorization": "Bearer " + token})


def poll():
    sec = load_json(SECRETS, None)
    if not sec or not sec.get("client_id") or not sec.get("client_secret"):
        log("no secrets.json yet — skipping")
        return 0
    state = load_json(STATE, {})
    try:
        token = get_token(sec)
        if not state.get("account_id"):
            acc, _ = api_get(token, "/accounts")
            state["account_id"] = acc["accounts"][0]["id"]
            save_json(STATE, state)
        aid = state["account_id"]
        # refresh device list at most every 6 hours
        if time.time() - state.get("devices_at", 0) > 6 * 3600 or not state.get("devices"):
            dev, _ = api_get(token, "/accounts/%s/devices" % aid)
            state["devices"] = {d["serialNumber"]: {"name": d.get("name", ""),
                                                    "type": d.get("type", ""),
                                                    "location": (d.get("home") or d.get("location") or {}).get("name", "") if isinstance(d.get("home") or d.get("location"), dict) else str(d.get("location", ""))}
                                for d in dev.get("devices", [])}
            state["devices_at"] = time.time()
            save_json(STATE, state)
        sens, hdrs = api_get(token, "/accounts/%s/sensors?unit=imperial" % aid)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()[:300]
        except Exception:
            body = ""
        log("API error %s %s" % (e.code, body))
        return 1
    except Exception as e:
        log("poll error: %r" % e)
        return 1

    now = datetime.datetime.now(datetime.timezone.utc)
    ts_utc = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    ts_local = now.astimezone().strftime("%Y-%m-%d %H:%M")
    new_file = not os.path.exists(READINGS)
    latest = {}
    rows = []
    for r in sens.get("results", []):
        sn = r.get("serialNumber", "")
        meta = state["devices"].get(sn, {})
        vals = {}
        for s in r.get("sensors", []):
            st = s.get("sensorType")
            v = s.get("value")
            u = s.get("unit", "")
            if st is None or v is None:
                continue
            vals[st] = {"value": v, "unit": u}
            rows.append([ts_utc, ts_local, sn, meta.get("name", ""), meta.get("location", ""), st, v, u])
        if r.get("batteryPercentage") is not None:
            vals["battery"] = {"value": r["batteryPercentage"], "unit": "%"}
        latest[sn] = {"name": meta.get("name", ""), "location": meta.get("location", ""),
                      "recorded": r.get("recorded"), "sensors": vals, "polled": ts_local}
    if rows:
        with open(READINGS, "a", newline="") as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(CSV_COLS)
            w.writerows(rows)
        save_json(LATEST, latest)
    log("polled %d device(s), %d values, ratelimit-remaining=%s" %
        (len(latest), len(rows), hdrs.get("X-RateLimit-Remaining", "?")))
    check_alerts(latest, state)
    return 0


JOSHUA_PHONE = "+18049304221"   # iMessage to Joshua's own number (his preference 2026-09-05: text, not Slack DM)


def notify(text):
    """Text Joshua via Messages.app (iMessage). Technical failures go to poll.log only."""
    script = (
        'on run argv\n'
        'tell application "Messages"\n'
        '  set svc to 1st account whose service type = iMessage\n'
        '  set buddyRef to participant (item 1 of argv) of svc\n'
        '  send (item 2 of argv) to buddyRef\n'
        'end tell\n'
        'end run'
    )
    try:
        r = subprocess.run(["osascript", "-e", script, JOSHUA_PHONE, text],
                           capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            log("imessage failed: %s" % r.stderr.strip()[:200])
            return False
        return True
    except Exception as e:
        log("imessage error: %r" % e)
        return False


slack_dm = notify  # legacy name used below


def fmt(v):
    return ("%.1f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def check_alerts(latest, state):
    cool = state.setdefault("cooldowns", {})
    msgs = []
    for sn, d in latest.items():
        where = d.get("name") or d.get("location") or sn
        for st, cfg in THRESHOLDS.items():
            if st not in d["sensors"]:
                continue
            lo, hi, label, unit = cfg
            v = d["sensors"][st]["value"]
            breach = (hi is not None and v >= hi) or (lo is not None and v <= lo)
            key = "%s|%s" % (sn, st)
            pend = state.setdefault("pending", {})
            if not breach:
                cool.pop(key, None)
                pend.pop(key, None)
                continue
            # require 2 consecutive polls (30 min) in breach before texting — one-off spikes
            # (cooking, a shower) are normal and would just be noise
            if st != "radonShortTermAvg" and not pend.get(key):
                pend[key] = time.time()
                continue
            if time.time() - cool.get(key, 0) < ALERT_COOLDOWN_S:
                continue
            cool[key] = time.time()
            if hi is not None and v >= hi:
                msgs.append("%s at %s is high: %s %s (watch level is %s)." % (label, where, fmt(v), unit, fmt(hi)))
            else:
                msgs.append("%s at %s is low: %s %s (watch level is %s)." % (label, where, fmt(v), unit, fmt(lo)))
    save_json(STATE, state)
    if msgs:
        text = "Air quality heads-up — " + " ".join(msgs) + " I'll stay quiet on this one for the next 6 hours unless it changes."
        if slack_dm(text):
            log("alert sent: %s" % text)


def digest(send=True):
    rows = []
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
    try:
        with open(READINGS, newline="") as f:
            for r in csv.DictReader(f):
                try:
                    t = datetime.datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
                except Exception:
                    continue
                if t >= cutoff:
                    rows.append(r)
    except FileNotFoundError:
        log("digest: no readings yet")
        return 0
    if not rows:
        log("digest: no rows in last 24h")
        return 0
    by = {}
    for r in rows:
        try:
            v = float(r["value"])
        except Exception:
            continue
        k = (r["device_name"] or r["serial"], r["sensor"])
        by.setdefault(k, []).append(v)
    order = ["radonShortTermAvg", "co2", "pm25", "voc", "humidity", "temp"]
    devices = sorted({k[0] for k in by})
    lines = ["Air quality, last 24 hours:"]
    flags = []
    for dev in devices:
        parts = []
        for st in order:
            vals = by.get((dev, st))
            if not vals:
                continue
            lo, hi, label, unit = THRESHOLDS.get(st, (None, None, st, ""))
            avg = sum(vals) / len(vals)
            mx, mn = max(vals), min(vals)
            parts.append("%s avg %s%s (%s–%s)" % (label, fmt(round(avg, 1)), (" " + unit) if unit != "%" else "%", fmt(round(mn, 1)), fmt(round(mx, 1))))
            if hi is not None and mx >= hi:
                flags.append("%s peaked at %s %s at %s" % (label, fmt(round(mx, 1)), unit, dev))
            if lo is not None and mn <= lo:
                flags.append("%s dipped to %s %s at %s" % (label, fmt(round(mn, 1)), unit, dev))
        lines.append("• %s — %s" % (dev, "; ".join(parts)))
    lines.append("Everything stayed in the comfortable range." if not flags else "Worth a look: " + "; ".join(flags) + ".")
    text = "\n".join(lines)
    print(text)
    if send:
        slack_dm(text)
    log("digest sent" if send else "digest printed")
    return 0


if __name__ == "__main__":
    if "--digest" in sys.argv:
        sys.exit(digest(send="--no-send" not in sys.argv))
    sys.exit(poll())
