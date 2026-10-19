import json, glob, collections as C, datetime as dt
B='/sessions/festive-trusting-clarke/mnt/Projects/Call Analysis/week_2026-09-28/'
R=[]
for f in sorted(glob.glob(B+'review_*.json')): R+=json.load(open(f))
idx={x['n']:x for x in json.load(open(B+'calls_index.json'))}
print('reviewed',len(R),'unique',len({r['call'] for r in R}),'of',len(idx))
def wk(n):
    d=idx[n]['time'].split()[1]; m,dd=map(int,d.split('/'))
    D=dt.date(2026,m,dd); return 1 if D<=dt.date(2026,10,4) else 2 if D<=dt.date(2026,10,11) else 3
for r in R: r['store']=idx[r['call']]['store']; r['wk']=wk(r['call'])
for s in ['CUL','HAR','WAY','LEX','ROA','PRESTON']:
    rs=[r for r in R if r['store']==s]; cu=[r for r in rs if r['type']=='customer']
    if not rs: continue
    sl=[r for r in cu if r['intent'] in('sell_item','pawn_loan_new')]
    rt=[r['service_rating'] for r in cu if r['service_rating']]
    print(f"== {s} rec {len(rs)} cust {len(cu)} | deals {sum(r['outcome']=='deal_or_customer_coming_in' for r in cu)} cb-promised {sum(r['outcome']=='unresolved_callback_promised' for r in cu)} nohelp {sum(r['outcome']=='unresolved_no_help' for r in cu)} turned {sum(r['outcome'] in ('turned_away_we_dont_take','declined_price_or_condition') for r in cu)} nis {sum(r['outcome']=='not_in_stock' for r in cu)} | qual {sum(r['qualifying_questions'] is True for r in sl)}/{sum(r['qualifying_questions'] is not None for r in sl)} loanoffer {sum(r['offered_loan_vs_buy'] is True for r in sl)}/{len(sl)} | rating {round(sum(rt)/len(rt),2) if rt else '-'}")
    print('  intents',C.Counter(r['intent'] for r in cu).most_common(5))
    fl=C.Counter()
    for r in rs:
        for f in r['flags']:
            fl[f.lower()[:45]]+=1
    print('  flags',fl.most_common(12))
    print('  staff',C.Counter(r['staff_name'] for r in cu if r['staff_name']).most_common(6))
    print('  NIS',[r['item'][:30] for r in cu if r['outcome']=='not_in_stock'])
    print('  TURNED',[(r['item'][:25],r['turned_away_reason'][:30]) for r in cu if r['outcome'] in ('turned_away_we_dont_take','declined_price_or_condition')][:25])
