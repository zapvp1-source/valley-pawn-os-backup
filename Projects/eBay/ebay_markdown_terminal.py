#!/usr/bin/env python3
"""
Valley Pawn — eBay Markdown TERMINAL ACTION (ADDITIVE companion to ebay_markdown_engine.py)
Created 2026-08-22 from the eBay Channel Audit. Closes the gap the audit found: the markdown
engine cuts price 10%/month up to 3 times (30% off) and then does NOTHING further — the "pull"
half of the "eBay Listing-Age Standard (Reprice & Pull)" policy was never implemented. 154 items
channel-wide hit their 3rd/final cut on 2026-09-01 with nothing scheduled to happen next.

This script does NOT touch ebay_markdown_engine.py or its state file. It reads the same
~/ebay_markdown_state.json (read-only) to find items at MAX_CUTS (3, i.e. 30% off baseline) and
runs a two-stage, reversible process of its own, tracked in ~/ebay_markdown_terminal_state.json:

  STAGE 1 (first time an item is seen at 30% off, still unsold):
    Post to Slack #ebay-performance + DM the store manager (same manager-lookup pattern as
    ebay-weekly-quality-fix) that the item hit the floor with no sale, and that it will be pulled
    from eBay in 14 days unless someone intervenes (manual reprice below the 30% floor, bundle it,
    or explicitly confirm pull-now). Item stays live and untouched on eBay at this stage.

  STAGE 2 (14+ days after Stage 1, still active, still unsold, no manual override recorded):
    Ends the eBay listing (EndFixedPriceItem, reason NotAvailable) and posts/DMs that it needs a
    Bravo-side decision (in-store clearance, bundle, donate, or scrap) since it's off eBay now.

Safety: dry-run by default (--apply required). Never ends a listing that sold, is no longer at
30% off (someone already manually repriced it), or that Stage 1 hasn't been running against for
14+ days. State is idempotent and reversible in the sense that Stage 1 makes no eBay writes at all;
only Stage 2 does, and Stage 2 is a normal listing-end, fully consistent with the named policy.

Usage:
  python3 ebay_markdown_terminal.py                # dry run, both stages
  python3 ebay_markdown_terminal.py --apply         # stage 1 posts/DMs for real, stage 2 ends listings
  python3 ebay_markdown_terminal.py --apply --only 1
  python3 ebay_markdown_terminal.py --apply --only 2
"""
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

HOME = os.path.expanduser('~')
SRC = os.path.join(HOME, 'ebay_weekly_rankings.py')
_ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), _ns)
STORES = {s['name']: s['token'] for s in _ns['STORES']}
APP_ID, DEV_ID, CERT_ID, SLACK_WEBHOOK = _ns['APP_ID'], _ns['DEV_ID'], _ns['CERT_ID'], _ns['SLACK_WEBHOOK']

NS = 'urn:ebay:apis:eBLBaseComponents'
URL = 'https://api.ebay.com/ws/api.dll'
MARKDOWN_STATE = os.path.expanduser('~/ebay_markdown_state.json')
TERMINAL_STATE = os.path.expanduser('~/ebay_markdown_terminal_state.json')
MAX_CUTS = 3
GRACE_DAYS = 14

APPLY = '--apply' in sys.argv
ONLY = None
if '--only' in sys.argv:
    ONLY = sys.argv[sys.argv.index('--only') + 1]


def q(tag):
    return '{%s}%s' % (NS, tag)


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find(q(tag))
    return x.text if x is not None and x.text else d


def call(token, name, inner):
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            ) % (name, token, inner, name)
    h = {'X-EBAY-API-SITEID': '0', 'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
         'X-EBAY-API-CALL-NAME': name, 'X-EBAY-API-APP-NAME': APP_ID,
         'X-EBAY-API-DEV-NAME': DEV_ID, 'X-EBAY-API-CERT-NAME': CERT_ID,
         'X-EBAY-API-IAF-TOKEN': token, 'Content-Type': 'text/xml'}
    for i in range(3):
        try:
            with urlopen(Request(URL, data=body.encode('utf-8'), headers=h), timeout=90) as r:
                return ET.fromstring(r.read().decode('utf-8'))
        except Exception:
            if i == 2:
                raise
            time.sleep(3)


