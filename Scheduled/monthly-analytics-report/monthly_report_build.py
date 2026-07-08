import sys, json, subprocess
DIR=sys.argv[1]
MONTHLABEL=sys.argv[2] if len(sys.argv)>2 else 'June 2026'
PRIORLABEL=sys.argv[3] if len(sys.argv)>3 else 'June 2025'
YTDLABEL=sys.argv[4] if len(sys.argv)>4 else 'Jan-Jun 2026 vs Jan-Jun 2025'
T12LABEL=sys.argv[5] if len(sys.argv)>5 else 'Jul 2025-Jun 2026 vs Jul 2024-Jun 2025'
PREPARED=sys.argv[6] if len(sys.argv)>6 else 'July 1, 2026'
raw=json.loads(subprocess.check_output(['/usr/bin/python3','/Users/joshuadavis/Documents/Claude/Scheduled/monthly-analytics-report/parse_eom.py',DIR]).decode())
STORES=['CUL','HAR','LEX','ROA','WAY']
FULL={'CUL':'Culpeper','HAR':'Harrisonburg','LEX':'Lexington','ROA':'Roanoke','WAY':'Waynesboro'}
mets=['inventory_balance','loan_balance','total_sales','scrap_cost','psc','net_revenue']
mlab={'inventory_balance':'Inventory','loan_balance':'Loan','total_sales':'Sales','scrap_cost':'Scrap Cost','psc':'PSC','net_revenue':'Net Rev'}
mlabFull={'inventory_balance':'Inventory Balance','loan_balance':'Loan Balance','total_sales':'Total Sales (Retail+Scrap)','scrap_cost':'Scrap Cost (Refined)','psc':'PSC','net_revenue':'Net Revenue'}
D=chr(36); NL=chr(10)
def get(win,store,m): return raw.get(win+'_'+store+'.xlsx',{}).get(m,0) or 0
def gt(win,m): return sum(get(win,s,m) for s in STORES)
def money(x): return D+format(int(round(x)),',')
def yoy(c,p): return ((c-p)/p*100.0) if p else 0.0
def flag(y,p):
    if p==0: return ''
    if y<0: return ' warning'.replace('warning',chr(9888))
    if y>30: return ' '+chr(128293)
    return ' '+chr(9989)
views=[('VIEW 1 - Same Month: '+MONTHLABEL+' vs '+PRIORLABEL,'same-month-current','same-month-prior'),
       ('VIEW 2 - YTD: '+YTDLABEL,'ytd-current','ytd-prior'),
       ('VIEW 3 - Trailing 12 Months: '+T12LABEL,'t12m-current','t12m-prior')]
c=[]
c.append(chr(128202)+' *Monthly Analytics - '+MONTHLABEL+' | Company-Wide*')
c.append('_Prepared '+PREPARED+' | Source: Bravo POS End-of-Month pipeline | Net Revenue = In-Store Svc Charges + Sales Profit (matches Bravo Company Performance report)_')
c.append('_Per-store breakdown -> #store-performance_')
watches=[]
for title,cw,pw in views:
    c.append('')
    c.append('*'+title+'*')
    c.append('| Metric | Current | Prior | $ Chg | YoY |')
    c.append('|---|---|---|---|---|')
    for m in mets:
        cur=gt(cw,m); pri=gt(pw,m); y=yoy(cur,pri); chg=cur-pri
        sign='+' if chg>=0 else '-'
        c.append('| '+mlabFull[m]+' | '+money(cur)+' | '+money(pri)+' | '+sign+money(abs(chg))+' | '+('%+.1f'%y)+'%'+flag(y,pri)+' |')
        if pri and y<0 and title.startswith('VIEW 1'): watches.append(mlabFull[m]+' '+('%+.1f'%y)+'% YoY')
c.append('')
if watches: c.append(chr(9888)+' _Watch: '+'; '.join(watches)+'_')
c.append(chr(128203)+' _Full data -> Google Sheets: Monthly Analytics - '+MONTHLABEL+'_')
open(DIR+'/_msg_company.txt','w').write(NL.join(c))
s=[]
s.append(chr(128202)+' *Monthly Analytics - '+MONTHLABEL+' | By Store*')
s.append('_Per-store detail - company totals -> #company-performance_')
for title,cw,pw in views:
    s.append('')
    s.append('*'+title+'*')
    s.append('_Actuals_')
    s.append('| Store | '+' | '.join(mlab[m] for m in mets)+' |')
    s.append('|---|'+('---|'*len(mets)))
    for st in STORES:
        s.append('| '+FULL[st]+' | '+' | '.join(money(get(cw,st,m)) for m in mets)+' |')
    s.append('_YoY %_')
    s.append('| Store | '+' | '.join(mlab[m] for m in mets)+' |')
    s.append('|---|'+('---|'*len(mets)))
    for st in STORES:
        s.append('| '+FULL[st]+' | '+' | '.join(('%+.0f'%yoy(get(cw,st,m),get(pw,st,m)))+'%' for m in mets)+' |')
open(DIR+'/_msg_store.txt','w').write(NL.join(s))
print('BUILT company='+str(len(c))+' lines, store='+str(len(s))+' lines')
