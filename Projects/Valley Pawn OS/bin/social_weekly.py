#!/usr/bin/env python3
"""social_weekly.py [--render] [--week YYYY-MM-DD] — native weekly social batch (2026-10-05).

Native replacement for the Cowork task `vp-content-batch-weekly` (+ the deals-social and deal-reel lanes),
dark since ~9/23 because every step went through the Mac connector. It drives the EXISTING engine in
Refine Social Media/vp_social (planner, caption QA, Publer publisher, ledger de-dupe) — nothing re-invented:
  1 deals: this Monday's #deal-of-the-week submissions (same reader/extractor as deal_of_week_pick.py),
    manager's REAL photo saved to deal_of_week_uploads/, written as state/deals_<week>.json
  2 reels: vp_deal_reel.py per store + vp_deal_compilation.py, copied to the names the planner expects
  3 plan: `python3 -m vp_social plan --week <monday> --deals ...` (fills each account only to its weekly target,
    counting what is already scheduled — so re-runs and other lanes never stack)
  4 captions: Claude writes each slot from the slot's own contract (facts from the submission only,
    channel rules, hard rules), then the engine's qa_caption checks it; one rewrite on failure, else left empty
    (the publisher skips empty captions — nothing half-baked ships)
  5 publish: `python3 -m vp_social publish <plan> --live` (the engine's only writer; Publer API)
  6 DM Joshua a plain summary.
Brand slots get a Brand hero from the asset library when one exists, else post as text. Engagement and
humor slots are left for their own lanes (empty caption = skipped).
"""
import datetime as dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_ai  # noqa: E402
import vp_slack  # noqa: E402
import deal_of_week_pick as dow  # noqa: E402

AGENT = "vp-content-batch-weekly"
ET = ZoneInfo("America/New_York")
RSM = os.path.expanduser("~/Documents/Claude/Projects/Refine Social Media")
HEROES = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn Studios/asset-library/heroes")
LEDGER = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS/fleet/FAILURE_LEDGER.md")
JOSHUA = "U03BB52MDSA"
PY = "/usr/bin/python3"
ENV = dict(os.environ, PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin")
CODE = {"Culpeper": "CUL", "Waynesboro": "WAY", "Harrisonburg": "HAR", "Lexington": "LEX", "Roanoke": "ROA"}

sys.path.insert(0, RSM)
from vp_social import publish as vps_publish  # noqa: E402
from vp_social import config as vps_config  # noqa: E402
from vp_social import plan as vps_plan  # noqa: E402

VOICE = ("You write social posts for Valley Pawn, a family-owned pawn shop with five stores in Virginia (since 2014; "
         "motto 'What's Right Is Right'). Write like the store's own manager posted it: plain talk, contractions, short "
         "sentences, warm and specific. Never: 'hidden gem', 'nestled', 'look no further', 'elevate', rhetorical-question "
         "openers, poetic flourish, invented specs, invented retail comparisons or savings percentages, firearms/guns/ammo, "
         "'Dixie Pawn', 'Full Circle Finance', 'fast cash', 'instant cash', 'no credit check'. Every sold item carries a "
         "30-day warranty. Use ONLY facts given to you.")


def ledger(sentence):
    with open(LEDGER, "a") as fh:
        fh.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence))


def run(cmd, cwd=RSM, timeout=1800):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=ENV)
    return p.returncode, p.stdout, p.stderr


