"""PM/jewelry/coin loan-growth list builder (Joshua 10/7/2026).
Reads <end>_<STORE>_pm-loan-growth-p2*.csv (Claude Loan Portfolio 2026 + FDP layout), keeps ON LOAN,
keeps precious-metal items, ticket-level LTV vs melt, >=1 paid extension, headroom to 75% of melt,
joins contacts (forfeiture-winback-comparison-contacts), writes JSON for the workbook step."""
import csv, glob, re, json, sys, os, datetime as dt, collections
OUT, SPOTF, TODAY = sys.argv[1], sys.argv[2], dt.date.fromisoformat(sys.argv[3])
CAP = 0.75
spot = json.load(open(SPOTF)); AU, AG = spot['gold_usd_per_ozt'], spot['silver_usd_per_ozt']
STORES = ['CUL','HAR','LEX','ROA','WAY']
def money(s):
    s=(s or '').replace('$','').replace(',','').strip()
    if not s: return 0.0
    neg=s.startswith('('); v=float(s.strip('()')); return -v if neg else v
def d(s):
    try: m,dd,y=s.split()[0].split('/'); return dt.date(int(y),int(m),int(dd))
    except Exception: return None
KPUR={'8':8/24,'9':.375,'10':.417,'12':.5,'14':.585,'15':.625,'16':16/24,'18':.75,'20':20/24,'21':.875,'22':.916,'24':.999}
def melt(cat, desc):
    """returns (melt_usd or None, metal, basis)"""
    u=desc.upper()
    m=re.search(r'(\d+(?:\.\d+)?)\s*DWT\s+(\d{1,2})K', u)
    if m:
        k=m.group(2)
        if k in KPUR: return float(m.group(1))*0.05*KPUR[k]*AU, 'gold', f'{m.group(1)}dwt {k}K'
    m=re.search(r'(\d+(?:\.\d+)?)\s*DWT\s+SILV-?(\d{3})', u)
    if m: return float(m.group(1))*0.05*int(m.group(2))/1000*AG, 'silver', f'{m.group(1)}dwt .{m.group(2)}'
    m=re.search(r'(\d+(?:\.\d+)?)\s*DWT\s+PLAT', u)
    if m: return None, 'platinum', f'{m.group(1)}dwt plat (counter appraisal)'
    c=cat.upper()
    if 'COIN' in c or 'BULLION' in c or 'BULLION' in u or 'COIN' in u:
        # quantity is not in the export, so coin/bullion value is left to the counter (verified 10/9: a '1 OZ' bullion line carried a $1,320 loan)
        return None, ('gold' if 'GOLD' in c+u else 'silver'), 'coin/bullion (counter appraisal)'
    return None, None, ''
PM_WORDS=('GOLD','SILVER','PLATINUM','DIAMOND','RING','CHAIN','BRACELET','NECKLACE','PENDANT','EARRING','CHARM','BROOCH','COIN','BULLION','SCRAP','JEWEL','STONE','ANKLET')
def is_pm(cat, desc, metal):
    if metal: return True
    c=cat.upper()
    return any(w in c for w in PM_WORDS) and 'WATCH' not in c
# contacts: newest file per store
contacts={}
for st in STORES:
    fs=sorted(glob.glob(os.path.join(OUT,f'*_{st}_forfeiture-winback-comparison-contacts.csv')), key=os.path.getmtime)
    for f in fs:  # oldest first, newest overwrites
        for x in csv.DictReader(open(f,encoding='utf-8-sig')):
            contacts[(st,x['Name'].strip().upper())]=x
rows=[]; files={}
for st in STORES:
    fs=sorted(glob.glob(os.path.join(OUT,f'*_{st}_pm-loan-growth-p2*.csv')))
    files[st]=[os.path.basename(f) for f in fs]
    seen=set()
    for f in fs:
        rd=csv.DictReader(open(f,encoding='utf-8-sig'))
        if 'Category' not in (rd.fieldnames or []):
            print('SKIP (no FDP layout):', os.path.basename(f)); continue
        for x in rd:
            x['_store']=st; x['_file']=os.path.basename(f); rows.append(x)
onl=[x for x in rows if x['Disposition'].strip().upper()=='ON LOAN']
tickets=collections.defaultdict(list)
for x in onl: tickets[(x['_store'],x['Ticket Number'])].append(x)
out=[]; stats=collections.Counter()
for (st,tk),items in tickets.items():
    pm=[];other=0.0
    for x in items:
        mv,metal,basis=melt(x['Category'],x['Full Description'])
        if is_pm(x['Category'],x['Full Description'],metal): pm.append((x,mv,metal,basis))
        else: other+=money(x['Loan Amount'])
    if not pm: continue
    stats['pm_tickets']+=1
    stones=any(re.search(r'DIAMOND|STONE|CTW',p[0]['Category'].upper()+p[0]['Full Description'].upper()) for p in pm)
    x0=items[0]
    loan=sum(money(p[0]['Loan Amount']) for p in pm)
    known=[p for p in pm if p[1] is not None]; unknown=[p for p in pm if p[1] is None]
    meltv=sum(p[1] for p in known); loan_known=sum(money(p[0]['Loan Amount']) for p in known)
    due=d(x0['Due Date']); age=int(x0['Age']) if x0['Age'].strip().isdigit() else None
    pawn=(TODAY-dt.timedelta(days=age)) if age is not None else None
    paid=bool(x0['Last Payment'].strip()) or (due and pawn and (due-pawn).days>31)
    pull=d(x0['Pull Date'])
    status = 'current' if (due and due>=TODAY) else ('grace (past due, before pull date)' if (pull and pull>=TODAY) else 'past pull date')
    pastdue = due is not None and due < TODAY
    c=contacts.get((st,x0['Customer'].strip().upper()),{})
    rec=dict(store=st,ticket=tk,customer=x0['Customer'].strip(),phone=c.get('Phone',''),email=c.get('E-Mail',''),
        sms=x0['SMS'],mobilepawn=x0['MobilePawn'],items=len(pm),desc='; '.join(f"{p[0]['Category']}: {p[3] or p[0]['Full Description'][:40]}" for p in pm),
        loan=round(loan,2),loan_on_metal=round(loan_known,2),melt=round(meltv,2),unpriced_items=len(unknown),
        pct_melt=round(loan_known/meltv*100,1) if meltv else None,
        extra=round(max(0,CAP*meltv-loan_known),2) if meltv else None,
        other_collateral_loan=round(other,2),last_payment=x0['Last Payment'].split()[0] if x0['Last Payment'].strip() else '',
        due=x0['Due Date'],pawn=str(pawn) if pawn else '',paid=bool(paid),pastdue=bool(pastdue),status=status,pull=x0['Pull Date'],stones=stones)
    out.append(rec)
    stats['paid' if paid else 'never_paid']+=1
json.dump(dict(files=files,spot=dict(gold=AU,silver=AG,updated=spot['updated_at']),total_rows=len(rows),onloan_rows=len(onl),
    stats=stats,tickets=out),open(sys.argv[4],'w'),indent=0,default=str)
print('rows',len(rows),'onloan',len(onl),dict(stats))
