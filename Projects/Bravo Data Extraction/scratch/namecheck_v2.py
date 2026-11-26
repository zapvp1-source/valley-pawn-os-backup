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
RELIABLE_STORES = {'HAR','LEX','ROA'}  # CUL, WAY excluded this run - incomplete capture, no Sep-Dec 2026 rows found at all

def parse_dt(s):
    s2 = re.sub(r'\s*[-+]\d{2}:\d{2}$', '', s.strip())
    return datetime.strptime(s2, "%m/%d/%Y %I:%M:%S %p")

month_in_name_re = re.compile(r'(20\d\d)[-/\s]?(0[1-9]|1[0-2])')

def infer_month_from_name(name):
    m = month_in_name_re.search(name)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None

candidates = []
for row in rows:
    store = row['Store'].strip()
    if store not in RELIABLE_STORES:
        continue
    name = row['BucketName'].strip()
    status = row['Status'].strip()
    created_raw = row['CreatedOn'].strip()
    nameU = name.upper()
    if 'GOLD' not in nameU and 'SILVER' not in nameU:
        continue
    if 'PLAT' in nameU:
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

def norm_type(name):
    nameU = ' '.join(name.upper().split())
    if 'GOLD' in nameU and 'STONE' in nameU:
        return 'GOLD WITH STONES'
    if 'GOLD' in nameU:
        return 'GOLD'
    if 'SILVER' in nameU and 'STONE' in nameU:
        return 'SILVER WITH STONES'
    if 'SILVER' in nameU:
        return 'SILVER'
    return None

def is_standard(name, month):
    nameU = ' '.join(name.upper().split())
    opts = {f"{month} GOLD", f"{month} GOLD WITH STONES", f"{month} SILVER", f"{month} SILVER WITH STONES"}
    return nameU in opts

print("=== candidates (reliable stores only: HAR, LEX, ROA) ===")
for c in sorted(candidates, key=lambda x:(x['store'], x['created_dt'])):
    print(c['store'], '|', repr(c['name']), '|', c['status'], '|', c['created'], '| month=', c['inferred_month'], '| type=', norm_type(c['name']))

print("\n=== violations ===")
for c in candidates:
    if not c['inferred_month']:
        print('NO_MONTH_INFERRED', c['store'], c['name'])
        continue
    if not is_standard(c['name'], c['inferred_month']):
        print('BAD_NAME', c['store'], repr(c['name']), 'month=', c['inferred_month'])

print("\n=== true duplicates (same store+month+exact type) ===")
groups = defaultdict(list)
for c in candidates:
    key = (c['store'], c['inferred_month'], norm_type(c['name']))
    groups[key].append(c)
for key, items in groups.items():
    if len(items) > 1:
        print("DUP:", key, [i['name'] for i in items])
