import sys
sys.path.insert(0,'/Users/joshuadavis/Documents/Claude/Scheduled/monthly-analytics-report')
from importlib import import_module
K=import_module('kpi_data_2026-06'.replace('-','_')) if False else None
exec(open('/Users/joshuadavis/Documents/Claude/Scheduled/monthly-analytics-report/kpi_data_2026-06.py').read())
D=chr(36); NL=chr(10)
STORES=['Culpeper','Harrisonburg','Lexington','Roanoke','Waynesboro']
mets=[('retail','Retail Sales'),('retail_cost','Retail COGS'),('retail_gp','Retail GP'),('scrap','Scrap Sales'),('scrap_cost','Scrap COGS'),('scrap_gp','Scrap GP'),('psc','PSC'),('net','Net Revenue')]
def money(x): return D+format(int(round(x)),',')
def yoy(c,p): return ((c-p)/p*100.0) if p else 0.0
def flag(y):
    if y<0: return ' '+chr(9888)
    if y>30: return ' '+chr(128293)
    return ' '+chr(9989)
views=[('VIEW 1 - Same Month: June 2026 vs June 2025','same-month-current','same-month-prior'),
       ('VIEW 2 - YTD: Jan-Jun 2026 vs Jan-Jun 2025','ytd-current','ytd-prior'),
       ('VIEW 3 - T12M: Jul 2025-Jun 2026 vs Jul 2024-Jun 2025','t12m-current','t12m-prior')]
c=[]
c.append(chr(128202)+' *Monthly Analytics - June 2026 | Company-Wide — Retail vs Scrap channel split*')
c.append('_Source: Bravo Company Performance (KPI) report, all 6 windows | matches Bravo to the penny_')
for title,cw,pw in views:
    c.append(''); c.append('*'+title+'*'); c.append('')
    c.append('| Metric | Current | Prior | $ Chg | YoY |')
    c.append('|---|---|---|---|---|')
    for m,lab in mets:
        cur=sum(W[cw][m]); pri=sum(W[pw][m]); y=yoy(cur,pri); chg=cur-pri
        sign='+' if chg>=0 else '-'
        c.append('| '+lab+' | '+money(cur)+' | '+money(pri)+' | '+sign+money(abs(chg))+' | '+('%+.1f'%y)+'%'+flag(y)+' |')
    # margin lines
    rm_c=sum(W[cw]['retail_gp'])/sum(W[cw]['retail'])*100; rm_p=sum(W[pw]['retail_gp'])/sum(W[pw]['retail'])*100
    sm_c=sum(W[cw]['scrap_gp'])/sum(W[cw]['scrap'])*100; sm_p=sum(W[pw]['scrap_gp'])/sum(W[pw]['scrap'])*100
    c.append('_Retail margin '+('%.1f'%rm_c)+'%% (prior '+('%.1f'%rm_p)+'%%) | Scrap margin '+('%.1f'%sm_c)+'%% (prior '+('%.1f'%sm_p)+'%%) | Scrap = '+('%.0f'%(sum(W[cw]['scrap_gp'])/(sum(W[cw]['retail_gp'])+sum(W[cw]['scrap_gp']))*100))+'%% of merch GP_'.replace('%%','%'))
open('/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-06/_msg_company_split.txt','w').write(NL.join(c).replace('%%','%'))
s=[]
s.append(chr(128202)+' *Monthly Analytics - June 2026 | By Store — Retail vs Scrap split*')
for title,cw,pw in views:
    s.append(''); s.append('*'+title+'*'); s.append('')
    s.append('| Store | Retail | R-GP | Scrap | S-GP | PSC | Net Rev | Net YoY |')
    s.append('|---|---|---|---|---|---|---|---|')
    for i,st in enumerate(STORES):
        y=yoy(W[cw]['net'][i],W[pw]['net'][i])
        s.append('| '+st+' | '+money(W[cw]['retail'][i])+' | '+money(W[cw]['retail_gp'][i])+' | '+money(W[cw]['scrap'][i])+' | '+money(W[cw]['scrap_gp'][i])+' | '+money(W[cw]['psc'][i])+' | '+money(W[cw]['net'][i])+' | '+('%+.0f'%y)+'%'+flag(y)+' |')
open('/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/monthly-analytics/2026-06/_msg_store_split.txt','w').write(NL.join(s))
print('BUILT')
