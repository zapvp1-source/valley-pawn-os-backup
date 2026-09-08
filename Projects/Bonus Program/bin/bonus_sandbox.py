#!/usr/bin/env python3
"""SANDBOX comparison runner — PROPOSED bonus regime vs live regime.
ADDITIVE. Imports bonus_engine read-only, writes ONLY under sandbox/.
Never touches data/, out/, the ledger, Slack, or bonus_engine.py.
Created 2026-09-07 for Joshua's target-method review."""
import os,sys,json,copy,datetime as dt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'bin'))
import bonus_engine as BE

STORES=BE.STORES
def prev_month(m): return BE.prev_month(m)
def trailing(m,n): return BE.trailing_months(m,n)

class SCtx(BE.Ctx):
    def __init__(self,root,pipeline,month):
        super().__init__(root,pipeline,month)
        self.out=os.path.join(root,'sandbox',month); os.makedirs(self.out,exist_ok=True)

def proposal(rules): return rules['_proposals'][0]

def seasonal(rules,month): return proposal(rules)['target_method']['seasonal_yield_factors'][month[5:7]]

def proposed_target(ctx,hist,store,target_month):
    """trail12 yield x seasonal[target] x prior-month ending assets, collared."""
    R=ctx.rules; P=proposal(R); completed=prev_month(target_month)
    ys=[]
    for m in trailing(completed,12):
        cur=hist.get(m,{}).get(store); prv=hist.get(prev_month(m),{}).get(store)
        if cur and prv and prv['ending_assets']: ys.append(cur['net_revenue']/prv['ending_assets'])
    if len(ys)<9: return None,{'hold':'fewer than 9 yields'}
    y=sum(ys)/len(ys)
    ea=hist[completed][store]['ending_assets']
    sf=seasonal(R,target_month)
    raw=y*sf*ea
    # collar: deseasonalised trailing-3 revenue, reseasonalised to the target month
    r3=[]
    for m in trailing(completed,3):
        d=hist.get(m,{}).get(store)
        if d: r3.append(d['net_revenue']/seasonal(R,m))
    cap=None
    if len(r3)==3:
        cap=sum(r3)/3*sf*P['target_method']['collar_multiple']
    tgt=min(raw,cap) if cap else raw
    return round(tgt),{'trail12_yield':round(y,4),'seasonal':sf,'ending_assets':ea,
                       'uncollared':round(raw),'collar':round(cap) if cap else None,
                       'collar_bound':bool(cap and cap<raw)}

def factor(rules,attainment):
    c=proposal(rules)['payout_curve']
    a=attainment
    if a<c['threshold']: return c['below_threshold']
    if a<c['target']:
        return c['threshold_factor']+(a-c['threshold'])/(c['target']-c['threshold'])*(c['target_factor']-c['threshold_factor'])
    if a<c['stretch']:
        return c['target_factor']+(a-c['target'])/(c['stretch']-c['target'])*(c['stretch_factor']-c['target_factor'])
    return c['stretch_factor']

