"""
Weekly planner. Produces ONE plan JSON for the week with every slot the engine will
publish, de-conflicted against the ledger, with a creative contract per slot for the
model to fill captions into. Nothing here talks to Publer directly (ledger only).

"Fill to target": for every account the planner first counts what is already scheduled
in the ledger for that week (legacy lanes still running, hand posts, anything) and only
adds slots up to the per-account cadence target. That is what makes the parallel-run
period safe and what stops three lanes stacking the same deal on one page.

Usage
  python3 -m vp_social plan --week 2026-09-07 --deals state/deals_2026-09-07.json
  -> state/plans/plan_2026-09-07.json  (captions null, contracts filled)
"""
from __future__ import annotations
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from creative_drift import DriftEngine, season_for  # noqa: E402
from . import config, ledger

# per-account weekly cadence targets (placements/week)
TARGETS = {"Brand": 7, "BrandIG": 10, "BrandTwitter": 3, "BrandTikTok": 3,
           **{s: 7 for s in config.STORES}, **{f"GBP_{s}": 7 for s in config.STORES}}

STORE_DAY = {"Culpeper": 1, "Waynesboro": 2, "Harrisonburg": 3, "Lexington": 4, "Roanoke": 5}  # Tue..Sat
DEAL_PHOTO_TIMES = {"Culpeper": "10:00", "Waynesboro": "11:30", "Harrisonburg": "13:00",
                    "Lexington": "14:30", "Roanoke": "15:30"}
COMMUNITY_TIMES = ["08:30", "12:15", "17:45", "10:45"]
BRAND_PILLARS = [("how_it_works", "How pawn loans / buying / layaway actually work at Valley Pawn — plain, honest, one concrete detail"),
                 ("value_warranty", "A real value angle: 30-day warranty, price vs new, or a category we buy — one concrete number"),
                 ("story_team", "A people or heritage story — a real employee (name + tenure), a store, family-owned since 2014")]

CHANNEL_RULES = {
    "fb": "Facebook Page: 2-5 sentences, no hashtags, warm and specific, end with a soft invitation.",
    "gbp": "Google Business Profile: informational tone, NO hashtags, NO phone numbers, NO all-caps, max 2 emojis, "
           "150-400 chars, must differ from the Facebook caption, no text overlay expected on image.",
    "ig": "Instagram: 3+ sentences, 5-8 niche hashtags plus #ValleyPawn #WhatsRightIsRight #TheValleyPawn, "
          "may use 1-2 emojis, five-store footer required for Brand posts.",
    "x": "X: under 260 characters total, one line, no hashtags beyond #ValleyPawn.",
    "tiktok": "TikTok: 1-2 short lines, 3-5 hashtags, casual.",
}
HARD_RULES = ("Never mention firearms/guns/ammo. Never 'Dixie Pawn'. Never 'Full Circle Finance'. "
              "Never 'fast cash'/'instant cash'/'no credit check'. Hours: Culpeper Mon-Sat 10-6; all others "
              "Mon/Tue/Thu/Fri/Sat 10-6, closed Wed & Sun; nobody closes at 5. Every caption needs one concrete real "
              "detail (price + item, real employee + tenure, named landmark, dated fact). Community posts: no Valley Pawn "
              "CTA, no product, no price. Humor never mocks customers or money troubles.")


def _week_monday(week: str) -> dt.date:
    d = dt.date.fromisoformat(week)
    return d - dt.timedelta(days=d.weekday())


def _at(monday: dt.date, day_offset: int, hhmm: str) -> str:
    h, m = map(int, hhmm.split(":"))
    return dt.datetime.combine(monday + dt.timedelta(days=day_offset), dt.time(h, m), tzinfo=config.TZ).isoformat()


def _rules_for(acct: str) -> str:
    if acct.startswith("GBP_"):
        return CHANNEL_RULES["gbp"]
    if acct == "BrandIG":
        return CHANNEL_RULES["ig"]
    if acct == "BrandTwitter":
        return CHANNEL_RULES["x"]
    if acct == "BrandTikTok":
        return CHANNEL_RULES["tiktok"]
    return CHANNEL_RULES["fb"]


def _slot(slot_id, lane, item_key, accounts, kind, at, week, media_path=None, contract=None, **extra) -> dict:
    s = {"slot_id": slot_id, "lane": lane, "item_key": item_key, "accounts": accounts, "kind": kind,
         "scheduled_at": at, "week": week, "media_path": media_path,
         "captions": {a: None for a in accounts},
         "contract": dict(contract or {}, channel_rules={a: _rules_for(a) for a in accounts}, hard_rules=HARD_RULES)}
    s.update(extra)
    return s


