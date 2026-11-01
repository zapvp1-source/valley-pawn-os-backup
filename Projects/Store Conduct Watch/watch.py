"""Store Conduct Watch — recorder (built 2026-10-31).
Streams one store's counter cameras over the Nest SDM API (reuses Store Traffic Counter/nest_stream.py,
read-only import), and for each camera:
  * saves a still every STILL_EVERY seconds (<=1280x720 JPEG) + index.jsonl  -> used by analyze.py
  * records continuous 960x540 @ 6 fps video + mono audio in 10-minute .mkv segments -> clips + audio review
Data lives OUTSIDE Projects (large, not for Drive/iCloud): ~/.vp-studio/conduct-watch/{frames,rec,state}/
Usage: watch.py <Store> [--until-close | --minutes N]
"""
import asyncio, datetime as dt, fractions, json, os, sys, time, traceback, zoneinfo
import av
sys.path.insert(0, os.path.expanduser('~/Documents/Claude/Projects/Store Traffic Counter'))
import nest_stream as ns

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, 'config.json')))
TZ = zoneinfo.ZoneInfo('America/New_York')
DATA = os.path.expanduser('~/.vp-studio/conduct-watch')
EXTEND_EVERY = 240          # SDM WebRTC sessions expire after 5 min
SEG_SECS = 600
STILL_EVERY = CFG.get('_still_every', 20)
W, H, FPS = 640, 360, 6   # SDM streams arrive at 640x360 most of the time; no point upscaling
MIN_FREE_GB = 15   # Mac SSD is ~91% full: below this, stills only (no video)
VCODECS = ['h264_videotoolbox', 'libx264', 'mpeg4']

def now():
    return dt.datetime.now(TZ)

def log(*a):
    print(now().strftime('%H:%M:%S'), *a, flush=True)

def slug(s):
    return ''.join(c if c.isalnum() else '_' for c in s).strip('_')

def pick_vcodec():
    for c in VCODECS:
        try:
            av.codec.Codec(c, 'w'); return c
        except Exception:
            pass
    return None

VCODEC = pick_vcodec()

class Segment:
    """One .mkv file: video (VCODEC) + mono AAC audio, pts from wall clock relative to segment start."""
    def __init__(self, store, cam):
        self.t0 = time.time(); d = now()
        self.dir = os.path.join(DATA, 'rec', store, slug(cam), d.strftime('%Y-%m-%d'))
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, d.strftime('%H%M%S') + '.mkv')
        self.c = av.open(self.path, 'w', format='matroska')
        self.v = self.c.add_stream(VCODEC, rate=FPS)
        self.v.width, self.v.height, self.v.pix_fmt = W, H, 'yuv420p'
        self.v.bit_rate = 300_000
        self.a = self.c.add_stream('aac', rate=48000)
        try: self.a.layout = 'mono'
        except Exception:
            try: self.a.codec_context.layout = 'mono'
            except Exception: pass
        self.last_vpts = -1; self.apts = 0
        self.fifo = av.AudioFifo(); self.rs = av.AudioResampler(format='fltp', layout='mono', rate=48000)
        meta = {'start': d.strftime('%H:%M:%S'), 'epoch': self.t0, 'codec': VCODEC}
        with open(self.path + '.json', 'w') as f: json.dump(meta, f)

    def video(self, frame, t):
        pts = int(round((t - self.t0) * FPS))
        if pts <= self.last_vpts: return
        vf = frame.reformat(width=W, height=H, format='yuv420p')
        vf.pts = pts; vf.time_base = fractions.Fraction(1, FPS)
        for p in self.v.encode(vf): self.c.mux(p)
        self.last_vpts = pts

    def audio(self, frame, t):
        want = int((t - self.t0) * 48000)
        if abs(want - self.apts) > 24000: self.apts = max(want, self.apts)   # resync after a gap
        for rf in self.rs.resample(frame):
            rf.pts = None; self.fifo.write(rf)
        while self.fifo.samples >= 1024:
            out = self.fifo.read(1024); out.pts = self.apts; out.time_base = fractions.Fraction(1, 48000)
            self.apts += 1024
            for p in self.a.encode(out): self.c.mux(p)

    def close(self):
        for s in (self.v, self.a):
            try:
                for p in s.encode(None): self.c.mux(p)
            except Exception: pass
        try: self.c.close()
        except Exception: pass
        try:
            m = json.load(open(self.path + '.json')); m['end'] = now().strftime('%H:%M:%S'); m['secs'] = round(time.time() - self.t0)
            json.dump(m, open(self.path + '.json', 'w'))
        except Exception: pass

