"""Valley Pawn door counter. Streams one Nest door camera, detects people ~4 fps, tracks feet
points, counts crossings of a virtual line. Writes hourly IN/OUT to counts/<store>.csv.
Usage: python3 counter.py <store> [--minutes N] [--debug]
Config: config.json (per-store camera + line). Secrets: $VPST_DIR (default ~/.vpst)."""
import asyncio, random, csv, datetime as dt, json, math, os, sys, time, zoneinfo
import cv2, numpy as np
import nest_stream as ns, detector

HERE = os.path.dirname(os.path.abspath(__file__))
TZ = zoneinfo.ZoneInfo('America/New_York')
CFG = json.load(open(os.path.join(HERE, 'config.json')))
EXTEND_EVERY = 240  # SDM WebRTC sessions expire after 5 min

def side(p, a, b):  # sign of point p relative to line a->b
    return np.sign((b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0]))

def seg_cross(p, q, a, b):  # does movement p->q cross segment a-b
    return side(p, a, b) != side(q, a, b) and side(a, p, q) != side(b, p, q)

class Tracker:
    """Nearest-neighbour tracker in NORMALIZED coords (0..1). v5 (2026-10-31): gate grows with time since the
    track was last seen (speed allowance) and tracks survive short occlusions (max_age), so a walker is one
    track from door to counter instead of several fragments."""
    def __init__(self, max_dist=0.08, max_age=3.0, speed=0.30):
        self.tracks, self.nid, self.max_dist, self.max_age, self.speed = {}, 0, max_dist, max_age, speed
    def expire(self, now, force=False):
        done = []
        for tid, t in list(self.tracks.items()):
            if force or now - t['ts'] > self.max_age: done.append(self.tracks.pop(tid))
        return done
    def update(self, pts, now):
        moves, used = [], set()
        pairs = []
        for i, p in enumerate(pts):
            for tid, t in self.tracks.items():
                d = math.dist(p, t['p'])
                if d <= self.max_dist + self.speed * max(0.0, now - t['ts']):
                    pairs.append((d, i, tid))
        pairs.sort()
        taken = set()
        for d, i, tid in pairs:
            if i in taken or tid in used: continue
            t = self.tracks[tid]; moves.append((tid, t['p'], pts[i])); t['p'], t['ts'] = pts[i], now; t['n'] += 1
            used.add(tid); taken.add(i)
        for i, p in enumerate(pts):
            if i not in taken:
                self.nid += 1; self.tracks[self.nid] = {'p': p, 'p0': p, 'ts': now, 'n': 1}
        return moves

def in_door(p, cfg, pad=0.0):
    dz = cfg.get('door_zone')
    return dz is None or (dz.get('x_min', -1) - pad <= p[0] <= dz['x_max'] + pad and dz['y_min'] - pad <= p[1] <= dz.get('y_max', 1.01) + pad)

def inside(p, cfg):
    """Clearly inside the store: past the vertical line (line_x mode) or, in zone mode, outside the
    door zone grown by 'clear' on every side."""
    if 'line_x' in cfg: return p[0] > cfg['line_x'] + cfg.get('band', 0.03)
    return not in_door(p, cfg, pad=cfg.get('clear', 0.10))

def decide(t, cfg):
    """Count a finished track once. IN = track STARTS in the door zone and ends clearly inside the store
    (past the line + hysteresis band). OUT = the reverse. People browsing the window display next to the
    door (ID swaps / jitter near the line) never start or end in the door zone, so they are not counted."""
    if t['n'] < cfg.get('min_hits', 3): return None
    p0, p1 = t['p0'], t['p']
    if in_door(p0, cfg) and inside(p1, cfg): return 'in'
    if in_door(p1, cfg) and inside(p0, cfg): return 'out'
    return None

_DET = {}
def log_dets(store, now, feet):
    """Raw per-frame feet points -> dets/<store>/<date>.jsonl so the tracker + rules can be re-run offline (retrack.py)."""
    day = dt.datetime.fromtimestamp(now, TZ).strftime('%Y-%m-%d')
    f = _DET.get(store)
    if f is None or f[0] != day:
        if f: f[1].close()
        d = os.path.join(HERE, 'dets', store); os.makedirs(d, exist_ok=True)
        _DET[store] = f = (day, open(os.path.join(d, day + '.jsonl'), 'a', buffering=1))
    f[1].write(json.dumps([round(now, 2), [[round(x, 3), round(y, 3)] for x, y in feet]]) + '\n')