def existing_counts(monday: dt.date) -> Counter:
    rows = ledger.posts_between(monday.isoformat(), (monday + dt.timedelta(days=6)).isoformat())
    return Counter(r["account_key"] for r in rows)


def build(week: str, deals_path: Path | None, seed: int | None = None) -> dict:
    monday = _week_monday(week)
    week = monday.isoformat()
    plan_id = f"plan_{week}"
    have = existing_counts(monday)
    remaining = {k: max(0, TARGETS[k] - have.get(k, 0)) for k in TARGETS}
    season = season_for(monday)
    slots: list[dict] = []
    notes: list[str] = []

    def take(acct: str) -> bool:
        if remaining.get(acct, 0) > 0:
            remaining[acct] -= 1
            return True
        return False

    def accounts_ok(accts: list[str]) -> list[str]:
        return [a for a in accts if take(a)]

    # ---- Deal of the Week: 1 photo (Thu, FB+GBP) + 1 video (store day, FB + BrandIG) per store ----
    deals = json.loads(Path(deals_path).read_text()) if deals_path and Path(deals_path).exists() else []
    if not deals:
        notes.append("no deals file — deal lanes skipped")
    for d in deals:
        store = d["store"]
        if store not in config.STORES:
            notes.append(f"unknown store in deals: {store}")
            continue
        slug = "".join(ch for ch in d["product"].lower() if ch.isalnum())[:24]
        item_key = f"deal:{week}:{store}:{slug}"
        base = {"store": store, "store_facts": config.STORE_FACTS[store], "product": d["product"],
                "price": d.get("price"), "retail": d.get("retail"), "hook": d.get("hook"), "pillar": "deal",
                "min_words": {"fb": 25, "gbp": 20}}
        accts = accounts_ok([store, f"GBP_{store}"])
        if accts:
            slots.append(_slot(f"deal-photo-{store}", "deal_photo", item_key, accts, "photo",
                               _at(monday, 3, DEAL_PHOTO_TIMES[store]), week, media_path=d.get("photo"), contract=base))
        video = d.get("video") or str(config.REELS_DIR / f"deal_{store.lower()}_{week}.mp4")
        accts = accounts_ok([store, "BrandIG"])
        if accts:
            slots.append(_slot(f"deal-video-{store}", "deal_video", item_key, accts, "video",
                               _at(monday, STORE_DAY[store], "10:30"), week, media_path=video,
                               contract=dict(base, note="15-30s vertical reel of the actual item; caption must name item + price")))
    if len(deals) >= 3:
        accts = accounts_ok(["Brand", "BrandIG", "BrandTikTok"])
        if accts:
            slots.append(_slot("deal-compilation", "deal_video", f"deal:{week}:compilation", accts, "video",
                               _at(monday, 5, "16:00"), week, media_path=str(config.REELS_DIR / f"deal_compilation_{week}.mp4"),
                               contract={"pillar": "deal", "deals": [{"store": x["store"], "product": x["product"], "price": x.get("price")} for x in deals],
                                         "note": "compilation of this week's five deals; Brand caption lists all five with prices",
                                         "min_words": {"fb": 40, "ig": 40, "tiktok": 8}}))

    # ---- Brand pillars: Mon/Wed/Fri 6 PM -> Brand + IG + X ----
    for i, (pid, brief) in enumerate(BRAND_PILLARS):
        accts = accounts_ok(["Brand", "BrandIG", "BrandTwitter"])
        if accts:
            slots.append(_slot(f"brand-{pid}", "brand", f"brand:{week}:{pid}", accts, "photo",
                               _at(monday, [0, 2, 4][i], "18:00"), week, media_path=None,
                               contract={"pillar": pid, "brief": brief, "season": season,
                                         "media_contract": "pick one hero from Valley Pawn Studios/asset-library/heroes not used in 30 days "
                                                           "matching the pillar; set media_path; never a firearm; never a named make/model without a real photo",
                                         "footer": config.FIVE_STORE_FOOTER, "min_words": {"fb": 40, "ig": 40, "x": 12}}))

    # ---- Community (Lane C): fill each store FB + GBP to target with drift picks ----
    engine = DriftEngine()
    for store in config.STORES:
        need = min(4, max(remaining.get(store, 0), remaining.get(f"GBP_{store}", 0)))
        if need <= 0:
            continue
        picks = engine.select("community", need, account=store, today=monday, seed=seed)
        if len(picks) < need:
            notes.append(f"community: only {len(picks)}/{need} eligible formats for {store} (cooldowns) — top up creative_state")
        for j, f in enumerate(picks):
            accts = accounts_ok([store, f"GBP_{store}"])
            if not accts:
                break
            day = [0, 2, 4, 6][j % 4] if store != "Culpeper" else [0, 2, 4, 6][j % 4]
            slots.append(_slot(f"community-{store}-{j+1}", "community", f"{f.id}:{store}:{week}", accts, "status",
                               _at(monday, day, COMMUNITY_TIMES[j % 4]), week, media_path=None, format_id=f.id,
                               contract={"store": store, "store_facts": config.STORE_FACTS[store], "pillar": "community",
                                         "format": {"id": f.id, "title": f.title, "template": f.template, "hook_key": f.hook_key},
                                         "kb": str(config.COMMUNITY_KB), "season": season,
                                         "rule": "text only; real named place/event from CITY_COMMUNITY_KB with its [C26]/[PATTERN] tag; "
                                                 "no CTA, no product, no price; FB and GBP captions must differ", "min_words": {"fb": 30, "gbp": 25}}))

    # ---- Engagement (Lane D): 2 brand + 1 rotating store; reveal for any guess format ----
    picks = engine.select("engagement", 3, account="Brand", today=monday, seed=seed)
    rot_store = config.STORES[(monday.isocalendar()[1]) % len(config.STORES)]
    for j, f in enumerate(picks):
        if j < 2:
            accts = accounts_ok(["Brand", "BrandIG", "BrandTwitter"])
            day, tm = [1, 3][j], "17:30"
        else:
            accts = accounts_ok([rot_store])
            day, tm = 2, "17:45"
        if not accts:
            continue
        sid = f"engagement-{j+1}"
        slots.append(_slot(sid, "engagement", f"{f.id}:{week}:{j}", accts, "photo",
                           _at(monday, day, tm), week, media_path=None, format_id=f.id,
                           contract={"pillar": "engagement", "format": {"id": f.id, "title": f.title, "template": f.template},
                                     "media_contract": "a real deal photo from deal_of_week_uploads or an engagement card from engagement_lane/make_cards.py",
                                     "min_words": {"fb": 20, "ig": 20, "x": 8}}))
        if "guess" in f.id or "answer" in f.id:
            slots.append(_slot(f"{sid}-reveal", "reveal", f"{f.id}:{week}:{j}:reveal", list(accts), "status",
                               _at(monday, day + 1, "18:00"), week, media_path=None, format_id=f.id,
                               contract={"pillar": "engagement", "note": "the promised answer/reveal for the previous day's post — must include the real number",
                                         "min_words": {"fb": 12, "ig": 12, "x": 6}}))

    # ---- Humor (Lane B3): exactly one comedy reel, produced midweek ----
    hp = engine.select("humor", 1, account="Brand", today=monday, seed=seed)
    if hp:
        f = hp[0]
        accts = accounts_ok(["Brand", "BrandIG", "BrandTikTok"])
        if accts:
            slots.append(_slot("humor-1", "humor", f"{f.id}:{week}", accts, "video",
                               _at(monday, 3, "18:30"), week, media_path=str(config.REELS_DIR / f"comedy_{week}_1.mp4"),
                               format_id=f.id, deferred=True,
                               contract={"pillar": "humor", "format": {"id": f.id, "title": f.title, "template": f.template},
                                         "note": "rendered by vp_comedy_reel.py in the midweek run; caption 1-2 lines", "min_words": {"fb": 8, "ig": 8, "tiktok": 4}}))

    plan = {"plan_id": plan_id, "week": week, "created_at": dt.datetime.now(config.TZ).isoformat(timespec="seconds"),
            "season": season, "existing_counts": dict(have), "remaining_after_plan": remaining, "notes": notes,
            "slots": slots}
    out = config.PLANS_DIR / f"{plan_id}.json"
    out.write_text(json.dumps(plan, indent=1))
    for s in slots:
        for a in s["accounts"]:
            ledger.upsert_planned(plan_id, s, a, "planned")
    return plan


def summary(plan: dict) -> str:
    c = Counter(s["lane"] for s in plan["slots"])
    placements = sum(len(s["accounts"]) for s in plan["slots"])
    lines = [f"{plan['plan_id']}: {len(plan['slots'])} slots / {placements} placements",
             "  " + " · ".join(f"{k} {v}" for k, v in c.items())]
    if plan["notes"]:
        lines += ["  notes: " + "; ".join(plan["notes"])]
    return "\n".join(lines)