def payouts(ctx,hist,stores_state,rules):
    """Mirrors bonus_engine.stage_close payout logic, with the graduated factor
    replacing the binary Bridge-1 gate. Eligibility rules are unchanged."""
    R=ctx.rules; reg=ctx.regime(); P=proposal(R); month=ctx.month
    roster=BE.read_json(ctx,'roster.json',required=True)
    active=[e for e in roster if not e.get('terminated')]
    pay=[]
    for s in STORES:
        st=stores_state[s]; name=R['stores'][s]; fac=st['factor']
        rd,act=BE.read_employee_activity(ctx,s)
        if fac<=0:
            pay.append({'store':s,'employee':'(store)','role':'—','basis':None,'rate':0,'bonus':0.0,'factor':0.0,
                        'note':'below %d%% threshold (%.0f%% of target) — $0'%(P['payout_curve']['threshold']*100,st['attainment']*100)})
            continue
        tier2=st['tier2']
        mrate=reg['rates']['manager']['hit' if tier2 else 'miss']
        arate=reg['rates']['associate']['hit' if tier2 else 'miss']
        mgrs=[e for e in active if e['department']==name and e['title'] in R['eligibility']['manager_titles']]
        elig=[]
        for e in mgrs:
            hd=dt.date.fromisoformat(e['hire_date'])
            if R['eligibility']['manager_full_month'] and hd>dt.date(int(month[:4]),int(month[5:7]),1): continue
            elig.append(e)
        if not elig and act:
            leads=[]
            for code,a in act.items():
                if code in R['bravo_ignore_codes']: continue
                e=BE.map_bravo_to_roster(ctx,code,a['name'],active)
                if e and e['department']==name and e['title'] in R['eligibility']['associate_titles']:
                    leads.append((a['retail_sales'],e))
            if leads:
                leads.sort(key=lambda t:-t[0]); elig=[leads[0][1]]
        for e in elig:
            b=st['net_revenue']*mrate*fac
            pay.append({'store':s,'employee':e['display'],'uuid':e['uuid'],'role':'Manager','basis':st['net_revenue'],
                        'rate':mrate,'factor':round(fac,4),'bonus':round(b,2),
                        'note':'attainment %.0f%% -> factor %.2f; Tier 2 %s'%(st['attainment']*100,fac,'hit' if tier2 else 'missed')})
        if act:
            for code,a in act.items():
                if code in R['bravo_ignore_codes']: continue
                e=BE.map_bravo_to_roster(ctx,code,a['name'],roster)
                if e is None or e.get('terminated'): continue
                if e in elig or e['title'] not in R['eligibility']['associate_titles']: continue
                if a['retail_gp']<=0: continue
                b=a['retail_gp']*arate*fac
                pay.append({'store':s,'employee':e['display'],'uuid':e['uuid'],'role':e['title'],'basis':a['retail_gp'],
                            'rate':arate,'factor':round(fac,4),'bonus':round(b,2),
                            'note':('home store '+e['department']+'; ' if e['department']!=name else '')+'factor %.2f'%fac})
    return pay

def run(month,root=ROOT):
    pipeline=os.path.join(os.path.dirname(root),'Bravo Data Extraction')
    ctx=SCtx(root,pipeline,month)
    R=ctx.rules; P=proposal(R); hist=BE.load_history(ctx)
    live=json.load(open(os.path.join(root,'out',month,'close.json'))) if os.path.exists(os.path.join(root,'out',month,'close.json')) else None
    ss={}
    for s in STORES:
        tgt,meta=proposed_target(ctx,hist,s,month)
        nr=hist[month][s]['net_revenue']
        att=nr/tgt if tgt else None
        t2=(live['stores'][s]['tier2'] if live else None)
        ss[s]={'net_revenue':nr,'target':tgt,'meta':meta,'attainment':att,
               'factor':factor(R,att) if att else 0.0,'tier2':bool(t2),
               'live_target':(live['stores'][s]['target'] if live else None),
               'live_bridge1':(live['stores'][s]['bridge1'] if live else None)}
    pay=payouts(ctx,hist,ss,R)
    # top store pool + market manager, both under the curve
    if live and live.get('top_store'):
        ts=live['top_store']
        if ss[ts]['factor']>0:
            pay.append({'store':ts,'employee':'(Top store pool)','role':'pool','basis':None,'rate':None,
                        'factor':1.0,'bonus':reg_pool(R),'note':'%s — paid in full, competition prize'%R['stores'][ts]})
    preston=next((e for e in BE.read_json(ctx,'roster.json',required=True) if e['title']=='Market Manager' and not e.get('terminated')),None)
    if preston:
        per=ctx.regime()['market_manager_per_bridge1_store']
        amt=sum(per*ss[s]['factor'] for s in STORES)
        pay.append({'store':'ALL','employee':preston['display'],'uuid':preston['uuid'],'role':'Market Manager',
                    'basis':None,'rate':per,'factor':None,'bonus':round(amt,2),
                    'note':'sum of %s x each store factor (%s)'%(BE.fmt0(per),', '.join('%s %.2f'%(s,ss[s]['factor']) for s in STORES))})
    total=round(sum(p['bonus'] for p in pay),2)
    res={'month':month,'basis':'SANDBOX — PROPOSED regime, not live','generated':dt.datetime.now().isoformat(timespec='seconds'),
         'seasonal_factor':seasonal(R,month),'stores':ss,'payouts':pay,'total_payout':total,
         'live_total':(live['total_payout'] if live else None)}
    json.dump(res,open(os.path.join(ctx.out,'proposed.json'),'w'),indent=1)
    return res

def reg_pool(R):
    for r in R['regimes']:
        if 'top_store_pool' in r: return r['top_store_pool']
    return 300.0

