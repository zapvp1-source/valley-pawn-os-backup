#!/usr/bin/env python3
"""guesty_pull.py — Bald Rock data rail over the Guesty Open API (LOGINS project, 2026-10-14).

Replaces the signed-in app.guesty.com / airbnb.com / vrbo.com browser reads in the Bald Rock tasks
(monday briefing, 15-day contract, guest reviews). Client-credentials OAuth: no browser, no login, no
expiry Joshua has to touch. Credentials live only in the macOS Keychain (vp-guesty-client-id /
vp-guesty-client-secret, saved by api_keys_setup.sh guesty). The access token (24 h; Guesty allows 5
per key per day) is cached in the Keychain as vp-guesty-token and reused until 1 h before expiry.

Writes ONE snapshot the cloud tasks read with the Google Drive connector:
  My Drive/Bald Rock Data/guesty_snapshot.json  — listings, reservations (past 30 → next 180 days,
  with guest name/phone/email, channel, status, money, check-in/out), recent conversations (14 days,
  last 5 posts each) and reviews (60 days).
  guesty_pull.py            pull + write snapshot
  guesty_pull.py --check    verify credentials only (prints OK / reason; no secrets)
Silent when no credentials are saved yet (exit 0, one log line) so the agent can be installed first.
"""
import datetime as dt, json, os, subprocess, sys, time, urllib.parse, urllib.request

API = "https://open-api.guesty.com"
OUT_DIR = os.path.expanduser("~/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/Bald Rock Data")
LEDGER = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
UA = "ValleyPawnOps/1.0"


