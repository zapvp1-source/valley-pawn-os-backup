"""Retention for Store Conduct Watch data under ~/.vp-studio/conduct-watch (config retain_*_days). Prints what it removed."""
import datetime as dt, json, os, shutil
CFG = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')))
DATA = os.path.expanduser('~/.vp-studio/conduct-watch')
today = dt.date.today()
for kind, days in (('rec', CFG.get('retain_rec_days', 3)), ('frames', CFG.get('retain_frames_days', 14)), ('transcripts', 60)):
    root = os.path.join(DATA, kind)
    for dp, dns, fns in os.walk(root):
        for n in list(dns) + list(fns):
            stem = n.split('.')[0]
            try: d = dt.date.fromisoformat(stem)
            except ValueError: continue
            if (today - d).days > days:
                p = os.path.join(dp, n); (shutil.rmtree if os.path.isdir(p) else os.remove)(p); print('removed', p)
import sys
if len(sys.argv) > 1:   # cleanup.py <date>: the day was analyzed completely -> its raw video is no longer needed (clips are kept)
    d = sys.argv[1]; rj = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports', d, 'run.json')
    if os.path.exists(rj) and json.load(open(rj)).get('complete') and json.load(open(rj)).get('version', 1) >= 2:
        for p in __import__('glob').glob(os.path.join(DATA, 'rec', '*', '*', d)): shutil.rmtree(p); print('removed analyzed video', p)
st = shutil.disk_usage(os.path.expanduser('~')); print('disk free GB', round(st.free / 1e9))
