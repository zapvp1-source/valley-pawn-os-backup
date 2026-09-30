#!/usr/bin/env python3
"""MobilePawn participation by store, from Bravo End-of-Month xlsx already pulled by the
Bravo Data Extraction pipeline. Zero Bravo UI. Read-only on pipeline output.

Participation (payments) = MobilePawn Loan Payments qty /
    (MobilePawn Loan Payments + In-Store Renewals + Partial Payments + Extensions)
  -> share of all loan-keeping payments (not redemptions) made through the app.
Participation ($) = MobilePawn Interest+Fees+Misc / (that + In-Store Interest+Fees+Misc)
Customer reach   = MobilePawn 'Customers Active' / Ending Loan Base qty (loans, proxy).
Only files whose 'Reporting Dates' header is a full calendar month (or current MTD) are used.
"""
import openpyxl, glob, os, re, sys, calendar, datetime as dt, csv
OUT = os.path.expanduser('~/Documents/Claude/Projects/Bravo Data Extraction/output')
STORES = ['CUL','HAR','LEX','ROA','WAY']

def num(x):
    return x if isinstance(x,(int,float)) and not isinstance(x,bool) else None

def parse(path):
    ws = openpyxl.load_workbook(path, data_only=True, read_only=True).active
    rows = [[c for c in r if c not in (None,'')] for r in ws.iter_rows(values_only=True)]
    rows = [r for r in rows if r]
    d = {}
    def row(label, start=0):
        for r in rows:
            if isinstance(r[0],str) and r[0].strip()==label: return r
            if len(r)>1 and r[0]=='-' and isinstance(r[1],str) and r[1].strip()==label: return r[1:]
        return None
    rd = next((r[1] for r in rows if r[0]=='Reporting Dates:'), None)
    store = rows[1][0] if len(rows)>1 else None
    d['store'], d['range'] = store, rd
    # In-store payment rows: [label, qty, principal, principal pymt, interest, fees, misc, total]
    ins = {}
    in_sec = False
    for r in rows:
        if r[0]=='In-Store Txns': in_sec=True; continue
        if in_sec and r[0] in ('Renewals','Partial Payments','Extensions','Redemptions','In-Store Subtotal'):
            v=[num(x) or 0 for x in r[1:]]
            v += [0]*(7-len(v))
            ins[r[0]] = v
            if r[0]=='In-Store Subtotal': break
    # MobilePawn
    mp = {}; mp_sec=False
    for r in rows:
        if isinstance(r[0],str) and r[0].startswith('MobilePawn Activity'): mp_sec=True; continue
        if mp_sec:
            lab = str(r[0]).strip()
            if lab=='Loan Payments': mp['pay_qty']=num(r[1]) or 0; mp['int']=num(r[3]) or 0; mp['fee']=num(r[4]) or 0; mp['misc']=num(r[5]) or 0; mp['loan_total']=num(r[6]) or 0
            elif lab=='Loan Renewals': mp['ren_qty']=num(r[1]) or 0
            elif lab=='Layaway Payments': mp['lay_qty']=num(r[1]) or 0; mp['lay_amt']=num(r[2]) or 0
            elif lab.startswith('Totals from'): mp['tot_qty']=num(r[1]) or 0; mp['tot_amt']=num(r[-2]) or 0
            elif lab=='Customers Active': mp['cust']=num(r[1]) or 0
            elif lab=='MobilePawn Convenience Fees': mp['conv_qty']=num(r[1]) or 0; mp['conv_amt']=num(r[2]) or 0; break
    lb = row('Ending Loan Base') 
    if lb is None:
        lb = next((r for r in rows if isinstance(r[0],str) and r[0].startswith('Ending Loan Base')), None)
    d['loans_qty'] = num(lb[-2]) if lb else None
    d['ins'], d['mp'] = ins, mp
    return d

def month_ok(rd):
    m = re.match(r'(\d+)/(\d+)/(\d{4}) - (\d+)/(\d+)/(\d{4})', rd or '')
    if not m: return None
    a = dt.date(int(m[3]),int(m[1]),int(m[2])); b = dt.date(int(m[6]),int(m[4]),int(m[5]))
    if a.day!=1 or (a.year,a.month)!=(b.year,b.month): return None
    full = b.day==calendar.monthrange(b.year,b.month)[1]
    return a, b, full

def metrics(d, fn, key, b, full):
    ins, mp = d['ins'], d['mp']
    in_pay = sum(ins.get(k,[0])[0] for k in ('Renewals','Partial Payments','Extensions'))
    in_ifm = sum(ins.get('In-Store Subtotal',[0]*7)[i] for i in (3,4,5))
    mp_ifm = mp['int']+mp['fee']+mp['misc']
    return dict(store=d['store'], month=f'{key[0]}-{key[1]:02d}', through=b.isoformat(), full_month=full,
        mp_loan_pmts=mp['pay_qty'], instore_pmts=in_pay,
        pct_pmts_mobile=round(100*mp['pay_qty']/(mp['pay_qty']+in_pay),1) if (mp['pay_qty']+in_pay) else None,
        mp_int_fees=round(mp_ifm,2), instore_int_fees=round(in_ifm,2),
        pct_dollars_mobile=round(100*mp_ifm/(mp_ifm+in_ifm),1) if (mp_ifm+in_ifm) else None,
        mp_layaway_pmts=mp.get('lay_qty',0), mp_total_collected=round(mp.get('tot_amt',0),2),
        mp_customers_active=mp.get('cust',0), loans_outstanding=d['loans_qty'],
        conv_fees=round(mp.get('conv_amt',0),2), source=fn)


def history(out=OUT, quiet=False):
    err = open(os.devnull, 'w') if quiet else sys.stderr
    results = []
    for st in STORES:
        best = {}
        for f in sorted(glob.glob(os.path.join(out, f'20??-??-??_{st}_end-of-month.xlsx'))):
            try: d = parse(f)
            except Exception as e: print('SKIP', f, e, file=err); continue
            if d['store']!=st: print('SKIP store mismatch', f, d['store'], file=err); continue
            mo = month_ok(d['range'])
            if not mo: print('SKIP range', f, d['range'], file=err); continue
            a,b,full = mo
            key=(a.year,a.month)
            if key not in best or b > best[key][1]: best[key]=(d,b,full,os.path.basename(f))
        for key,(d,b,full,fn) in sorted(best.items()):
            if not d['mp'] or 'pay_qty' not in d['mp']: print('SKIP no MP block', fn, file=err); continue
            results.append(metrics(d, fn, key, b, full))
    return results


if __name__ == '__main__':
    results = history(sys.argv[1] if len(sys.argv) > 1 else OUT)
    w = csv.DictWriter(sys.stdout, fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)
