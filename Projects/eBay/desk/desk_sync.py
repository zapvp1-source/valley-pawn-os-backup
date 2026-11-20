#!/usr/bin/env python3
"""eBay Desk — sync and rules logic (design v2, 2026-11-19). Companion to desk_core.py.

OFFLINE BY CONSTRUCTION, same as desk_core: no network import, no token import. Every function
turns data into a PLAN; a separate runner (not in this file) is the only thing allowed to send.

  takedown_plan   Bravo "sold today" rows + live eBay listings -> listings to end (counter sale)
  ring_plan       paid eBay lines + Bravo sold data            -> ring / already rung / exception
  classify_message, render_reply                               -> auto-send or draft-for-store
  shipping_mode, price_floor, listing_gate                     -> the listing standards
"""
import re
from datetime import date, datetime, timedelta
from desk_core import bravo_code

# ---------------------------------------------------------------- counter sale -> end eBay listing
TAKEDOWN_CAP_PER_RUN = 10          # more than this in one pull = bad data, not a busy day: halt
TAKEDOWN_MAX_AGE_DAYS = 2


def live_index(active_by_store):
    """{store: [ {ItemID, SKU, Title}, ... ]} -> {bravo number: (store, ItemID, Title)}.
    A number that appears on two live listings is ambiguous and is left out (returned separately)."""
    idx, dup = {}, set()
    for store, items in active_by_store.items():
        for it in items:
            code = bravo_code(it.get("SKU"), it.get("Title"))
            if not code:
                continue
            if code in idx:
                dup.add(code)
            idx[code] = (store, it.get("ItemID"), it.get("Title", ""))
    for c in dup:
        idx.pop(c, None)
    return idx, sorted(dup)


def takedown_plan(index, bravo_sold, ebay_sold_codes, today, already_ended=()):
    """bravo_sold: {number: {'date': date, 'price': float}} from the Bravo sold pull.
    Ends a listing only when Bravo shows the item SOLD in the last TAKEDOWN_MAX_AGE_DAYS, the item
    is live on eBay, it did NOT sell on eBay (that sale is rung, not ended), and it was not already
    ended. Returns {'end': [...], 'halt': reason or ''}. Over the cap -> end nothing."""
    skip = {c.upper() for c in ebay_sold_codes} | {c.upper() for c in already_ended}
    end = []
    for code, hit in sorted(bravo_sold.items()):
        if code not in index or code in skip:
            continue
        age = (today - hit["date"]).days
        if age < 0 or age > TAKEDOWN_MAX_AGE_DAYS:
            continue
        store, item_id, title = index[code]
        end.append({"store": store, "item_id": item_id, "bravo_no": code, "title": title,
                    "sold_in_store": hit["date"].isoformat(), "reason": "NotAvailable"})
    if len(end) > TAKEDOWN_CAP_PER_RUN:
        return {"end": [], "halt": "%d listings to end in one run exceeds the cap of %d; nothing ended"
                % (len(end), TAKEDOWN_CAP_PER_RUN), "held": end}
    return {"end": end, "halt": ""}