if __name__=='__main__':
    for m in sys.argv[1:]:
        r=run(m)
        print('\n===== %s  (seasonal factor %.4f) ====='%(m,r['seasonal_factor']))
        print('%-6s %10s %10s %10s %8s %7s'%('store','net rev','LIVE tgt','PROP tgt','attain','factor'))
        for s in STORES:
            x=r['stores'][s]
            lt='%10.0f'%x['live_target'] if x['live_target'] else '%10s'%'-'
            print('%-6s %10.0f %s %10.0f %7.0f%% %7.2f'%(s,x['net_revenue'],lt,x['target'],x['attainment']*100,x['factor']))
        print('  collar bound at:',[s for s in STORES if r['stores'][s]['meta'].get('collar_bound')] or 'none')


def factor2(rules, nr, collared, uncollared):
    # Threshold/target measured on the collared target; stretch on the uncollared one.
    c = proposal(rules)['payout_curve']
    a = nr / collared
    if a < c['threshold']:
        return c['below_threshold'], a
    if a < c['target']:
        return c['threshold_factor'] + (a - c['threshold']) / (c['target'] - c['threshold']) * (c['target_factor'] - c['threshold_factor']), a
    au = nr / uncollared
    if au <= c['target']:
        return c['target_factor'], a
    if au < c['stretch']:
        return c['target_factor'] + (au - c['target']) / (c['stretch'] - c['target']) * (c['stretch_factor'] - c['target_factor']), a
    return c['stretch_factor'], a


def run2(month, root=ROOT):
    # Final proposed run: collar-aware stretch + market-manager cap.
    pipeline = os.path.join(os.path.dirname(root), 'Bravo Data Extraction')
    ctx = SCtx(root, pipeline, month)
    R = ctx.rules
    P = proposal(R)
    hist = BE.load_history(ctx)
    lp = os.path.join(root, 'out', month, 'close.json')
    live = json.load(open(lp)) if os.path.exists(lp) else None
    ss = {}
    for s in STORES:
        tgt, meta = proposed_target(ctx, hist, s, month)
        nr = hist[month][s]['net_revenue']
        fac, att = factor2(R, nr, tgt, meta['uncollared'])
        ss[s] = {'net_revenue': nr, 'target': tgt, 'meta': meta, 'attainment': att, 'factor': fac,
                 'tier2': bool(live['stores'][s]['tier2']) if live else False,
                 'live_target': live['stores'][s]['target'] if live else None,
                 'live_bridge1': live['stores'][s]['bridge1'] if live else None}
    pay = payouts(ctx, hist, ss, R)
    if live and live.get('top_store') and ss[live['top_store']]['factor'] > 0:
        ts = live['top_store']
        pay.append({'store': ts, 'employee': '(Top store pool)', 'role': 'pool', 'basis': None,
                    'rate': None, 'factor': 1.0, 'bonus': reg_pool(R),
                    'note': R['stores'][ts] + ' - paid in full, competition prize'})
    roster = BE.read_json(ctx, 'roster.json', required=True)
    preston = next((e for e in roster if e['title'] == 'Market Manager' and not e.get('terminated')), None)
    if preston:
        per = ctx.regime()['market_manager_per_bridge1_store']
        cap = P['payout_curve']['market_manager_factor_cap']
        amt = sum(per * min(ss[s]['factor'], cap) for s in STORES)
        pay.append({'store': 'ALL', 'employee': preston['display'], 'uuid': preston['uuid'],
                    'role': 'Market Manager', 'basis': None, 'rate': per, 'factor': None,
                    'bonus': round(amt, 2),
                    'note': 'sum of per-store amount x each store factor, each capped at 1.0'})
    total = round(sum(p['bonus'] for p in pay if p.get('uuid')), 2)  # engine convention: uuid only
    pool = round(sum(p['bonus'] for p in pay if not p.get('uuid')), 2)
    res = {'month': month, 'basis': 'SANDBOX - PROPOSED regime (final), not live', 'pool_excluded_from_total': pool,
           'generated': dt.datetime.now().isoformat(timespec='seconds'),
           'seasonal_factor': seasonal(R, month), 'stores': ss, 'payouts': pay,
           'total_payout': total, 'live_total': live['total_payout'] if live else None}
    json.dump(res, open(os.path.join(ctx.out, 'proposed_final.json'), 'w'), indent=1)
    return res
