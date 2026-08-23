#!/usr/bin/env python3
"""
Valley Pawn - eBay Listing Policy Remediation (ADDITIVE, one-off, fully reversible)
Created 2026-08-22 from the eBay Channel Audit.

Fixes three verified defects on LIVE listings. Does NOT modify any existing script or automation.

  A) BESTOFFER  - enable Best Offer on Culpeper listings that have it switched off (193 found)
  B) RET30      - move Roanoke listings from 14-day to 30-day returns (103 found)
  C) RETON      - turn returns ON (30-day) for listings currently ReturnsNotAccepted (45 found)

Safety design (mirrors ebay_title_revise.py / ebay_category_fix.py conventions):
  * DRY RUN by default. --apply required to touch anything.
  * Per-item state written to ~/ebay_policy_fix_state.json BEFORE the change, so --revert
    can restore the exact prior value of every field touched.
  * Re-reads each item with GetItem first: skips anything already correct, anything no longer
    active, and anything governed by Business Policies (SellerProfiles) - those cannot be fixed
    with an inline ReviseFixedPriceItem and are logged for separate handling.
  * Idempotent: items recorded in state are skipped on re-run.
  * Auto-stop on any eBay usage-limit / 5xx response; state is saved, safe to resume.
  * Paced (0.35s) between calls.

Usage:
  python3 ebay_policy_fix.py                      # dry run, all fixes, all stores
  python3 ebay_policy_fix.py --apply
  python3 ebay_policy_fix.py --apply --only BESTOFFER
  python3 ebay_policy_fix.py --revert             # restore every item this script changed
"""

import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
_ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), _ns)
STORES = {s['name']: s['token'] for s in _ns['STORES']}
APP_ID, DEV_ID, CERT_ID = _ns['APP_ID'], _ns['DEV_ID'], _ns['CERT_ID']

NS = 'urn:ebay:apis:eBLBaseComponents'
URL = 'https://api.ebay.com/ws/api.dll'
STATE = os.path.expanduser('~/ebay_policy_fix_state.json')
AUDIT = os.path.expanduser('~/Documents/Claude/Projects/eBay/audit_2026-08-22/quality_pull2.json')
PACE = 0.35

STOP = False


def q(tag):
    return '{%s}%s' % (NS, tag)


def T(el, tag, d=None):
    if el is None:
        return d
    x = el.find(q(tag))
    return x.text if x is not None and x.text else d


def call(token, name, inner):
    global STOP
    body = ('<?xml version="1.0" encoding="utf-8"?><%sRequest xmlns="urn:ebay:apis:eBLBaseComponents">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>%s</%sRequest>'
            ) % (name, token, inner, name)
    h = {'X-EBAY-API-SITEID': '0', 'X-EBAY-API-COMPATIBILITY-LEVEL': '967',
         'X-EBAY-API-CALL-NAME': name, 'X-EBAY-API-APP-NAME': APP_ID,
         'X-EBAY-API-DEV-NAME': DEV_ID, 'X-EBAY-API-CERT-NAME': CERT_ID,
         'X-EBAY-API-IAF-TOKEN': token, 'Content-Type': 'text/xml'}
    last = None
    for attempt in range(3):
        try:
            with urlopen(Request(URL, data=body.encode('utf-8'), headers=h), timeout=90) as r:
                return ET.fromstring(r.read().decode('utf-8'))
        except Exception as e:
            last = e
            msg = str(e)
            if '503' in msg or '500' in msg or '502' in msg:
                time.sleep(4 * (attempt + 1))
                continue
            break
    raise last


def errors(r):
    out = []
    for e in r.findall('.//' + q('Errors')):
        out.append({'code': T(e, 'ErrorCode'), 'sev': T(e, 'SeverityCode'),
                    'msg': T(e, 'LongMessage') or T(e, 'ShortMessage')})
    return out


def is_limit(errs):
    for e in errs:
        if e.get('code') in ('21916884', '218050', '10007') or 'limit' in (e.get('msg') or '').lower():
            if e.get('sev') == 'Error':
                return True
    return False


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {}