# ---------------------------------------------------------------- eBay sale -> ring in Bravo
def ring_plan(lines, bravo_sold, ledger=None):
    """lines: paid eBay lines (desk_core.parse_get_orders). ledger: {key: state} of earlier runs.
    One decision per line, keyed store|line_id so a line can never be rung twice:
      verified   Bravo already shows the item sold on/after the eBay paid date (rung, by us or by hand)
      ring       has a Bravo number, not in Bravo sold data, not rung by us before
      recheck    we rang it earlier but Bravo's sold data does not show it yet
      exception  no Bravo number, or Bravo shows it sold BEFORE the eBay sale (sold at the counter first)"""
    ledger = ledger or {}
    out = []
    for ln in lines:
        key = "%s|%s" % (ln["store"], ln["line_id"])
        row = dict(ln, key=key)
        paid_day = (datetime.fromisoformat(ln["paid_utc"]) - timedelta(hours=5)).date()
        hit = bravo_sold.get(ln.get("bravo_no") or "")
        if not ln.get("bravo_no"):
            row.update(action="exception", why="no Bravo item number on the listing")
        elif hit and hit["date"] >= paid_day:
            row.update(action="verified", bravo_date=hit["date"].isoformat(),
                       price_gap=round(hit["price"] - ln["ring_price"], 2))
        elif hit and hit["date"] < paid_day and (paid_day - hit["date"]).days <= 30:
            row.update(action="exception", why="Bravo shows this item sold %s, before the eBay sale" % hit["date"])
        elif ledger.get(key) in ("rung", "recheck"):
            row.update(action="recheck")
        else:
            row.update(action="ring")
        out.append(row)
    return out


# ---------------------------------------------------------------- buyer messages
_DRAFT = [  # checked first: anything here is never auto-answered
    ("offer", r"\$\s?\d|\b\d{2,5}\s?(\?|dollars|bucks|shipped|obo)|^\s*\d{2,5}\s*\??\s*$|\b(offer(ing)?|lowest|least|best price|discount|"
              r"(can|could|would|will) (you|u) (do|take|accept|go)|i('ll| will| would| can)? (pay|go|do|give)|negotiable|lower|cheaper|deal|firm|"
              r"how about|what about)\b"),
    ("condition", r"\b(condition|scratch|crack|damage|work(s|ing)?|tested|function|battery|defect|broken|wear|dent|chip)\b"),
    ("authentic", r"\b(authentic|genuine|real|fake|counterfeit|replica|certificate|appraisal|karat|\d+k\b|grams?|weight|carat)\b"),
    ("order", r"\b(tracking|where is|hasn'?t arrived|not received|received|package|delivered|delivery estimate|movement|refund|"
              r"return(ing)? (it|this)|return date|cancel|wrong item|not as described|broken on arrival|missing|feedback|purchased|bought|my order)\b"),
    ("request", r"\b(send|add|more|another) (me )?(a |some |more )?(pic|pics|picture|pictures|photo|photos|video)|\b(video|pictures?|photos?) of\b|\bpassword|serial|imei|unlocked?\b"),
    ("contact", r"\b(phone|call me|text me|email me|paypal|zelle|venmo|cash ?app|outside (of )?ebay|pick ?up|local)\b"),
]
_AUTO = [
    ("available", r"\b(still available|available\??|still have|in stock|still for sale)\b"),
    ("combine", r"\b(combine|combined) (shipping|postage)|ship (them )?together|bundle shipping\b"),
    ("shipping", r"\b(shipping|ship to|how (long|fast|soon)|when (will|would) (it|this) ship|delivery|postage|handling time)\b"),
    ("returns", r"\b(return policy|returns?|can i return|refund policy)\b"),
]
TEMPLATES = {
    "available": "Hi, yes, this is available and ready to ship. {ship_line} Thanks for looking. - Valley Pawn",
    "shipping": "Hi, thanks for asking. {ship_line} Tracking is uploaded as soon as it ships. - Valley Pawn",
    "combine": "Hi, yes. Add the items to your cart and send them as one order and we will ship them together; any shipping overpaid is refunded after it ships. - Valley Pawn",
    "returns": "Hi, this item has a {return_days}-day return policy. Details are in the Shipping and returns section of the listing. - Valley Pawn",
    "after_hours": "Hi, thanks for your message. Our team is in at 10 AM Eastern and will answer you then. - Valley Pawn",
}


