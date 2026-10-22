#!/usr/bin/env python3
"""chekkit_ops.py — two Chekkit API jobs that need no browser (comms review 2026-10-21, Joshua: "build it").

  reviews-owed   GET /v1/reviews?unanswered=true per store (google + facebook) -> how many reviews are still
                 owed a reply, oldest waiting, low-star count. Writes fleet/state/chekkit_ops/reviews_owed.json.
                 The daily texting scorecard shows the line; nothing is posted by this command.
  assign-stale   Every 5 min in store hours: a customer text that has sat 10+ minutes with no reply from a
                 real staff member (automatic/AI texts don't count) is assigned in Chekkit to that store's
                 manager (PATCH /v1/conversations/{id} addAssignees, notify true -> the manager gets
                 Chekkit's normal push). Never removes anyone, never messages the customer, never touches a
                 thread already assigned to the manager, never re-assigns the same customer message twice.
                 Sign-offs ("thanks", "ok", emoji) and STOP/opt-out texts are skipped.
  probe          Read-only: team members per store (name, access level, whether they match the roster
                 manager), conversation fields, unanswered review counts. Use after roster changes.

Managers come from hr/ROSTER.json (department == store, title contains "Manager"), matched to the Chekkit
user by login email, then by name (first + last, case-insensitive; Sandra/Sandi, George/Benjie aliases).
Override per store in fleet/chekkit_ops_config.json {"managers": {"CUL": "login@example.com"}}.

  chekkit_ops.py reviews-owed [--render]
  chekkit_ops.py assign-stale [--render]      --render = decide and print, change nothing
  chekkit_ops.py probe
Logs carry first names and last-4 only. Failure policy v3: one FAILURE_LEDGER row a day, never a ping.
"""
import datetime as dt, json, os, re, sys, time, urllib.error, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import chekkit_api as ck  # noqa: E402

OS_DIR = os.path.dirname(HERE)
FLEET = os.path.join(OS_DIR, "fleet")
STATE = os.path.join(FLEET, "state", "chekkit_ops")
CFG = os.path.join(FLEET, "chekkit_ops_config.json")
MCT = os.path.join(FLEET, "missed_call_text_config.json")
ROSTER = os.path.join(OS_DIR, "hr", "ROSTER.json")
LEDGER = os.path.join(FLEET, "FAILURE_LEDGER.md")
ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
STORES = ["CUL", "WAY", "HAR", "LEX", "ROA"]
NAMES = {"CUL": "Culpeper", "WAY": "Waynesboro", "HAR": "Harrisonburg", "LEX": "Lexington", "ROA": "Roanoke"}
ALIASES = {"sandra": "sandi", "sandy": "sandi", "george": "benjie", "benji": "benjie", "chad": "chadd"}
STALE_MIN = 10
LOOKBACK_H = 6
ENDERS = {"thanks", "thank you", "thank u", "thankyou", "ty", "thx", "ok", "okay", "k", "kk", "sounds good", "got it",
          "bye", "will do", "perfect", "great", "awesome", "cool", "yes", "yep", "yup", "no problem", "np", "👍", "🙏", "❤️"}
STOP_RE = re.compile(r"^\s*(stop|unsubscribe|stop texting me|remove me|wrong number|cancel|end|quit)\s*[.!]*\s*$", re.I)


def now_et():
    return dt.datetime.now(ET)


def log(*a):
    print(now_et().strftime("%H:%M:%S"), *a, flush=True)


def ledger_once(task, sentence):
    today = now_et().strftime("%Y-%m-%d")
    try:
        for l in open(LEDGER, errors="replace").read().splitlines()[-300:]:
            if l.startswith("| " + today) and task in l and sentence[:50] in l:
                return
    except OSError:
        pass
    with open(LEDGER, "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (now_et().strftime("%Y-%m-%d %H:%M ET"), task, sentence))


def load(p, default):
    try:
        return json.load(open(p))
    except Exception:
        return default


def save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1)
    os.replace(tmp, p)


def req(code, method, path, body=None):
    tok = ck.token(code)
    if not tok:
        raise RuntimeError("no Chekkit token for %s" % code)
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(ck.BASE + path, data=data, method=method, headers={
        "Authorization": "Bearer " + tok, "Accept": "application/json", "Content-Type": "application/json",
        "User-Agent": "ValleyPawnOps/1.0"})
    for i in range(3):
        try:
            with urllib.request.urlopen(r, timeout=30) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(int(e.headers.get("Retry-After") or 3 + 3 * i)); continue
            raise RuntimeError("%s %s -> %s %s" % (method, path.split("?")[0], e.code, e.read()[:160].decode(errors="replace")))
    raise RuntimeError("%s %s -> retries exhausted" % (method, path.split("?")[0]))


def first(name):
    w = (name or "").strip().split()
    f = w[0].lower() if w else ""
    return ALIASES.get(f, f)


def norm_name(name):
    w = (name or "").lower().split()
    return (ALIASES.get(w[0], w[0]) + " " + w[-1]) if len(w) >= 2 else (w[0] if w else "")


