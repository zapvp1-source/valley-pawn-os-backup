"""Store Conduct Watch — nightly analysis (built 2026-10-31). Run after close for a business date.
  1. SCREEN: per camera, 4x3 contact sheets of one still per minute -> fast model flags possible problems (recall).
  2. VERIFY: every flagged window is re-checked on all 20-second stills by the stronger model (precision).
  3. LISTEN: the day's audio is transcribed locally (faster-whisper); cussing / rude phrases become candidates,
     each judged with its transcript context + the matching still.
  4. CLIP: every verified severity>=2 moment gets a captioned ~24 s clip with sound cut from the local recording.
Output: Projects/Store Conduct Watch/reports/<date>/{episodes.json, summary.md, clips/*.mp4, run.json}
Usage: analyze.py [YYYY-MM-DD] [--store S] [--no-audio] [--no-clips]
"""
import base64, concurrent.futures as cf, datetime as dt, glob, io, json, os, re, sys, time, traceback, zoneinfo
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/Documents/Claude/Projects/Valley Pawn OS/bin'))
import vp_ai
CFG = json.load(open(os.path.join(HERE, 'config.json')))
TZ = zoneinfo.ZoneInfo('America/New_York')
DATA = os.path.expanduser('~/.vp-studio/conduct-watch')
FONT = next((p for p in ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
                         '/System/Library/Fonts/Helvetica.ttc'] if os.path.exists(p)), None)
def font(n):
    try: return ImageFont.truetype(FONT, n) if FONT else ImageFont.load_default()
    except Exception: return ImageFont.load_default()
def slug(s): return ''.join(c if c.isalnum() else '_' for c in s).strip('_')
def secs(hms): h, m, s = (hms.split(':') + ['0'])[:3]; return int(h) * 3600 + int(m) * 60 + int(s)
def clock(t): t = int(t); h, m = t // 3600, (t // 60) % 60; return f"{(h - 1) % 12 + 1}:{m:02d} {'PM' if h >= 12 else 'AM'}"
def log(*a): print(dt.datetime.now(TZ).strftime('%H:%M:%S'), *a, flush=True)

RUBRIC = """You review store security-camera stills for Valley Pawn, a pawn shop. The owner wants to know about
TRUE BAD behavior by employees (staff are behind the counter / at the workstations; customers are on the floor side):
- IGNORED: a customer waiting at the counter while an employee is right there but not engaging (on a phone, on the computer for personal use, chatting with a coworker, reclined).
- LEFT WAITING: a customer at the counter with no employee in view for 2+ minutes.
- PHONE WITH CUSTOMER: employee using a personal phone while a customer is at/near the counter.
- FEET UP: employee reclined with feet on the desk/counter, especially with customers present.
- CONDUCT: eating at the counter, sitting/lying on the floor, sleeping/head down, horseplay, a child or non-employee behind the counter, cash or merchandise left out unattended, rude body language toward a customer.
- IDLE: phone scrolling / feet up / idle for 10+ straight minutes even with no customer.
NOT a problem: helping customers, short glances at a phone, phone held to the ear (business call), photographing merchandise, quiet store with staff tidying or on the register computer."""

USAGE = {'screen': 0, 'verify': 0, 'lang': 0}
def people_counts(paths):
    """Person counts per still via people_filter.py in a separate process (fails open: -1 = unknown)."""
    import subprocess
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, 'people_filter.py')], input='\n'.join(paths), capture_output=True, text=True, timeout=1800)
        return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:
        log('people filter failed', repr(e)[:120]); return {}

def stills(store, cam, date):
    d = os.path.join(DATA, 'frames', store, slug(cam), date); out = []
    if not os.path.exists(os.path.join(d, 'index.jsonl')): return out
    for l in open(os.path.join(d, 'index.jsonl')):
        try: r = json.loads(l); r['s'] = secs(r['t']); r['path'] = os.path.join(d, r['f']); out.append(r)
        except Exception: pass
    return [r for r in out if os.path.exists(r['path'])]

