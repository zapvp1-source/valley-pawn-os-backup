#!/usr/bin/env python3
"""Valley Pawn eBay engine — shared helpers (Trading API, 5 store accounts).

Credentials come ONLY from ~/.vp_secrets/ebay_store_tokens.py (STORES, APP_ID, DEV_ID, CERT_ID).
This module has no side effects on import and performs no eBay writes by itself.
Python 3.9 stdlib only (runs under /usr/bin/python3 from launchd).
"""
import json, os, re, sys, time
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

sys.path.insert(0, os.path.expanduser("~/.vp_secrets"))
from ebay_store_tokens import STORES, APP_ID, DEV_ID, CERT_ID  # never hardcode

NS = "urn:ebay:apis:eBLBaseComponents"
URL = "https://api.ebay.com/ws/api.dll"
STORE_ORDER = ["Culpeper", "Roanoke", "Waynesboro", "Harrisonburg", "Lexington"]
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ENGINE_DIR, "data")
LEDGER = os.path.join(ENGINE_DIR, "ledger.jsonl")
LOCK = os.path.expanduser("~/ebay_engine.lock")

# Bravo intake code as it appears in titles, e.g. "(VAP031234)", "(VA1056309)", "(CUL12345)"
CODE_RE = re.compile(r"\(([A-Za-z]{1,4}\d{3,}[A-Za-z]?)\)")


def token_for(store):
    for s in STORES:
        if s["name"].lower() == store.lower():
            return s["token"]
    raise SystemExit("unknown store: %s" % store)


def call(tok, name, inner, retries=3):
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="%s">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            % (name, NS, tok, inner, name)).encode()
    h = {"X-EBAY-API-SITEID": "0", "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
         "X-EBAY-API-CALL-NAME": name, "X-EBAY-API-APP-NAME": APP_ID,
         "X-EBAY-API-DEV-NAME": DEV_ID, "X-EBAY-API-CERT-NAME": CERT_ID,
         "X-EBAY-API-IAF-TOKEN": tok, "Content-Type": "text/xml"}
    last = None
    for i in range(retries):
        try:
            raw = urlopen(Request(URL, data=body, headers=h), timeout=90).read().decode()
            return ET.fromstring(raw)
        except (URLError, HTTPError, ET.ParseError) as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError("%s failed after %d tries: %s" % (name, retries, last))


def t(el, path, default=None):
    v = el.findtext(".//{%s}%s" % (NS, path))
    return v if v is not None else default


def ack_ok(r):
    return r.findtext("{%s}Ack" % NS, "") in ("Success", "Warning")


def errors(r):
    out = []
    for e in r.findall(".//{%s}Errors" % NS):
        out.append((e.findtext("{%s}SeverityCode" % NS, ""), e.findtext("{%s}ShortMessage" % NS, ""),
                    e.findtext("{%s}LongMessage" % NS, "")))
    return out


def active_items(tok):
    """All active listings for one store via GetMyeBaySelling ActiveList.
    Returns list of dicts: ItemID, Title, SKU, StartPrice, StartTime, Quantity, QuantityAvailable."""
    out = []
    page = 1
    while True:
        r = call(tok, "GetMyeBaySelling",
                 "<ActiveList><Include>true</Include><IncludeNotes>false</IncludeNotes>"
                 "<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>"
                 "</ActiveList><DetailLevel>ReturnAll</DetailLevel>" % page)
        if not ack_ok(r):
            raise RuntimeError("GetMyeBaySelling: %s" % errors(r))
        for it in r.findall(".//{%s}ActiveList/{%s}ItemArray/{%s}Item" % (NS, NS, NS)):
            g = lambda p: it.findtext("{%s}%s" % (NS, p))
            out.append({
                "ItemID": g("ItemID"), "Title": g("Title") or "", "SKU": g("SKU") or "",
                "StartPrice": it.findtext(".//{%s}SellingStatus/{%s}CurrentPrice" % (NS, NS)) or g("BuyItNowPrice") or "",
                "StartTime": it.findtext(".//{%s}ListingDetails/{%s}StartTime" % (NS, NS)) or "",
                "Quantity": g("Quantity") or "", "QuantityAvailable": g("QuantityAvailable") or "",
            })
        tp = r.findtext(".//{%s}ActiveList/{%s}PaginationResult/{%s}TotalNumberOfPages" % (NS, NS, NS))
        try:
            tp = int(tp)
        except Exception:
            tp = page
        if page >= tp:
            break
        page += 1
    return out


def get_item(tok, iid):
    # IncludeItemSpecifics is REQUIRED — without it GetItem returns no ItemSpecifics node at all
    # and every listing looks like it has zero specifics (verified 2026-09-06).
    r = call(tok, "GetItem", "<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>"
                             "<IncludeItemSpecifics>true</IncludeItemSpecifics>" % iid)
    if not ack_ok(r):
        return None, errors(r)
    return r, None


def revise(tok, iid, inner_item_xml):
    """ReviseFixedPriceItem with the given <Item> children (already escaped). Returns (ok, errors)."""
    r = call(tok, "ReviseFixedPriceItem", "<Item><ItemID>%s</ItemID>%s</Item>" % (iid, inner_item_xml))
    return ack_ok(r), errors(r)


def ledger_append(entry):
    entry = dict(entry)
    entry.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%S"))
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class Lock:
    """Single engine-wide lock so two apply passes can never overlap."""
    def __enter__(self):
        if os.path.exists(LOCK):
            age = time.time() - os.path.getmtime(LOCK)
            if age < 3 * 3600:
                raise SystemExit("engine lock held (%d min old): %s" % (age // 60, LOCK))
        open(LOCK, "w").write(str(os.getpid()))
        return self

    def __exit__(self, *a):
        try:
            os.remove(LOCK)
        except OSError:
            pass