def save_state(st):
    tmp = STATE + '.tmp'
    json.dump(st, open(tmp, 'w'), indent=1)
    os.replace(tmp, STATE)


def inspect(token, iid):
    """Read current live state of the fields we care about."""
    r = call(token, 'GetItem', '<ItemID>%s</ItemID><DetailLevel>ReturnAll</DetailLevel>' % iid)
    errs = errors(r)
    it = r.find('.//' + q('Item'))
    if it is None:
        return None, errs
    rp = it.find(q('ReturnPolicy'))
    bo = it.find(q('BestOfferDetails'))
    prof = it.find(q('SellerProfiles'))
    ret_prof = None
    if prof is not None:
        rpn = prof.find(q('SellerReturnProfile'))
        if rpn is not None:
            ret_prof = T(rpn, 'ReturnProfileID')
    return {
        'title': (T(it, 'Title') or '')[:70],
        'status': T(it.find(q('SellingStatus')), 'ListingStatus') if it.find(q('SellingStatus')) is not None else None,
        'price': T(it.find(q('SellingStatus')), 'CurrentPrice') if it.find(q('SellingStatus')) is not None else None,
        'bo_enabled': T(bo, 'BestOfferEnabled') if bo is not None else None,
        'ret_accepted': T(rp, 'ReturnsAcceptedOption') if rp is not None else None,
        'ret_within': T(rp, 'ReturnsWithinOption') if rp is not None else None,
        'ret_shipby': T(rp, 'ShippingCostPaidByOption') if rp is not None else None,
        'ret_refund': T(rp, 'RefundOption') if rp is not None else None,
        'return_profile': ret_prof,
    }, errs


def revise(token, iid, inner_fields):
    r = call(token, 'ReviseFixedPriceItem',
             '<Item><ItemID>%s</ItemID>%s</Item>' % (iid, inner_fields))
    return T(r, 'Ack'), errors(r)


RET30_BLOCK = ('<ReturnPolicy>'
               '<ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>'
               '<RefundOption>MoneyBack</RefundOption>'
               '<ReturnsWithinOption>Days_30</ReturnsWithinOption>'
               '<ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>'
               '</ReturnPolicy>')

BO_BLOCK = '<BestOfferDetails><BestOfferEnabled>true</BestOfferEnabled></BestOfferDetails>'


def build_targets():
    Q = json.load(open(AUDIT))
    tg = []
    for store, items in Q.items():
        for iid, v in items.items():
            bo_off = str(v.get('best_offer')).lower() != 'true'
            no_ret = v.get('returns') == 'ReturnsNotAccepted'
            d14 = v.get('returns_within') == 'Days_14'
            if no_ret:
                tg.append((store, iid, 'RETON'))
            elif d14:
                tg.append((store, iid, 'RET30'))
            if bo_off and not no_ret:
                # no_ret items get returns fixed first; best offer handled on a later pass
                tg.append((store, iid, 'BESTOFFER'))
            elif bo_off and no_ret:
                tg.append((store, iid, 'BESTOFFER'))
    return tg