# ---------------------------------------------------------------- reviews owed
def reviews_owed(render=False):
    out = {"checked_at": now_et().isoformat(timespec="seconds"), "stores": {}, "errors": {}}
    for code in STORES:
        s = {"owed": 0, "low_star": 0, "oldest_days": None, "by_platform": {}}
        try:
            for plat in ("google", "facebook"):
                n, page = 0, 1
                while page <= 10:
                    b = req(code, "GET", "/v1/reviews?platform=%s&unanswered=true&limit=50&page=%d" % (plat, page))
                    rs = b.get("reviews") or []
                    for r in rs:
                        if r.get("reply"):
                            continue
                        n += 1
                        rt = r.get("rating")
                        if (isinstance(rt, (int, float)) and rt <= 3) or r.get("recommendationType") == "negative":
                            s["low_star"] += 1
                        t = ck.ts(r.get("createdAt"))
                        if t:
                            age = (dt.datetime.now(UTC) - t).days
                            s["oldest_days"] = max(s["oldest_days"] or 0, age)
                    if not b.get("hasMore"):
                        break
                    page += 1
                    time.sleep(1.1)
                s["by_platform"][plat] = n
                s["owed"] += n
                time.sleep(1.1)
        except Exception as e:  # noqa: BLE001
            out["errors"][code] = str(e)[:160]
        out["stores"][code] = s
    out["total_owed"] = sum(v["owed"] for v in out["stores"].values())
    if not render:
        save(os.path.join(STATE, "reviews_owed.json"), out)
        if len(out["errors"]) == len(STORES):
            ledger_once("chekkit-reviews-owed", "The daily count of reviews still owed a reply could not read Chekkit for any store.")
    print(json.dumps({k: (v["owed"], v["low_star"], v["oldest_days"]) for k, v in out["stores"].items()}), "errors:", list(out["errors"]))
    return 0


# ---------------------------------------------------------------- managers
def roster_managers():
    r = load(ROSTER, {})
    emp = r.get("employees", []) if isinstance(r, dict) else r
    m = {}
    for e in emp or []:
        dept = (e.get("department") or "").strip()
        code = next((c for c, n in NAMES.items() if n.lower() == dept.lower()), None)
        if code and "manager" in (e.get("title") or "").lower() and _reportable(e.get("name")):
            m[code] = {"name": e.get("name"), "email": (e.get("email") or "").lower()}
    return m


def _reportable(name):
    """Fleet-wide rule (Joshua 2026-10-21, bin/vp_people.py): only current staff, never a Davis. This is a
    routing action, not a report: a stale roster must not stop routing, so it falls back to the Davis check only."""
    import vp_people
    try:
        return vp_people.is_reportable(name)
    except vp_people.RosterHold:
        return not vp_people.is_davis(name)


def team(code):
    b = req(code, "GET", "/v1/team-members")
    return b.get("teamMembers") or b.get("team_members") or []


def tm_login(t):
    return (t.get("login") or t.get("username") or t.get("email") or "").lower()


def manager_login(code, roster, cfg, members):
    over = (cfg.get("managers") or {}).get(code)
    if over:
        return over, "config"
    mgr = roster.get(code)
    if not mgr:
        return None, "no manager in roster"
    for t in members:
        if mgr["email"] and tm_login(t) == mgr["email"]:
            return tm_login(t), "email"
    want = norm_name(mgr["name"])
    hits = [t for t in members if norm_name(t.get("name") or "") == want]
    if len(hits) == 1:
        return tm_login(hits[0]) or hits[0].get("id") or hits[0].get("name"), "name"
    return None, "not found in Chekkit team (%s)" % mgr["name"]


# ---------------------------------------------------------------- assign stale
def during_hours(t, s):
    if t.weekday() not in s.get("days", []):
        return False
    o = dt.time.fromisoformat(s.get("open", "10:00"))
    c = dt.time.fromisoformat(s.get("close_by_weekday", {}).get(str(t.weekday()), s.get("close", "18:00")))
    return o <= t.time() < c


def is_ender(text):
    t = re.sub(r"[^\w\s']", "", (text or "").strip().lower()).strip()
    if not t:
        return True        # emoji / tapback / image-only reactions
    return t in ENDERS or (len(t) <= 12 and any(t.startswith(x) for x in ("thank", "ok", "ty ")))


def assignee_logins(conv):
    out = set()
    for key in ("assignees", "assignedTo", "assigned", "teamMembers"):
        v = conv.get(key)
        if isinstance(v, list):
            for a in v:
                if isinstance(a, dict):
                    out.add((a.get("login") or a.get("username") or a.get("email") or a.get("name") or "").lower())
                else:
                    out.add(str(a).lower())
        elif isinstance(v, dict):
            out.add((v.get("login") or v.get("email") or v.get("name") or "").lower())
        elif isinstance(v, str):
            out.add(v.lower())
    return {x for x in out if x}