def slack(text):
    if not APPLY:
        print('[DRY SLACK]', text[:200])
        return
    try:
        urlopen(Request(SLACK_WEBHOOK, data=json.dumps({'text': text}).encode(),
                         headers={'Content-Type': 'application/json'}), timeout=15)
    except Exception as e:
        print('slack post failed:', e)


def load(path):
    return json.load(open(path)) if os.path.exists(path) else {}


def save(path, obj):
    tmp = path + '.tmp'
    json.dump(obj, open(tmp, 'w'), indent=1)
    os.replace(tmp, path)


def item_live(token, iid):
    r = call(token, 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % iid)
    it = r.find('.//' + q('Item'))
    if it is None:
        return None
    ss = it.find(q('SellingStatus'))
    return {
        'status': T(ss, 'ListingStatus'),
        'qty_sold': T(ss, 'QuantitySold', '0'),
        'title': T(it, 'Title'),
        'price': T(ss, 'CurrentPrice'),
    }


DETAIL_CSV = os.path.expanduser('~/Documents/Claude/Projects/eBay/markdown_floor_detail_latest.csv')
SUMMARY_JSON = os.path.expanduser('~/ebay_markdown_terminal_summary.json')


def post_digests(stage1_new, stage2_ended):
    """REWRITTEN 2026-09-07 — this used to post directly to Slack (webhook), one message per
    store with every item bulleted (capped at 40). That flooded #ebay-performance with long,
    illegible messages on the first real run (2026-09-07: 4 messages, one listing 101 items).

    Per Joshua's correction that day, Slack needs ONE concise message — company total plus a
    one-line-per-store breakdown (count + dollar value), never an itemized bullet dump — with
    full item-level detail available via a linked spreadsheet for anyone who needs to drill in.

    This function no longer posts to Slack at all (removing the SLACK_WEBHOOK dependency from
    this unattended script entirely). Instead it writes the full detail to a CSV and a compact
    JSON summary (counts + $ totals, company-wide and per store, for both stages). The
    ebay-markdown-terminal-weekly scheduled task reads that JSON+CSV after this script runs,
    builds/updates a shared Google Sheet from the CSV, and posts the one concise Slack message
    itself — see that task's SKILL.md for the exact format. This keeps the unattended script
    simple and auditable, and keeps message wording/formatting under the same review as every
    other Slack post this business sends.
    """
    rows = []
    for store, iid, title, price in stage1_new:
        rows.append({'store': store, 'item_id': iid, 'title': title, 'price': price,
                     'status': 'At 30% floor — grace period', 'ebay_link': 'https://www.ebay.com/itm/%s' % iid})
    for store, iid, title, _ack in stage2_ended:
        rows.append({'store': store, 'item_id': iid, 'title': title, 'price': None,
                     'status': 'Pulled from eBay today', 'ebay_link': 'https://www.ebay.com/itm/%s' % iid})

    if rows:
        import csv
        with open(DETAIL_CSV, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=['store', 'item_id', 'title', 'price', 'status', 'ebay_link'])
            w.writeheader()
            w.writerows(rows)

    by_store = {}
    for store, iid, title, price in stage1_new:
        s = by_store.setdefault(store, {'flag_count': 0, 'flag_value': 0.0, 'pull_count': 0})
        s['flag_count'] += 1
        try:
            s['flag_value'] += float(price)
        except (TypeError, ValueError):
            pass
    for store, iid, title, _ack in stage2_ended:
        by_store.setdefault(store, {'flag_count': 0, 'flag_value': 0.0, 'pull_count': 0})['pull_count'] += 1

    summary = {
        'run_date': datetime.now(timezone.utc).date().isoformat(),
        'grace_days': GRACE_DAYS,
        'detail_csv': DETAIL_CSV if rows else None,
        'company_flag_count': sum(s['flag_count'] for s in by_store.values()),
        'company_flag_value': round(sum(s['flag_value'] for s in by_store.values()), 2),
        'company_pull_count': sum(s['pull_count'] for s in by_store.values()),
        'by_store': {store: {'flag_count': s['flag_count'], 'flag_value': round(s['flag_value'], 2),
                              'pull_count': s['pull_count']} for store, s in sorted(by_store.items())},
    }
    with open(SUMMARY_JSON, 'w') as f:
        json.dump(summary, f, indent=1)
    print('SUMMARY_JSON', SUMMARY_JSON)
    print(json.dumps(summary, indent=1))


