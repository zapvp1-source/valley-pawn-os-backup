"""Offline re-track: replay raw detections (dets/<Key>/<date>.jsonl, written by counter.py v5) through the
live Tracker + decide() rules with the CURRENT config.json (or overrides) and print hourly IN/OUT.
Usage: python3 retrack.py <Key> <date> [--set max_dist=0.15 speed=0.4 ...] [--write]
--write replaces that day's rows in counts/<Key>.csv (same as rescore.py)."""
import csv, datetime as dt, json, os, sys, types
for m in ('cv2', 'nest_stream', 'detector'):          # tracker/rules need none of these; allow running anywhere
    try: __import__(m)
    except Exception: sys.modules[m] = types.ModuleType(m)
import counter as C

def replay(key, date, cfg):
    path = os.path.join(C.HERE, 'dets', key, date + '.jsonl')
    trk = C.Tracker(cfg.get('max_dist', 0.08), cfg.get('max_age', 3.0), cfg.get('speed', 0.30), cfg.get('cap', 0.25))
    counts, last = {}, None
    def done(ts, tracks):
        for t in tracks:
            d = C.decide(t, cfg)
            if d: counts.setdefault(C.bucket(ts), {'in': 0, 'out': 0})[d] += 1
    for line in open(path):
        try: now, feet = json.loads(line)
        except Exception: continue
        if last is not None and now - last > 30: done(last, trk.expire(last, force=True))  # stream gap = reconnect
        trk.update([tuple(p) for p in feet], now)
        done(now, trk.expire(now)); last = now
    if last is not None: done(last, trk.expire(last, force=True))
    return counts

if __name__ == '__main__':
    key, date = sys.argv[1], sys.argv[2]
    cfg = dict(C.CFG[key])
    if '--set' in sys.argv:
        for kv in sys.argv[sys.argv.index('--set') + 1:]:
            if kv.startswith('--'): break
            k, v = kv.split('='); cfg[k] = json.loads(v)
    counts = replay(key, date, cfg)
    ti = sum(c['in'] for c in counts.values()); to = sum(c['out'] for c in counts.values())
    for h in sorted(counts): print(h, counts[h]['in'], counts[h]['out'])
    print(f'TOTAL in={ti} out={to} visitors={(ti + to) / 2:.0f}')
    if '--write' in sys.argv:
        p = os.path.join(C.HERE, 'counts', f'{key}.csv'); rows = []
        if os.path.exists(p): rows = [r for r in csv.DictReader(open(p)) if not r['hour'].startswith(date)]
        rows += [{'hour': h, 'in': c['in'], 'out': c['out']} for h, c in counts.items()]
        rows.sort(key=lambda r: r['hour'])
        with open(p, 'w', newline='') as f:
            w = csv.DictWriter(f, ['hour', 'in', 'out']); w.writeheader(); w.writerows(rows)
        print('wrote', p)
