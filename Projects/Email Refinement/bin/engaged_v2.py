#!/usr/bin/env python3
"""engaged_v2.py — build/refresh the bot-resistant "Engaged v2" audience list in Brevo.

Email Dept plan 2026-09-05 (file 19), Phase 1 item 9. Finding F5: list 7 ("Engaged List") is fed by a
Brevo automation rule "any link click -> add to list 7", which recruits security scanners that click
every link the instant the mail lands. List-7 sends have reported 58-136% click-of-delivered.

This script scores contacts from per-contact click data (GET /contacts/{email} -> statistics.clicked,
which DOES carry campaignId, url, eventTime, ip, count — contrary to the 8/22 audit's assumption) and
maintains a SEPARATE list, never touching list 7:

    HUMAN-ENGAGED (90d) if, in at least one campaign in the last 90 days, the contact clicked an
    INTENT link (primary CTA, any store call / text / map button, store finder, website button) AND
    that campaign's click pattern is not scanner-shaped:
        - first click >= 45 s after delivery to that contact   (scanners click on arrival)
        - <= 7 distinct URLs clicked in that campaign          (scanners walk the whole footer)
        - not ONLY chrome links (logo / instagram / facebook / unsubscribe / mirror)

Universe scanned each run = current list 7 members + every recipient list of the most recently SENT
weekly campaign(s) in the last 8 days (engaged + seeds + waves), deduped. ~2.5k GETs, ~5 min.
Seeds (list 10) are excluded from v2 — they are staff.

    python3 engaged_v2.py            # dry run: scores + would-add / would-remove counts
    python3 engaged_v2.py --apply    # create list (first run) and sync membership
    python3 engaged_v2.py --apply --compare   # also print list-7 vs v2 overlap for the log

Additive-only: creates list "Engaged v2 — human-verified (90d)" once (stores id in engaged_v2_state.json
next to this file); adds/removes contacts ONLY on that list. Never edits list 7, attributes, or campaigns.
"""
import argparse, datetime as dt, json, os, sys, time, urllib.request, urllib.error, urllib.parse

BASE = "https://api.brevo.com/v3"
KEY = open(os.path.expanduser("~/.config/valley-pawn/brevo_api_key")).read().strip()
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "engaged_v2_state.json")
LIST_NAME = "Engaged v2 — human-verified (clicked call/text/CTA in 90d, not scanner-shaped)"
ENGAGED_OLD, SEEDS = 7, 10
WINDOW_DAYS = 90
MIN_DELAY_S = 45
MAX_DISTINCT_URLS = 7
CHROME = ("utm_content=logo", "footer_instagram", "brand_facebook", "instagram_follow", "footer_website_",
          "unsubscribe", "mirror", "update-profile", "[UNSUBSCRIBE]", "[MIRROR]")
INTENT = ("utm_content=primary_cta", "_call", "_text", "_map", "store_finder", "footer_website", "/c/", "/t/")


