import calendar, json, os, time

B = '/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction'
TRIG = f'{B}/triggers'

# trailing 12 complete months: Aug 2025 .. Jul 2026
months = [(2025,8),(2025,9),(2025,10),(2025,11),(2025,12),
          (2026,1),(2026,2),(2026,3),(2026,4),(2026,5),(2026,6),(2026,7)]
stores = ['WAY','CUL','HAR','LEX','ROA']   # store-first ordering

n = 0
for s in stores:
    for (y,m) in months:
        n += 1
        last = calendar.monthrange(y,m)[1]
        start = f'{y:04d}-{m:02d}-01'
        end   = f'{y:04d}-{m:02d}-{last:02d}'
        tid = f'ttm-{n:02d}-{s}-{y:04d}{m:02d}'
        trig = {
            "id": tid,
            "requested_at": "2026-08-11T15:00:00-04:00",
            "reports": [ { "name":"nics-transfers", "stores":[s], "date": f"{start}..{end}" } ]
        }
        with open(f'{TRIG}/{tid}.json','w') as f:
            json.dump(trig, f)
        time.sleep(0.05)   # keep mtime order = drop order

print(f'dropped {n} TTM triggers (store-first, {len(stores)} stores x {len(months)} months)')
