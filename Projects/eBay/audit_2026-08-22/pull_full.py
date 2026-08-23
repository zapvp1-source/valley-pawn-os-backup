#!/usr/bin/env python3
# Valley Pawn eBay full audit pull - ADDITIVE, read-only. 2026-08-22
import json, os, sys, time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

SRC = os.path.expanduser('~/ebay_weekly_rankings.py')
ns = {}
exec(compile(open(SRC).read(), SRC, 'exec'), ns)
STORES = ns['STORES']; APP_ID = ns['APP_ID']; DEV_ID = ns['DEV_ID']; CERT_ID = ns['CERT_ID']
NS = 'urn:ebay:apis:eBLBaseComponents'
URL = 'https://api.ebay.com/ws/api.dll'
OUT = os.path.expanduser('~/Documents/Claude/Projects/eBay/audit_2026-08-22')

def call(token, name, inner, tries=3):
    body = ('<?xml version=\"1.0\" encoding=\"utf-8\"?>'
            '<%sRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">'
            '<RequesterCredentials><eBayAuthToken>%s</eBayAuthToken></RequesterCredentials>'
            '%s</%sRequest>') % (name, token, inner, name)
    h = {'X-EBAY-API-SITEID':'0','X-EBAY-API-COMPATIBILITY-LEVEL':'967',
         'X-EBAY-API-CALL-NAME':name,'X-EBAY-API-APP-NAME':APP_ID,
         'X-EBAY-API-DEV-NAME':DEV_ID,'X-EBAY-API-CERT-NAME':CERT_ID,
         'X-EBAY-API-IAF-TOKEN':token,'Content-Type':'text/xml'}
    for i in range(tries):
        try:
            with urlopen(Request(URL, data=body.encode('utf-8'), headers=h), timeout=120) as r:
                return ET.fromstring(r.read().decode('utf-8'))
        except Exception as e:
            if i == tries-1: raise
            time.sleep(3)

def t(el, path, d=None):
    if el is None: return d
    x = el.find(path.replace('X:', '{%s}' % NS) if 'X:' in path else path)
    return x.text if x is not None and x.text is not None else d

def q(name): return '{%s}%s' % (NS, name)

now = datetime.now(timezone.utc)

def dashboard(store):
    try:
        r = call(store['token'], 'GetSellerDashboard', '<DetailLevel>ReturnAll</DetailLevel>')
    except Exception as e:
        return {'error': str(e)}
    out = {'raw_ack': t(r, q('Ack'))}
    ss = r.find(q('SellerLevel'))
    out['seller_level'] = ss.text if ss is not None else None
    perf = r.find(q('PerformanceDashboard'))
    if perf is not None:
        out['site'] = t(perf, q('Site'))
        out['status'] = t(perf, q('Status'))
        alerts = []
        for a in perf.findall(q('Alert')):
            alerts.append({'type': t(a,q('Type')), 'severity': t(a,q('Severity')), 'text': t(a,q('Text'))})
        out['alerts'] = alerts
    ps = r.find(q('PowerSellerStatus'))
    if ps is not None:
        out['powerseller'] = {'level': t(ps,q('Level')), 'status': t(ps,q('Status'))}
    fee = r.find(q('SellerFeeDiscount'))
    if fee is not None:
        out['fee_discount'] = {'status': t(fee,q('Status')), 'text': t(fee,q('Text'))}
    # dump full xml text for anything missed
    out['xml'] = ET.tostring(r, encoding='unicode')[:20000]
    return out

def active_listings(store):
    items = []
    page = 1
    while True:
        inner = ('<ActiveList><Include>true</Include><Pagination>'
                 '<EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber>'
                 '</Pagination></ActiveList><DetailLevel>ReturnAll</DetailLevel>') % page
        r = call(store['token'], 'GetMyeBaySelling', inner)
        al = r.find(q('ActiveList'))
        if al is None: break
        got = al.findall(q('ItemArray') + '/' + q('Item')) or al.findall('.//' + q('Item'))
        for it in got:
            items.append(it)
        pr = al.find(q('PaginationResult'))
        tot = int(t(pr, q('TotalNumberOfPages'), '1') or 1)
        if page >= tot: break
        page += 1
    return items

