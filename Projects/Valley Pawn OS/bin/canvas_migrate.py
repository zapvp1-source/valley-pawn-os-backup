#!/usr/bin/env python3
"""canvas_migrate.py create|status — bot-owned replacements for the 5 weekly canvases (2026-10-14).

WHY: the original canvases (F0BH6BJ0PK7 loan, F0BJ48BMZGQ layaway, F0BH9UK284S employee, F0BHDL6AULU aged,
F0BH6S9U5FX store) were created by Joshua's account through the Cowork Slack connector. files.info shows
editors=[Joshua] only and the channel share is access "read", so the Goldilocks bot can read them but
canvases.edit returns restricted_action. Only the owner can change their access, and Slack has no
"transfer canvas ownership" API. So the bot creates its own canvas per channel (it owns it, so it can always
edit it), tabbed in the same channel, channel members READ, Joshua WRITE.

create: idempotent. For each kind without a bot-owned id in fleet/canvas_state/canvas_ids.json: canvases.create
  (same title, channel_id = the channel) with a one-line placeholder; canvases.access.set channel read +
  Joshua write; files.info to confirm creator = bot and the channel share; record the id. Copies the layaway
  two-owner state file to the new id. Never edits, deletes or re-permissions the ORIGINAL canvases.
status: read-only — prints the mapping and each new canvas's files.info summary.
"""
import json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_slack

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
STATE_DIR = os.path.join(OS_DIR, "fleet", "canvas_state")
IDS = os.path.join(STATE_DIR, "canvas_ids.json")
OLD = {  # kind: (original canvas id, channel id, channel name, title)
    "loan": ("F0BH6BJ0PK7", "C0B08RS2BMK", "loan-review", ":clipboard: Loan & Layaway Review — Current"),
    "layaway": ("F0BJ48BMZGQ", "C04N24STDP1", "layaway-review", ":clipboard: Layaway Review — Current"),
    "employee": ("F0BH9UK284S", "C0ATTLPQHR8", "employee-performance", ":clipboard: Employee Sales Rankings — Current"),
    "aged": ("F0BHDL6AULU", "C04NGH4FF35", "aged-inventory-review", ":clipboard: Aged Inventory Review — Current"),
    "store": ("F0BH6S9U5FX", "C03CGTN3KN1", "store-performance", ":clipboard: Store Performance Rankings — Current"),
}
PLACEHOLDER = "*Refreshing — this week's numbers are being written now.*"


def load():
    try:
        return json.load(open(IDS))
    except (OSError, ValueError):
        return {"canvases": {}}


def save(d):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = IDS + ".tmp"
    json.dump(d, open(tmp, "w"), indent=1, ensure_ascii=False)
    os.replace(tmp, IDS)


def summary(cid):
    f = vp_slack.call("files.info", params={"file": cid}).get("file") or {}
    return {"creator": f.get("canvas_creator_id") or f.get("user"), "title": f.get("title"),
            "channels": f.get("channels"), "access": f.get("access"), "editors": f.get("editors"),
            "shares": {ch: [s.get("access") for s in v] for ch, v in ((f.get("shares") or {}).get("public") or {}).items()},
            "users": f.get("dm_mpdm_users_with_file_access")}


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    at = vp_slack.call("auth.test")
    bot = at.get("user_id")
    d = load()
    d.setdefault("canvases", {})
    if cmd == "status":
        for k, v in d["canvases"].items():
            print(k, v.get("id"), json.dumps(summary(v["id"]), ensure_ascii=False))
        return 0
    if cmd != "create":
        sys.exit(__doc__)
    rc = 0
    for kind, (old, ch, chname, title) in OLD.items():
        cur = d["canvases"].get(kind) or {}
        if cur.get("id") and summary(cur["id"]).get("creator") == bot:
            print(kind, "already has bot-owned canvas", cur["id"])
            continue
        r = vp_slack.call("canvases.create", {"title": title, "channel_id": ch,
                                              "document_content": {"type": "markdown", "markdown": PLACEHOLDER}})
        how = "channel_id"
        if not r.get("ok"):
            print(kind, "create with channel_id failed:", r.get("error"), r.get("detail") or "")
            r = vp_slack.call("canvases.create", {"title": title,
                                                  "document_content": {"type": "markdown", "markdown": PLACEHOLDER}})
            how = "standalone+share"
        if not r.get("ok"):
            print(kind, "CREATE FAILED:", r.get("error"), r.get("detail") or "")
            rc = 1
            continue
        cid = r["canvas_id"]
        a1 = vp_slack.call("canvases.access.set", {"canvas_id": cid, "access_level": "read", "channel_ids": [ch]})
        a2 = vp_slack.call("canvases.access.set", {"canvas_id": cid, "access_level": "write", "user_ids": [vp_slack.JOSHUA]})
        s = summary(cid)
        print(kind, "created", cid, "via", how, "| channel read:", a1.get("ok") or a1.get("error"),
              "| Joshua write:", a2.get("ok") or a2.get("error"), "|", json.dumps(s, ensure_ascii=False))
        d["canvases"][kind] = {"id": cid, "channel": ch, "channel_name": chname, "former_id": old, "created_via": how,
                               "created": __import__("datetime").datetime.now().isoformat(timespec="seconds")}
        save(d)
        if kind == "layaway":
            src, dst = os.path.join(STATE_DIR, old + ".json"), os.path.join(STATE_DIR, cid + ".json")
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
                print("layaway state copied", src, "->", dst)
    d["_note"] = ("2026-10-14: bot-owned replacements for the Joshua-owned originals (bot had read-only -> "
                  "canvases.edit restricted_action). weekly_canvases.py / layaway_yield_weekly.py use these ids.")
    save(d)
    print("exit=%d" % rc)
    return rc


if __name__ == "__main__":
    sys.exit(main())
