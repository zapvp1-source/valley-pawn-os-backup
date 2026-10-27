#!/usr/bin/env python3
"""campaign_scorecard_measure.py -- read-only measurement for the weekly
Social campaign scorecard task (trig_01MSfQtbd8d2vVUzCJcXKKvT). Added 2026-10-26.

Pulls Publer post_insights (paginated, page 0 = newest, NO `limit` param) for the
5 store FB pages over [from, to), tags each post by format using state/plans/*.json
(account + scheduled_at within 15 min), and writes per-store / per-format stats.
Never schedules, edits or deletes anything.

usage: python3 campaign_scorecard_measure.py FROM TO OUT.json
"""
import json, sys, time, glob, statistics, datetime as dt
from pathlib import Path
import requests

ROOT = Path(__file__).parent
STORES = ["Culpeper", "Waynesboro", "Harrisonburg", "Lexington", "Roanoke"]
FMT = {"com_only_locals_know": "debate", "com_then_now": "history", "com_hs_game_week": "hs_game"}

def fetch(frm, to):
    cfg = json.loads((ROOT / "publer_config.json").read_text())
    acc = json.loads((ROOT / "publer_accounts.json").read_text())["accounts"]
    H = {"Authorization": f"Bearer-API {cfg['api_key']}", "Publer-Workspace-Id": cfg["workspace_id"],
         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
         "Accept": "application/json"}
    base = cfg["api_base"].rstrip("/")
    out = {}
    for s in STORES:
        aid = acc[s]["publer_id"]; rows = []; seen = set()
        for pg in range(100):
            r = None
            for att in range(3):
                r = requests.get(f"{base}/analytics/{aid}/post_insights", headers=H, timeout=60,
                                 params={"from": frm, "to": to, "sort": "scheduled_at", "account_id": aid, "page": pg})
                if r.ok: break
                time.sleep(3 * (att + 1))
            r.raise_for_status()
            d = r.json(); rr = (d.get("posts") or d.get("data") or []) if isinstance(d, dict) else d
            new = [x for x in rr if x.get("id") not in seen]
            if not new: break
            for x in new: seen.add(x.get("id"))
            rows += new
            if isinstance(d, dict) and isinstance(d.get("total"), int) and len(rows) >= d["total"]: break
        out[s] = rows
    return out

def slot_index():
    idx = []
    for f in glob.glob(str(ROOT / "state/plans/*.json")):
        if f.endswith("_results.json"): continue
        p = json.loads(Path(f).read_text()); slots = p["slots"] if isinstance(p, dict) else p
        for x in slots:
            fm = x.get("format") or {}
            idx.append((set(x.get("accounts") or []), dt.datetime.fromisoformat(x["scheduled_at"]), x["lane"],
                        fm.get("id") if isinstance(fm, dict) else fm, x.get("topic_id") or (x.get("contract") or {}).get("topic_id"), x["slot_id"]))
    return idx

def tag(store, post, idx):
    t = dt.datetime.fromisoformat(post["scheduled_at"])
    best = None
    for accs, st, lane, fid, topic, sid in idx:
        if store in accs and abs((st - t).total_seconds()) <= 900:
            best = (lane, fid, topic, sid); break
    if not best:
        return ("staff_video" if post.get("type") == "video" else "other"), None, None
    lane, fid, topic, sid = best
    if lane == "community":
        return FMT.get(fid, "other_community"), topic, sid
    return {"deal_video": "deal_video", "hiring": "hiring", "deal_photo": "deal_photo"}.get(lane, "other"), topic, sid

def val(p, k):
    v = (p.get("analytics") or {}).get(k)
    v = v.get("value") if isinstance(v, dict) else v
    try: return float(v or 0)
    except Exception: return 0.0

def main(frm, to, outp):
    followers = json.loads((ROOT / "state/store_followers.json").read_text())["followers"]
    data = fetch(frm, to); idx = slot_index(); posts = []
    for s, rows in data.items():
        for p in rows:
            if p.get("state") not in (None, "published"): continue
            f, topic, sid = tag(s, p, idx)
            posts.append({"store": s, "format": f, "topic": topic, "slot": sid, "at": p["scheduled_at"], "type": p.get("type"),
                          "reach": val(p, "reach"), "likes": val(p, "likes"), "comments": val(p, "comments"),
                          "shares": val(p, "shares"), "clicks": val(p, "post_clicks"), "link": p.get("post_link"),
                          "text": (p.get("text") or "")[:90]})
    def agg(ps, fol=None):
        if not ps: return {"posts": 0}
        r = [p["reach"] for p in ps]; med = statistics.median(r)
        return {"posts": len(ps), "median_reach": med, "pct_followers": round(100 * med / fol, 1) if fol else None,
                "engagements": sum(p["likes"] + p["comments"] + p["shares"] for p in ps),
                "comments": sum(p["comments"] for p in ps), "shares": sum(p["shares"] for p in ps)}
    COMM = ("debate", "history", "hs_game", "other_community")
    res = {"window": [frm, to], "generated": dt.datetime.now().isoformat(timespec="seconds"), "per_store": {}, "per_format": {}, "per_store_format": {}, "posts": posts}
    for s in STORES:
        ps = [p for p in posts if p["store"] == s]
        res["per_store"][s] = {"all": agg(ps, followers.get(s)), "community": agg([p for p in ps if p["format"] in COMM], followers.get(s))}
        res["per_store_format"][s] = {f: agg([p for p in ps if p["format"] == f], followers.get(s)) for f in sorted({p["format"] for p in ps})}
    for f in sorted({p["format"] for p in posts}):
        res["per_format"][f] = agg([p for p in posts if p["format"] == f])
    Path(outp).parent.mkdir(parents=True, exist_ok=True)
    Path(outp).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("window", "per_store", "per_format")}, indent=1))

if __name__ == "__main__":
    main(*sys.argv[1:4])