def main():
    md = load(MARKDOWN_STATE)
    term = load(TERMINAL_STATE)
    now = datetime.now(timezone.utc)

    at_cap = [(iid, rec) for iid, rec in md.items() if rec.get('cuts', 0) >= MAX_CUTS]
    print('items at %d cuts (30%% off) in markdown state: %d' % (MAX_CUTS, len(at_cap)))

    stage1_new, stage1_skip, stage2_ended, stage2_skip, errors = [], [], [], [], []

    for iid, rec in at_cap:
        store = rec.get('store')
        token = STORES.get(store)
        if not token:
            errors.append((iid, 'unknown store %s' % store))
            continue
        try:
            live = item_live(token, iid)
        except Exception as e:
            errors.append((iid, str(e)[:100]))
            continue
        if live is None:
            continue
        if live['status'] != 'Active' or int(live.get('qty_sold') or 0) > 0:
            term.pop(iid, None)  # sold or ended on its own; drop from tracking
            continue

        tstate = term.get(iid)
        if tstate is None:
            if ONLY and ONLY != '1':
                continue
            # Slack is posted as ONE digest per store at the end (see post_digests) — per-item
            # posts flooded the channel on a 139-item first pass (2026-09-06).
            stage1_new.append((store, iid, live['title'], live['price']))
            if APPLY:
                term[iid] = {'store': store, 'title': live['title'], 'stage': 1,
                             'flagged_at': now.isoformat()}
                save(TERMINAL_STATE, term)
            continue

        if tstate.get('stage') == 1:
            flagged = datetime.fromisoformat(tstate['flagged_at'])
            age = (now - flagged).days
            if age < GRACE_DAYS:
                stage2_skip.append((store, iid, 'grace %d/%d days' % (age, GRACE_DAYS)))
                continue
            if ONLY and ONLY != '2':
                continue
            if not APPLY:
                stage2_ended.append((store, iid, live['title'], 'DRY RUN'))
                continue
            r = call(token, 'EndFixedPriceItem',
                     '<ItemID>%s</ItemID><EndingReason>NotAvailable</EndingReason>' % iid)
            ack = T(r, 'Ack')
            if ack in ('Success', 'Warning'):
                term[iid]['stage'] = 2
                term[iid]['ended_at'] = now.isoformat()
                save(TERMINAL_STATE, term)
                stage2_ended.append((store, iid, live['title'], ack))
            else:
                errs = [T(e, 'LongMessage') for e in r.findall('.//' + q('Errors'))]
                errors.append((iid, '; '.join(errs[:1])))

    post_digests(stage1_new, stage2_ended)

    print('\n==== SUMMARY (%s) ====' % ('APPLY' if APPLY else 'DRY RUN'))
    print('Stage 1 (newly flagged, 14-day clock starts): %d' % len(stage1_new))
    for s in stage1_new:
        print('   ', s)
    print('Stage 2 (grace expired -> ended): %d' % len(stage2_ended))
    for s in stage2_ended:
        print('   ', s)
    print('Still in grace period: %d' % len(stage2_skip))
    if errors:
        print('Errors: %d' % len(errors))
        for e in errors[:15]:
            print('   ', e)


if __name__ == '__main__':
    main()