def build_deals(monday, render):
    _, msgs = dow.submissions(monday)
    if not msgs:
        return []
    found = {}
    for d in dow.extract(msgs):
        m = d["msg"]
        imgs = [f for f in (m.get("files") or []) if (f.get("mimetype") or "").startswith("image/")]
        if d["store"] and d["price"] and imgs:
            found[d["store"]] = (d, imgs[0])
    out = []
    os.makedirs(os.path.join(RSM, "deal_of_week_uploads"), exist_ok=True)
    for store in dow.ORDER:
        if store not in found:
            continue
        d, f = found[store]
        slug = re.sub(r"[^a-z0-9]", "", d["item"].lower())[:24] or "deal"
        dst = os.path.join(RSM, "deal_of_week_uploads", "%s_%s_%s.jpg" % (monday.strftime("%Y%m%d"), CODE[store], slug))
        if not render and not os.path.exists(dst):
            src = dst + ".src"
            req = urllib.request.Request(f["url_private_download"], headers={"Authorization": "Bearer " + vp_slack.token()})
            open(src, "wb").write(urllib.request.urlopen(req, timeout=60).read())
            subprocess.run(["sips", "-Z", "1600", "-s", "format", "jpeg", src, "--out", dst], capture_output=True, timeout=60)
            os.remove(src)
        out.append({"store": store, "photo": dst, "product": d["item"], "price": d["price"], "hook": d["pitch"],
                    "address": vps_config.STORE_FACTS[store].get("address")})
    return out


def render_reels(deals, week):
    spec = os.path.join(RSM, "state", "reels_spec_%s.json" % week)
    json.dump(deals, open(spec, "w"), indent=1)
    rc, out, err = run([PY, "vp_deal_reel.py", "--spec", spec, "--outdir", os.path.join(RSM, "reels")])
    today = dt.date.today().strftime("%Y%m%d")
    made = 0
    for d in deals:
        c = sorted(glob.glob(os.path.join(RSM, "reels", "%s_%s_dealreel_*.mp4" % (today, CODE[d["store"]]))))
        if c:
            shutil.copy2(c[-1], os.path.join(RSM, "reels", "deal_%s_%s.mp4" % (d["store"].lower(), week)))
            made += 1
    if made >= 3:
        run([PY, "vp_deal_compilation.py"])
        c = sorted(glob.glob(os.path.join(RSM, "reels", "publish", "%s_BRAND_dealreel_weekcompilation.mp4" % today)))
        if c:
            shutil.copy2(c[-1], os.path.join(RSM, "reels", "deal_compilation_%s.mp4" % week))
    return made


def brand_hero(used):
    c = [p for p in glob.glob(os.path.join(HEROES, "*", "*BRAND*")) if p.lower().endswith((".png", ".jpg", ".jpeg"))
         and "firearm" not in p.lower() and p not in used]
    return sorted(c)[-1] if c else None


def write_captions(slot, kb):
    rules = slot["contract"].get("channel_rules") or {a: vps_plan._rules_for(a) for a in slot["accounts"]}
    extra = ("\n\nCOMMUNITY KNOWLEDGE BASE (use one real, named place/event from it):\n" + kb) if slot["lane"] == "community" else ""
    prompt = ("Write one caption per account for this scheduled post. Accounts: %s.\nSlot contract (facts + rules): %s\n"
              "Channel rules per account: %s\nScheduled for: %s.%s\n\nReturn ONLY a JSON object {account_key: caption}."
              % (", ".join(slot["accounts"]), json.dumps(slot["contract"]), json.dumps(rules), slot["scheduled_at"], extra))
    caps = vp_ai.ask_json(prompt, VOICE, max_tokens=2500)
    return {a: (caps.get(a) or "").strip() for a in slot["accounts"]}


ENG_SYS = VOICE + (" You write ENGAGEMENT posts whose whole job is to get a reply: every caption ends on one genuine, easy "
                   "question. No store-visit CTA. Real items only — never invent an item, a price, or a fact.")