def req(method, path, body=None, tries=6):
    data = json.dumps(body).encode() if body is not None else None
    for a in range(tries):
        r = urllib.request.Request(BASE + path, data=data, method=method,
                                   headers={"api-key": KEY, "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else {})
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(3 + 3 * a); continue
            return e.code, e.read().decode()
        except Exception as ex:  # transient network
            time.sleep(2 + 2 * a)
    return 599, "gave up"


def list_members(list_id):
    out, off = [], 0
    while True:
        st, d = req("GET", f"/contacts/lists/{list_id}/contacts?limit=500&offset={off}")
        if st != 200: raise SystemExit(f"list {list_id} read failed {st} {d}")
        cs = d.get("contacts", [])
        out += [c["email"] for c in cs if not c.get("emailBlacklisted")]
        if len(cs) < 500: break
        off += 500
    return out


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def score(contact):
    """Return (engaged: bool, reason: str)."""
    st = contact.get("statistics") or {}
    delivered = {}
    for d in st.get("delivered") or []:
        delivered.setdefault(d["campaignId"], ts(d["eventTime"]))
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=WINDOW_DAYS)
    reasons = []
    for c in st.get("clicked") or []:
        links = c.get("links") or []
        if not links: continue
        times = [ts(l["eventTime"]) for l in links]
        if max(times) < cutoff: continue
        urls = [l["url"] for l in links]
        distinct = len(set(urls))
        intent = [u for u in urls if any(k in u for k in INTENT) and not any(k in u for k in CHROME)]
        if not intent:
            reasons.append(f"c{c['campaignId']}:chrome-only"); continue
        if distinct > MAX_DISTINCT_URLS:
            reasons.append(f"c{c['campaignId']}:walked-{distinct}-urls"); continue
        dlv = delivered.get(c["campaignId"])
        if dlv is not None:
            delay = (min(times) - dlv).total_seconds()
            if delay < MIN_DELAY_S:
                reasons.append(f"c{c['campaignId']}:clicked-{int(delay)}s-after-delivery"); continue
        return True, f"c{c['campaignId']}:intent-click"
    return False, ";".join(reasons) or "no-clicks-90d"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="debug: scan only N contacts")
    ap.add_argument("--max-universe", type=int, default=2600,
                    help="cap contacts scanned per run (~0.35 s each). Priority: current v2 members, "
                         "then list 7, then a rotating slice of everyone else so the big lists get "
                         "covered across successive runs. 0 = no cap.")
    a = ap.parse_args()

    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    v2_id = state.get("list_id")

    # ---- universe, in priority tiers -------------------------------------------------
    # A contact can only qualify if they were SENT something in the window, so the universe is
    # every list a recent send went to. That includes the 13k master when the monthly Gold & Silver
    # ran, which is too big to scan in one pass — hence tiering + a rotating slice.
    seeds = set(list_members(SEEDS))
    tier_v2 = set(list_members(v2_id)) if v2_id else set()   # never drop someone without re-scoring
    tier_7 = set(list_members(ENGAGED_OLD))                  # the incumbent audience
    st, sent = req("GET", "/emailCampaigns?status=sent&limit=20&sort=desc")
    recent_lists, rest = set(), set()
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=WINDOW_DAYS)
    for c in (sent.get("campaigns") or []):
        sd = c.get("sentDate")
        if sd and ts(sd) >= since:
            for l in (c.get("recipients", {}).get("lists") or []):
                if l != SEEDS: recent_lists.add(l)
    for l in sorted(recent_lists):
        rest |= set(list_members(l))
    rest -= (tier_v2 | tier_7 | seeds)

    priority = [e for e in sorted(tier_v2 | tier_7) if e not in seeds]
    others = sorted(rest)
    cap = a.limit or a.max_universe or 0
    rotated = 0
    if cap and len(priority) + len(others) > cap:
        room = max(cap - len(priority), 0)
        off = int(state.get("rotate_offset", 0)) % max(len(others), 1)
        slice_ = (others + others)[off:off + room]          # wrap-around slice
        state["rotate_offset"] = (off + room) % max(len(others), 1)
        rotated = len(slice_)
        universe = priority + slice_
    else:
        universe = priority + others
    print(f"universe {len(universe)} of {len(priority) + len(others)} "
          f"(priority: v2+list7 = {len(priority)}; rotating slice of the rest: {rotated}; "
          f"recent-send lists {sorted(recent_lists)}; seeds excluded)")

    engaged, dropped, errors = [], [], 0
    reasons_hist = {}
    for i, em in enumerate(universe):
        st, c = req("GET", f"/contacts/{urllib.parse.quote(em)}")
        if st != 200:
            errors += 1; continue
        ok, why = score(c)
        key = why.split(":")[-1] if ":" in why else why
        reasons_hist[key] = reasons_hist.get(key, 0) + 1
        (engaged if ok else dropped).append(em)
        if i % 250 == 0: print(f"  scanned {i}/{len(universe)}  engaged so far {len(engaged)}")
        time.sleep(0.12)
    print(f"scored: engaged {len(engaged)} | not-engaged {len(dropped)} | errors {errors}")
    print("reasons:", json.dumps(dict(sorted(reasons_hist.items(), key=lambda x: -x[1])), indent=0))

    if a.compare:
        old = set(list_members(ENGAGED_OLD))
        e = set(engaged)
        print(f"compare: list7={len(old)}  v2={len(e)}  both={len(old & e)}  list7-only(scanner-shaped or stale)={len(old - e)}  v2-only(new humans)={len(e - old)}")

    if not a.apply:
        print("DRY RUN — pass --apply to create/sync the v2 list"); return 0

    if not v2_id:
        st, r = req("POST", "/contacts/lists", {"name": LIST_NAME, "folderId": 1})
        if st >= 300: raise SystemExit(f"list create failed {st} {r}")
        v2_id = r["id"]; state["list_id"] = v2_id
        json.dump(state, open(STATE, "w"), indent=2)
        print(f"created list {v2_id}")
    current = set(list_members(v2_id))
    to_add = sorted(set(engaged) - current)
    to_remove = sorted(current - set(engaged))
    for i in range(0, len(to_add), 150):
        st, r = req("POST", f"/contacts/lists/{v2_id}/contacts/add", {"emails": to_add[i:i + 150]})
        print("add", st, str(r)[:120]); time.sleep(0.5)
    for i in range(0, len(to_remove), 150):
        st, r = req("POST", f"/contacts/lists/{v2_id}/contacts/remove", {"emails": to_remove[i:i + 150]})
        print("remove", st, str(r)[:120]); time.sleep(0.5)
    final = len(list_members(v2_id))
    state.update({"last_run": dt.datetime.now().isoformat(timespec="seconds"), "last_count": final,
                  "added": len(to_add), "removed": len(to_remove)})
    json.dump(state, open(STATE, "w"), indent=2)
    print(f"v2 list {v2_id}: +{len(to_add)} -{len(to_remove)} -> {final} members (verified by re-read)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
