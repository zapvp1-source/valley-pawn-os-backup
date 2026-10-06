#!/usr/bin/env python3
"""comedy_weekly.py [--render] [--week YYYY-MM-DD] — native vp-comedy-reel-weekly (Wed 17:00, 2026-10-05).

Fills the week's humor slot that social_weekly.py planned (deferred), using the existing engine
Refine Social Media/vp_comedy_reel.py (beat-timed deadpan cards, works muted, guardrails in code):
  1 Claude writes ONE bit about a REAL item from this week's Deal of the Week (its photo is the backdrop) —
    punches at the object, never at a customer, money trouble, or firearms; no invented numbers
  2 vp_comedy_reel.check_script must pass (one rewrite allowed) -> render -> reels/comedy_<week>_1.mp4
  3 captions for the slot's accounts via the slot contract + engine qa_caption
  4 `python3 -m vp_social publish <plan> --live` — idempotent, so only the new slot goes out
Skips silently if there is no plan, no deal photo, or the guardrail blocks twice."""
import datetime as dt
import json
import os
import subprocess
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_ai  # noqa: E402
import social_weekly as sw  # noqa: E402

ET = ZoneInfo("America/New_York")
RSM = sw.RSM
sys.path.insert(0, RSM)
import vp_comedy_reel as vcr  # noqa: E402

BIT_SYS = sw.VOICE + (" You write deadpan short-form video bits: 4-6 beats, each under 70 characters, the last one the "
                      "punchline. Funny about the OBJECT itself (its personality, its patience, what it has seen). Never mock a "
                      "customer, never joke about needing money or hard times, never firearms, never invented numbers or specs.")


def main():
    render = "--render" in sys.argv
    now = dt.datetime.now(ET)
    monday = dt.date.fromisoformat(sys.argv[sys.argv.index("--week") + 1]) if "--week" in sys.argv else now.date() - dt.timedelta(days=now.weekday())
    week = monday.isoformat()
    ppath = os.path.join(RSM, "state", "plans", "plan_%s.json" % week)
    if not os.path.exists(ppath):
        print("no plan for", week); return 0
    plan = json.load(open(ppath))
    slot = next((s for s in plan["slots"] if s["lane"] == "humor"), None)
    if not slot:
        print("no humor slot this week"); return 0
    if any(slot["captions"].values()) and os.path.exists(slot["media_path"]):
        print("humor slot already filled"); return 0
    deals = json.load(open(os.path.join(RSM, "state", "deals_%s.json" % week))) if os.path.exists(os.path.join(RSM, "state", "deals_%s.json" % week)) else []
    deals = [d for d in deals if os.path.exists(d.get("photo", ""))]
    if not deals:
        print("no deal photo to build a bit on"); return 0
    d = deals[now.isocalendar()[1] % len(deals)]
    prompt = ("Write one bit about this real item, which is for sale at our %s store: %s ($%s). Manager's note: %s\n"
              "Return ONLY JSON: {\"title\": str, \"beats\": [{\"text\": str, \"hold\": seconds 1.8-3.0, \"punch\": bool}]}"
              % (d["store"], d["product"], d["price"], d.get("hook", "")))
    spec = None
    for attempt in range(2):
        b = vp_ai.ask_json(prompt, BIT_SYS, max_tokens=1200)
        ok, probs = vcr.check_script(b.get("beats", []), b.get("title", ""))
        if ok:
            spec = b; break
        prompt += "\nThe last draft was blocked for: %s. Write a different bit." % "; ".join(probs)
    if not spec:
        print("guardrail blocked twice — no comedy reel this week"); return 0
    spec.update({"id": "comedy_%s_1" % week.replace("-", "_"), "image": d["photo"], "voice": False, "endcard_store": d["store"]})
    print("bit:", spec["title"], "|", " / ".join(x["text"] for x in spec["beats"]))
    if render:
        return 0
    ok, msg, out = vcr.render_comedy(spec, Path(RSM, "reels"))
    if not ok or not out:
        print("render failed:", msg); return 1
    os.replace(str(out), slot["media_path"])
    slot["contract"] = dict(slot["contract"], bit=spec, item=d["product"], store=d["store"])
    slot.pop("deferred", None)
    caps = sw.write_captions(slot, "")
    for a, c in caps.items():
        slot["captions"][a] = c if c and not sw.vps_publish.qa_caption(c, a, "video", sw.min_words(a)) else None
    json.dump(plan, open(ppath, "w"), indent=1)
    # publish ONLY the humor slot (10/5: a whole-plan re-publish re-sent 16 community slots the ledger hadn't
    # recorded yet — Publer showed no duplicates, but never rely on that)
    one = dict(plan, plan_id=plan["plan_id"] + "-humor", slots=[slot])
    opath = ppath.replace(".json", "-humor.json")
    json.dump(one, open(opath, "w"), indent=1)
    rc, o, e = sw.run([sw.PY, "-m", "vp_social", "publish", opath, "--live"], timeout=1800)
    print(o[-1500:], e[-400:])
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
