import os, json, csv, sys
try:
    import openpyxl
except ImportError:
    print('NO_OPENPYXL'); sys.exit(0)

base = os.path.expanduser('~/Documents/Claude/Projects/Taxes 2026')
found = json.load(open(os.path.join(base, '_lodestar_attachments.json')))
outdir = os.path.join(base, '_lodestar_xlsx')
os.makedirs(outdir, exist_ok=True)

n = 0
index = []
for e in found:
    for f in e['files']:
        if not f['f'].lower().endswith('.xlsx'):
            continue
        try:
            wb = openpyxl.load_workbook(f['p'], data_only=True)
        except Exception as ex:
            print('ERR', f['f'], ex); continue
        safe = ''.join(c if c.isalnum() or c in '._-' else '_' for c in f['f'])
        outfn = os.path.join(outdir, '%04d_%s.csv' % (e['i'], safe.replace('.xlsx', '')))
        with open(outfn, 'w', newline='') as fh:
            w = csv.writer(fh)
            for ws in wb.worksheets:
                w.writerow(['### SHEET', ws.title])
                for row in ws.iter_rows(values_only=True):
                    if any(c is not None and str(c).strip() != '' for c in row):
                        w.writerow(['' if c is None else str(c) for c in row])
        index.append({'i': e['i'], 'subject': e['subject'], 'ts': e['ts'], 'src': f['f'], 'csv': os.path.basename(outfn)})
        n += 1

json.dump(index, open(os.path.join(outdir, '_index.json'), 'w'), indent=1)
print('parsed', n)