_AUD = {}
def audit_frame(store, img, cfg, feet, now):
    """Ground-truth sampler (v5.1): during cfg audit window (default 12:00-13:00) save a timestamped crop of the
    door area whenever the picture there changes (frame differencing - independent of the person detector),
    to audit/<store>/<date>/. A reviewer counts real walk-ins from these and compares with the counter's IN/OUT."""
    a = cfg.get('audit', CFG.get('_audit', {'start': '12:00', 'end': '13:00'}))
    t = dt.datetime.fromtimestamp(now, TZ); hm = t.strftime('%H:%M')
    if not (a['start'] <= hm < a['end']): return
    H, W = img.shape[:2]; dz = cfg.get('door_zone') or {}; pad = 0.15
    x0 = max(0, dz.get('x_min', 0) - pad); x1 = min(1, dz.get('x_max', 1) + pad + (0.1 if 'line_x' in cfg else 0))
    y0 = max(0, dz.get('y_min', 0) - pad); y1 = min(1, dz.get('y_max', 1) + pad)
    crop = img[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
    if crop.size == 0: return
    g = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY), (64, 48)).astype(np.int16)
    prev = _AUD.get(store); _AUD[store] = g
    if prev is None or prev.shape != g.shape or np.mean(np.abs(g - prev)) < cfg.get('audit_motion', 4.0): return
    im = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR); h, w = im.shape[:2]; sc = 320 / w; im = cv2.resize(im, (320, int(h * sc)))
    for fx, fy in feet:
        if x0 <= fx <= x1 and y0 <= fy <= y1: cv2.circle(im, (int((fx - x0) * W * sc), int((fy - y0) * H * sc)), 4, (0, 255, 0), -1)
    cv2.putText(im, t.strftime('%H:%M:%S'), (4, 14), 0, 0.45, (0, 255, 255), 1)
    d = os.path.join(HERE, 'audit', store, t.strftime('%Y-%m-%d')); os.makedirs(d, exist_ok=True)
    cv2.imwrite(os.path.join(d, t.strftime('%H%M%S') + f'_{int(now * 10) % 10}.jpg'), im, [cv2.IMWRITE_JPEG_QUALITY, 60])

def log_track(store, t, d):
    """Every finished track -> tracks/<store>/<date>.jsonl so rules can be re-scored offline."""
    td = os.path.join(HERE, 'tracks', store); os.makedirs(td, exist_ok=True)
    with open(os.path.join(td, dt.datetime.now(TZ).strftime('%Y-%m-%d') + '.jsonl'), 'a') as f:
        f.write(json.dumps({'t': dt.datetime.now(TZ).strftime('%H:%M:%S'), 'p0': [round(v, 4) for v in t['p0']],
                            'p': [round(v, 4) for v in t['p']], 'n': t['n'], 'd': d}) + '\n')

def evidence(store, img, cfg, t, d):
    H, W = img.shape[:2]; ev = os.path.join(HERE, 'evidence', store, dt.datetime.now(TZ).strftime('%Y-%m-%d'))
    os.makedirs(ev, exist_ok=True); im = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if 'line_x' in cfg: lx = int(cfg['line_x'] * W); cv2.line(im, (lx, 0), (lx, H), (0, 0, 255), 3)
    cv2.arrowedLine(im, (int(t['p0'][0] * W), int(t['p0'][1] * H)), (int(t['p'][0] * W), int(t['p'][1] * H)), (0, 255, 255), 4)
    dz = cfg.get('door_zone')
    if dz: cv2.rectangle(im, (int(max(dz.get('x_min', 0), 0) * W), int(dz['y_min'] * H)), (int(dz['x_max'] * W), int(min(dz.get('y_max', 1), 1) * H)), (255, 0, 255), 2)
    base = os.path.join(ev, dt.datetime.now(TZ).strftime('%H%M%S') + f'_{d}')
    k = 0
    while os.path.exists(f'{base}{"_" + str(k) if k else ""}.jpg'): k += 1
    cv2.imwrite(f'{base}{"_" + str(k) if k else ""}.jpg', cv2.resize(im, (960, 540)))

def bucket(now):
    return dt.datetime.fromtimestamp(now, TZ).strftime('%Y-%m-%d %H:00')

def flush(store, counts):
    os.makedirs(os.path.join(HERE, 'counts'), exist_ok=True)
    path = os.path.join(HERE, 'counts', f'{store}.csv')
    rows = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path)): rows[r['hour']] = r
    for h, c in counts.items():
        r = rows.setdefault(h, {'hour': h, 'in': 0, 'out': 0})
        r['in'] = int(r['in']) + c['in']; r['out'] = int(r['out']) + c['out']
    with open(path + '.tmp', 'w', newline='') as f:
        w = csv.DictWriter(f, ['hour', 'in', 'out']); w.writeheader()
        for h in sorted(rows): w.writerow(rows[h])
    os.replace(path + '.tmp', path); counts.clear()