def sheet(frames, cols, tw, th, labels):
    S = Image.new('RGB', (cols * tw, ((len(frames) + cols - 1) // cols) * th), 'black'); g = ImageDraw.Draw(S); f = font(max(16, tw // 22))
    for i, fr in enumerate(frames):
        x, y = (i % cols) * tw, (i // cols) * th
        try: S.paste(Image.open(fr['path']).convert('RGB').resize((tw, th)), (x, y))
        except Exception: pass
        g.rectangle([x, y, x + tw, y + max(16, tw // 22) + 10], fill=(0, 0, 0)); g.text((x + 6, y + 4), labels[i], fill=(255, 220, 0), font=f)
        g.rectangle([x, y, x + tw - 1, y + th - 1], outline=(0, 0, 0), width=3)
    b = io.BytesIO(); S.save(b, 'JPEG', quality=82); return b.getvalue()

def img_block(jpg):
    return {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg', 'data': base64.b64encode(jpg).decode()}}

def ask_json(model, text, images, max_tokens=2500):
    content = [img_block(j) for j in images] + [{'type': 'text', 'text': text}]
    last = None
    for attempt in range(3):
        try:
            return vp_ai.ask_json('', model=model, max_tokens=max_tokens, content=content)
        except Exception as e:
            last = e
            if 'usage limit' in str(e).lower() or 'credit' in str(e).lower(): raise
            time.sleep(5 * (attempt + 1))
    raise last

def screen_camera(store, cam, frames):
    """One still per minute, 12 per sheet. Returns candidate windows [(start_s, end_s, cat, note)]."""
    per_min, last = [], -999
    step = CFG.get('screen_every', 60) - 2
    for r in frames:
        if r['s'] - last >= step: per_min.append(r); last = r['s']
    pc = people_counts([r['path'] for r in per_min])
    per_min = [r for r in per_min if pc.get(r['path'], -1) != 0]   # skip empty-counter stills (local detector, free)
    budget = max(0, CFG.get('max_screen_calls_per_day', 300) - USAGE['screen'])
    jobs = [per_min[i:i + 12] for i in range(0, len(per_min), 12)][:budget]
    USAGE['screen'] += len(jobs)
    def one(chunk):
        labels = [f"{i + 1}  {clock(r['s'])}" for i, r in enumerate(chunk)]
        q = (RUBRIC + f"\n\nThis is {store}, camera '{cam}'. The sheet shows {len(chunk)} stills one minute apart (numbered, with the time). "
             "Flag tile ranges that likely show one of the problems. A problem must be visible in at least 2 consecutive tiles (2+ minutes apart), EXCEPT a customer clearly left waiting with no staff, a child/non-employee behind the counter, or cash/merchandise left out — those count from one tile. A stronger reviewer re-checks every flag, but don't flag normal work. "
             'Answer ONLY JSON: {"flags":[{"tiles":[first,last],"cat":"IGNORED|LEFT WAITING|PHONE WITH CUSTOMER|FEET UP|CONDUCT|IDLE","note":"who/what in a few words"}]} — empty list if nothing.')
        res = ask_json(CFG['screen_model'], q, [sheet(chunk, 4, 480, 270, labels)], 2000)
        out = []
        for fl in (res.get('flags') or []):
            try:
                a, b = int(fl['tiles'][0]) - 1, int(fl['tiles'][-1]) - 1; a, b = max(0, a), min(len(chunk) - 1, b)
                out.append((chunk[a]['s'], chunk[b]['s'], fl.get('cat', ''), fl.get('note', '')))
            except Exception: pass
        return out
    cands = []
    with cf.ThreadPoolExecutor(4) as ex:
        for r in ex.map(one, jobs): cands += r
    # merge overlapping / adjacent windows
    cands.sort(); merged = []
    for c in cands:
        if merged and c[0] <= merged[-1][1] + 300:
            m = merged[-1]; merged[-1] = (m[0], max(m[1], c[1]), m[2], (m[3] + '; ' + c[3])[:300])
        else: merged.append(c)
    return merged, len(jobs)

def verify(store, cam, frames, cand):
    s0, s1, cat, note = cand
    win = [r for r in frames if s0 - 60 <= r['s'] <= s1 + 60]
    if len(win) > 12: step = len(win) / 12; win = [win[int(i * step)] for i in range(12)]
    if not win: return None
    labels = [f"{i + 1}  {r['t'][:5]}" for i, r in enumerate(win)]
    imgs = [sheet(win[i:i + 6], 3, 640, 360, labels[i:i + 6]) for i in range(0, len(win), 6)]
    q = (RUBRIC + f"\n\nThis is {store}, camera '{cam}', stills about 20 seconds apart covering {clock(win[0]['s'])}-{clock(win[-1]['s'])}. "
         f"A first-pass reviewer flagged: {cat} — {note}. Decide carefully whether it is REAL. Be strict: only confirm what is clearly visible. "
         "severity: 3 = customer-insulting or fire-able (customer ignored/left waiting while staff idle, child/non-employee behind counter, sleeping, cash left out), "
         "2 = clearly unacceptable (phone or feet up with a customer present, 10+ min idle, eating at the counter), 1 = sloppy. "
         'Answer ONLY JSON: {"real":true|false,"cat":"...","severity":1|2|3,"start":"h:mm AM/PM","end":"h:mm AM/PM","best_tile":n,'
         '"who":"employee description (clothes/position)","customer":"customer description or none","what":"one plain sentence a store owner can read","confidence":"high|medium|low"}')
    r = ask_json(CFG['verify_model'], q, imgs, 2500)
    if not r.get('real') or r.get('confidence') == 'low': return None
    bt = win[min(len(win) - 1, max(0, int(r.get('best_tile') or 1) - 1))]
    r.update({'store': store, 'camera': cam, 'best_s': bt['s'], 'best_still': bt['path'], 'win': [win[0]['s'], win[-1]['s']], 'source': 'video'})
    return r

# ---------------- audio ----------------
PROFANITY = re.compile(r"\b(fuck\w*|shit\w*|bitch\w*|asshole\w*|bullshit|damn\w*|goddamn\w*|dick\w*|cunt\w*|bastard\w*|piss\w*|retard\w*|motherf\w*)\b", re.I)

def transcribe_camera(store, cam, date, deadline):
    out_p = os.path.join(DATA, 'transcripts', store, slug(cam), date + '.jsonl'); os.makedirs(os.path.dirname(out_p), exist_ok=True)
    done = set()
    if os.path.exists(out_p):
        for l in open(out_p):
            try: done.add(json.loads(l)['seg'])
            except Exception: pass
    import av, numpy as np
    from faster_whisper import WhisperModel
    global _WM
    if '_WM' not in globals(): _WM = WhisperModel(CFG.get('whisper_model', 'base.en'), device='cpu', compute_type='int8')
    for seg in sorted(glob.glob(os.path.join(DATA, 'rec', store, slug(cam), date, '*.mkv'))):
        base = os.path.basename(seg)
        if base in done: continue
        if time.time() > deadline: log('audio deadline reached'); return False
        try:
            meta = json.load(open(seg + '.json')); t0 = secs(meta['start'])
            c = av.open(seg); rs = av.AudioResampler(format='s16', layout='mono', rate=16000); chunks = []
            if not c.streams.audio: continue
            for fr in c.decode(c.streams.audio[0]):
                for r in rs.resample(fr): chunks.append(r.to_ndarray().reshape(-1))
            c.close()
            if not chunks: continue
            a = np.concatenate(chunks).astype(np.float32) / 32768.0
            segs, _ = _WM.transcribe(a, vad_filter=True, beam_size=1, language='en', condition_on_previous_text=False)
            with open(out_p, 'a') as f:
                lines = [{'seg': base, 's': round(t0 + s.start, 1), 'e': round(t0 + s.end, 1), 'text': s.text.strip()} for s in segs]
                for l in lines: f.write(json.dumps(l) + '\n')
                if not lines: f.write(json.dumps({'seg': base, 's': t0, 'e': t0, 'text': ''}) + '\n')
        except Exception as e:
            log('transcribe failed', seg, repr(e)[:150])
    return True

SPEECH_CATS = "CUSSING|RUDE TO CUSTOMER|ABUSE|BAD SERVICE|ARGUMENT|TALKING ABOUT CUSTOMER"
SPEECH_RUBRIC = """You are listening (via a speech-to-text transcript) to the counter area of Valley Pawn, a pawn shop. The owner wants to know about:
- CUSSING: an employee cussing / swearing (worst if a customer can hear).
- RUDE TO CUSTOMER: an employee being rude, dismissive, sarcastic, condescending, impatient or disrespectful to a customer.
- ABUSE: insults, name-calling, threats, harassment, slurs, or demeaning talk (staff to customer, staff to staff, or a customer abusing staff that staff should report).
- BAD SERVICE: refusing to help, brushing a customer off ("I don't know", "not my problem", "come back later" with no effort), arguing over policy instead of solving, telling a customer to wait while chatting.
- ARGUMENT: a heated exchange or raised voices with a customer or between employees.
- TALKING ABOUT CUSTOMER: staff mocking or bad-mouthing a customer.
Ignore: song lyrics / store music / TV, normal friendly banter, firm-but-polite policy explanations, phone calls handled politely, speech-to-text garble."""

def speech_screen(store, cams, date):
    """-> (merged transcript rows, candidate list best-first)"""
    rows = []
    for cam in cams:
        p = os.path.join(DATA, 'transcripts', store, slug(cam), date + '.jsonl')
        if not os.path.exists(p): continue
        for l in open(p):
            try: r = json.loads(l)
            except Exception: continue
            if r.get('text') and len(r['text']) > 2: r['cam'] = cam; rows.append(r)
    rows.sort(key=lambda r: r['s']); merged = []
    for r in rows:
        if any(abs(r['s'] - m['s']) < 4 and r['text'][:20].lower() == m['text'][:20].lower() for m in merged[-6:]): continue
        merged.append(r)
    if not merged: return merged, []
    cands = []
    for r in merged:
        if PROFANITY.search(r['text']): cands.append({'s': r['s'], 'cam': r['cam'], 'cat': 'CUSSING', 'quote': r['text'], 'rank': 1})
    for i in range(0, len(merged), 250):
        chunk = merged[i:i + 250]
        text = '\n'.join(f"[{n}] {clock(r['s'])} {r['text']}" for n, r in enumerate(chunk))
        q = (SPEECH_RUBRIC + f"\n\nTranscript lines from {store} (numbered, with time):\n{text}\n\n"
             'Flag lines that are likely one of the problems (a stronger reviewer re-checks each). Put the worst first. Answer ONLY JSON: '
             '{"flags":[{"line":n,"cat":"' + SPEECH_CATS + '","quote":"the words","customer_involved":true|false}]} — empty list if nothing.')
        USAGE['lang'] += 1
        try: res = ask_json(CFG['screen_model'], q, [], 3000)
        except Exception as e: log('speech screen failed', repr(e)[:120]); continue
        for fl in res.get('flags') or []:
            try:
                r = chunk[int(fl['line'])]
                cands.append({'s': r['s'], 'cam': r['cam'], 'cat': fl.get('cat', ''), 'quote': fl.get('quote') or r['text'],
                              'rank': 0 if fl.get('customer_involved') or fl.get('cat') != 'CUSSING' else 1})
            except Exception: pass
    cands.sort(key=lambda c: c['s']); dedup = []
    for c in cands:
        if dedup and c['s'] - dedup[-1]['s'] < 45:
            dedup[-1]['rank'] = min(dedup[-1]['rank'], c['rank']); continue
        dedup.append(c)
    dedup.sort(key=lambda c: (c['rank'], c['s']))   # customer-involved / non-cussing problems first
    return merged, dedup

def speech_verify(store, h, merged, frames):
    ctx = '\n'.join(f"{clock(r['s'])} {r['text']}" for r in merged if -90 <= r['s'] - h['s'] <= 90)[:2500]
    fl = frames.get((store, h['cam']), [])
    fr = min(fl, key=lambda r: abs(r['s'] - h['s'])) if fl else None
    imgs = [sheet([fr], 1, 960, 540, [clock(fr['s'])])] if fr else []
    q = (SPEECH_RUBRIC + f"\n\nValley Pawn {store}, counter microphone, around {clock(h['s'])}. A first pass flagged {h['cat']}: \"{h['quote']}\". "
         f"Transcript ±90 s:\n{ctx}\nThe still shows the counter at that moment. Decide strictly whether this is REAL (an employee's words, or a customer abusing staff), "
         "not lyrics, not a mis-hearing, not normal banter. severity: 3 = cussing at/in front of a customer, rude/abusive to a customer, mocking a customer they can hear; "
         "2 = cussing or bad-mouthing with customers in the store, brushing a customer off; 1 = mild / no customer around. "
         'Answer ONLY JSON: {"real":true|false,"cat":"' + SPEECH_CATS + '","severity":1|2|3,"customer_present":true|false,'
         '"what":"one plain sentence for the owner (do not spell out swear words here)","quote":"the key words, lightly censored like f***","confidence":"high|medium|low"}')
    USAGE['speech_verify'] = USAGE.get('speech_verify', 0) + 1
    r = ask_json(CFG['verify_model'], q, imgs, 2500)
    if not r.get('real') or r.get('confidence') == 'low': return None
    return {'store': store, 'camera': h['cam'], 'cat': r.get('cat') or h['cat'], 'severity': r.get('severity', 2), 'start': clock(h['s']), 'end': clock(h['s']),
            'what': r.get('what', ''), 'quote': r.get('quote', ''), 'who': '', 'customer': 'yes' if r.get('customer_present') else 'none',
            'best_s': h['s'], 'best_still': fr['path'] if fr else None, 'win': [h['s'] - 20, h['s'] + 20], 'confidence': r.get('confidence'), 'source': 'audio'}


# ---------------- clips ----------------
def cut_clip(ep, date, out_path, secs_len):
    import av, fractions
    segs = []
    for seg in sorted(glob.glob(os.path.join(DATA, 'rec', ep['store'], slug(ep['camera']), date, '*.mkv'))):
        try: m = json.load(open(seg + '.json')); segs.append((secs(m['start']), secs(m.get('end', '23:59:59')), seg))
        except Exception: pass
    t_start = ep['best_s'] - secs_len * 0.4
    seg = next((s for s in segs if s[0] <= ep['best_s'] < s[1]), None)
    if not seg: return False
    off = max(0.0, t_start - seg[0])
    inp = av.open(seg[2]); vs = inp.streams.video[0]; as_ = inp.streams.audio[0] if inp.streams.audio else None
    out = av.open(out_path, 'w')
    vcodec = next((c for c in ['h264_videotoolbox', 'libx264', 'mpeg4'] if _can(c)), 'mpeg4')
    ov = out.add_stream(vcodec, rate=6); ov.width, ov.height, ov.pix_fmt = 960, 540, 'yuv420p'; ov.bit_rate = 1_200_000
    oa = out.add_stream('aac', rate=48000) if as_ else None
    cap1 = f"{ep['store']} · {ep['camera']} · {dt.date.fromisoformat(date).strftime('%b %-d')} · {ep.get('start', '')}"
    cap2 = f"{ep['cat'].title()}: {ep['what']}"[:95]
    f1, f2 = font(24), font(20)
    def overlay(img):
        g = ImageDraw.Draw(img); g.rectangle([0, 0, 960, 76], fill=(0, 0, 0)); g.rectangle([0, 0, 8, 76], fill=(229, 72, 77))
        g.text((18, 8), cap1, fill=(255, 209, 102), font=f1); g.text((18, 44), cap2, fill=(255, 255, 255), font=f2); return img
    inp.seek(int(max(0, off - 2) / vs.time_base), stream=vs)
    n = 0; vpts = 0; apts = 0; fifo = av.AudioFifo(); rs = av.AudioResampler(format='fltp', layout='mono', rate=48000)
    done = False
    for pkt in inp.demux(*( [vs, as_] if as_ else [vs])):
        if done: break
        for fr in pkt.decode():
            t = float(fr.pts * fr.time_base) if fr.pts is not None else 0
            if t < off: continue
            if t > off + secs_len:
                if isinstance(fr, av.VideoFrame): done = True
                break
            if isinstance(fr, av.VideoFrame):
                img = overlay(fr.to_image().convert('RGB').resize((960, 540)))
                vf = av.VideoFrame.from_image(img).reformat(format='yuv420p'); vf.pts = vpts; vf.time_base = fractions.Fraction(1, 6); vpts += 1
                for p in ov.encode(vf): out.mux(p)
            elif oa:
                for r in rs.resample(fr): r.pts = None; fifo.write(r)
                while fifo.samples >= 1024:
                    o = fifo.read(1024); o.pts = apts; o.time_base = fractions.Fraction(1, 48000); apts += 1024
                    for p in oa.encode(o): out.mux(p)
    for s in [ov] + ([oa] if oa else []):
        for p in s.encode(None): out.mux(p)
    out.close(); inp.close()
    return vpts > 8

def _can(c):
    import av
    try: av.codec.Codec(c, 'w'); return True
    except Exception: return False

# ---------------- main ----------------
def round_robin(groups, budget):
    """groups: {key: [items best-first]} -> list of (key, item) taking one per key in turn until budget is spent."""
    out, i = [], 0
    while len(out) < budget and any(i < len(v) for v in groups.values()):
        for k, v in groups.items():
            if i < len(v) and len(out) < budget: out.append((k, v[i]))
        i += 1
    return out

def still_clip(ep, date, out_path):
    """Fallback when the raw video is gone: a captioned slideshow of the 20-second stills around the moment."""
    import av, fractions
    fr = [r for r in stills(ep['store'], ep['camera'], date) if ep['win'][0] - 20 <= r['s'] <= ep['win'][1] + 20][:12]
    if not fr: return False
    out = av.open(out_path, 'w'); vc = next((c for c in ['h264_videotoolbox', 'libx264', 'mpeg4'] if _can(c)), 'mpeg4')
    ov = out.add_stream(vc, rate=6); ov.width, ov.height, ov.pix_fmt = 960, 540, 'yuv420p'; ov.bit_rate = 1_200_000
    f1, f2 = font(24), font(20); n = 0
    cap2 = f"{ep['cat'].title()}: {ep.get('what', '')}"[:95]
    for r in fr:
        img = Image.open(r['path']).convert('RGB').resize((960, 540)); g = ImageDraw.Draw(img)
        g.rectangle([0, 0, 960, 76], fill=(0, 0, 0)); g.rectangle([0, 0, 8, 76], fill=(229, 72, 77))
        g.text((18, 8), f"{ep['store']} · {ep['camera']} · {dt.date.fromisoformat(date).strftime('%b %-d')} · {clock(r['s'])} (photos 20 s apart)", fill=(255, 209, 102), font=f1)
        g.text((18, 44), cap2, fill=(255, 255, 255), font=f2)
        for _ in range(12):   # 2 s per photo
            vf = av.VideoFrame.from_image(img).reformat(format='yuv420p'); vf.pts = n; vf.time_base = fractions.Fraction(1, 6); n += 1
            for pk in ov.encode(vf): out.mux(pk)
    for pk in ov.encode(None): out.mux(pk)
    out.close(); return n > 0

def run(date, only_store=None, audio=True, clips=True):
    rep = os.path.join(HERE, 'reports', date); os.makedirs(os.path.join(rep, 'clips'), exist_ok=True)
    runinfo = {'date': date, 'started': dt.datetime.now(TZ).isoformat(timespec='seconds'), 'stores': {}, 'complete': False}
    deadline = time.time() + CFG.get('audio_budget_min', 360) * 60
    episodes = []; dow = dt.date.fromisoformat(date).strftime('%a')
    stores = {st: sc for st, sc in CFG['stores'].items() if (not only_store or st == only_store) and dow in sc['hours']}
    frames, cands = {}, {}
    # 1. SCREEN every camera first
    for store, sc in stores.items():
        runinfo['stores'][store] = {'cams': {}}
        for cam in sc['cameras']:
            fr = stills(store, cam, date); frames[(store, cam)] = fr; ci = {'stills': len(fr)}
            runinfo['stores'][store]['cams'][cam] = ci
            if len(fr) < 30: ci['note'] = 'too little footage'; continue
            try: c, nsheets = screen_camera(store, cam, fr)
            except Exception as e: log('screen failed', store, cam, repr(e)[:150]); ci['screen_error'] = True; continue
            c.sort(key=lambda x: -(x[1] - x[0]))   # longest windows first
            cands[(store, cam)] = c; ci.update(sheets=nsheets, flagged=len(c))
    # 2. VERIFY, budget shared fairly across cameras (round-robin)
    for (store, cam), c in round_robin(cands, CFG['max_verify_per_day']):
        ci = runinfo['stores'][store]['cams'][cam]
        try:
            USAGE['verify'] += 1; v = verify(store, cam, frames[(store, cam)], c); ci['verified'] = ci.get('verified', 0) + 1
            if v: episodes.append(v)
        except Exception as e: log('verify failed', repr(e)[:150]); ci['verify_errors'] = ci.get('verify_errors', 0) + 1
    for (store, cam), c in cands.items():
        ci = runinfo['stores'][store]['cams'][cam]; ci['unverified'] = len(c) - ci.get('verified', 0) - ci.get('verify_errors', 0)
    # 3. LISTEN: transcribe, screen transcripts, verify fairly across stores
    if audio:
        for store, sc in stores.items():
            for cam in sc['cameras']:
                try: runinfo['stores'][store]['cams'][cam]['audio_done'] = transcribe_camera(store, cam, date, deadline)
                except Exception as e: log('audio failed', repr(e)[:150]); runinfo['stores'][store]['cams'][cam]['audio_done'] = False
        sc_cands = {}
        for store, sc in stores.items():
            try: sc_cands[store] = speech_screen(store, sc['cameras'], date)
            except Exception as e: log('speech screen failed', repr(e)[:150])
        for store, h in round_robin({k: v[1] for k, v in sc_cands.items()}, CFG.get('max_speech_verify_per_day', 20)):
            try:
                ep = speech_verify(store, h, sc_cands[store][0], frames)
                if ep: episodes.append(ep)
            except Exception as e: log('speech verify failed', repr(e)[:150])
    episodes.sort(key=lambda e: (e['store'], -int(e.get('severity', 1)), e['best_s']))
    # 4. CLIPS (video with sound; photo slideshow if the video is gone)
    if clips:
        for e in episodes:
            if int(e.get('severity', 1)) < 2: continue
            p = os.path.join(rep, 'clips', f"{slug(e['store'])}_{slug(e['camera'])}_{int(e['best_s'])}_{slug(e['cat'])}.mp4")
            try:
                if os.path.exists(p) or cut_clip(e, date, p, CFG.get('clip_secs', 24)) or still_clip(e, date, p): e['clip'] = p
            except Exception as ex:
                log('clip failed', repr(ex)[:150])
                try:
                    if still_clip(e, date, p): e['clip'] = p
                except Exception: pass
    sfx = f'.test-{slug(only_store)}' if only_store else ''
    json.dump(episodes, open(os.path.join(rep, f'episodes{sfx}.json'), 'w'), indent=1)
    runinfo.update(finished=dt.datetime.now(TZ).isoformat(timespec='seconds'), episodes=len(episodes), complete=not only_store, partial=bool(only_store), version=3, usage=USAGE,
                   est_cost_usd=round(USAGE['screen'] * 0.003 + USAGE['verify'] * 0.015 + USAGE['lang'] * 0.004 + USAGE.get('speech_verify', 0) * 0.012, 2))
    json.dump(runinfo, open(os.path.join(rep, f'run{sfx}.json'), 'w'), indent=1)
    log('done', date, len(episodes), 'episodes')
    return runinfo

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('date', nargs='?'); ap.add_argument('--store')
    ap.add_argument('--no-audio', action='store_true'); ap.add_argument('--no-clips', action='store_true'); ap.add_argument('--clip-test', action='store_true')
    a = ap.parse_args()
    if (a.date or dt.datetime.now(TZ).date().isoformat()) > CFG.get('trial_end', '9999'): print('trial ended'); sys.exit(0)
    d = a.date or dt.datetime.now(TZ).date().isoformat()
    if a.clip_test and a.store:   # cut one captioned clip from the store's first camera, ~1 min into the earliest segment
        cam = CFG['stores'][a.store]['cameras'][0]
        segs = sorted(glob.glob(os.path.join(DATA, 'rec', a.store, slug(cam), d, '*.mkv')))
        if segs:
            m = json.load(open(segs[0] + '.json')); t = secs(m['start']) + 60
            ep = {'store': a.store, 'camera': cam, 'cat': 'TEST', 'what': 'clip pipeline test', 'start': clock(t), 'best_s': t}
            out = os.path.join(HERE, 'reports', d, 'clips', '_test.mp4'); os.makedirs(os.path.dirname(out), exist_ok=True)
            print('clip test', cut_clip(ep, d, out, 12), out, os.path.getsize(out) if os.path.exists(out) else 0)
    run(d, a.store, audio=not a.no_audio, clips=not a.no_clips)