def eng_card(path, kicker, headline, sub):
    """Same look as engagement_lane/make_cards.py (navy field, gold frame, Playfair headline, logo)."""
    from PIL import Image, ImageDraw, ImageFont
    NAVY, GOLD, IVORY = (0x0F, 0x1A, 0x2E), (0xB0, 0x8A, 0x3E), (0xF4, 0xED, 0xE0)
    S, margin = 1080, 110
    img = Image.new("RGB", (S, S), NAVY); d = ImageDraw.Draw(img)
    d.rectangle([46, 46, S - 46, S - 46], outline=GOLD, width=2)
    fk, fh, fs = (ImageFont.truetype(os.path.join(RSM, "fonts", f), n) for f, n in (("Inter.ttf", 30), ("PlayfairDisplay.ttf", 78), ("Inter.ttf", 34)))
    def wrap(t, f):
        out, cur = [], ""
        for w in t.split():
            x = (cur + " " + w).strip()
            if d.textlength(x, font=f) <= S - 2 * margin: cur = x
            else: out.append(cur); cur = w
        return out + ([cur] if cur else [])
    hl, sl = wrap(headline, fh)[:4], wrap(sub, fs)[:4]
    y = (S - (84 + len(hl) * 96 + 30 + len(sl) * 50)) // 2 - 30
    d.text((margin, y), kicker.upper(), font=fk, fill=GOLD); y += 44
    d.line([margin, y + 14, margin + 90, y + 14], fill=GOLD, width=3); y += 40
    for ln in hl: d.text((margin, y), ln, font=fh, fill=IVORY); y += 96
    y += 30
    for ln in sl: d.text((margin, y), ln, font=fs, fill=(0xC9, 0xC2, 0xB6)); y += 50
    logo = os.path.join(RSM, "brand_assets", "valley_pawn_landscape_transparent.png")
    if os.path.exists(logo):
        lg = Image.open(logo).convert("RGBA"); lw = 300
        lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
        img.paste(lg, ((S - lw) // 2, S - 86 - lg.height), lg)
    img.save(path, "PNG")
    return path


def fill_engagement(slot, deals, week):
    """Formats that need a hidden answer (guess-the-price, what-is-this) are turned into an answerable question
    about real items so no promise to the audience is ever left open; the reveal slot is never needed."""
    items = [{"store": d["store"], "item": d["product"]} for d in deals]
    prompt = ("Engagement post. Format from the planner: %s. Accounts: %s. Channel rules: %s.\n"
              "Real items in stores this week (you may reference them by name, NOT their price): %s\n"
              "If the format needs a hidden answer revealed later (guess the price, what is this, answer tomorrow), "
              "instead write a 'This or That' between two of those real items, or a straight 'What should we stock more of?' poll.\n"
              "Return ONLY JSON: {\"kicker\": 2-3 words, \"headline\": the question (max 60 chars), \"sub\": one line (max 110 chars), "
              "\"captions\": {account_key: caption}}" % (json.dumps(slot["contract"].get("format")), ", ".join(slot["accounts"]),
              json.dumps({a: vps_plan._rules_for(a) for a in slot["accounts"]}), json.dumps(items)))
    j = vp_ai.ask_json(prompt, ENG_SYS, max_tokens=1800)
    out = os.path.join(RSM, "engagement_lane", week); os.makedirs(out, exist_ok=True)
    slot["media_path"] = eng_card(os.path.join(out, "%s.png" % slot["slot_id"]), j["kicker"], j["headline"], j["sub"])
    slot["kind"] = "photo"
    for a in slot["accounts"]:
        c = (j.get("captions") or {}).get(a, "").strip()
        slot["captions"][a] = c if c and "?" in c and not vps_publish.qa_caption(c, a, "photo", min(20, min_words(a))) else None


def min_words(acct):
    r = vps_config.RULES
    if acct == "BrandTikTok":
        return 6
    return r["min_words_brand"] if acct.startswith("Brand") and acct != "BrandTwitter" else (12 if acct == "BrandTwitter" else r["min_words_store"])


def main():
    render = "--render" in sys.argv
    now = dt.datetime.now(ET)
    monday = dt.date.fromisoformat(sys.argv[sys.argv.index("--week") + 1]) if "--week" in sys.argv else now.date() - dt.timedelta(days=now.weekday())
    week = monday.isoformat()

    deals = build_deals(monday, render)
    dpath = os.path.join(RSM, "state", "deals_%s.json" % week)
    json.dump(deals, open(dpath, "w"), indent=1)
    print("deals:", ", ".join("%s %s $%s" % (d["store"], d["product"], d["price"]) for d in deals) or "none")
    reels = 0 if render or not deals else render_reels(deals, week)
    print("reels:", reels)

    rc, out, err = run([PY, "-m", "vp_social", "sync", "--back", "7", "--forward", "14"])
    rc, out, err = run([PY, "-m", "vp_social", "plan", "--week", week, "--deals", dpath])
    if rc != 0:
        ledger("Weekly social plan for %s could not be built." % week)
        print(out, err[-1500:])
        return 1
    ppath = os.path.join(RSM, "state", "plans", "plan_%s.json" % week)
    plan = json.load(open(ppath))
    kb = open(os.path.join(RSM, "CITY_COMMUNITY_KB.md"), errors="replace").read()
    used, filled, empty = set(), 0, 0
    for s in plan["slots"]:
        if s["lane"] == "engagement" and not s.get("deferred"):
            if dt.datetime.fromisoformat(s["scheduled_at"]) >= now + dt.timedelta(minutes=30):
                try:
                    fill_engagement(s, deals, week)
                    filled += sum(1 for c in s["captions"].values() if c)
                except Exception as e:
                    print("engagement failed", s["slot_id"], e)
            continue
        if s.get("deferred") or s["lane"] in ("reveal", "humor"):
            continue
        if dt.datetime.fromisoformat(s["scheduled_at"]) < now + dt.timedelta(minutes=30):
            continue                     # slot time already passed (late run) — never post a stale slot
        if s["kind"] == "video" and not os.path.exists(s.get("media_path") or ""):
            continue
        if s["lane"] == "brand" and not s.get("media_path"):
            h = brand_hero(used)
            if h:
                s["media_path"] = h; used.add(h)
            else:
                s["kind"] = "status"
        try:
            caps = write_captions(s, kb)
        except Exception as e:
            print("caption failed", s["slot_id"], e)
            continue
        for a, cap in caps.items():
            probs = vps_publish.qa_caption(cap, a, s["kind"], min_words(a))
            if probs:
                try:
                    cap = write_captions(dict(s, contract=dict(s["contract"], fix_these=probs, previous=cap)), kb).get(a, "")
                except Exception:
                    cap = ""
                if vps_publish.qa_caption(cap, a, s["kind"], min_words(a)):
                    cap = ""
            s["captions"][a] = cap or None
            filled += bool(cap); empty += not cap
    json.dump(plan, open(ppath, "w"), indent=1)
    print("captions filled %d, left empty %d" % (filled, empty))
    if render:
        for s in plan["slots"]:
            for a, c in s["captions"].items():
                if c:
                    print("--- %s %s %s\n%s" % (s["scheduled_at"][:16], s["slot_id"], a, c))
        return 0
    rc, out, err = run([PY, "-m", "vp_social", "publish", ppath, "--live"], timeout=3600)
    print(out[-3000:], err[-800:])
    res = {}
    try:
        res = json.load(open(ppath.replace(".json", "_results.json")))
    except Exception:
        pass
    n = res.get("scheduled", 0)
    if not n:
        ledger("Weekly social batch for %s scheduled nothing." % week)
        return 1
    os.environ["VP_TASK"] = AGENT
    vp_slack.post(JOSHUA, "Social for the week of %s is scheduled: %d posts across the store pages, Google profiles and brand accounts.\n"
                          "Deals: %s.\nReels: %d.\nCalendar: https://app.publer.com" % (monday.strftime("%b %-d"), n,
                          ", ".join("%s (%s)" % (d["product"], d["store"]) for d in deals) or "none this week", reels))
    return 0


if __name__ == "__main__":
    sys.exit(main())
