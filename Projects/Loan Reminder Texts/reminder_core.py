#!/usr/bin/env python3
"""Loan / layaway reminder texts — planning core. OFFLINE: there is no send function in this file
and no network import. It turns a Bravo open-loan list + a phone/consent list into a daily PLAN.
Python 3.9 stdlib only."""
import re
from datetime import date, datetime, timedelta

# Schedule copied from Bravo's Schedule Mobile Event screen, read in all 5 stores 2026-11-18.
# Roanoke gets the same schedule as the other four (Joshua 11/18).
def loan_kind(due, today):
    """Which loan reminder is due today, or None. 1 day before; 1 day after; then every Friday while past due."""
    d = (today - due).days
    if d == -1: return "courtesy"
    if d == 1: return "past_due"
    if d > 1 and today.weekday() == 4: return "past_due"
    return None


def layaway_kind(next_due, today):
    """Layaway notices: 5 days and 1 day before the next due date; every 5 days while late."""
    d = (today - next_due).days
    if d in (-5, -1): return "layaway_notice"
    if d > 0 and d % 5 == 0: return "layaway_late"
    return None


TEMPLATES = {   # loan wording APPROVED by Joshua 2026-11-18 12:43 PM ("looks good"); layaway wording not drafted yet
    "courtesy": "Valley Pawn {store}: your loan{s} {tickets} {is_are} due {due}. Pay in store or in the MobilePawn app: thevalleypawn.com/app Reply STOP to opt out.",
    "past_due": "Valley Pawn {store}: your loan{s} {tickets} {is_are} past due. Call or text us here, or pay in the MobilePawn app: thevalleypawn.com/app Reply STOP to opt out.",
}
LIVE_DISPOSITIONS = {"ON LOAN"}          # POLICE LOAN HOLD / COURTESY HOLD are never texted


def norm_name(n):
    return re.sub(r"[^a-z]", "", (n or "").lower())


def phone10(p):
    d = re.sub(r"\D", "", p or "")
    if len(d) == 11 and d.startswith("1"):
        d = d[1:]
    return d if len(d) == 10 and d[0] not in "01" else ""


def parse_date(s):
    for f in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
        try:
            return datetime.strptime((s or "").strip().split(" ")[0], f).date()
        except ValueError:
            pass
    return None


def tickets_from_rows(rows):
    """Bravo rows are per ITEM. Collapse to one record per ticket."""
    t = {}
    for r in rows:
        k = (r.get("Ticket Number") or "").strip()
        if k and k not in t:
            t[k] = {"ticket": k, "customer": (r.get("Customer") or "").strip(), "due": parse_date(r.get("Due Date")),
                    "disposition": (r.get("Disposition") or "").strip().upper(), "sms": (r.get("SMS") or "").strip().upper()}
    return list(t.values())


def build_plan(store, tickets, contacts, today, sent_keys=frozenset()):
    """contacts: {norm_name: [ {'phone':..., 'dnt': bool}, ... ]}. Returns (texts, skipped).
    Do-not-text = CHEKKIT ONLY (Joshua 2026-11-18: "chekkit is the source of truth on Do not text, ignore
    bravo"). 'dnt' must be filled from Chekkit opt-outs; Bravo's SMS/DNT column is read but never used.
    One text per customer per kind per day; every ticket carries a reason when skipped."""
    groups, skipped = {}, []
    for t in tickets:
        why = None
        kind = loan_kind(t["due"], today) if t["due"] else None
        if t["disposition"] not in LIVE_DISPOSITIONS: why = "not on loan (%s)" % t["disposition"]
        elif not t["due"]: why = "no due date"
        elif not kind: continue                                   # nothing due to send today
        else:
            c = contacts.get(norm_name(t["customer"]), [])
            phones = {phone10(x.get("phone")) for x in c} - {""}
            key = "%s|%s|%s|%s" % (t["ticket"], kind, t["due"].isoformat(), today.isoformat() if kind == "past_due" else "")
            if not c: why = "no phone on file"
            elif any(x.get("dnt") for x in c): why = "opted out in Chekkit"
            elif len(phones) != 1: why = "name matches %d phone numbers" % len(phones)
            elif key in sent_keys: why = "already sent"
            else:
                groups.setdefault((phones.pop(), kind, t["due"]), []).append((t, key))
        if why: skipped.append({"store": store, "ticket": t["ticket"], "reason": why})
    texts = []
    for (phone, kind, due), items in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1])):
        n = len(items)
        body = TEMPLATES[kind].format(store=store, s="s" if n > 1 else "", is_are="are" if n > 1 else "is",
                                      tickets=", ".join("#" + i[0]["ticket"] for i in items), due=due.strftime("%-m/%-d"))
        texts.append({"store": store, "phone": phone, "kind": kind, "text": body, "keys": [i[1] for i in items], "segments": -(-len(body) // 153) if len(body) > 160 else 1})
    return texts, skipped
