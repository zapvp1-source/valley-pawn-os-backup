#!/usr/bin/env python3
"""shop_refresh.py — native, Claude-free refresh of https://thevalleypawn.com/shop/ (WP page 833).

Replaces the per-run improvised method of the `vp-website-shop-nightly` Cowork task with ONE
deterministic pipeline (built 2026-09-05, Website Analytics plan Phase 1/2):

    fetch (5 eBay storefronts)  ->  gate  ->  generate_shop_block.py (unchanged)  ->  wrap
    ->  publish (App Password)  ->  verify (REST ground truth + live page, CDN-lag aware)
    ->  result.json + history.csv  ->  Slack #website (exact body, or left for the verifier task)

Rules honoured:
  * Rule 18 — never publish or post a short/partial list. A store that fails after retries
    reuses its last-good part if < 36 h old; otherwise the run WITHHOLDS (exit 2), posts nothing.
  * Rule 16 — nothing technical to Slack. On withhold: one plain DM to Joshua (if a token is
    available), detail to the log.
  * Same-slot guard — a second fire inside 3.5 h is a no-op (exit 0, "SKIP"), so double triggers
    and catch-up runs can never double-publish or double-post.
  * Additive — generate_shop_block.py, /retail/, page 1110 and the Bravo pipeline are untouched.

Usage:
    python3 shop_refresh.py            # normal run (respects same-slot guard)
    python3 shop_refresh.py --force    # ignore the slot guard
    python3 shop_refresh.py --dry-run  # fetch + build + gate, no publish, no post
    python3 shop_refresh.py --post-only  # (re)post the last result's Slack body if not yet posted

Exit codes: 0 ok/skip · 2 withheld (gate failed) · 3 publish/verify failed.
Outputs (Website/analytics/data/shop/):
    result.json   latest run (counts, verified, slack_body, posted)
    history.csv   one row per completed run
    parts/<Store>.json   last-good per-store fetch
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                      # Projects/Website
BUILD = ROOT / "shop-build"
DATA = ROOT / "analytics" / "data" / "shop"
LOGS = ROOT / "analytics" / "logs"
PARTS = DATA / "parts"
for d in (DATA, LOGS, PARTS):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(HERE))
from wp_client import WP  # noqa: E402

PAGE_ID = 833
CHANNEL_WEBSITE = "C0ASE9C0GQ0"
JOSHUA = "U03BB52MDSA"
STORES = [  # display name, eBay storefront slug
    ("Culpeper", "vpculpeper"),
    ("Waynesboro", "valleypawnwaynesboro"),
    ("Harrisonburg", "valleypawnharrisonburg"),
    ("Lexington", "valleypawnlexington"),
    ("Roanoke", "valleypawnroanoke"),
]
COLORS = {"Culpeper": "#0099DD", "Waynesboro": "#2D1A5E", "Harrisonburg": "#E07A5F",
          "Lexington": "#3DB8E8", "Roanoke": "#2A9D8F"}
# Identical to generate_shop_block.py — counts in Slack must equal what the generator kept.
BAN = re.compile(r"\b(gun|guns|rifle|pistol|handgun|firearm|ammo|ammun|magazine|tactical|holster|"
                 r"silencer|suppressor|scope|red dot|optic|bayonet|knife|blade|dagger|machete)\b", re.I)
SLOT_HOURS = 3.5
PART_MAX_AGE_H = 36
MIN_STORE_FRACTION = 0.5   # a store returning < 50% of its last-good count is treated as a bad fetch

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
TITLE_RE = re.compile(r'str-item-card__property-title[^>]*>.*?class=[\'"]?str-text-span[^>]*>([^<]*)<', re.S)
PRICE_RE = re.compile(r'str-item-card__property-displayPrice[^>]*>([^<]*)<')
ITEM_RE = re.compile(r'ebay\.com/itm/(\d+)')
IMG_RE = re.compile(r'imageId=([A-Za-z0-9~_-]+)')

LOG_FILE = LOGS / f"shop_refresh_{dt.date.today():%Y-%m-%d}.log"


def log(msg: str) -> None:
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}"
    print(line, flush=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------- fetch
def _opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def _get(opener, url: str) -> str:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-Dest": "document",
        "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1",
    })
    with opener.open(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def parse_articles(html: str) -> list[dict]:
    items = []
    for c in html.split("<article"):
        if "str-item-card" not in c:
            continue
        m_id, m_t, m_p, m_i = ITEM_RE.search(c), TITLE_RE.search(c), PRICE_RE.search(c), IMG_RE.search(c)
        if not (m_id and m_t and m_p):
            continue
        price = m_p.group(1).strip()
        if not re.match(r"^\$[\d,]+\.?\d*$", price):
            continue
        items.append({"id": m_id.group(1), "t": re.sub(r"\s+", " ", m_t.group(1)).strip(), "p": price,
                      "u": f"https://www.ebay.com/itm/{m_id.group(1)}",
                      "img": f"https://i.ebayimg.com/images/g/{m_i.group(1)}/s-l500.webp" if m_i else ""})
    return items


def fetch_store(name: str, slug: str) -> list[dict]:
    opener = _opener()
    seen, out = set(), []
    for pgn in range(1, 7):
        url = f"https://www.ebay.com/str/{slug}?_pgn={pgn}&_ipg=240&_tab=shop"
        parsed = []
        for attempt in range(1, 5):
            try:
                parsed = parse_articles(_get(opener, url))
            except Exception as e:  # network / 4xx / 5xx
                log(f"  {name} p{pgn} attempt {attempt}: {e}")
                parsed = []
            if parsed:
                break
            time.sleep(4 * attempt)
        new = [i for i in parsed if i["id"] not in seen]
        if not new:
            break
        for i in new:
            seen.add(i["id"])
            out.append(i)
        log(f"  {name} p{pgn}: +{len(new)} (total {len(out)})")
        if len(parsed) < 200:
            break
        time.sleep(2)
    return [{"t": i["t"], "p": i["p"], "u": i["u"], "img": i["img"], "s": name} for i in out]


def load_part(name: str) -> tuple[list[dict] | None, float]:
    p = PARTS / f"{name}.json"
    if not p.exists():
        return None, 1e9
    age_h = (time.time() - p.stat().st_mtime) / 3600
    try:
        return json.loads(p.read_text()), age_h
    except Exception:
        return None, 1e9


def gather() -> tuple[list[dict], dict, list[str]]:
    """Returns (items, per_store_scraped, reused_stores). Raises on an unrecoverable store."""
    items, scraped, reused = [], {}, []
    for name, slug in STORES:
        prev, prev_age = load_part(name)
        prev_n = len(prev) if prev else 0
        log(f"fetch {name} (last-good {prev_n}, {prev_age:.1f} h old)")
        got = fetch_store(name, slug)
        bad = (not got) or (prev_n and len(got) < prev_n * MIN_STORE_FRACTION)
        if bad:
            if prev and prev_age < PART_MAX_AGE_H:
                log(f"  {name}: fetch returned {len(got)} — reusing last-good part ({prev_n})")
                got, reused = prev, reused + [name]
            else:
                raise RuntimeError(f"{name}: fetch returned {len(got)} and no usable last-good part")
        else:
            (PARTS / f"{name}.json").write_text(json.dumps(got))
        scraped[name] = len(got)
        items.extend(got)
    return items, scraped, reused


# ---------------------------------------------------------------- build / publish / verify
def build_block(items: list[dict]) -> tuple[str, dict, int]:
    (BUILD / "items.json").write_text(json.dumps({"colors": COLORS, "items": items}))
    r = subprocess.run([sys.executable, "generate_shop_block.py"], cwd=BUILD, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"generate_shop_block.py failed: {r.stderr[-400:]}")
    block = (BUILD / "shop-block.html").read_text(encoding="utf-8")
    kept = [i for i in items if not BAN.search(i["t"])]
    counts = {n: sum(1 for i in kept if i["s"] == n) for n, _ in STORES}
    built = block.count('class="vp-card"')
    if built != len(kept):
        raise RuntimeError(f"generator kept {built} cards but filter expects {len(kept)}")
    if block.count("VP-SHOP-START") != 1 or block.count("VP-SHOP-END") != 1:
        raise RuntimeError("generator block does not carry exactly one marker pair")
    # Wrap with the Gutenberg comments ONLY — the generator already emits VP-SHOP markers (8/27 gotcha).
    wrapped = "<!-- wp:html -->\n" + block + "\n<!-- /wp:html -->"
    (BUILD / "shop-block-wrapped.html").write_text(wrapped, encoding="utf-8")
    return wrapped, counts, len(kept)


def page_checks(html: str, expected: int) -> dict:
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    itemlist = False
    for s in lds:
        try:
            j = json.loads(s)
            if isinstance(j, dict) and j.get("@type") == "ItemList":
                itemlist = True
        except Exception:
            pass
    return {
        "cards": html.count('class="vp-card"'),
        "cards_ok": html.count('class="vp-card"') == expected,
        "markers_ok": html.count("VP-SHOP-START") == 1 and html.count("VP-SHOP-END") == 1,
        "h1_ok": html.count('class="vp-h1"') == 1,
        "itemlist_ok": itemlist,
        "no_woo_hijack": "woocommerce-shop" not in html,
    }


def publish_and_verify(wp: WP, wrapped: str, expected: int) -> dict:
    j = wp.update_page(PAGE_ID, wrapped)
    log(f"published id={j.get('id')} status={j.get('status')} modified={j.get('modified_gmt')}")
    raw = wp.get_page_raw(PAGE_ID)
    rest = page_checks(raw, expected)
    if not (rest["cards_ok"] and rest["markers_ok"]):
        raise RuntimeError(f"REST readback mismatch: {rest}")
    ok, live_html = wp.wait_live("/shop/", lambda h: page_checks(h, expected)["cards_ok"], tries=9, delay=20)
    live = page_checks(live_html, expected) if live_html else {}
    log(f"live verify: {'OK' if ok else 'CDN still stale after 160 s (REST is ground truth)'} {live}")
    if live and not live["no_woo_hijack"]:
        raise RuntimeError("WooCommerce hijack detected on live /shop/ — check woocommerce_shop_page_id (must be 1110)")
    return {"rest": rest, "live": live, "live_matched": ok}


# ---------------------------------------------------------------- slack
def slack_token() -> str | None:
    try:
        sys.path.insert(0, "/Users/joshuadavis/Documents/Claude/Projects/Business Continuity")
        import common  # type: ignore
        t = common.get_slack_token()
        if t:
            return t
    except Exception:
        pass
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", "vp-ops-slack-bot-token", "-w"],
                           capture_output=True, text=True, timeout=10)
        t = r.stdout.strip()
        if t.startswith("xoxb-"):
            return t
    except Exception:
        pass
    return None


def slack_post(channel: str, text: str) -> str | None:
    tok = slack_token()
    if not tok:
        return None
    data = json.dumps({"channel": channel, "text": text, "mrkdwn": True}).encode()
    req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=data, method="POST",
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            j = json.loads(r.read().decode())
        return j.get("ts") if j.get("ok") else None
    except Exception as e:
        log(f"slack post error: {e}")
        return None


def slack_dm_joshua(text: str) -> None:
    tok = slack_token()
    if not tok:
        return
    try:
        data = json.dumps({"users": JOSHUA}).encode()
        req = urllib.request.Request("https://slack.com/api/conversations.open", data=data, method="POST",
                                     headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            ch = json.loads(r.read().decode()).get("channel", {}).get("id")
        if ch:
            slack_post(ch, text)
    except Exception:
        pass


def slack_body(counts: dict, total: int, excluded: int, scraped_total: int) -> str:
    """LOCKED FORMAT. The Cowork verifier task must post this string verbatim, never rewrite it."""
    per = " · ".join(f"{n}: {counts[n]}" for n, _ in STORES)
    return (":shopping_trolley: *Shop refreshed* — thevalleypawn.com/shop/\n"
            f"{per}\n"
            f"_Total live: {total}_ · excluded (weapons-adjacent): {excluded} of {scraped_total} scraped")


# ---------------------------------------------------------------- state
def load_state() -> dict:
    p = DATA / "state.json"
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def save_state(s: dict) -> None:
    (DATA / "state.json").write_text(json.dumps(s, indent=2))


def slot_id(now: dt.datetime) -> str:
    return f"{now:%Y-%m-%d}-{'AM' if now.hour < 12 else 'PM'}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--post-only", action="store_true")
    ap.add_argument("--no-post", action="store_true", help="publish + verify, but do not post to Slack (proving runs)")
    a = ap.parse_args()
    now = dt.datetime.now()
    state = load_state()
    result_path = DATA / "result.json"

    if a.post_only:
        try:
            res = json.loads(result_path.read_text())
        except Exception:
            log("post-only: no result.json")
            return 3
        if res.get("posted"):
            log("post-only: already posted")
            return 0
        ts = slack_post(CHANNEL_WEBSITE, res["slack_body"])
        res["posted"] = bool(ts); res["slack_ts"] = ts
        result_path.write_text(json.dumps(res, indent=2))
        log(f"post-only: {'posted' if ts else 'no token / failed'}")
        return 0 if ts else 3

    # same-slot guard
    last = state.get("last_success_epoch", 0)
    if not a.force and not a.dry_run and last and (time.time() - last) < SLOT_HOURS * 3600:
        log(f"SKIP — last success {(time.time() - last) / 60:.0f} min ago (< {SLOT_HOURS} h)")
        return 0

    # lock
    lock = DATA / ".lock"
    if lock.exists() and (time.time() - lock.stat().st_mtime) < 40 * 60:
        log("SKIP — another run holds the lock")
        return 0
    lock.write_text(str(os.getpid()))
    try:
        log(f"=== shop_refresh start ({slot_id(now)}){' DRY-RUN' if a.dry_run else ''}")
        try:
            items, scraped, reused = gather()
        except Exception as e:
            log(f"WITHHOLD — {e}")
            result_path.write_text(json.dumps({"ts": now.isoformat(), "status": "withheld", "reason": str(e),
                                               "posted": False}, indent=2))
            slack_dm_joshua(f"⚠️ Scheduled task \"vp-website-shop-nightly\" did not complete — {now:%b %-d, %Y}.")
            return 2
        scraped_total = sum(scraped.values())
        wrapped, counts, total = build_block(items)
        excluded = scraped_total - total
        body = slack_body(counts, total, excluded, scraped_total)
        log(f"built total={total} excluded={excluded} scraped={scraped} reused={reused}")
        if a.dry_run:
            print(body)
            return 0
        try:
            ver = publish_and_verify(WP(), wrapped, total)
        except Exception as e:
            log(f"PUBLISH/VERIFY FAILED — {e}")
            result_path.write_text(json.dumps({"ts": now.isoformat(), "status": "failed", "reason": str(e),
                                               "posted": False}, indent=2))
            slack_dm_joshua(f"⚠️ Scheduled task \"vp-website-shop-nightly\" did not complete — {now:%b %-d, %Y}.")
            return 3
        posted_ts = None
        if a.no_post:
            log("no-post: Slack suppressed for this proving run")
        elif state.get("last_posted_slot") != slot_id(now):
            posted_ts = slack_post(CHANNEL_WEBSITE, body)
        res = {"ts": now.isoformat(), "slot": slot_id(now), "status": "ok", "scraped": scraped,
               "scraped_total": scraped_total, "counts": counts, "total": total, "excluded": excluded,
               "reused_stores": reused, "verify": ver, "slack_body": body,
               "posted": bool(posted_ts) or a.no_post, "slack_ts": posted_ts,
               "posted_by": "suppressed(no-post)" if a.no_post else ("runner" if posted_ts else None)}
        result_path.write_text(json.dumps(res, indent=2))
        with (DATA / "history.csv").open("a", newline="") as f:
            w = csv.writer(f)
            if f.tell() == 0:
                w.writerow(["ts", "slot", "scraped", "excluded", "published", *[n for n, _ in STORES],
                            "live_matched", "posted", "reused"])
            w.writerow([now.isoformat(timespec="seconds"), slot_id(now), scraped_total, excluded, total,
                        *[counts[n] for n, _ in STORES], ver["live_matched"], bool(posted_ts), ";".join(reused)])
        state.update({"last_success_epoch": time.time(), "last_slot": slot_id(now)})
        if posted_ts:
            state["last_posted_slot"] = slot_id(now)
        save_state(state)
        log(f"DONE total={total} posted={'yes' if posted_ts else ('suppressed' if a.no_post else 'NO (verifier task will post)')}")
        return 0
    finally:
        try:
            lock.unlink()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