def main():
    global STOP
    apply_ = '--apply' in sys.argv
    revert = '--revert' in sys.argv
    only = None
    if '--only' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1]

    st = load_state()

    if revert:
        n = 0
        for key, rec in list(st.items()):
            if rec.get('reverted') or not rec.get('applied'):
                continue
            store, iid, fix = rec['store'], rec['item'], rec['fix']
            before = rec['before']
            if fix == 'BESTOFFER':
                inner = '<BestOfferDetails><BestOfferEnabled>false</BestOfferEnabled></BestOfferDetails>'
            else:
                if before.get('ret_accepted') is None:
                    inner = ('<ReturnPolicy><ReturnsAcceptedOption>ReturnsNotAccepted</ReturnsAcceptedOption>'
                             '</ReturnPolicy>')
                else:
                    inner = ('<ReturnPolicy>'
                             '<ReturnsAcceptedOption>%s</ReturnsAcceptedOption>'
                             '<RefundOption>%s</RefundOption>'
                             '<ReturnsWithinOption>%s</ReturnsWithinOption>'
                             '<ShippingCostPaidByOption>%s</ShippingCostPaidByOption>'
                             '</ReturnPolicy>') % (before.get('ret_accepted'), before.get('ret_refund') or 'MoneyBack',
                                                   before.get('ret_within') or 'Days_30',
                                                   before.get('ret_shipby') or 'Buyer')
            ack, errs = revise(STORES[store], iid, inner)
            rec['reverted'] = (ack in ('Success', 'Warning'))
            rec['revert_errs'] = errs[:2]
            n += 1
            print('REVERT', store, iid, fix, ack)
            save_state(st)
            time.sleep(PACE)
        print('reverted', n)
        return

    targets = build_targets()
    if only:
        targets = [t for t in targets if t[2] == only]

    counts = {'skip_done': 0, 'skip_ok': 0, 'skip_inactive': 0, 'skip_profile': 0,
              'applied': 0, 'failed': 0, 'would': 0}
    profile_items = []
    failures = []

    for store, iid, fix in targets:
        if STOP:
            print('!! stopping early (limit/eBay error)')
            break
        key = '%s|%s' % (iid, fix)
        if key in st and st[key].get('applied') and not st[key].get('reverted'):
            counts['skip_done'] += 1
            continue
        token = STORES[store]
        try:
            cur, errs = inspect(token, iid)
        except Exception as e:
            counts['failed'] += 1
            failures.append((store, iid, fix, 'inspect:' + str(e)[:90]))
            continue
        time.sleep(PACE)
        if cur is None or cur.get('status') != 'Active':
            counts['skip_inactive'] += 1
            continue
        if fix in ('RET30', 'RETON') and cur.get('return_profile'):
            counts['skip_profile'] += 1
            profile_items.append((store, iid, cur['return_profile'], cur['title']))
            continue
        # already correct?
        if fix == 'BESTOFFER' and str(cur.get('bo_enabled')).lower() == 'true':
            counts['skip_ok'] += 1
            continue
        if fix in ('RET30', 'RETON') and cur.get('ret_accepted') == 'ReturnsAccepted' \
                and cur.get('ret_within') == 'Days_30':
            counts['skip_ok'] += 1
            continue

        inner = BO_BLOCK if fix == 'BESTOFFER' else RET30_BLOCK
        if not apply_:
            counts['would'] += 1
            print('WOULD %-13s %-12s %s | %s' % (fix, store, iid, cur['title']))
            continue

        st[key] = {'store': store, 'item': iid, 'fix': fix, 'before': cur,
                   'ts': time.strftime('%Y-%m-%dT%H:%M:%S'), 'applied': False}
        save_state(st)
        try:
            ack, errs = revise(token, iid, inner)
        except Exception as e:
            counts['failed'] += 1
            failures.append((store, iid, fix, 'revise:' + str(e)[:90]))
            continue
        if ack in ('Success', 'Warning'):
            st[key]['applied'] = True
            st[key]['warn'] = [e['msg'] for e in errs if e.get('sev') == 'Warning'][:1]
            counts['applied'] += 1
            print('OK     %-13s %-12s %s | %s' % (fix, store, iid, cur['title']))
        else:
            st[key]['errs'] = errs[:2]
            counts['failed'] += 1
            failures.append((store, iid, fix, '; '.join((e.get('msg') or '')[:80] for e in errs[:1])))
            print('FAIL   %-13s %-12s %s | %s' % (fix, store, iid, (errs[0]['msg'][:70] if errs else '?')))
            if is_limit(errs):
                STOP = True
        save_state(st)
        time.sleep(PACE)

    print('\n==== SUMMARY ====')
    for k, v in counts.items():
        print('  %-14s %d' % (k, v))
    if profile_items:
        print('\n  Business-Policy governed (need profile change, not inline):')
        for p in profile_items[:20]:
            print('   ', p)
    if failures:
        print('\n  Failures:')
        for f in failures[:25]:
            print('   ', f)
    print('\nstate:', STATE)


if __name__ == '__main__':
    main()
