#!/usr/bin/env python3
# Analysis pass over raw_pull.json -> summary.json + summary.md (2026-08-31 run)
import json, os, statistics
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(BASE, 'raw_pull.json')))
STORES = ['Culpeper','Waynesboro','Harrisonburg','Lexington','Roanoke']

def median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 1) if xs else None

def price_band(p):
    if p is None: return 'unknown'
    if p < 25: return '<$25'
    if p < 50: return '$25-49'
    if p < 100: return '$50-99'
    if p < 250: return '$100-249'
    if p < 500: return '$250-499'
    if p < 1000: return '$500-999'
    return '$1000+'

md_state = raw.get('_markdown_state', {}) or {}

summary = {'stores': {}, 'channel': {}}
channel_active = 0
channel_listed_value = 0.0
channel_orders = 0
channel_revenue = 0.0
channel_fees = 0.0
channel_aged90plus_count = 0
channel_aged90plus_value = 0.0
channel_unread_msgs = 0
channel_unread_return_refund = 0
channel_unread_case_dispute = 0
channel_neg_neutral_no_response = []
channel_trs_eligible = 0
channel_open_bestoffers = 0
channel_expiring_bestoffers = 0
channel_markdown_capped_no_action = []
fee_cat_totals = {}

for name in STORES:
    rec = raw.get(name, {})
    active = rec.get('active', [])
    sold90 = rec.get('sold90', [])
    fees90 = rec.get('fees90', [])
    msgfb = rec.get('msgfb', {})
    offers = rec.get('offers', {})
    store_info = rec.get('store_info', {})

    listed_value = sum((a.get('price') or 0) * (a.get('qty') or 1) for a in active)
    aging = {}
    for a in active:
        b = a.get('aging_bucket', 'unknown')
        aging[b] = aging.get(b, 0) + 1
    aged90plus_items = [a for a in active if (a.get('days_live') or 0) > 90]
    aged90plus_value = sum((a.get('price') or 0) * (a.get('qty') or 1) for a in aged90plus_items)

    best_offer_on = sum(1 for a in active if a.get('best_offer'))
    returns_accepted = sum(1 for a in active if a.get('returns_accepted') == 'ReturnsAccepted')
    no_returns = sum(1 for a in active if a.get('returns_accepted') and a.get('returns_accepted') != 'ReturnsAccepted')
    returns_window = {}
    for a in active:
        w = a.get('returns_within') or 'none'
        returns_window[w] = returns_window.get(w, 0) + 1
    ship_paid_by = {}
    for a in active:
        w = a.get('shipping_cost_paid_by') or 'unknown'
        ship_paid_by[w] = ship_paid_by.get(w, 0) + 1
    dispatch = {}
    for a in active:
        d = a.get('dispatch_max') or 'unknown'
        dispatch[d] = dispatch.get(d, 0) + 1
    avg_pics = round(sum(a.get('pics') or 0 for a in active) / len(active), 1) if active else None
    avg_specifics = round(sum(a.get('specifics_count') or 0 for a in active) / len(active), 1) if active else None

    trs_eligible = sum(1 for a in active if (a.get('dispatch_max') in ('0','1'))
                        and (a.get('returns_within') in ('Days_30','Days_60'))
                        and (a.get('shipping_cost_paid_by') == 'Seller')
                        and a.get('returns_accepted') == 'ReturnsAccepted')

    units = sum(s.get('qty') or 1 for s in sold90)
    revenue = sum((s.get('price') or 0) * (s.get('qty') or 1) for s in sold90)
    dts = median([s.get('days_to_sell') for s in sold90])
    dts_coverage = round(100.0 * sum(1 for s in sold90 if s.get('days_to_sell') is not None) / len(sold90), 1) if sold90 else None
    bands = {}
    for s in sold90:
        b = price_band(s.get('price'))
        bands[b] = bands.get(b, 0) + 1

    fee_cats = {}
    fee_total = 0.0
    for f in fees90:
        cat = f.get('category', 'other')
        amt = f.get('amt') or 0
        fee_cats[cat] = round(fee_cats.get(cat, 0) + amt, 2)
        fee_total += amt
        fee_cat_totals[cat] = round(fee_cat_totals.get(cat, 0) + amt, 2)
    fee_pct_of_rev = round(100.0 * fee_total / revenue, 1) if revenue else None

    msgs = msgfb.get('messages', [])
    unread = [m for m in msgs if (m.get('read') or '').lower() == 'false']
    unread_return_refund = sum(1 for m in unread if m.get('category') == 'return_refund')
    unread_case_dispute = sum(1 for m in unread if m.get('category') == 'case_dispute')

    fb = msgfb.get('feedback', {})
    neg_neutral = msgfb.get('neg_neutral', [])
    neg_no_response = [n for n in neg_neutral if not n.get('response')]

    bo_active = offers.get('offers', [])
    bo_expiring = [o for o in bo_active if o.get('expiring_soon')]

    # markdown-cap cross-reference: items at cuts>=3, still active, no further scheduled action
    capped_items = []
    for item_id, st in md_state.items():
        if st.get('store') != name: continue
        if (st.get('cuts') or 0) >= 3:
            still_active = any(a.get('id') == item_id for a in active)
            if still_active:
                capped_items.append({'item_id': item_id, 'baseline': st.get('baseline'), 'last_cut': st.get('last')})

    channel_markdown_capped_no_action.extend([{**c, 'store': name} for c in capped_items])

    summary['stores'][name] = {
        'active_count': len(active),
        'listed_value': round(listed_value, 2),
        'aging_buckets': aging,
        'aged_90plus_count': len(aged90plus_items),
        'aged_90plus_value': round(aged90plus_value, 2),
        'best_offer_enabled': best_offer_on,
        'best_offer_disabled': len(active) - best_offer_on,
        'returns_accepted_count': returns_accepted,
        'no_returns_count': no_returns,
        'returns_window_breakdown': returns_window,
        'shipping_cost_paid_by_breakdown': ship_paid_by,
        'dispatch_time_breakdown': dispatch,
        'avg_photos': avg_pics,
        'avg_item_specifics': avg_specifics,
        'trs_eligible_count': trs_eligible,
        'subscription': store_info.get('subscription'),
        'sold90_units': units,
        'sold90_revenue': round(revenue, 2),
        'days_to_sell_median': dts,
        'days_to_sell_coverage_pct': dts_coverage,
        'price_band_breakdown_sold': bands,
        'fees90_by_category': fee_cats,
        'fees90_total': round(fee_total, 2),
        'fee_pct_of_revenue': fee_pct_of_rev,
        'messages_total_60d': len(msgs),
        'messages_unread_60d': len(unread),
        'unread_return_refund': unread_return_refund,
        'unread_case_dispute': unread_case_dispute,
        'messages_truncated': msgfb.get('messages_truncated', False),
        'feedback_score': fb.get('score'),
        'feedback_pos_pct_1mo': fb.get('pos_pct_1mo'),
        'feedback_pos_pct_6mo': fb.get('pos_pct_6mo'),
        'feedback_pos_pct_12mo': fb.get('pos_pct_12mo'),
        'neg_neutral_count': len(neg_neutral),
        'neg_neutral_no_response_count': len(neg_no_response),
        'neg_neutral_no_response_detail': neg_no_response,
        'open_best_offers': len(bo_active),
        'best_offers_expiring_48h': len(bo_expiring),
        'markdown_capped_items_active_no_action': capped_items,
        'markdown_capped_count': len(capped_items),
    }

    channel_active += len(active)
    channel_listed_value += listed_value
    channel_orders += units
    channel_revenue += revenue
    channel_fees += fee_total
    channel_aged90plus_count += len(aged90plus_items)
    channel_aged90plus_value += aged90plus_value
    channel_unread_msgs += len(unread)
    channel_unread_return_refund += unread_return_refund
    channel_unread_case_dispute += unread_case_dispute
    channel_neg_neutral_no_response.extend([{**n, 'store': name} for n in neg_no_response])
    channel_trs_eligible += trs_eligible
    channel_open_bestoffers += len(bo_active)
    channel_expiring_bestoffers += len(bo_expiring)