def parse_item(it):
    def g(p, d=None):
        x = it.find(p)
        return x.text if x is not None and x.text is not None else d
    ld = it.find(q('ListingDetails'))
    sp = it.find(q('SellingStatus'))
    pd = it.find(q('PictureDetails'))
    start = t(ld, q('StartTime'))
    days = None
    if start:
        try:
            st = datetime.strptime(start[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
            days = (now - st).days
        except Exception: pass
    price = None
    for p in [q('CurrentPrice'), q('ConvertedCurrentPrice')]:
        x = sp.find(p) if sp is not None else None
        if x is not None:
            try: price = float(x.text); break
            except Exception: pass
    if price is None:
        x = it.find(q('BuyItNowPrice'))
        try: price = float(x.text) if x is not None else None
        except Exception: price = None
    title = g(q('Title'), '') or ''
    pics = len(pd.findall(q('PictureURL'))) if pd is not None else 0
    bo = it.find(q('BestOfferDetails'))
    bo_en = t(bo, q('BestOfferEnabled'))
    if bo_en is None:
        bo_en = g(q('BestOfferEnabled'))
    rp = it.find(q('ReturnPolicy'))
    return {
        'id': g(q('ItemID')),
        'title': title,
        'title_len': len(title),
        'price': price,
        'qty': int(g(q('Quantity'), '1') or 1),
        'days_live': days,
        'start': start,
        'pics': pics,
        'listing_type': t(ld, q('ListingType')) or g(q('ListingType')),
        'category': t(it.find(q('PrimaryCategory')), q('CategoryName')) if it.find(q('PrimaryCategory')) is not None else None,
        'category_id': t(it.find(q('PrimaryCategory')), q('CategoryID')) if it.find(q('PrimaryCategory')) is not None else None,
        'best_offer': bo_en,
        'watch_count': g(q('WatchCount')),
        'hit_count': g(q('HitCount')),
        'qty_sold': t(sp, q('QuantitySold')) if sp is not None else None,
        'condition': g(q('ConditionDisplayName')),
        'dispatch_max': g(q('DispatchTimeMax')),
        'returns_accepted': t(rp, q('ReturnsAcceptedOption')) if rp is not None else None,
        'returns_within': t(rp, q('ReturnsWithinOption')) if rp is not None else None,
        'shipping_cost_paid_by': t(rp, q('ShippingCostPaidByOption')) if rp is not None else None,
        'specifics_count': len(it.findall('.//' + q('NameValueList'))),
        'sku': g(q('SKU')),
    }

def sold(store, days_back=90):
    # GetSellerTransactions max 30 day window
    out = []
    end = now
    for chunk in range(0, days_back, 30):
        e = end - timedelta(days=chunk)
        s = end - timedelta(days=min(chunk+30, days_back))
        page = 1
        while True:
            inner = ('<ModTimeFrom>%s</ModTimeFrom><ModTimeTo>%s</ModTimeTo>'
                     '<IncludeContainingOrder>true</IncludeContainingOrder>'
                     '<Pagination><EntriesPerPage>200</EntriesPerPage><PageNumber>%d</PageNumber></Pagination>'
                     '<DetailLevel>ReturnAll</DetailLevel>') % (
                     s.strftime('%Y-%m-%dT%H:%M:%S.000Z'), e.strftime('%Y-%m-%dT%H:%M:%S.000Z'), page)
            r = call(store['token'], 'GetSellerTransactions', inner)
            if t(r, q('Ack')) in ('Failure',):
                break
            txs = r.findall('.//' + q('Transaction'))
            for tx in txs:
                it = tx.find(q('Item'))
                amt = t(tx, q('TransactionPrice'))
                created = t(tx, q('CreatedDate'))
                ld = it.find(q('ListingDetails')) if it is not None else None
                st = t(ld, q('StartTime')) if ld is not None else None
                dts = None
                if st and created:
                    try:
                        a = datetime.strptime(st[:19], '%Y-%m-%dT%H:%M:%S')
                        b = datetime.strptime(created[:19], '%Y-%m-%dT%H:%M:%S')
                        dts = (b-a).days
                    except Exception: pass
                fees = {}
                fa = tx.find(q('FinalValueFee'))
                out.append({
                    'item_id': t(it, q('ItemID')) if it is not None else None,
                    'title': t(it, q('Title')) if it is not None else None,
                    'category': t(it.find(q('PrimaryCategory')), q('CategoryName')) if it is not None and it.find(q('PrimaryCategory')) is not None else None,
                    'price': float(amt) if amt else None,
                    'qty': int(t(tx, q('QuantityPurchased'), '1') or 1),
                    'created': created,
                    'start': st,
                    'days_to_sell': dts,
                    'fvf': float(fa.text) if fa is not None and fa.text else None,
                    'ship_charged': t(tx.find(q('ShippingServiceSelected')), q('ShippingServiceCost')) if tx.find(q('ShippingServiceSelected')) is not None else None,
                    'ship_service': t(tx.find(q('ShippingServiceSelected')), q('ShippingService')) if tx.find(q('ShippingServiceSelected')) is not None else None,
                    'buyer_state': t(tx.find(q('Buyer')), q('UserID')) if False else None,
                })
            pr = r.find('.//' + q('PaginationResult'))
            tot = int(t(pr, q('TotalNumberOfPages'), '1') or 1)
            if page >= tot: break
            page += 1
    # dedupe by item+created
    seen = set(); ded = []
    for o in out:
        k = (o['item_id'], o['created'])
        if k in seen: continue
        seen.add(k); ded.append(o)
    return ded

result = {}
for s in STORES:
    name = s['name']
    print('== ' + name, flush=True)
    rec = {}
    try:
        rec['dashboard'] = dashboard(s)
    except Exception as e:
        rec['dashboard'] = {'error': str(e)}
    print('  dashboard done', flush=True)
    try:
        items = active_listings(s)
        rec['active'] = [parse_item(i) for i in items]
    except Exception as e:
        rec['active'] = []; rec['active_error'] = str(e)
    print('  active: %d' % len(rec.get('active', [])), flush=True)
    try:
        rec['sold90'] = sold(s, 90)
    except Exception as e:
        rec['sold90'] = []; rec['sold_error'] = str(e)
    print('  sold90: %d' % len(rec.get('sold90', [])), flush=True)
    result[name] = rec

with open(os.path.join(OUT, 'raw_pull.json'), 'w') as f:
    json.dump(result, f, indent=1)
print('DONE', flush=True)
