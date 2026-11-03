#!/usr/bin/env python3
"""conduct_watch_export.py — read-only export from the Store Conduct Watch data for a human/Claude deep dive (2026-11-02, additive).

  sheets  --out DIR [--days N]      one contact sheet per 12 minutes per camera-day (1 still/min, 480x270 tiles, 4x3),
                                    plus every transcript .jsonl, into DIR/<date>/<store>/<cam>/. Also DIR/index.json.
  stills  --out DIR --store S --cam C --date D --from HH:MM --to HH:MM   full-size 20-s stills for one window.
  clip    --out FILE --store S --cam C --date D --at HH:MM:SS [--secs 30] [--cap "text"]   mp4 with audio from the raw
                                    recording (3-day retention) via analyze.cut_clip; falls back to a still slideshow.
Never writes anywhere but --out. Never touches the watch's own state."""
import os, sys, json, glob, argparse, datetime as dt
sys.path.insert(0, os.path.expanduser('~/Documents/Claude/Projects/Store Conduct Watch'))
from PIL import Image, ImageDraw, ImageFont
import analyze as A
DATA = A.DATA

def cams():
    for store, cfg in A.CFG['stores'].items():
        for cam in cfg['cameras']: yield store, cam

def sheets(out, days):
    today = dt.date.today(); idx = []
    for store, cam in cams():
        for d in range(days):
            date = (today - dt.timedelta(days=d)).isoformat()
            fr = A.stills(store, cam, date)
            if not fr: continue
            # 1 still per minute
            pm = {}
            for r in fr: pm.setdefault(int(r['s']) // 60, r)
            mins = sorted(pm)
            od = os.path.join(out, date, store, A.slug(cam)); os.makedirs(od, exist_ok=True)
            f = ImageFont.load_default()
            for i in range(0, len(mins), 12):
                chunk = [pm[m] for m in mins[i:i + 12]]
                S = Image.new('RGB', (4 * 480, 3 * 270), 'black'); g = ImageDraw.Draw(S)
                for j, r in enumerate(chunk):
                    try: im = Image.open(r['path']).convert('RGB').resize((480, 270))
                    except Exception: continue
                    x, y = (j % 4) * 480, (j // 4) * 270; S.paste(im, (x, y))
                    g.rectangle([x, y, x + 110, y + 18], fill=(0, 0, 0)); g.text((x + 3, y + 3), A.clock(r['s']), fill=(255, 255, 0), font=f)
                name = f"{A.clock(chunk[0]['s']).replace(':', '').replace(' ', '')}.jpg"
                S.save(os.path.join(od, name), quality=72)
                idx.append({'date': date, 'store': store, 'cam': cam, 'sheet': os.path.join(date, store, A.slug(cam), name), 'from': A.clock(chunk[0]['s']), 'to': A.clock(chunk[-1]['s']), 'n': len(chunk)})
            tp = os.path.join(DATA, 'transcripts', store, A.slug(cam), date + '.jsonl')
            if os.path.exists(tp):
                import shutil; shutil.copy2(tp, os.path.join(od, 'transcript.jsonl'))
    json.dump(idx, open(os.path.join(out, 'index.json'), 'w'), indent=1)
    print('sheets', len(idx))

def stills(out, store, cam, date, t0, t1):
    s0, s1 = A.secs(t0), A.secs(t1); os.makedirs(out, exist_ok=True); n = 0
    for r in A.stills(store, cam, date):
        if s0 <= r['s'] <= s1:
            import shutil; shutil.copy2(r['path'], os.path.join(out, f"{store}_{A.slug(cam)}_{date}_{os.path.basename(r['path'])}")); n += 1
    print('stills', n)

def clip(out, store, cam, date, at, secs_len, cap, cat='review'):
    s = A.secs(at)
    ep = {'store': store, 'camera': cam, 'best_s': s, 'start': A.clock(s), 'cat': cat, 'what': cap or '', 'win': [s - 60, s + 60]}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ok = False
    try: ok = A.cut_clip(ep, date, out, secs_len)
    except Exception as e: print('cut_clip failed', repr(e)[:200])
    if not ok:
        try: ok = A.still_clip(ep, date, out)
        except Exception as e: print('still_clip failed', repr(e)[:200])
    print('clip', 'ok' if ok else 'FAILED', out)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('mode'); ap.add_argument('--out', required=True)
    ap.add_argument('--days', type=int, default=3); ap.add_argument('--store'); ap.add_argument('--cam'); ap.add_argument('--date')
    ap.add_argument('--from', dest='t0'); ap.add_argument('--to', dest='t1'); ap.add_argument('--at'); ap.add_argument('--secs', type=int, default=30); ap.add_argument('--cap', default=''); ap.add_argument('--cat', default='review'); ap.add_argument('--data')
    a = ap.parse_args()
    if a.data: A.DATA = a.data  # cut from a kept copy of the recordings instead of the live watch data
    if a.mode == 'sheets': sheets(a.out, a.days)
    elif a.mode == 'stills': stills(a.out, a.store, a.cam, a.date, a.t0, a.t1)
    elif a.mode == 'clip': clip(a.out, a.store, a.cam, a.date, a.at, a.secs, a.cap, a.cat)
    elif a.mode == 'describe':
        # describe --out FILE.json --store DIR_OF_FOLDERS : for each sub-folder of 20-s stills, ask the verify model (vision)
        # a fixed staff-conduct question; read-only, writes only --out.
        import io
        from PIL import Image
        Q = ('These are 20-second-apart stills from a pawn-shop security camera. Only people BEHIND the counter / at the workstation are employees; '
             'people across the counter are customers. Uniform = Valley Pawn branded polo or work shirt in any colour; coats, jackets, hoodies and hats/head wraps '
             'are not uniform. Answer ONLY JSON: {"employee_visible": bool, "employee_clothing": "<what the employee behind the counter is wearing, head to toe as visible>", '
             '"out_of_uniform": true|false|"unsure", "why": "<one sentence>", "customer_present": bool, "phone_in_hand": true|false|"unsure", '
             '"phone_detail": "<if a handheld device is visible: personal smartphone being looked at, store handset, item being serviced, or unclear>", "best_frame": <1-based index>}')
        res = {}
        for d in sorted(os.listdir(a.store)):
            if a.cam and d != a.cam: continue
            fs = sorted(glob.glob(os.path.join(a.store, d, '*.jpg')))
            if not fs: continue
            pick = fs[::max(1, len(fs) // 6)][:6]
            imgs = []
            for f in pick:
                b = io.BytesIO(); Image.open(f).convert('RGB').resize((960, 540)).save(b, 'JPEG', quality=80); imgs.append(b.getvalue())
            try: res[d] = {'frames': [os.path.basename(f) for f in pick], 'answer': A.ask_json(A.CFG.get('verify_model', 'claude-sonnet-5-5'), Q, imgs, 2500)}
            except Exception as e: res[d] = {'error': repr(e)[:300]}
            print(d, json.dumps(res[d])[:400], flush=True)
        json.dump(res, open(a.out, 'w'), indent=1)
    elif a.mode == 'keep':
        # keep --out KEEPROOT --date D : copy that day's raw recordings (all cameras) out of the watch's rec/ before nightly retention
        # removes them, so clips with audio can still be cut later with  clip --data KEEPROOT ...
        import shutil
        tot = 0
        for src in glob.glob(os.path.join(DATA, 'rec', '*', '*', a.date)):
            rel = os.path.relpath(src, DATA); dst = os.path.join(a.out, rel)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            n = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(dst) for f in fs); tot += n
            print('kept', rel, round(n / 1e6), 'MB')
        print('keep total MB', round(tot / 1e6))
    elif a.mode == 'pack':
        # pack --out FILE.tar --store SRC_DIR : tar a directory (used to hand sheets/clips to the cloud session)
        import tarfile
        src = a.store
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        with tarfile.open(a.out, 'w') as tf: tf.add(src, arcname=os.path.basename(src.rstrip('/')))
        print('pack ok', a.out, os.path.getsize(a.out))
