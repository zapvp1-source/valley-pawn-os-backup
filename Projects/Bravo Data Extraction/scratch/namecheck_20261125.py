import csv, re, os
from datetime import datetime
from collections import defaultdict

local_path = os.path.expanduser("~/mnt/Projects/Bravo Data Extraction/results-scrap/scrap-namecheck-20261125.buckets.csv")
rows = []
with open(local_path, encoding='utf-8-sig') as f:
    r = csv.DictReader(f)
    for row in r:
        rows.append(row)

CUTOFF = datetime(2026,10,1)

def parse_dt(s):
    s2 = re.sub(r'\s*[-+]\d{2}:\d{2}$', '', s.strip())
    return datetime.strptime(s2, "%m/%d/%Y %I:%M:%S %p")

month_in_name_re = re.compile(r'(20\d\d)[-/\s]?(0[1-9]|1[0-2])')
month_word_re = re.compile(r'\b(JAN(?:UARY)?|FEB(?:RUARY)?|MAR(?:CH)?|APR(?:IL)?|MAY|JUN(?:E)?|JUL(?:Y)?|AUG(?:UST)?|SEP(?:T(?:EMBER)?)?|OCT(?:OBER)?|NOV(?:EMBER)?|DEC(?:EMBER)?)\.?\s*(20\d\d)\b', re.I)
MONTHS = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06','JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}

def infer_month_from_name(name):
    m = month_in_name_re.search(name)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m2 = month_word_re.search(name)
    if m2:
        key = m2.group(1)[:3].upper()
        return f"{m2.group(2)}-{MONTHS[key]}"
    return None

candidates = []
for row in rows:
    store = row['Store'].strip()
    name = row['BucketName'].strip()
    status = row['Status'].strip()
    created_raw = row['CreatedOn'].strip()
    nameU = name.upper()
    if 'GOLD' not in nameU and 'SILVER' not in nameU:
        continue
    if 'PLATINUM' in nameU or 'PLAT.' in nameU or re.search(r'\bPLAT\b', nameU):
        continue
    try:
        created = parse_dt(created_raw)
    except Exception:
        created = None
    if status.upper() == 'CLOSED':
        continue
    if not created or created < CUTOFF:
        continue
    inferred_month = infer_month_from_name(name) or (created.strftime("%Y-%m") if created else None)
    candidates.append({'store':store,'name':name,'status':status,'created':created_raw,'created_dt':created,'inferred_month':inferred_month})

print(f"in-scope (non-CLOSED, CreatedOn>=2026-10-01) GOLD/SILVER buckets: {len(candidates)}\n")
for c in sorted(candidates, key=lambda x:(x['store'], x['created_dt'])):
    print(c['store'], '|', c['name'], '|', c['status'], '|', c['created'], '|', 'month=', c['inferred_month'])

print("\n=== violation check ===")
def is_standard(name, month):
    nameU = ' '.join(name.upper().split())
    opts = {f"{month} GOLD", f"{month} GOLD WITH STONES", f"{month} SILVER", f"{month} SILVER WITH STONES"}
    return nameU in opts

violations = []
for c in candidates:
    if not c['inferred_month']:
        violations.append((c, 'NO_MONTH_INFERRED'))
        continue
    if not is_standard(c['name'], c['inferred_month']):
        violations.append((c, 'BAD_NAME'))

for c, reason in violations:
    print(reason, '|', c['store'], '|', c['name'], '|', c['inferred_month'])

print("\n=== duplicate check (same store+month+type among in-scope) ===")
def bucket_type(name):
    nameU = name.upper()
    if 'GOLD' in nameU:
        return 'GOLD'
    if 'SILVER' in nameU:
        return 'SILVER'
    return None

groups = defaultdict(list)
for c in candidates:
    key = (c['store'], c['inferred_month'], bucket_type(c['name']))
    groups[key].append(c)
for key, items in groups.items():
    if len(items) > 1:
        print("DUP:", key, [i['name'] for i in items])