summary['channel'] = {
    'active_count': channel_active,
    'listed_value': round(channel_listed_value, 2),
    'sold90_units': channel_orders,
    'sold90_revenue': round(channel_revenue, 2),
    'fees90_total': round(channel_fees, 2),
    'fee_pct_of_revenue': round(100.0 * channel_fees / channel_revenue, 1) if channel_revenue else None,
    'fees90_by_category': fee_cat_totals,
    'aged_90plus_count': channel_aged90plus_count,
    'aged_90plus_value': round(channel_aged90plus_value, 2),
    'messages_unread_60d': channel_unread_msgs,
    'unread_return_refund': channel_unread_return_refund,
    'unread_case_dispute': channel_unread_case_dispute,
    'neg_neutral_no_response_count': len(channel_neg_neutral_no_response),
    'neg_neutral_no_response_detail': channel_neg_neutral_no_response,
    'trs_eligible_count': channel_trs_eligible,
    'open_best_offers': channel_open_bestoffers,
    'best_offers_expiring_48h': channel_expiring_bestoffers,
    'markdown_capped_active_no_action_count': len(channel_markdown_capped_no_action),
    'markdown_capped_active_no_action_detail': channel_markdown_capped_no_action,
}
summary['pull_time_utc'] = raw.get('_pull_time_utc')
summary['store_errors'] = raw.get('_store_errors', {})

