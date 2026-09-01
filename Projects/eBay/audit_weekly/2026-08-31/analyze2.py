#!/usr/bin/env python3
# Second analysis pass: fold sample_results.json (GetItem-verified fields) into summary.json
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
summary = json.load(open(os.path.join(BASE, 'summary.json')))
sample = json.load(open(os.path.join(BASE, 'sample_results.json')))
STORES = ['Culpeper','Waynesboro','Harrisonburg','Lexington','Roanoke']

channel_sample_n = 0
channel_bo_on = 0
channel_no_returns = 0
channel_returns_accepted = 0
channel_trs_elig = 0
channel_pics_sum = 0
channel_specifics_sum = 0
channel_title_sum = 0
channel_dispatch = {}
channel_ship_paid = {}
channel_returns_window = {}

for name in STORES:
    samp = sample.get(name, {})
    items = samp.get('items', [])
    n = len(items)
    st = summary['stores'][name]
    if n == 0:
        st['sample_note'] = 'no sample data'
        continue
    bo_on = sum(1 for i in items if i.get('best_offer'))
    no_ret = sum(1 for i in items if i.get('returns_accepted') and i.get('returns_accepted') != 'ReturnsAccepted')
    ret_acc = sum(1 for i in items if i.get('returns_accepted') == 'ReturnsAccepted')
    trs = sum(1 for i in items if i.get('dispatch_max') in ('0','1')
              and i.get('returns_within') in ('Days_30','Days_60')
              and i.get('shipping_cost_paid_by') == 'Seller'
              and i.get('returns_accepted') == 'ReturnsAccepted')
    avg_pics = round(sum(i.get('pics') or 0 for i in items)/n, 1)
    avg_spec = round(sum(i.get('specifics_count') or 0 for i in items)/n, 1)
    avg_title = round(sum(i.get('title_len') or 0 for i in items)/n, 1)
    dispatch = {}
    ship_paid = {}
    ret_window = {}
    for i in items:
        d = i.get('dispatch_max') or 'unknown'; dispatch[d] = dispatch.get(d,0)+1
        p = i.get('shipping_cost_paid_by') or 'unknown'; ship_paid[p] = ship_paid.get(p,0)+1
        w = i.get('returns_within') or 'none'; ret_window[w] = ret_window.get(w,0)+1

    st['sample_size'] = n
    st['sample_pct_of_population'] = round(100.0*n/samp.get('population_size', n), 1)
    st['sample_best_offer_enabled_pct'] = round(100.0*bo_on/n, 1)
    st['sample_no_returns_pct'] = round(100.0*no_ret/n, 1)
    st['sample_returns_accepted_pct'] = round(100.0*ret_acc/n, 1)
    st['sample_trs_eligible_pct'] = round(100.0*trs/n, 1)
    st['sample_avg_photos'] = avg_pics
    st['sample_avg_item_specifics'] = avg_spec
    st['sample_avg_title_len'] = avg_title
    st['sample_dispatch_breakdown'] = dispatch
    st['sample_shipping_paid_by_breakdown'] = ship_paid
    st['sample_returns_window_breakdown'] = ret_window
    # extrapolate TRS-eligible count to full population using sample rate
    st['trs_eligible_count_est'] = round(trs/n * st['active_count'])
    st['best_offer_enabled_count_est'] = round(bo_on/n * st['active_count'])
    st['no_returns_count_est'] = round(no_ret/n * st['active_count'])

    channel_sample_n += n
    channel_bo_on += bo_on
    channel_no_returns += no_ret
    channel_returns_accepted += ret_acc
    channel_trs_elig += trs
    channel_pics_sum += sum(i.get('pics') or 0 for i in items)
    channel_specifics_sum += sum(i.get('specifics_count') or 0 for i in items)
    channel_title_sum += sum(i.get('title_len') or 0 for i in items)
    for k,v in dispatch.items(): channel_dispatch[k] = channel_dispatch.get(k,0)+v
    for k,v in ship_paid.items(): channel_ship_paid[k] = channel_ship_paid.get(k,0)+v
    for k,v in ret_window.items(): channel_returns_window[k] = channel_returns_window.get(k,0)+v

ch = summary['channel']
ch['sample_size'] = channel_sample_n
ch['sample_best_offer_enabled_pct'] = round(100.0*channel_bo_on/channel_sample_n, 1)
ch['sample_no_returns_pct'] = round(100.0*channel_no_returns/channel_sample_n, 1)
ch['sample_trs_eligible_pct'] = round(100.0*channel_trs_elig/channel_sample_n, 1)
ch['sample_avg_photos'] = round(channel_pics_sum/channel_sample_n, 1)
ch['sample_avg_item_specifics'] = round(channel_specifics_sum/channel_sample_n, 1)
ch['sample_avg_title_len'] = round(channel_title_sum/channel_sample_n, 1)
ch['sample_dispatch_breakdown'] = channel_dispatch
ch['sample_shipping_paid_by_breakdown'] = channel_ship_paid
ch['sample_returns_window_breakdown'] = channel_returns_window
ch['trs_eligible_count_est'] = round(channel_trs_elig/channel_sample_n * ch['active_count'])
ch['best_offer_enabled_count_est'] = round(channel_bo_on/channel_sample_n * ch['active_count'])
ch['no_returns_count_est'] = round(channel_no_returns/channel_sample_n * ch['active_count'])

with open(os.path.join(BASE, 'summary.json'), 'w') as f:
    json.dump(summary, f, indent=1)

print('=== CHANNEL SAMPLE-DERIVED ===')
for k in ['sample_size','sample_best_offer_enabled_pct','sample_no_returns_pct','sample_trs_eligible_pct',
          'sample_avg_photos','sample_avg_item_specifics','sample_avg_title_len',
          'sample_dispatch_breakdown','sample_shipping_paid_by_breakdown','sample_returns_window_breakdown',
          'trs_eligible_count_est','best_offer_enabled_count_est','no_returns_count_est']:
    print(k, ':', ch.get(k))
print()
for name in STORES:
    st = summary['stores'][name]
    print(name, '| n=', st.get('sample_size'), '| BO%', st.get('sample_best_offer_enabled_pct'),
          '| noret%', st.get('sample_no_returns_pct'), '| TRS%', st.get('sample_trs_eligible_pct'),
          '| pics', st.get('sample_avg_photos'), '| specs', st.get('sample_avg_item_specifics'),
          '| dispatch', st.get('sample_dispatch_breakdown'), '| shipPaidBy', st.get('sample_shipping_paid_by_breakdown'),
          '| retWindow', st.get('sample_returns_window_breakdown'))
print('DONE2')