async def run(store, minutes, debug):
    cfg = CFG[store]   # all geometry is normalized (0..1)
    end = time.time() + minutes * 60; counts = {}; trk = None; seen = 0
    backoff = 0
    while time.time() < end:
        try:   # v5.1: a refused/rate-limited (429) connect backs off and retries instead of crashing the agent
            at = ns.token(); at_ts = time.time(); cam = ns.camera(cfg.get('store', store), cfg['camera'])
            pc, fut, sid = await ns.open_stream(at, cam)
        except Exception as e:
            backoff = min(300, backoff * 2 if backoff else 20)
            print(dt.datetime.now(TZ).strftime('%H:%M:%S'), 'connect failed', repr(e)[:100], f'retry {backoff}s', flush=True)
            await asyncio.sleep(backoff + random.uniform(0, 10)); continue
        backoff = 0; started = time.time(); last = 0; nf = 0; ext_try = 0
        try:
            track = await asyncio.wait_for(fut, 30)
            while time.time() < end:
                if time.time() - started > EXTEND_EVERY and time.time() - ext_try > 15:
                    ext_try = time.time()
                    try:   # v5.1: retry a failed extend every 15 s until the session's 5-min life is nearly up
                        if time.time() - at_ts > 3000: at = ns.token(); at_ts = time.time()   # access tokens live 1 h
                        sid = ns.command(at, cam['id'], 'sdm.devices.commands.CameraLiveStream.ExtendWebRtcStream',
                                         {'mediaSessionId': sid})['results']['mediaSessionId']; started = time.time()
                    except Exception:
                        if time.time() - started > 290: break  # session about to expire -> reconnect
                f = await asyncio.wait_for(track.recv(), 20)
                now = time.time()
                if now - last < 0.25: continue
                last = now; img = f.to_ndarray(format='rgb24'); H, W = img.shape[:2]
                if trk is None:
                    trk = Tracker(cfg.get('max_dist', 0.08), cfg.get('max_age', 3.0), cfg.get('speed', 0.30))
                feet = [((x1 + x2) / 2 / W, y2 / H) for x1, y1, x2, y2, s in detector.people(img, conf=cfg.get('conf', 0.30))]
                log_dets(store, now, feet)
                try: audit_frame(store, img, cfg, feet, now)
                except Exception: pass
                trk.update(feet, now)
                for t in trk.expire(now):
                    d = decide(t, cfg)
                    if t['n'] >= cfg.get('min_hits', 3): log_track(store, t, d)
                    if d:
                        counts.setdefault(bucket(now), {'in': 0, 'out': 0})[d] += 1
                        print(dt.datetime.now(TZ).strftime('%H:%M:%S'), d.upper(), flush=True)
                        evidence(store, img, cfg, t, d)
                nf += 1; seen += len(feet)
                if nf % 240 == 0: print(dt.datetime.now(TZ).strftime('%H:%M:%S'), f'frames={nf} detections={seen} size={W}x{H}', flush=True); seen = 0
                if debug and nf % 40 == 1:
                    dbg = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    for x, y in feet: cv2.circle(dbg, (int(x * W), int(y * H)), 5, (0, 255, 0), -1)
                    cv2.imwrite(os.path.join(HERE, f'debug_{store}.jpg'), dbg)
                if counts and now % 60 < 0.3: flush(store, counts)
        except Exception as e:
            print('stream error', repr(e)[:120], flush=True); await asyncio.sleep(5)
        finally:
            if trk:
                for t in trk.expire(time.time(), force=True):
                    d = decide(t, cfg)
                    if d: counts.setdefault(bucket(time.time()), {'in': 0, 'out': 0})[d] += 1
            await ns.stop(at, cam, pc, sid); flush(store, counts)

if __name__ == '__main__':
    store = sys.argv[1]
    mins = float(sys.argv[sys.argv.index('--minutes') + 1]) if '--minutes' in sys.argv else 600
    if '--until-close' in sys.argv:   # launchd mode: run from now until 5 min after today's close
        now = dt.datetime.now(TZ); hrs = CFG[store]['hours'].get(now.strftime('%a'))
        if not hrs: print('closed today'); sys.exit(0)
        close = now.replace(hour=int(hrs[1][:2]), minute=int(hrs[1][3:]), second=0) + dt.timedelta(minutes=5)
        mins = (close - now).total_seconds() / 60
        if mins <= 0: print('already closed'); sys.exit(0)
    asyncio.run(run(store, mins, '--debug' in sys.argv))