def classify_message(text, has_order=False, is_precious_metal=False, store_open=True):
    """-> ('auto', template key) or ('draft', reason). Conservative: one doubt = draft.
    Hard rules: never invite an offer, never quote a markdown, never discuss precious-metal price."""
    t = " ".join((text or "").lower().split())
    if has_order:
        return ("draft", "message on a sold order")
    if "?" not in t and len(t) <= 80 and re.search(r"^(ok(ay)?|thanks?( you)?|thank you|thx|ty|cheers|great|perfect|got it|merci|gracias|much appreciated|will do)\b", t) \
            and not re.search(r"\d", t):
        return ("none", "thanks, no reply needed")
    for reason, pat in _DRAFT:
        if re.search(pat, t):
            return ("draft", reason)
    if is_precious_metal and re.search(r"\b(price|cost|how much|\$)\b", t):
        return ("draft", "price question on precious metal")
    hits = [k for k, pat in _AUTO if re.search(pat, t)]
    if "combine" in hits and len(t) <= 300:
        return ("auto", "combine")
    if len(hits) == 1 and len(t) <= 300:
        return ("auto", hits[0])
    if len(hits) == 2 and set(hits) == {"available", "shipping"} and len(t) <= 300:
        return ("auto", "available")
    return ("auto", "after_hours") if not store_open else ("draft", "not a standard question")


def render_reply(key, listing):
    """listing: {'free_shipping': bool, 'handling_days': int, 'return_days': int}."""
    days = int(listing.get("handling_days") or 1)
    ship = ("Shipping is free" if listing.get("free_shipping") else
            "Shipping is calculated to your ZIP code and shows at checkout")
    ship_line = "%s and it ships within %d business day%s of payment." % (ship, days, "" if days == 1 else "s")
    return TEMPLATES[key].format(ship_line=ship_line, return_days=int(listing.get("return_days") or 30))


# ---------------------------------------------------------------- listing standards
HEAVY_LB = 5.0
SMALL_LIGHT = ("jewelry", "watch", "phone", "video game", "game", "coin", "card", "small electronics", "camera lens")
MIN_SINGLE_PRICE = 40.00
RESTRICTED = re.compile(r"\b(firearm|pistol|rifle|shotgun|revolver|handgun|ammo|ammunition|suppressor|silencer|receiver|magazine \d+ ?rd)\b", re.I)


def shipping_mode(category, weight_lb):
    """One rule, the store does not choose: 'free' (label built into price) for small and light,
    'calculated' (buyer pays by distance) for anything at or over HEAVY_LB or not on the small list."""
    if weight_lb is not None and weight_lb >= HEAVY_LB:
        return "calculated"
    c = (category or "").lower()
    if any(k in c for k in SMALL_LIGHT) and (weight_lb is None or weight_lb < HEAVY_LB):
        return "free"
    return "calculated" if weight_lb is None else "free"


def price_floor(cost, label_cost, fee_rate=0.15, per_order_fee=0.40, packing=1.50, bravo_created=False):
    """Lowest price that does not lose money: price - fees - label - packing - cost >= 0.
    label_cost is 0 for calculated shipping (buyer pays it). Bravo's 5% counts while Bravo-created."""
    rate = fee_rate + (0.05 if bravo_created else 0.0)
    return round((cost + label_cost + packing + per_order_fee) / (1.0 - rate) + 0.004, 2)


def listing_gate(title, category, price, cost, weight_lb, is_lot=False, label_cost=0.0, bravo_created=False):
    """-> (ok, [reasons]). Refuses restricted items, singles under the minimum, and prices under the floor."""
    why = []
    if RESTRICTED.search("%s %s" % (title or "", category or "")):
        why.append("restricted item: not listed on eBay")
    if price < MIN_SINGLE_PRICE and not is_lot:
        why.append("single item under $%.0f: sell in store or lot it" % MIN_SINGLE_PRICE)
    mode = shipping_mode(category, weight_lb)
    floor = price_floor(cost, label_cost if mode == "free" else 0.0, bravo_created=bravo_created)
    if price < floor:
        why.append("price $%.2f is under the floor $%.2f" % (price, floor))
    return (not why, why)
