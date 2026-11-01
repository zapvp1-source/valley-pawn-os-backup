"""Store Conduct Watch probe: list cameras (names only, no ids/secrets) and test live frames + audio for one camera.
Usage: probe.py list | probe.py grab "<Store>" "<Camera name>" [seconds]"""
import asyncio, json, os, sys, time
sys.path.insert(0, os.path.expanduser('~/Documents/Claude/Projects/Store Traffic Counter'))
import nest_stream as ns
HERE = os.path.dirname(os.path.abspath(__file__))

def lst():
    for c in json.load(open(os.path.join(ns.VPST, 'cameras.json'))):
        print(json.dumps({k: v for k, v in c.items() if k in ('store', 'name', 'type', 'room', 'model')}))

async def grab(store, name, secs=20):
    at = ns.token(); cam = ns.camera(store, name)
    pc, fut, sid = await ns.open_stream(at, cam); audio = {'n': 0, 'rate': None}
    try:
        track = await asyncio.wait_for(fut, 30)
        atr = next((r.track for r in pc.getReceivers() if r.track and r.track.kind == 'audio'), None)
        async def eat():
            while True:
                f = await atr.recv(); audio['n'] += 1; audio['rate'] = f.sample_rate
        task = asyncio.ensure_future(eat()) if atr else None
        t0 = time.time(); n = 0; sizes = set(); last = None
        while time.time() - t0 < secs:
            f = await asyncio.wait_for(track.recv(), 20); n += 1; sizes.add((f.width, f.height)); last = f
        if task: task.cancel()
        out = os.path.join(HERE, 'probe', f"{store}_{name}.jpg".replace(' ', '_'))
        last.to_image().save(out, quality=88)
        print(json.dumps({'store': store, 'cam': name, 'frames': n, 'fps': round(n / secs, 1), 'sizes': sorted(sizes),
                          'audio_frames': audio['n'], 'audio_rate': audio['rate'], 'out': os.path.basename(out)}))
    finally:
        await ns.stop(at, cam, pc, sid)

def status():
    import datetime as dt, glob, shutil
    data = os.path.expanduser('~/.vp-studio/conduct-watch'); d = dt.date.today().isoformat()
    for f in sorted(glob.glob(os.path.join(data, 'state', '*.json'))):
        st = json.load(open(f)); print('STATE', st['store'], st['updated'])
        for c in st['cams']: print('   ', json.dumps(c))
    for p in sorted(glob.glob(os.path.join(data, 'frames', '*', '*', d))): print('stills', p.split('frames/')[1], len(glob.glob(p + '/*.jpg')))
    for p in sorted(glob.glob(os.path.join(data, 'rec', '*', '*', d))):
        fs = glob.glob(p + '/*.mkv'); print('video', p.split('rec/')[1], len(fs), 'files', round(sum(os.path.getsize(x) for x in fs) / 1e6), 'MB')
    print('disk free GB', round(shutil.disk_usage(data).free / 1e9))

if __name__ == '__main__':
    if sys.argv[1] == 'list': lst()
    elif sys.argv[1] == 'status': status()
    else: asyncio.run(grab(sys.argv[2], sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 20))
