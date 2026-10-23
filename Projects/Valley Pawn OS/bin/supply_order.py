#!/usr/bin/env python3
"""supply_order.py — native weekly Amazon Business supply order for the 5 Valley Pawn stores (2026-10-21).

WHY NATIVE: the old Cowork chain (daily-supply-order -> tuesday-supply-summary -> tuesday-supply-checkout) failed
because the model declined to charge the card on unattended runs, not because of the clicking (Joshua 10/21, and
the 9/9 CHANGELOG diagnosis). This script places the order itself under Joshua's rules (purchasing/supply_rules.json).

SUBCOMMANDS
  run [--dry-run] [--no-post]   Tue 09:00. Read new #supply-request posts -> resolve each Amazon link in the browser
                                -> apply rules -> ORDER the clean items per store (separate checkout per store:
                                Location tag, store ship-to, Amex 3001) -> reply in each request's thread + one DM to
                                Joshua. Held items: neutral "waiting on Joshua's OK" thread reply, reasons in Joshua's DM.
  approvals [--dry-run]         every 2 h Tue-Thu 11-17. Joshua replies "approve" (or "skip") in a held item's thread in
                                #supply-request -> approved items get ordered.
  watch                         Mon 07:30. Read the last 7 days of Amazon order history (everything bought on the account,
                                not just this pipeline) and DM Joshua spend by store + anything outside the rules.
  resolve <url>                 debug: print what the browser reads for one link.

STATE  purchasing/state.json — last_ts read, processed message ts, held items, catalog of ordered ASINs (price, qty,
       last date, store). Every run writes purchasing/runs/<stamp>.json + screenshots under purchasing/runs/<stamp>/.

SAFETY  * never more than one run at a time (vp_lock in the .sh)  * a store is ordered only if every item in it is clean
        or approved  * review screen must show the store street + card 3001 + every Location set + total within 10% of
        the computed total, else NOT placed  * order numbers captured from the page (never invented)  * Amazon asks for a
        sign-in -> stop, one DM, ledger row  * --dry-run goes to the review screen, screenshots, removes what it added.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

OS_DIR = os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
sys.path.insert(0, BIN)
P = os.path.join(OS_DIR, "purchasing")
RULES = os.path.join(P, "supply_rules.json")
STATE = os.path.join(P, "state.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
ET = ZoneInfo("America/New_York")
AGENT = "supply-order"
NOW = dt.datetime.now(ET)
STAMP = NOW.strftime("%Y%m%d-%H%M")
RUNDIR = os.path.join(P, "runs", STAMP)
ASIN_RE = re.compile(r"/(?:dp|gp/product|clp|gp/aw/d)/([A-Z0-9]{10})")
LINK_RE = re.compile(r"https?://(?:www\.)?(?:amazon\.com|a\.co|amzn\.to|smile\.amazon\.com)/[^\s|>]+", re.I)
ORDER_RE = re.compile(r"\b(\d{3}-\d{7}-\d{7})\b")
_seen_orders = set()


def log(*a):
    print(dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def ledger(sentence, human="no"):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, human))
    except OSError:
        pass


def load(path, default):
    try:
        return json.load(open(path))
    except Exception:
        return default


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    json.dump(obj, open(tmp, "w"), indent=1, default=str)
    os.replace(tmp, path)


def shot(page, name):
    try:
        os.makedirs(RUNDIR, exist_ok=True)
        page.screenshot(path=os.path.join(RUNDIR, name + ".png"), full_page=True)
        # 2026-10-22: never persist the raw DOM — it carries anti-CSRF/session tokens and tripped the nightly
        # backup's secret scan. vp_redact strips scripts, hidden-input/meta token values, secret shapes, PANs.
        from vp_redact import redact_html
        open(os.path.join(RUNDIR, name + ".html"), "w").write(redact_html(page.content()))
    except Exception:
        pass


# ------------------------------------------------------------------ Slack
import vp_slack  # noqa: E402


def slack(method, **params):
    r = vp_slack.call(method, params=params)
    if not r.get("ok"):
        raise RuntimeError("slack %s: %s" % (method, r.get("error")))
    return r


def dm(text):
    if "--no-post" in sys.argv:
        log("DM (suppressed):", text)
        return
    subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "dm", text], timeout=60)


def thread_reply(channel, ts, text):
    if "--no-post" in sys.argv:
        log("THREAD (suppressed):", ts, text)
        return
    vp_slack.call("chat.postMessage", {"channel": channel, "thread_ts": ts, "text": text})


_users = {}


def user_name(uid):
    if uid not in _users:
        try:
            u = slack("users.info", user=uid)["user"]
            _users[uid] = (u.get("real_name") or u.get("name") or uid)
        except Exception:
            _users[uid] = uid
    return _users[uid]


def new_requests(rules, st):
    ch = rules["channels"]["requests"]
    oldest = st.get("last_ts") or "%.6f" % (time.time() - 8 * 86400)
    msgs, cursor = [], None
    while True:
        kw = {"channel": ch, "oldest": oldest, "limit": 200}
        if cursor:
            kw["cursor"] = cursor
        r = slack("conversations.history", **kw)
        msgs += r.get("messages", [])
        cursor = (r.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break
    # posts we asked to re-send links (cut-off paste): staff often answer IN THE THREAD, so read those replies too
    for pts, why in list(st.get("processed", {}).items()):
        if why != "unreadable":
            continue
        try:
            rr = slack("conversations.replies", channel=ch, ts=pts, limit=100)
        except Exception:
            continue
        parent = (rr.get("messages") or [{}])[0]
        for m in rr.get("messages", [])[1:]:
            if m.get("bot_id") or m["ts"] in st.get("processed", {}) or not LINK_RE.findall(m.get("text", "")):
                continue
            m = dict(m)
            # carry the parent's store word so store_for() can still tell which store it is
            m["text"] = (parent.get("text", "").split("\n")[0] + "\n" + m.get("text", ""))
            msgs.append(m)
    out = []
    for m in sorted(msgs, key=lambda m: float(m["ts"])):
        if m.get("subtype") in ("channel_join", "bot_message") or m.get("bot_id"):
            continue
        if m["ts"] in st.get("processed", {}):
            continue
        text = m.get("text", "")
        links = LINK_RE.findall(text)
        for f in m.get("files", []) or []:
            pass
        if not links:
            continue
        out.append({"ts": m["ts"], "user": m.get("user"), "who": user_name(m.get("user", "")), "text": text, "links": links})
    return out


def store_for(req, rules):
    t = req["text"].lower()
    for s in rules["stores"]:
        if s.lower() in t:
            return s
    first = (req["who"] or "").split()[0].lower() if req["who"] else ""
    return rules["poster_to_store"].get(first)


def quantities(req):
    """{link: qty}. Ask the model to read free text; fall back to 1 each."""
    q = {l: 1 for l in req["links"]}
    try:
        import vp_ai
        # number the links (long Amazon URLs echoed back blew the token limit, 10/21)
        msg = req["text"]
        for n, l in enumerate(req["links"], 1):
            msg = msg.replace(l, "[LINK %d]" % n)
        ans = vp_ai.ask_json(
            "A store employee posted this supply request in Slack. For each [LINK n], how many units do they want? "
            "Default 1 if not stated. Answer with JSON only, no code fence: {\"1\": <int>, \"2\": <int>, ...}\n\n"
            "Message:\n" + msg[:3000], max_tokens=200)
        for k, n in (ans or {}).items():
            try:
                idx = int(re.sub(r"\D", "", str(k))) - 1
            except ValueError:
                continue
            if 0 <= idx < len(req["links"]) and isinstance(n, (int, float)) and 1 <= int(n) <= 100:
                q[req["links"][idx]] = int(n)
    except Exception as e:
        log("qty parse fallback:", e)
    return q


# ------------------------------------------------------------------ browser / Amazon
def ensure_signed_in(page):
    page.goto("https://www.amazon.com/gp/css/order-history", wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    if "signin" in page.url or "ap/signin" in page.url or page.locator("#ap_password, #ap_email").count():
        raise RuntimeError("AMAZON_SIGNIN")


def resolve(page, link):
    page.goto(link, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    m = ASIN_RE.search(page.url) or ASIN_RE.search(link)
    asin = m.group(1) if m else None
    info = page.evaluate("""() => {
        const q = s => document.querySelector(s);
        const pv = (q('#twister-plus-price-data-price')||{}).value || (q('#attach-base-product-price')||{}).value;
        const prEl = q('#corePriceDisplay_desktop_feature_div .a-offscreen') || q('#corePrice_feature_div .a-offscreen')
                || q('#apex_desktop .a-offscreen') || q('#tp_price_block_total_price_ww .a-offscreen')
                || q('#price_inside_buybox') || q('#newBuyBoxPrice') || q('#buybox .a-price .a-offscreen')
                || q('#corePriceDisplay_desktop_feature_div .a-price-whole') || q('.a-price .a-offscreen');
        const pr = pv ? {innerText: '$' + pv} : prEl;
        return {title: (document.querySelector('#productTitle')||{}).innerText || document.title,
                price: pr ? pr.innerText : null,
                avail: ((document.querySelector('#availability')||{}).innerText || '').slice(0,60),
                cart: !!document.querySelector('#add-to-cart-button')};
    }""")
    price = None
    if info.get("price"):
        try:
            price = float(re.sub(r"[^\d.]", "", info["price"]))
        except ValueError:
            price = None
    return {"asin": asin, "url": "https://www.amazon.com/dp/%s" % asin if asin else link,
            "title": re.sub(r"\s+", " ", info.get("title") or "").strip()[:140], "price": price,
            "avail": info.get("avail", "").strip(), "can_add": bool(info.get("cart"))}


def cart_count(page):
    try:
        return int(re.sub(r"\D", "", page.locator("#nav-cart-count").first.inner_text()) or 0)
    except Exception:
        return -1


def add_to_cart(page, item):
    page.goto(item["url"], wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    before = cart_count(page)
    if item["qty"] > 1:
        try:
            page.select_option("select#quantity", str(item["qty"]))
            time.sleep(1)
        except Exception:
            pass
    page.locator("#add-to-cart-button").first.click()
    time.sleep(5)
    for sel in ("#attachSiNoCoverage", "input[aria-labelledby='attachSiNoCoverage-announce']",
                "button:has-text('No thanks')", "span:has-text('No Thanks')"):
        try:
            b = page.locator(sel).first
            if b.count() and b.is_visible():
                b.click()
                time.sleep(2)
                break
        except Exception:
            pass
    after = cart_count(page)
    return after == -1 or before == -1 or after > before


def _cart_row(page, asin):
    # active cart rows come first; Saved-for-later rows share the markup, so take the first match (mapped 10/21)
    return page.locator("div[data-asin='%s'][data-csa-c-owner='CartX']" % asin).first


def isolate_cart(page, asins):
    """Cart shows ONLY our ASINs as selected (Joshua parks other items there — deselect, never delete them)."""
    page.goto("https://www.amazon.com/gp/cart/view.html", wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    for cb in page.locator("div[data-csa-c-owner='CartX'] input[type=checkbox][aria-label^='Select']").all():
        try:
            row_asin = cb.locator("xpath=ancestor::div[@data-asin][1]").get_attribute("data-asin")
            want = row_asin in asins
            if cb.is_checked() != want:
                cb.evaluate("e => e.click()")
                time.sleep(1.5)
        except Exception:
            continue
    time.sleep(2)
    found = set()
    for a in asins:
        cb = _cart_row(page, a).locator("input[type=checkbox][aria-label^='Select']").first
        if cb.count() and cb.is_checked():
            found.add(a)
    return found


def remove_from_cart(page, asins):
    page.goto("https://www.amazon.com/gp/cart/view.html", wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    for a in asins:
        for _ in range(3):  # a row can appear twice if added twice
            row = _cart_row(page, a)
            d = row.locator("input[data-action='delete-active'], input[value='Delete']").first
            if not (row.count() and d.count()):
                break
            d.evaluate("e => e.click()")
            time.sleep(2.5)


def click_first(page, selectors, timeout=8000):
    for s in selectors:
        try:
            el = page.locator(s).first
            el.wait_for(state="visible", timeout=timeout)
            el.click()
            return s
        except Exception:
            continue
    return None


def order_blocks(page):
    """Your Orders as a list of {date, total, ship_to, order} parsed from the page TEXT, one block per order.
    (The page wraps every order in ONE .js-order-card element, so per-card selectors don't separate them — 10/22.)"""
    t = page.inner_text("body")
    out = []
    for blk in re.split(r"\n\s*Order placed\s*\n", t)[1:]:
        d = re.match(r"\s*(\w+ \d{1,2}, \d{4})", blk)
        num = ORDER_RE.search(blk)
        tot = re.search(r"Total\s*\n?\s*\$([\d,]+\.\d{2})", blk)
        ship = re.search(r"Ship to\s*\n(.+?)\n\s*Placed by", blk, re.S)
        if d and num:
            out.append({"date": d.group(1), "order": num.group(1),
                        "total": float(tot.group(1).replace(",", "")) if tot else None,
                        "ship_to": re.sub(r"\s+", " ", ship.group(1)).strip() if ship else ""})
    return out


def find_today_order(page, store, rules, exclude=(), total=None):
    """Order # placed TODAY shipping to this store (closest total wins when several)."""
    page.goto("https://www.amazon.com/your-orders/orders?timeFilter=last30", wait_until="domcontentloaded", timeout=60000)
    time.sleep(4)
    today = "%s %d, %d" % (NOW.strftime("%B"), NOW.day, NOW.year)
    sinfo = rules["stores"][store]
    hits = [b for b in order_blocks(page) if b["date"] == today and b["order"] not in exclude
            and (sinfo["street"] in b["ship_to"].upper() or sinfo["label"].upper() in b["ship_to"].upper())]
    if not hits:
        return None
    if total is not None:
        # Amazon can split one checkout into several orders: take every new order for this store today when
        # together they add up to the checkout total (+/- $1), else the single closest one
        if abs(sum(b["total"] or 0 for b in hits) - total) <= 1.0:
            return [b["order"] for b in hits]
        hits.sort(key=lambda b: abs((b["total"] or 0) - total))
    return [hits[0]["order"]]


def checkout_store(page, store, items, rules, dry):
    """One store = one checkout. Returns dict(status, orders[], total, note)."""
    sinfo = rules["stores"][store]
    asins = [i["asin"] for i in items]
    tag = "%s-%s" % (store, STAMP)
    remove_from_cart(page, asins)  # start clean: a leftover copy would double the quantity
    for it in items:
        if not add_to_cart(page, it):
            log(store, "add-to-cart did not register for", it["asin"], "- retrying once")
            if not add_to_cart(page, it):
                return {"status": "add-failed", "note": "Amazon did not take %s" % it["title"][:60]}
    found = isolate_cart(page, asins)
    if set(asins) - found:
        shot(page, tag + "-cart")
        return {"status": "cart-mismatch", "note": "items missing in cart: %s" % ", ".join(set(asins) - found)}
    shot(page, tag + "-cart")
    if not click_first(page, ["input[name='proceedToRetailCheckout']", "#sc-buy-box-ptc-button input",
                              "input[value*='Proceed to checkout']", "a:has-text('Proceed to checkout')"]):
        return {"status": "no-checkout-button"}
    time.sleep(5)
    click_first(page, ["a:has-text('Continue to checkout')", "input[value*='Continue to checkout']",
                       "button:has-text('Continue to checkout')"], timeout=4000)
    time.sleep(3)
    if "signin" in page.url:
        raise RuntimeError("AMAZON_SIGNIN")
    # --- Checkout is an accordion (mapped 2026-10-21): Business Order Information (PO + custom "Location" dropdown,
    #     required) -> Continue -> Select a delivery address -> Payment method -> Review items -> Place your order.
    shot(page, tag + "-1-business-info")
    def loc_select():
        for sel in page.locator("select[id$='_searchableDropdownNativeId'], select").all():
            try:
                vals = [v.strip() for v in sel.locator("option").all_inner_texts()]
                if store in vals and "Corporate" in vals:
                    return sel
            except Exception:
                continue
        return None
    def set_location():
        sel = loc_select()
        if sel is None:
            return "absent"
        if sel.input_value().strip() == store:
            return "set"
        # select2 widget sits right after the hidden <select> (mapped 10/21)
        box = sel.locator("xpath=following-sibling::span[contains(@class,'select2')][1]//span[contains(@class,'select2-selection')]").first
        try:
            box.click()
            time.sleep(1.5)
            srch = page.locator("input.select2-search__field:visible").first
            if srch.count():
                srch.fill(store)
                time.sleep(1.5)
            opt = page.locator("li.select2-results__option:visible", has_text=store).first
            opt.click()
            time.sleep(1.5)
        except Exception as e:
            log("select2 click path failed:", e)
        if sel.input_value().strip() != store:
            # last resort: set the native select and let select2 hear the change
            sel.evaluate("(e, v) => { e.value = v; e.dispatchEvent(new Event('change', {bubbles: true})); "
                         "if (window.jQuery) jQuery(e).val(v).trigger('change'); }", store)
            time.sleep(1.5)
        return "set" if sel.input_value().strip() == store else "failed"
    loc = set_location()
    log(store, "location:", loc)
    if loc == "failed":
        shot(page, tag + "-location")
        return {"status": "location-not-set", "note": "could not pick %s in the Location box" % store}
    def section_continue():
        return click_first(page, ["#checkout-primary-continue-button-id input", "input[data-testid='bottom-continue-button']",
                                  "span.a-button-primary:visible input[type=submit]", "button:has-text('Continue'):visible",
                                  "input[value='Continue']:visible", "span:has-text('Continue'):visible"], timeout=6000)
    if loc == "set":
        section_continue()
        time.sleep(5)
    shot(page, tag + "-2-spc")
    # After Location, Amazon jumps to the single-page review with ITS defaults (Joshua's FL home + Amex 2003).
    # Each section has its own Change link (ids mapped 10/21).
    def section_text(word):
        t = page.inner_text("body")
        i = t.find(word)
        return t[i:i + 400].upper() if i >= 0 else ""
    def pick_row(match, exclude=None, must=None):
        for row in page.locator("div.a-radio, label, [data-testid*='address'], .address-ui-widgets-address-wrapper, "
                                "div.pmts-instrument-selector, div[class*='instrument'], li").all():
            try:
                if not row.is_visible():
                    continue
                t = row.inner_text()
                tu = t.upper()
                if len(t) > 600 or match.upper() not in tu:
                    continue
                if exclude and exclude.upper() in tu:
                    continue
                if must and must.upper() not in tu:
                    continue
                r = row.locator("input[type=radio]").first
                (r if r.count() else row).click()
                return True
            except Exception:
                continue
        return False
    # --- delivery address
    if sinfo["street"] not in section_text("Delivering to"):
        if not click_first(page, ["a[data-csa-c-slot-id='checkout-change-shipaddressselect']", "#change-delivery-link"], timeout=8000):
            return {"status": "no-address-change-link"}
        time.sleep(5)
        shot(page, tag + "-3-addresses")
        if not pick_row(sinfo["street"]):
            click_first(page, ["a:has-text('Show more addresses')", "a:has-text('Show more')"], timeout=3000)
            time.sleep(2)
            if not pick_row(sinfo["street"]):
                shot(page, tag + "-address-notfound")
                return {"status": "address-not-found", "note": "store address %s not in the list" % sinfo["street"]}
        time.sleep(1)
        click_first(page, ["input[data-testid='Address_selectShipToThisAddress']", "#shipToThisAddressButton input",
                           "span:has-text('Deliver to this address'):visible input", "button:has-text('Deliver to this address'):visible",
                           "span:has-text('Use this address'):visible input", "button:has-text('Use this address'):visible",
                           "input[value*='this address']:visible"])
        time.sleep(6)
        shot(page, tag + "-4-after-address")
        if sinfo["street"] not in section_text("Delivering to"):
            return {"status": "address-not-applied", "note": "still not delivering to %s" % store}
    # --- payment: Amex 3001 "Provided by your organization", never the Business Platinum 3001 or the default 2003
    def pay_ok():
        # both 3001 cards read "Business Platinum Card 3001" here; pick_row() below is what tells them apart
        seg = section_text("Paying with")
        return rules["payment_card_last4"] in seg[:120] and "2003" not in seg[:120]
    if True:  # ALWAYS choose explicitly: both 3001 cards read "American Express 3001" on the review (10/21)
        if not click_first(page, ["a[data-csa-c-slot-id='checkout-change-payselect']", "#change-payment-link"], timeout=8000):
            return {"status": "no-payment-change-link"}
        time.sleep(5)
        shot(page, tag + "-5-payments")
        if not pick_row(rules["payment_card_last4"], exclude=rules["payment_card_must_not_say"], must=rules["payment_card_must_say"]):
            shot(page, tag + "-payment-notfound")
            return {"status": "card-not-found", "note": "Amex %s 'Provided by your organization' not offered" % rules["payment_card_last4"]}
        time.sleep(1)
        # verify the CHECKED card is the organization one before confirming (both read "Platinum 3001")
        ok_card = page.evaluate("""(must) => {
            const r = [...document.querySelectorAll('input[type=radio]')].find(x => x.checked && /3001/.test(
                (x.closest('div.a-radio, div.pmts-instrument-selector, [class*=instrument], li, div.a-row') || {}).innerText || ''));
            if (!r) return false;
            let el = r; for (let i = 0; i < 6 && el; i++) { if ((el.innerText||'').includes(must)) return !(el.innerText||'').includes('Rewards Points available'); el = el.parentElement; }
            return false; }""", rules["payment_card_must_say"])
        if not ok_card:
            shot(page, tag + "-payment-wrongcard")
            return {"status": "card-not-verified", "note": "could not confirm the organization Amex 3001 is the selected card"}
        click_first(page, ["input[name='ppw-widgetEvent:SetPaymentPlanSelectContinueEvent']",
                           "span:has-text('Use this payment method'):visible input", "button:has-text('Use this payment method'):visible",
                           "input[value*='Use this payment method']:visible"])
        time.sleep(6)
        shot(page, tag + "-6-after-payment")
        if not pay_ok():
            return {"status": "card-not-applied", "note": "still not paying with Amex %s" % rules["payment_card_last4"]}
    if loc != "absent":
        set_location()
    # --- delivery speed: Amazon pre-selects "Consolidated Shipping in fewest deliveries" (Oct 31 vs Oct 23 on 10/21).
    #     Take the free Prime option in every shipment group when it is offered.
    try:
        for opt in page.locator("div.a-radio:visible, label:visible").all():
            t = opt.inner_text()
            if "FREE Prime Delivery" in t and len(t) < 200:
                r = opt.locator("input[type=radio]").first
                if r.count() and not r.is_checked():
                    r.click()
                    time.sleep(3)
    except Exception as e:
        log(store, "delivery-speed choice skipped:", e)
    # --- review checks
    shot(page, tag + "-review")
    body = page.inner_text("body")
    up = body.upper()
    expect = sum((i["price"] or 0) * i["qty"] for i in items)
    tot = re.search(r"Order total:?\s*\$([\d,]+\.\d{2})", body)
    total = float(tot.group(1).replace(",", "")) if tot else None
    problems = []
    if sinfo["street"] not in up:
        problems.append("ship-to is not the %s store" % store)
    if not pay_ok():
        problems.append("card is not Amex %s" % rules["payment_card_last4"])
    for sel in page.locator("select").all():
        try:
            opts = sel.locator("option").all_inner_texts()
            if any("Corporate" in o for o in opts) and sel.input_value().strip() in ("", "Select", "select", "Select one", "ab-cof-search-placeholder"):
                problems.append("Location not set")
        except Exception:
            pass
    if total is None:
        problems.append("order total not readable")
    elif expect and not (0.9 * expect <= total <= expect * 1.2 + 15):  # tax + small price drift allowed
        problems.append("total $%.2f vs expected ~$%.2f" % (total, expect))
    if problems:
        return {"status": "review-failed", "note": "; ".join(problems), "total": total}
    if dry:
        remove_from_cart(page, asins)
        return {"status": "dry-run", "total": total, "note": "stopped on the review screen"}
    if not click_first(page, ["input[name='placeYourOrder1']", "#submitOrderButtonId input", "#placeYourOrder input",
                              "input[value='Place your order']", "button:has-text('Place your order')",
                              "span:has-text('Place your order') input"]):
        return {"status": "no-place-button", "total": total}
    time.sleep(10)
    shot(page, tag + "-thankyou")
    t = page.inner_text("body")
    ok = ("has been placed" in t or "Order placed" in t or "order has been placed" in t.lower())
    shipped_ok = sinfo["street"] in t.upper().split("SHIPPING TO", 1)[-1][:200] if "SHIPPING TO" in t.upper() else None
    # the business thank-you page carries no order number (10/21): match today's order card by ship-to store
    orders = []
    try:
        for wait in (15, 45, 90):  # Your Orders lags a minute behind the thank-you page (10/21)
            time.sleep(wait)
            n = find_today_order(page, store, rules, exclude=_seen_orders, total=total)
            if n:
                orders = n
                _seen_orders.update(n)
                break
    except Exception as e:
        log(store, "order-number lookup failed:", e)
    if shipped_ok is False:
        return {"status": "placed-wrong-address?", "orders": orders, "total": total,
                "note": "confirmation does not show the %s address" % store}
    return {"status": "placed" if (ok and orders) else "placed-unconfirmed", "orders": orders, "total": total}


# ------------------------------------------------------------------ rules
def evaluate(store, items, rules, st):
    cat = st.setdefault("catalog", {})
    held, clean = [], []
    approved = st.setdefault("approved_asins", {})
    for it in items:
        if it.get("asin") in approved and it.get("price") is not None and it.get("can_add"):
            clean.append(dict(it, reasons=[], approved=True))  # Joshua approved this item once -> never ask again
            continue
        reasons = []
        title = " %s " % it["title"].lower()
        for w in rules["blocked_words"]:
            if w.lower() in title:
                reasons.append("looks like '%s', not a supply" % w.strip())
                break
        if it["price"] is None or not it["can_add"]:
            reasons.append("price/availability not readable (%s)" % (it["avail"] or "no Add to Cart"))
        known = cat.get(it["asin"] or "")
        if it["price"] is not None:
            if not known and it["price"] > rules["new_item_auto_max_price"]:
                reasons.append("new item over $%.0f" % rules["new_item_auto_max_price"])
            if known and known.get("price") and it["price"] > known["price"] * (1 + rules["price_jump_pct"] / 100.0):
                reasons.append("price up from $%.2f to $%.2f" % (known["price"], it["price"]))
        usual = (known or {}).get("qty") or 1
        if it["qty"] > max(rules["max_qty_default"], usual * rules["qty_vs_usual_multiplier"]):
            reasons.append("quantity %d is unusual" % it["qty"])
        if known and known.get("store") == store and known.get("date"):
            try:
                if (NOW.date() - dt.date.fromisoformat(known["date"])).days < rules["repeat_window_days"]:
                    reasons.append("same item ordered for %s on %s" % (store, known["date"]))
            except ValueError:
                pass
        (held if reasons else clean).append(dict(it, reasons=reasons))
    tot = sum((i["price"] or 0) * i["qty"] for i in clean)
    store_reason = None
    if tot > rules["store_order_cap"]:
        store_reason = "%s order $%.2f is over the $%.0f cap" % (store, tot, rules["store_order_cap"])
    elif tot > rules["store_weekly_budget"]:
        store_reason = "%s order $%.2f is over the $%.0f weekly budget" % (store, tot, rules["store_weekly_budget"])
    if store_reason:
        held += [dict(i, reasons=[store_reason]) for i in clean if not i.get("approved")]
        clean = [i for i in clean if i.get("approved")]
    return clean, held


def remember(st, store, items, orders):
    cat = st.setdefault("catalog", {})
    for i in items:
        cat[i["asin"]] = {"title": i["title"], "price": i["price"], "qty": i["qty"], "store": store,
                          "date": NOW.date().isoformat(), "orders": orders}


# ------------------------------------------------------------------ commands
def browser():
    import vp_browser
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    ctx = vp_browser.launch(p)
    return p, ctx, vp_browser.first_page(ctx), vp_browser


def order_stores(page, by_store, rules, st, dry, run):
    results = {}
    for store, items in by_store.items():
        if not items:
            continue
        try:
            res = checkout_store(page, store, items, rules, dry)
        except RuntimeError:
            raise
        except Exception as e:
            shot(page, "%s-%s-error" % (store, STAMP))
            res = {"status": "error", "note": "%s: %s" % (type(e).__name__, str(e)[:200])}
        if not res["status"].startswith("placed") and res["status"] != "dry-run":
            try:
                remove_from_cart(page, [i["asin"] for i in items])  # never leave our additions in Joshua's cart
            except Exception:
                pass
        log(store, res)
        results[store] = res
        run.setdefault("orders", {})[store] = res
        if res["status"] == "placed" or res["status"] == "placed-unconfirmed":
            remember(st, store, items, res.get("orders", []))
            for o in res.get("orders", []) or ["?"]:
                st.setdefault("orders", []).append({
                    "order": o, "store": store, "placed": NOW.date().isoformat(), "total": res.get("total"),
                    "items": [{"asin": i["asin"], "title": i["title"][:80], "qty": i["qty"], "msg_ts": i["msg_ts"],
                               "requester": i.get("requester")} for i in items],
                    "status": "placed", "checks": []})
            save(STATE, st)
            for it in items:
                st["processed"][it["msg_ts"]] = "ordered"
                thread_reply(rules["channels"]["requests"], it["msg_ts"],
                             "Ordered: %s x%d, shipping to %s. Order %s" % (it["title"][:70], it["qty"], store,
                                                                         ", ".join(res.get("orders", [])) or "(see Amazon)"))
            save(STATE, st)
    return results


def summary_dm(results, held, couldnt, dry):
    lines = []
    placed = {s: r for s, r in results.items() if r["status"].startswith("placed")}
    if placed:
        lines.append("Supplies %s this week:" % ("dry run (nothing bought)" if dry else "ordered"))
        for s, r in placed.items():
            lines.append("• %s — $%.2f — order %s" % (s, r.get("total") or 0, ", ".join(r.get("orders", [])) or "?"))
    for s, r in results.items():
        if r["status"] == "dry-run":
            lines.append("• %s — would order $%.2f (dry run)" % (s, r.get("total") or 0))
        elif not r["status"].startswith("placed"):
            lines.append("• %s — not ordered: %s" % (s, r.get("note") or r["status"]))
    if held:
        lines.append("Waiting on your OK (reply *approve* or *skip* in the request's thread in #supply-request):")
        for h in held:
            lines.append("• %s — %s x%d $%s — %s" % (h["store"] or "?", h["title"][:60], h["qty"],
                                                    ("%.2f" % h["price"]) if h["price"] else "?", "; ".join(h["reasons"])))
    if couldnt:
        lines.append("Couldn't read: " + "; ".join(couldnt))
    if lines:
        dm("\n".join(lines))


def cmd_run(dry):
    rules = load(RULES, None)
    st = load(STATE, {"processed": {}, "held": [], "catalog": {}})
    st.setdefault("processed", {})
    st.setdefault("held", [])
    run = {"started": NOW.isoformat(), "dry_run": dry}
    reqs = new_requests(rules, st)
    log("new requests:", len(reqs))
    if not reqs:
        st["last_ts"] = "%.6f" % time.time() if not dry else st.get("last_ts")
        save(STATE, st)
        save(os.path.join(P, "runs", STAMP + ".json"), run)
        return 0
    p, ctx, page, vb = browser()
    try:
        ensure_signed_in(page)
        by_store, held_all, couldnt, unreadable = {}, [], [], []
        for req in reqs:
            store = store_for(req, rules)
            qty = quantities(req)
            items = []
            bad = []
            for l in req["links"]:
                try:
                    r = resolve(page, l)
                except Exception as e:
                    bad.append(l)
                    continue
                if not r["asin"]:
                    bad.append(l)
                    continue
                items.append(dict(r, qty=qty.get(l, 1), msg_ts=req["ts"], requester=req["who"], store=store))
            if bad:
                couldnt.append("%s (%s): %d link(s)" % (req["who"], store or "?", len(bad)))
                unreadable.append((req, len(bad), len(req["links"])))
            if not store:
                held_all += [dict(i, reasons=["couldn't tell which store"]) for i in items]
                continue
            # one line per ASIN per store (staff re-post items they're still waiting on)
            for i in items:
                prev = next((x for x in by_store.setdefault(store, []) if x["asin"] == i["asin"]), None)
                if prev:
                    prev["qty"] = max(prev["qty"], i["qty"])
                else:
                    by_store[store].append(i)
        clean_by_store = {}
        for store, items in by_store.items():
            clean, held = evaluate(store, items, rules, st)
            clean_by_store[store] = clean
            held_all += held
        run["planned"] = clean_by_store
        run["held"] = held_all
        results = order_stores(page, clean_by_store, rules, st, dry, run)
        if not dry:
            for h in held_all:
                st["held"].append(h)
                st["processed"][h["msg_ts"]] = "held"
                thread_reply(rules["channels"]["requests"], h["msg_ts"],
                             "%s x%d is waiting on Joshua's OK before it's ordered." % (h["title"][:70], h["qty"]))
            # 10/22: a request whose links can't be opened (cut-off paste, "…" in the URL) must never vanish silently
            for req, nbad, nall in unreadable:
                thread_reply(rules["channels"]["requests"], req["ts"],
                             "I couldn't open %s of the links in this post — they look cut off. Please repost the full "
                             "Amazon links (use Share > Copy Link in the Amazon app) and I'll order them next run."
                             % ("all %d" % nall if nbad == nall else "%d of %d" % (nbad, nall)))
            for req, nbad, nall in unreadable:
                if nbad == nall:
                    st["processed"][req["ts"]] = "unreadable"  # keep watching its thread for re-posted links
            for r in reqs:
                st["processed"].setdefault(r["ts"], "read")
            st["last_ts"] = reqs[-1]["ts"]
            save(STATE, st)
        summary_dm(results, held_all, couldnt, dry)
    except RuntimeError as e:
        if str(e) == "AMAZON_SIGNIN":
            dm("Amazon Business is asking for a sign-in before I can order supplies. Run Valley Pawn OS/bin/vp_signin_front.sh "
               "--only amazon, sign in (tick 'Keep me signed in'), quit that window, and I'll order on the next run.")
            ledger("Amazon Business sign-in needed on the automation Chrome", "yes, sign in to Amazon on pw-vp")
        else:
            raise
    finally:
        run["finished"] = dt.datetime.now(ET).isoformat()
        save(os.path.join(P, "runs", STAMP + ".json"), run)
        vb.close(ctx)
        p.stop()
    return 0


def cmd_approvals(dry):
    rules = load(RULES, None)
    st = load(STATE, {"processed": {}, "held": [], "catalog": {}})
    held = st.get("held", [])
    if not held:
        return 0
    ch = rules["channels"]["requests"]
    approved, skipped = [], []
    for h in held:
        try:
            r = slack("conversations.replies", channel=ch, ts=h["msg_ts"], limit=50)
        except Exception:
            continue
        verdict = None
        for m in r.get("messages", [])[1:]:
            if m.get("user") != vp_slack.JOSHUA:
                continue
            w = m.get("text", "").strip().lower()
            if re.search(r"\bapprove[d]?\b|\bok\b|\byes\b", w):
                verdict = "approve"
            if re.search(r"\bskip\b|\bno\b|\bcancel\b", w):
                verdict = "skip"
        if h.get("approved_in_chat"):
            verdict = "approve"
        if verdict == "approve":
            approved.append(h)
            st.setdefault("approved_asins", {})[h["asin"]] = {"title": h["title"][:80], "approved": NOW.date().isoformat(),
                                                             "first_store": h.get("store")}
        elif verdict == "skip":
            skipped.append(h)
    if not (approved or skipped):
        return 0
    for h in skipped:
        held.remove(h)
        st["processed"][h["msg_ts"]] = "skipped"
        thread_reply(ch, h["msg_ts"], "Not ordering %s this time." % h["title"][:70])
    run = {"started": NOW.isoformat(), "dry_run": dry, "approved": approved, "skipped": skipped}
    if approved:
        by_store = {}
        for h in approved:
            by_store.setdefault(h["store"], []).append({k: v for k, v in h.items() if k != "reasons"})
        p, ctx, page, vb = browser()
        try:
            ensure_signed_in(page)
            results = order_stores(page, by_store, rules, st, dry, run)
            for s, r in results.items():
                if r["status"].startswith("placed") and not dry:
                    for h in [x for x in approved if x["store"] == s]:
                        held.remove(h)
            summary_dm(results, [], [], dry)
        finally:
            vb.close(ctx)
            p.stop()
    st["held"] = held
    save(STATE, st)
    save(os.path.join(P, "runs", STAMP + "-approvals.json"), run)
    return 0


def cmd_watch():
    """Weekly read-only audit of everything bought on the account in the last 7 days."""
    rules = load(RULES, None)
    st = load(STATE, {"catalog": {}})
    p, ctx, page, vb = browser()
    rows = []
    try:
        ensure_signed_in(page)
        page.goto("https://www.amazon.com/your-orders/orders?timeFilter=last30", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        for _ in range(3):
            cards = page.locator(".order-card, .js-order-card, div.a-box-group.order").all()
            for c in cards:
                t = re.sub(r"\s+", " ", c.inner_text())
                d = re.search(r"ORDER PLACED\s+(\w+ \d{1,2}, \d{4})", t, re.I)
                tot = re.search(r"TOTAL\s+\$([\d,]+\.\d{2})", t, re.I)
                ship = re.search(r"SHIP TO\s+(.+?)\s+ORDER #", t, re.I)
                num = ORDER_RE.search(t)
                if not (d and num):
                    continue
                when = dt.datetime.strptime(d.group(1), "%B %d, %Y").date()
                if (NOW.date() - when).days > 7:
                    continue
                rows.append({"date": when.isoformat(), "order": num.group(1),
                             "total": float(tot.group(1).replace(",", "")) if tot else None,
                             "ship_to": ship.group(1).strip() if ship else "?", "text": t[:600]})
            nxt = page.locator("li.a-last a").first
            if not nxt.count():
                break
            nxt.click()
            time.sleep(4)
    finally:
        vb.close(ctx)
        p.stop()
    seen = {r["order"]: r for r in rows}
    rows = list(seen.values())
    by = {}
    flags = []
    pipeline_orders = {o for v in st.get("catalog", {}).values() for o in (v.get("orders") or [])}
    for r in rows:
        store = next((s for s, i in rules["stores"].items() if s.lower() in r["ship_to"].lower()
                      or i["label"].lower() in r["ship_to"].lower()), None)
        key = store or "Not a store (%s)" % r["ship_to"]
        by[key] = by.get(key, 0) + (r["total"] or 0)
        low = r["text"].lower()
        for w in rules["blocked_words"]:
            if w.lower() in " %s " % low:
                flags.append("%s %s — mentions '%s'" % (r["date"], r["order"], w.strip()))
                break
        if not store:
            flags.append("%s %s — $%.2f shipped to %s" % (r["date"], r["order"], r["total"] or 0, r["ship_to"]))
        elif r["order"] not in pipeline_orders and (r["total"] or 0) > rules["store_order_cap"]:
            flags.append("%s %s — $%.2f to %s, placed outside the supply run" % (r["date"], r["order"], r["total"] or 0, store))
    save(os.path.join(P, "runs", STAMP + "-watch.json"), {"rows": rows, "by": by, "flags": flags})
    lines = ["Amazon spend, last 7 days: " + (", ".join("%s $%.2f" % kv for kv in sorted(by.items())) or "nothing")]
    lines.append(("Look at: " + " | ".join(flags)) if flags else "Nothing unusual.")
    dm("\n".join(lines))
    return 0


STATUS_RE = re.compile(r"(Delivered[^\n]{0,30}|Arriving[^\n]{0,30}|Now expected[^\n]{0,30}|Out for delivery[^\n]{0,20}|"
                       r"Shipped[^\n]{0,30}|Delivery attempted[^\n]{0,30}|Undeliverable[^\n]{0,30}|Package (?:may be )?lost[^\n]{0,30}|"
                       r"Return(?:ed| started| complete)[^\n]{0,30}|Refunded[^\n]{0,30}|Cancelled[^\n]{0,20}|Not yet shipped|Preparing for shipment)",
                       re.I)


def read_order(page, num):
    """Ship-to + every shipment status for one order, from Amazon's order-details page."""
    page.goto("https://www.amazon.com/gp/your-account/order-details?orderID=%s" % num,
              wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    if "signin" in page.url:
        raise RuntimeError("AMAZON_SIGNIN")
    t = page.inner_text("body")
    ship = ""
    m = re.search(r"Ship(?:ping)? (?:to|address)\s*\n(.{5,250}?)\n\s*(?:Payment method|Payment Method|Order Summary|Change)", t, re.S)
    if m:
        ship = re.sub(r"\s+", " ", m.group(1)).strip()
    statuses = [re.sub(r"\s+", " ", s).strip() for s in STATUS_RE.findall(t)]
    total = re.search(r"Grand Total:?\s*\$([\d,]+\.\d{2})", t)
    return {"ship_to": ship, "statuses": statuses, "total": float(total.group(1).replace(",", "")) if total else None,
            "text": t[:3000]}


def store_of_address(addr, rules):
    up = (addr or "").upper()
    for s, i in rules["stores"].items():
        if i["street"] in up or (i["zip"] in up and s.upper() in up):
            return s
    return None


def classify(statuses):
    j = " | ".join(statuses).lower()
    if any(w in j for w in ("return complete", "returned", "refunded", "return started")):
        return "returned"
    if any(w in j for w in ("undeliverable", "lost", "delivery attempted", "cancelled")):
        return "problem"
    if statuses and all(s.lower().startswith("delivered") for s in statuses):
        return "delivered"
    if any(s.lower().startswith("delivered") for s in statuses):
        return "partly-delivered"
    return "in-transit"


def cmd_deliveries():
    """Daily: every order this pipeline placed is tracked until Amazon shows it delivered to the RIGHT store."""
    rules = load(RULES, None)
    st = load(STATE, {})
    open_orders = [o for o in st.get("orders", []) if o.get("status") not in ("delivered", "closed") and o["order"] != "?"]
    if not open_orders:
        return 0
    p, ctx, page, vb = browser()
    alerts, delivered = [], []
    try:
        ensure_signed_in(page)
        for o in open_orders:
            try:
                info = read_order(page, o["order"])
            except RuntimeError:
                raise
            except Exception as e:
                log("read_order failed", o["order"], e)
                continue
            shipped_to = store_of_address(info["ship_to"], rules)
            state = classify(info["statuses"])
            o["checks"].append({"at": dt.datetime.now(ET).isoformat(timespec="minutes"), "ship_to": info["ship_to"],
                                "statuses": info["statuses"], "state": state})
            o["checks"] = o["checks"][-10:]
            age = (NOW.date() - dt.date.fromisoformat(o["placed"])).days
            if info["ship_to"] and shipped_to != o["store"]:
                if not o.get("alerted_address"):
                    alerts.append("%s order %s was meant for %s but is shipping to: %s" % (o["placed"], o["order"], o["store"], info["ship_to"]))
                    o["alerted_address"] = True
            if state == "problem" and not o.get("alerted_problem"):
                alerts.append("%s order %s (%s): %s" % (o["placed"], o["order"], o["store"], "; ".join(info["statuses"])[:160]))
                o["alerted_problem"] = True
            elif state != "delivered" and age >= 8 and not o.get("alerted_late"):
                alerts.append("%s order %s (%s) still not delivered after %d days: %s" % (o["placed"], o["order"], o["store"], age,
                                                                                        "; ".join(info["statuses"])[:120] or "no tracking yet"))
                o["alerted_late"] = True
            if state == "delivered" and shipped_to == o["store"]:
                o["status"] = "delivered"
                o["delivered"] = info["statuses"][-1] if info["statuses"] else "Delivered"
                delivered.append(o)
                for ts in sorted({i["msg_ts"] for i in o["items"]}):
                    names = ", ".join(i["title"][:40] for i in o["items"] if i["msg_ts"] == ts)
                    thread_reply(rules["channels"]["requests"], ts, "%s — %s at %s." % (o["delivered"], names, o["store"]))
            save(STATE, st)
    finally:
        vb.close(ctx)
        p.stop()
    if alerts:
        dm("Supply deliveries — needs a look:\n• " + "\n• ".join(alerts))
    return 0


def cmd_audit(days=60):
    """One-off / on demand: every Amazon order in the last N days -> where it shipped + delivery status.
    Writes purchasing/audit-<stamp>.json + .md and DMs Joshua the exceptions."""
    rules = load(RULES, None)
    p, ctx, page, vb = browser()
    nums, rows = [], []
    try:
        ensure_signed_in(page)
        for flt in ("last30", "months-3"):
            page.goto("https://www.amazon.com/your-orders/orders?timeFilter=%s" % flt, wait_until="domcontentloaded", timeout=60000)
            time.sleep(4)
            for _ in range(12):
                for n in ORDER_RE.findall(page.inner_text("body")):
                    if n not in nums:
                        nums.append(n)
                nxt = page.locator("li.a-last a").first
                if not nxt.count():
                    break
                nxt.click()
                time.sleep(4)
        for n in nums:
            try:
                info = read_order(page, n)
            except RuntimeError:
                raise
            except Exception as e:
                rows.append({"order": n, "error": str(e)[:120]})
                continue
            placed = re.search(r"Order placed\s*\n?\s*(\w+ \d{1,2}, \d{4})", info["text"], re.I)
            pd = dt.datetime.strptime(placed.group(1), "%B %d, %Y").date() if placed else None
            if pd and (NOW.date() - pd).days > days:
                continue
            rows.append({"order": n, "placed": pd.isoformat() if pd else None, "ship_to": info["ship_to"],
                         "store": store_of_address(info["ship_to"], rules), "state": classify(info["statuses"]),
                         "statuses": info["statuses"], "total": info["total"]})
    finally:
        vb.close(ctx)
        p.stop()
    out = os.path.join(P, "audit-%s" % STAMP)
    save(out + ".json", rows)
    lines = ["# Amazon order audit — last %d days (%s)" % (days, NOW.date()), "",
             "| Placed | Order | Ship to | Store | Status | Total |", "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r.get("placed") or ""):
        lines.append("| %s | %s | %s | %s | %s | %s |" % (r.get("placed"), r["order"], (r.get("ship_to") or "")[:60],
                                                       r.get("store") or "NOT A STORE", r.get("state"), r.get("total")))
    open(out + ".md", "w").write("\n".join(lines) + "\n")
    stores = [r for r in rows if r.get("store")]
    probs = [r for r in rows if r.get("state") in ("problem", "in-transit") and r.get("placed")
             and (NOW.date() - dt.date.fromisoformat(r["placed"])).days >= 8]
    msg = ["Amazon delivery audit, last %d days: %d orders, %d to stores (%s)." % (
        days, len(rows), len(stores), ", ".join("%s %d" % (s, sum(1 for r in stores if r["store"] == s)) for s in rules["stores"]))]
    if probs:
        msg.append("Not delivered / problem: " + "; ".join("%s %s %s" % (r["order"], r.get("store") or r.get("ship_to", "")[:30], r["state"]) for r in probs[:12]))
    else:
        msg.append("Every store order older than a week shows delivered.")
    dm("\n".join(msg))
    return 0


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    dry = "--dry-run" in sys.argv
    cmd = a[0] if a else "run"
    if cmd == "run":
        return cmd_run(dry)
    if cmd == "approvals":
        return cmd_approvals(dry)
    if cmd == "watch":
        return cmd_watch()
    if cmd == "cleanup" and len(a) > 1:  # remove the given ASINs from the active cart (test leftovers)
        p, ctx, page, vb = browser()
        try:
            remove_from_cart(page, a[1:])
        finally:
            vb.close(ctx)
            p.stop()
        return 0
    if cmd == "firstweek":  # one-time Tue 10/27 11:00 check Joshua asked for (native; Cowork task creation is gone)
        if NOW.date() != dt.date(2026, 10, 27) and "--force" not in sys.argv:
            return 0  # the plist fires every 10/27; only this year's run does anything
        rules = load(RULES, None)
        st = load(STATE, {})
        runs = os.path.join(P, "runs")
        problems, good = [], []
        tue = sorted(f for f in os.listdir(runs) if re.fullmatch(r"20261027-0\d{3}\.json", f))
        if not tue:
            problems.append("the Tuesday 9 AM supply run didn't leave a record (was the Mac on?)")
        else:
            run = load(os.path.join(runs, tue[-1]), {})
            for store, items in (run.get("planned") or {}).items():
                if not items:
                    continue
                res = (run.get("orders") or {}).get(store, {})
                if not str(res.get("status", "")).startswith("placed"):
                    problems.append("%s wasn't ordered (%s)" % (store, res.get("note") or res.get("status") or "no result"))
        new = [o for o in st.get("orders", []) if o.get("placed") == "2026-10-27"]
        if any(o["order"] == "?" for o in new):
            problems.append("an order number wasn't captured")
        # ship-to + status straight from Amazon for every pipeline order
        p, ctx, page, vb = browser()
        try:
            for o in st.get("orders", []):
                if o["order"] == "?":
                    continue
                info = read_order(page, o["order"])
                if store_of_address(info["ship_to"], rules) != o["store"]:
                    problems.append("order %s for %s is shipping to: %s" % (o["order"], o["store"], info["ship_to"][:60]))
                elif o.get("placed") == "2026-10-27":
                    good.append("%s $%.2f" % (o["store"], o.get("total") or 0))
                if o.get("placed") in ("2026-10-21", "2026-10-22") and classify(info["statuses"]) != "delivered":
                    problems.append("last week's %s order %s still shows: %s" % (o["store"], o["order"], "; ".join(info["statuses"])[:80]))
        finally:
            vb.close(ctx)
            p.stop()
        if not any(f.startswith("20261026-07") and f.endswith("-watch.json") for f in os.listdir(runs)):
            problems.append("Monday's spending report didn't run")
        if problems:
            dm("Supply check (first automatic week) — needs a look: " + "; ".join(problems[:6]))
            ledger("first-week supply check: " + "; ".join(problems[:6]), "yes, see DM")
        else:
            dm("First automatic supply week checked: %s — all shipped to the right stores; last week's orders delivered; "
               "Monday's report ran." % (", ".join(good) or "no new requests this week"))
        return 0
    if cmd == "approve" and len(a) > 1:  # Joshua approved in chat: supply_order.py approve <ASIN> [<ASIN>...]
        st = load(STATE, {})
        for h in st.get("held", []):
            if h.get("asin") in a[1:]:
                h["approved_in_chat"] = True
        for x in a[1:]:
            st.setdefault("approved_asins", {}).setdefault(x, {"approved": NOW.date().isoformat(), "how": "chat"})
        save(STATE, st)
        return cmd_approvals("--dry-run" in sys.argv)
    if cmd == "reply" and len(a) > 2:  # supply_order.py reply <thread_ts> "<text>"
        rules = load(RULES, None)
        thread_reply(rules["channels"]["requests"], a[1], " ".join(a[2:]))
        return 0
    if cmd == "verify":  # every recorded pipeline order: Amazon ship-to, status, items vs what was requested
        rules = load(RULES, None)
        st = load(STATE, {})
        p, ctx, page, vb = browser()
        out = []
        try:
            for o in st.get("orders", []):
                info = read_order(page, o["order"])
                body = info["text"].upper()
                want = o.get("items", [])
                # Waynesboro was split into 2 Amazon orders: an item counts as found if it is on ANY of that store's orders today
                out.append({"order": o["order"], "store": o["store"], "ship_to": info["ship_to"],
                            "ship_ok": store_of_address(info["ship_to"], rules) == o["store"],
                            "statuses": info["statuses"], "state": classify(info["statuses"]), "total": info["total"],
                            "items_on_this_order": [i["title"][:45] for i in want if i["title"][:25].upper() in body]})
                shot(page, "verify-%s" % o["order"])
        finally:
            vb.close(ctx)
            p.stop()
        for r in out:
            print(json.dumps(r))
        save(os.path.join(P, "runs", STAMP + "-verify.json"), out)
        return 0
    if cmd == "payment":  # which card paid an order (reads order details)
        p, ctx, page, vb = browser()
        try:
            for n in a[1:]:
                page.goto("https://www.amazon.com/gp/your-account/order-details?orderID=%s" % n, wait_until="domcontentloaded", timeout=60000)
                time.sleep(4)
                t = page.inner_text("body")
                i = t.find("Payment method")
                print(n, "|", re.sub(r"\s+", " ", t[i:i + 260]) if i >= 0 else "payment section not found")
                shot(page, "order-%s" % n)
        finally:
            vb.close(ctx)
            p.stop()
        return 0
    if cmd == "orderspage":  # debug: save Your Orders page
        p, ctx, page, vb = browser()
        try:
            page.goto("https://www.amazon.com/your-orders/orders?timeFilter=last30", wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            shot(page, "orderspage")
        finally:
            vb.close(ctx)
            p.stop()
        return 0
    if cmd == "fixorders":  # re-read today's order numbers per store for orders recorded today
        rules = load(RULES, None)
        st = load(STATE, {})
        p, ctx, page, vb = browser()
        try:
            seen = set()
            for o in st.get("orders", []):
                if o.get("placed") == NOW.date().isoformat():
                    n = find_today_order(page, o["store"], rules, exclude=seen, total=o.get("total"))
                    log(o["store"], o["order"], "->", n)
                    if n:
                        o["order"] = n[0]
                        seen.update(n)
                        for v in st.get("catalog", {}).values():
                            if v.get("store") == o["store"] and v.get("date") == o["placed"]:
                                v["orders"] = n
            save(STATE, st)
        finally:
            vb.close(ctx)
            p.stop()
        return 0
    if cmd == "deliveries":
        return cmd_deliveries()
    if cmd == "audit":
        return cmd_audit(int(a[1]) if len(a) > 1 else 60)
    if cmd == "resolve" and len(a) > 1:
        p, ctx, page, vb = browser()
        try:
            ensure_signed_in(page)
            print(json.dumps(resolve(page, a[1]), indent=1))
        finally:
            vb.close(ctx)
            p.stop()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
