#!/usr/bin/env python3
"""email_fixes_20261020.py — fixes from the 2026-10-20 email channel audit. Host only, stdlib.

  --inspect   read-only: prints what WOULD change on every unsent (queued/draft) campaign; writes nothing remote
  --apply     backs up html + recipients to Email Refinement/_audit/backup_20261020_fixes/ first,
              then PUT + re-GET verify each campaign. Idempotent (a second run changes nothing).

Scope: unsent campaigns only. Never sends, never schedules, never touches a sent campaign or a [PARKED] draft.
  1 HOURS     Waynesboro 6-day footer + store block — the same patterns the master templates got 10/14
              (imports patch_html/residuals from bin/waysat5_brevo.py; templates themselves are not touched here).
  2 TRACKING  deal-of-week Maps buttons: utm_content=deal_of_week_<city> -> deal_of_week_<city>_map,
              so the Friday analytics counts them as directions clicks.
  3 AUDIENCE  weekly campaigns (lists include 7 Engaged) -> [7 Engaged, 10 Seeds, 13 new store-collected contacts].
              Dormant wave lists 14-18 come off the weekly; dormant contacts still get the monthly
              Gold & Silver (list 3) and are kept for the planned reactivation series.
"""
import functools, json, os, re, sys
print = functools.partial(print, flush=True)
HOME = os.path.expanduser("~")
BIN = os.path.join(HOME, "Documents", "Claude", "Projects", "Valley Pawn OS", "bin")
sys.path.insert(0, BIN)
from waysat5_brevo import req, patch_html, residuals  # noqa: E402  (same API wrapper + hours patterns)

BK = os.path.join(HOME, "Documents", "Claude", "Projects", "Email Refinement", "_audit", "backup_20261020_fixes")
ENGAGED, SEEDS, NEW_CONTACTS = 7, 10, 13
WEEKLY_LISTS = [ENGAGED, SEEDS, NEW_CONTACTS]
WAVES = {14, 15, 16, 17, 18}
RE_DOW = re.compile(r'(utm_content=deal_of_week_[a-z]+)(?=["&])')


def unsent():
    out = []
    for status in ("queued", "draft"):
        st, r = req("GET", f"/emailCampaigns?status={status}&limit=100&sort=desc")
        if st != 200:
            print("LIST FAILED", status, st, str(r)[:200]); sys.exit(2)
        out += r.get("campaigns", [])
    return out


def plan(c, full):
    h = full.get("htmlContent") or ""
    h2, n = patch_html(h)
    h2, nd = RE_DOW.subn(r"\1_map", h2)
    if nd: n["deal_map_utm"] = nd
    lists = (full.get("recipients") or {}).get("lists") or []
    new_lists = lists
    if ENGAGED in lists:
        new_lists = WEEKLY_LISTS + [l for l in lists if l not in WAVES and l not in WEEKLY_LISTS]
    return h, h2, n, lists, new_lists


def main(write):
    os.makedirs(BK, exist_ok=True)
    log = []
    for c in unsent():
        cid, name = c["id"], c.get("name", "")
        if name.startswith("[PARKED") or "CANCELLED" in name:
            continue
        st, full = req("GET", f"/emailCampaigns/{cid}")
        if st != 200:
            print(f"#{cid} GET FAILED {st}"); log.append({"id": cid, "error": st}); continue
        h, h2, n, lists, new_lists = plan(c, full)
        lists_change = sorted(lists) != sorted(new_lists)
        if not n and not lists_change:
            print(f"#{cid} {full.get('status')} '{name[:50]}' — already clean"); continue
        print(f"#{cid} {full.get('status')} '{name[:50]}' html {n or '-'} | lists {lists} -> {new_lists if lists_change else 'unchanged'}")
        if not write:
            continue
        bp = os.path.join(BK, f"campaign_{cid}.orig.json")
        if not os.path.exists(bp):
            json.dump({"id": cid, "name": name, "status": full.get("status"), "lists": lists,
                       "htmlContent": h}, open(bp, "w"))
        body = {}
        if n: body["htmlContent"] = h2
        if lists_change: body["recipients"] = {"listIds": new_lists}
        pst, r = req("PUT", f"/emailCampaigns/{cid}", body)
        gst, chk = req("GET", f"/emailCampaigns/{cid}")
        h3 = chk.get("htmlContent", "") if gst == 200 else ""
        l3 = (chk.get("recipients") or {}).get("lists") or [] if gst == 200 else []
        res = residuals(h3)
        ok = (pst in (200, 204) and (not n or h3 == h2) and sorted(l3) == sorted(new_lists) and not res
              and not RE_DOW.search(h3) and chk.get("status") == full.get("status"))
        print(f"   PUT {pst} -> verify {'OK' if ok else 'FAIL ' + str(r)[:200]} lists={l3} status={chk.get('status')} residuals={res[:2]}")
        log.append({"id": cid, "name": name, "put": pst, "changes": n, "lists_before": lists, "lists_after": l3,
                    "status": chk.get("status"), "verified": ok, "residuals": res})
    if write:
        json.dump(log, open(os.path.join(BK, "fix_log.json"), "w"), indent=1)
        bad = [x for x in log if not x.get("verified")]
        print("DONE apply —", len(log), "changed,", len(bad), "failed")
        return 1 if bad else 0
    print("DONE inspect")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--inspect" in a: sys.exit(main(False))
    if "--apply" in a: sys.exit(main(True))
    sys.exit(__doc__)