class Cam:
    def __init__(self, store, name):
        self.store, self.name = store, name
        self.stats = {'cam': name, 'stills': 0, 'segments': 0, 'reconnects': 0, 'last_frame': None, 'size': None, 'audio_frames': 0}
        self.seg = None; self.last_still = 0

    def still(self, frame, t):
        d = now(); fd = os.path.join(DATA, 'frames', self.store, slug(self.name), d.strftime('%Y-%m-%d'))
        os.makedirs(fd, exist_ok=True); im = frame.to_image()
        if im.width > 1280: im = im.resize((1280, int(1280 * im.height / im.width)))
        fn = d.strftime('%H%M%S') + '.jpg'; im.save(os.path.join(fd, fn), quality=75)
        with open(os.path.join(fd, 'index.jsonl'), 'a') as f:
            f.write(json.dumps({'t': d.strftime('%H:%M:%S'), 'f': fn, 'w': frame.width, 'h': frame.height}) + '\n')
        self.stats['stills'] += 1

    def rotate(self):
        if self.seg: self.seg.close()
        self.seg = None
        import shutil
        if shutil.disk_usage(DATA).free < MIN_FREE_GB * 1e9:
            self.stats['video_paused_low_disk'] = True; return
        if VCODEC:
            try: self.seg = Segment(self.store, self.name); self.stats['segments'] += 1
            except Exception as e: log(self.name, 'segment open failed', repr(e)[:150])

    async def run(self, end):
        while time.time() < end:
            at = ns.token(); cam = ns.camera(self.store, self.name); pc = sid = None
            try:
                pc, fut, sid = await ns.open_stream(at, cam); started = time.time()
                track = await asyncio.wait_for(fut, 30)
                atrack = next((r.track for r in pc.getReceivers() if r.track and r.track.kind == 'audio'), None)
                aq = asyncio.ensure_future(self.audio_loop(atrack)) if atrack else None
                self.rotate()
                while time.time() < end:
                    if time.time() - started > EXTEND_EVERY:
                        sid = ns.command(at, cam['id'], 'sdm.devices.commands.CameraLiveStream.ExtendWebRtcStream',
                                         {'mediaSessionId': sid})['results']['mediaSessionId']; started = time.time()
                    f = await asyncio.wait_for(track.recv(), 20); t = time.time()
                    self.stats['last_frame'] = now().strftime('%H:%M:%S'); self.stats['size'] = f'{f.width}x{f.height}'
                    if t - self.last_still >= STILL_EVERY:
                        self.last_still = t; self.still(f, t)
                    if self.seg:
                        if t - self.seg.t0 >= SEG_SECS: self.rotate()
                        try: self.seg.video(f, t)
                        except Exception as e: log(self.name, 'video enc', repr(e)[:120]); self.rotate()
                if aq: aq.cancel()
            except Exception as e:
                self.stats['reconnects'] += 1
                log(self.name, 'stream error', repr(e)[:160]); await asyncio.sleep(10)
            finally:
                if self.seg: self.seg.close(); self.seg = None
                if pc: await ns.stop(at, cam, pc, sid)

    async def audio_loop(self, t):
        while True:
            f = await t.recv(); self.stats['audio_frames'] += 1
            if self.seg:
                try: self.seg.audio(f, time.time())
                except Exception as e: log(self.name, 'audio enc', repr(e)[:120])

async def heartbeat(store, cams, end):
    sd = os.path.join(DATA, 'state'); os.makedirs(sd, exist_ok=True)
    while time.time() < end:
        st = {'store': store, 'updated': now().isoformat(timespec='seconds'), 'vcodec': VCODEC, 'cams': [c.stats for c in cams]}
        json.dump(st, open(os.path.join(sd, f'{store}.json'), 'w'), indent=1)
        await asyncio.sleep(60)

async def main(store, minutes):
    end = time.time() + minutes * 60
    cams = [Cam(store, n) for n in CFG['stores'][store]['cameras']]
    log(store, 'cameras', [c.name for c in cams], 'vcodec', VCODEC, 'minutes', round(minutes))
    await asyncio.gather(heartbeat(store, cams, end), *[c.run(end) for c in cams])

def minutes_until_close(store):
    n = now(); hrs = CFG['stores'][store]['hours'].get(n.strftime('%a'))
    if not hrs: return 0
    close = n.replace(hour=int(hrs[1][:2]), minute=int(hrs[1][3:]), second=0) + dt.timedelta(minutes=5)
    return (close - n).total_seconds() / 60

if __name__ == '__main__':
    store = sys.argv[1]
    mins = float(sys.argv[sys.argv.index('--minutes') + 1]) if '--minutes' in sys.argv else 60
    if now().date().isoformat() > CFG.get('trial_end', '9999'): print('trial ended', CFG.get('trial_end')); sys.exit(0)
    if '--until-close' in sys.argv:
        mins = minutes_until_close(store)
        if mins <= 0: print('closed / after close'); sys.exit(0)
    asyncio.run(main(store, mins))