with open(os.path.join(BASE, 'summary.json'), 'w') as f:
    json.dump(summary, f, indent=1)

# ---- Prior run comparison (2026-08-24 partial: active/sold90count/fees90count only) ----
prior_824 = {
    'Culpeper': {'active': 301, 'sold90_count': 231, 'fees90_count': 1609},
    'Waynesboro': {'active': 39, 'sold90_count': 67, 'fees90_count': 321},
    'Harrisonburg': {'active': 35, 'sold90_count': 63, 'fees90_count': 345},
    'Lexington': {'active': 27, 'sold90_count': 60, 'fees90_count': 334},
    'Roanoke': {'active': 103, 'sold90_count': 140, 'fees90_count': 874},
}
# 2026-08-22 full audit baseline (channel level, from eBay_Channel_Audit_2026-08-22.md)
baseline_822 = {
    'active': 514, 'listed_value': 83441, 'sold90_revenue': 82064, 'fees90_total': 13617,
    'aged_90plus_count': 207, 'aged_90plus_value': 27255,
}

deltas = {'vs_2026-08-24_partial': {}, 'vs_2026-08-22_baseline': {}}
for name in STORES:
    p = prior_824[name]
    c = summary['stores'][name]
    deltas['vs_2026-08-24_partial'][name] = {
        'active_delta': c['active_count'] - p['active'],
    }
deltas['vs_2026-08-22_baseline'] = {
    'active_delta': channel_active - baseline_822['active'],
    'listed_value_delta': round(channel_listed_value - baseline_822['listed_value'], 2),
    'sold90_revenue_delta': round(channel_revenue - baseline_822['sold90_revenue'], 2),
    'fees90_total_delta': round(channel_fees - baseline_822['fees90_total'], 2),
    'aged_90plus_count_delta': channel_aged90plus_count - baseline_822['aged_90plus_count'],
    'aged_90plus_value_delta': round(channel_aged90plus_value - baseline_822['aged_90plus_value'], 2),
}
summary['deltas'] = deltas
with open(os.path.join(BASE, 'summary.json'), 'w') as f:
    json.dump(summary, f, indent=1)

# ---- compact console report ----
print('=== CHANNEL ===')
print(json.dumps(summary['channel'], indent=1)[:3000])
print('=== DELTAS ===')
print(json.dumps(deltas, indent=1))
print('=== PER STORE HEADLINE ===')
for name in STORES:
    c = summary['stores'][name]
    print(name, '| active', c['active_count'], '| listed_value', c['listed_value'],
          '| sold90_rev', c['sold90_revenue'], '| fees90', c['fees90_total'],
          '| fee%', c['fee_pct_of_revenue'], '| aged90+', c['aged_90plus_count'],
          '| trs_elig', c['trs_eligible_count'], '/', c['active_count'],
          '| unread', c['messages_unread_60d'], '| neg_no_resp', c['neg_neutral_no_response_count'],
          '| markdown_capped', c['markdown_capped_count'], '| subscription', c['subscription'])
print('DONE_ANALYZE')