def assign_stale(render=False):
    mct = load(MCT, {})
    cfg = load(CFG, {})
    roster = roster_managers()
    st = load(os.path.join(STATE, "assigned.json"), {"done": {}})
    now = dt.datetime.now(UTC)
    since = now - dt.timedelta(hours=LOOKBACK_H)
    acted, errors = [], {}
    for code in STORES:
        s = (mct.get("stores") or {}).get(code)
        if not s or not during_hours(now.astimezone(ET), s):
            continue
        try:
            members = team(code)
            login, how = manager_login(code, roster, cfg, members)
            if not login:
                ledger_once("chekkit-assign-stale", "%s texts could not be routed to the manager: %s." % (NAMES[code], how))
                continue
            convs = ck.conversations_since(code, since)
            for phone, c in convs.items():
                last = c.get("lastMessage") or {}
                if last.get("sender") not in ("customer", "ai", "business"):
                    continue
                msgs = ck.messages(code, c.get("id"))
                msgs = [m for m in msgs if ck.ts(m.get("createdAt"))]
                msgs.sort(key=lambda m: ck.ts(m.get("createdAt")))
                cust = [m for m in msgs if m.get("sender") == "customer"]
                if not cust:
                    continue
                lc = cust[-1]
                t = ck.ts(lc.get("createdAt"))
                text = (lc.get("text") or "").strip()
                if (now - t).total_seconds() < STALE_MIN * 60 or not during_hours(t.astimezone(ET), s):
                    continue
                if STOP_RE.match(text) or (is_ender(text) and not lc.get("media")):
                    continue
                staff_after = any(m.get("sender") == "business" and not ck.is_automated(m) and ck.ts(m.get("createdAt")) > t
                                  for m in msgs)
                if staff_after:
                    continue
                key = "%s|%s" % (code, lc.get("id") or (phone + "|" + lc.get("createdAt", "")))
                if key in st["done"]:
                    continue
                if login.lower() in assignee_logins(c):
                    st["done"][key] = {"at": now.isoformat(), "how": "already-assigned"}
                    continue
                waited = int((now - t).total_seconds() // 60)
                line = "%s …%s waited %d min -> assign %s (%s)" % (code, phone[-4:], waited, first(roster.get(code, {}).get("name")), how)
                if render:
                    log("WOULD", line)
                else:
                    req(code, "PATCH", "/v1/conversations/%s" % c.get("id"), {"addAssignees": [login], "notify": True})
                    st["done"][key] = {"at": now.isoformat(), "waited_min": waited}
                    log("ASSIGNED", line)
                acted.append({"store": code, "last4": phone[-4:], "waited_min": waited})
                time.sleep(0.4)
        except Exception as e:  # noqa: BLE001
            errors[code] = str(e)[:160]
            log(code, "ERROR", errors[code])
    if not render:
        cutoff = (now - dt.timedelta(days=3)).isoformat()
        st["done"] = {k: v for k, v in st["done"].items() if v.get("at", "") >= cutoff}
        save(os.path.join(STATE, "assigned.json"), st)
        day = now_et().strftime("%Y-%m-%d")
        tally = load(os.path.join(STATE, "assigned_daily.json"), {})
        for a in acted:
            tally.setdefault(day, {}).setdefault(a["store"], 0)
            tally[day][a["store"]] += 1
        save(os.path.join(STATE, "assigned_daily.json"), dict(sorted(tally.items())[-60:]))
        if errors and len(errors) >= 3:
            ledger_once("chekkit-assign-stale", "Unanswered texts could not be routed to store managers this cycle (%s)." % ", ".join(sorted(errors)))
    log("done", len(acted), "assigned" if not render else "would assign", "errors:", list(errors))
    return 0


# ---------------------------------------------------------------- probe
def probe():
    roster = roster_managers()
    cfg = load(CFG, {})
    for code in STORES:
        try:
            members = team(code)
            login, how = manager_login(code, roster, cfg, members)
            print("==", code, "team:", [("%s %s" % (first(t.get("name")), (t.get("name") or "").split()[-1][:1] if t.get("name") else ""), t.get("accessLevel")) for t in members])
            print("   manager:", first(roster.get(code, {}).get("name")), "->", "OK via " + how if login else how)
            b = req(code, "GET", "/v1/conversations?limit=1")
            c = (b.get("conversations") or [{}])[0]
            print("   conversation keys:", sorted(c.keys()))
            for k in ("assignees", "assignedTo", "assigned", "department", "status"):
                if k in c:
                    v = c[k]
                    print("   ", k, "=", (type(v).__name__, (len(v) if isinstance(v, list) else str(v)[:40])))
            r = req(code, "GET", "/v1/reviews?unanswered=true&limit=50")
            print("   google reviews owed:", len([x for x in r.get("reviews") or [] if not x.get("reply")]), "hasMore", r.get("hasMore"))
        except Exception as e:  # noqa: BLE001
            print("==", code, "ERROR", str(e)[:200])
        time.sleep(1.5)
    return 0


def main(a):
    if not a:
        print(__doc__); return 2
    cmd, render = a[0], "--render" in a
    if cmd == "reviews-owed":
        return reviews_owed(render)
    if cmd == "assign-stale":
        return assign_stale(render)
    if cmd == "probe":
        return probe()
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) or 0)