def kc_get(svc):
    r = subprocess.run(["security", "find-generic-password", "-s", svc, "-w"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def kc_set(svc, val):
    subprocess.run(["security", "add-generic-password", "-s", svc, "-a", os.environ.get("USER", "vp"), "-w", val, "-U"],
                   capture_output=True)


def http(method, url, data=None, headers=None):
    h = {"User-Agent": UA, "Accept": "application/json"}
    h.update(headers or {})
    body = None
    if data is not None:
        if h.get("Content-Type") == "application/x-www-form-urlencoded":
            body = urllib.parse.urlencode(data).encode()
        else:
            body = json.dumps(data).encode(); h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(int(e.headers.get("Retry-After", "5")) + 1); continue
            raise


def token():
    cached = kc_get("vp-guesty-token")
    if cached:
        try:
            t = json.loads(cached)
            if t.get("exp", 0) - 3600 > time.time():
                return t["access_token"]
        except Exception:
            pass
    cid, sec = kc_get("vp-guesty-client-id"), kc_get("vp-guesty-client-secret")
    if not cid or not sec:
        return None
    r = http("POST", API + "/oauth2/token",
             {"grant_type": "client_credentials", "scope": "open-api", "client_id": cid, "client_secret": sec},
             {"Content-Type": "application/x-www-form-urlencoded"})
    kc_set("vp-guesty-token", json.dumps({"access_token": r["access_token"], "exp": time.time() + int(r.get("expires_in", 86400))}))
    return r["access_token"]


def get(tok, path, params=None):
    q = ("?" + urllib.parse.urlencode(params)) if params else ""
    return http("GET", API + path + q, headers={"Authorization": "Bearer " + tok})


def paged(tok, path, params, key="results", cap=1000):
    out, skip = [], 0
    while True:
        p = dict(params, limit=100, skip=skip)
        r = get(tok, path, p)
        rows = r.get(key) if isinstance(r, dict) else r
        rows = rows or []
        out += rows
        if len(rows) < 100 or len(out) >= cap:
            return out
        skip += 100


def main():
    check = "--check" in sys.argv
    tok = token()
    if not tok:
        print("NO_CREDENTIALS — run api_keys_setup.sh guesty"); return 0
    if check:
        r = get(tok, "/v1/listings", {"limit": 1, "fields": "_id title nickname"})
        print("OK — Guesty API reachable; listings visible:", r.get("count", len(r.get("results", []))))
        return 0
    today = dt.date.today()
    lo, hi = (today - dt.timedelta(days=30)).isoformat(), (today + dt.timedelta(days=180)).isoformat()
    listings = paged(tok, "/v1/listings", {"fields": "_id title nickname address.full active"})
    filters = json.dumps([{"field": "checkOut", "operator": "$gte", "value": lo},
                          {"field": "checkIn", "operator": "$lte", "value": hi}])
    res = paged(tok, "/v1/reservations", {
        "filters": filters, "sort": "checkIn",
        "fields": "_id confirmationCode status source integration.platform checkIn checkOut checkInDateLocalized "
                  "checkOutDateLocalized nightsCount guestsCount guest.fullName guest.phone guest.email "
                  "money.totalPaid money.balanceDue money.hostPayout money.fareAccommodation listingId createdAt"})
    since = (dt.datetime.utcnow() - dt.timedelta(days=14)).isoformat() + "Z"
    convs = []
    try:
        cv = get(tok, "/v1/communication/conversations", {"limit": 50, "sort": "-lastUpdatedAt"})
        for c in (cv.get("data", {}) or {}).get("conversations", cv.get("results", [])) or []:
            if (c.get("lastUpdatedAt") or c.get("modifiedAt") or "") < since:
                continue
            item = {"id": c.get("_id"), "reservationId": (c.get("meta") or {}).get("reservations", [{}])[0].get("_id") if (c.get("meta") or {}).get("reservations") else None,
                    "guest": (c.get("meta") or {}).get("guestName"), "lastUpdatedAt": c.get("lastUpdatedAt")}
            try:
                posts = get(tok, f"/v1/communication/conversations/{c.get('_id')}/posts", {"limit": 5, "sort": "-createdAt"})
                pl = (posts.get("data", {}) or {}).get("posts", posts.get("results", [])) or []
                item["posts"] = [{"at": p.get("createdAt"), "from": p.get("sentBy") or p.get("type"), "module": (p.get("module") or {}).get("type"),
                                  "text": (p.get("body") or "")[:1500]} for p in pl]
            except Exception as e:
                item["posts_error"] = str(e)[:120]
            convs.append(item)
    except Exception as e:
        convs = [{"error": "conversations unavailable: " + str(e)[:150]}]
    reviews = []
    try:
        rv = get(tok, "/v1/reviews", {"limit": 50, "sort": "-createdAt"})
        reviews = rv.get("data", rv.get("results", [])) or []
    except Exception as e:
        reviews = [{"error": "reviews unavailable: " + str(e)[:150]}]
    snap = {"pulled_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "window": [lo, hi],
            "listings": listings, "reservations": res, "conversations": convs, "reviews": reviews,
            "_about": "Written hourly by com.valleypawn.guesty-pull (bin/guesty_pull.py). Read this instead of opening app.guesty.com, airbnb.com or vrbo.com."}
    os.makedirs(OUT_DIR, exist_ok=True)
    tmp = os.path.join(OUT_DIR, ".guesty_snapshot.tmp")
    json.dump(snap, open(tmp, "w"), indent=1, default=str)
    os.replace(tmp, os.path.join(OUT_DIR, "guesty_snapshot.json"))
    print(f"snapshot written: {len(listings)} listings, {len(res)} reservations, {len(convs)} conversations, {len(reviews)} reviews")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M ET")
        line = f"| {stamp} (native) | guesty-pull | The Bald Rock booking data pull did not complete ({type(e).__name__}). | NEEDS_HUMAN: no | OPEN |\n"
        try:
            today_rows = [l for l in open(LEDGER, errors="replace") if "guesty-pull" in l and l.startswith("| " + stamp[:10])]
            if not today_rows:
                open(LEDGER, "a").write(line)
        except Exception:
            pass
        print("ERROR", type(e).__name__, str(e)[:200]); sys.exit(2)
