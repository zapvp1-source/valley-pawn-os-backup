"""Valley Pawn door counter. Streams one Nest door camera, detects people ~4 fps, tracks feet
points, counts crossings of a virtual line. Writes hourly IN/OUT to counts/<store>.csv.
Usage: python3 counter.py <store> [--minutes N] [--debug]
Config: config.json (per-store camera + line). Secrets: $VPST_DIR (default ~/.vpst)."""
import asyncio, csv, datetime as dt, json, math, os, sys, time, zoneinfo
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
    """Nearest-neighbour tracker in NORMALIZED coords (0..1), so stream resolution switches
    (Nest flips between 1920x1080 and 640x360 mid-stream) don't break it."""
    def __init__(self, max_dist=0.08, max_age=2.0):
        self.tracks, self.nid, self.max_dist, self.max_age = {}, 0, max_dist, max_age
    def expire(self, now, force=False):
        done = []
        for tid, t in list(self.tracks.items()):
            if force or now - t['ts'] > self.max_age: done.append(self.tracks.pop(tid))
        return done
    def update(self, pts, now):
        moves, used = [], set()
        for p in sorted(pts, key=lambda p: p[1]):
            best, bd = None, self.max_dist
            for tid, t in self.tracks.items():
                if tid in used: continue
                d = math.dist(p, t['p'])
                if d < bd: best, bd = tid, d
            if best is None:
                self.nid += 1; self.tracks[self.nid] = {'p': p, 'p0': p, 'ts': now, 'n': 1}; used.add(self.nid)
            else:
                t = self.tracks[best]; moves.append((best, t['p'], p)); t['p'], t['ts'] = p, now; t['n'] += 1; used.add(best)
        return moves

def decide(t, cfg):
    """Count a finished track once: IN if it started clearly on the outside of the door line and ended
    clearly inside (outside of a hysteresis band), OUT for the reverse. Jitter at the line = no count."""
    if t['n'] < cfg.get('min_hits', 3): return None
    lx, band, inside = cfg['line_x'], cfg.get('band', 0.03), cfg.get('inside', 'right')
    def zone(p):
        if p[1] < cfg.get('min_y', 0.39): return None   # ignore detections above the door area
        if p[0] < lx - band: return 'left'
        if p[0] > lx + band: return 'right'
        return None
    z0, z1 = zone(t['p0']), zone(t['p'])
    if not z0 or not z1 or z0 == z1: return None
    return 'in' if z1 == inside else 'out'

def evidence(store, img, cfg, t, d):
    H, W = img.shape[:2]; ev = os.path.join(HERE, 'evidence', store, dt.datetime.now(TZ).strftime('%Y-%m-%d'))
    os.makedirs(ev, exist_ok=True); im = cv2.cvtColor(img, cv2.COLOR_RGB2BGR); lx = int(cfg['line_x'] * W)
    cv2.line(im, (lx, 0), (lx, H), (0, 0, 255), 3)
    cv2.arrowedLine(im, (int(t['p0'][0] * W), int(t['p0'][1] * H)), (int(t['p'][0] * W), int(t['p'][1] * H)), (0, 255, 255), 4)
    cv2.imwrite(os.path.join(ev, dt.datetime.now(TZ).strftime('%H%M%S') + f'_{d}.jpg'), cv2.resize(im, (960, 540)))

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
    while time.time() < end:
        at = ns.token(); cam = ns.camera(store, cfg['camera'])
        pc, fut, sid = await ns.open_stream(at, cam); started = time.time(); last = 0; nf = 0
        try:
            track = await asyncio.wait_for(fut, 30)
            while time.time() < end:
                if time.time() - started > EXTEND_EVERY:
                    try:
                        sid = ns.command(at, cam['id'], 'sdm.devices.commands.CameraLiveStream.ExtendWebRtcStream',
                                         {'mediaSessionId': sid})['results']['mediaSessionId']; started = time.time()
                    except Exception:
                        break  # reconnect
                f = await asyncio.wait_for(track.recv(), 20)
                now = time.time()
                if now - last < 0.25: continue
                last = now; img = f.to_ndarray(format='rgb24'); H, W = img.shape[:2]
                if trk is None:
                    trk = Tracker(cfg.get('max_dist', 0.08))
                feet = [((x1 + x2) / 2 / W, y2 / H) for x1, y1, x2, y2, s in detector.people(img, conf=cfg.get('conf', 0.30))]
                trk.update(feet, now)
                for t in trk.expire(now):
                    d = decide(t, cfg)
                    if d:
                        counts.setdefault(bucket(now), {'in': 0, 'out': 0})[d] += 1
                        print(dt.datetime.now(TZ).strftime('%H:%M:%S'), d.upper(), flush=True)
                        evidence(store, img, cfg, t, d)
                nf += 1; seen += len(feet)
                if nf % 240 == 0: print(dt.datetime.now(TZ).strftime('%H:%M:%S'), f'frames={nf} detections={seen} size={W}x{H}', flush=True); seen = 0
                if debug and nf % 40 == 1:
                    dbg = cv2.cvtColor(img, cv2.COLOR_RGB2BGR); lx = int(cfg['line_x'] * W)
                    cv2.line(dbg, (lx, 0), (lx, H), (0, 0, 255), 2)
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
