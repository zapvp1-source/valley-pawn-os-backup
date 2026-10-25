#!/usr/bin/env python3
"""Build the November staff-meeting call playlist (2026-10-24).
picks.json clips -> parts [[recording_id, from_s, to_s], ...] cut from raw/<id>.mp3, optional bleeps [[id, from_s, to_s]] in source time.
Parts are joined with a 1.2 s gap, loudness-normalized, written as MP3 to ~/Desktop/November Meeting/Call Examples/ with a Play List page.
Run in the Cowork VM:  python3 build_playlist.py <home_mnt>"""
import json, os, subprocess, sys, html, tempfile, shutil
MNT = sys.argv[1]
HERE = os.path.join(MNT, "Documents/Claude/Projects/Call Analysis/november_clips")
OUT = os.path.join(MNT, "Desktop/November Meeting/Call Examples")
picks = json.load(open(os.path.join(HERE, "picks.json")))
SUB = {"good": "1 - Great Calls", "bad": "2 - Bad Calls", "gs": "3 - Sales - Great", "bs": "4 - Sales - Bad", "gl": "5 - Loans - Great", "bl": "6 - Loans - Bad"}
GOODK = {"good", "gs", "gl"}
for s in SUB.values(): os.makedirs(os.path.join(OUT, s), exist_ok=True)
T = tempfile.mkdtemp()
def run(*a): subprocess.check_call(list(a))
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]).strip())
def piece(src, a, b, out, tone=False):
    if tone:
        run("ffmpeg","-v","error","-y","-f","lavfi","-i","sine=frequency=1000:sample_rate=16000:duration=%.3f" % (b-a),"-af","volume=0.25","-ac","1","-ar","16000",out)
    else:
        run("ffmpeg","-v","error","-y","-ss","%.3f" % a,"-t","%.3f" % (b-a),"-i",src,"-ac","1","-ar","16000",out)
n = 0
for c in picks["clips"]:
    pieces = []
    bleeps = c.get("bleeps", [])
    for i, (rid, a, b) in enumerate(c["parts"]):
        src = os.path.join(HERE, "raw", rid + ".mp3")
        cuts = sorted([(x, y) for (r, x, y) in bleeps if r == rid and x < b and y > a])
        t = a
        for (x, y) in cuts:
            if x > t: n += 1; p = os.path.join(T, "%d.wav" % n); piece(src, t, x, p); pieces.append(p)
            n += 1; p = os.path.join(T, "%d.wav" % n); piece(src, max(x, a), min(y, b), p, tone=True); pieces.append(p); t = min(y, b)
        if b > t: n += 1; p = os.path.join(T, "%d.wav" % n); piece(src, t, b, p); pieces.append(p)
        if i < len(c["parts"]) - 1:
            n += 1; p = os.path.join(T, "%d.wav" % n)
            run("ffmpeg","-v","error","-y","-f","lavfi","-i","anullsrc=r=16000:cl=mono","-t","1.2",p); pieces.append(p)
    lst = os.path.join(T, "list.txt")
    open(lst, "w").write("".join("file '%s'\n" % p for p in pieces))
    joined = os.path.join(T, "joined.wav")
    run("ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",lst,"-c","copy",joined)
    dst = os.path.join(OUT, SUB[c["kind"]], c["file"])
    run("ffmpeg","-v","error","-y","-i",joined,"-af","loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.15","-ar","44100","-ac","1","-b:a","128k",dst)
    c["play_len"] = dur(dst); c["rel"] = SUB[c["kind"]] + "/" + c["file"]
shutil.rmtree(T)

def mmss(s): s = int(round(s)); return "%d:%02d" % (s // 60, s % 60)
def esc(x): return html.escape(x)
def card(c, k):
    look = "".join("<li>%s</li>" % esc(x) for x in c["listen_for"])
    tag = c["file"].split(" - ")[0] if c["kind"] in ("gs","bs","gl","bl") else (("G%02d" if c["kind"] == "good" else "B%02d") % k)
    lbl = "Listen for" if c["kind"] in GOODK else "What goes wrong"
    std = "The standard" if c["kind"] in GOODK else "The right way"
    return f"""<section class="card {'good' if c['kind'] in GOODK else 'bad'}"><div class="num">{tag}</div><div class="body">
<h3>{esc(c['title'])}</h3><p class="meta">{esc(c['store_name'])} &middot; {esc(c['when'])} &middot; {mmss(c['play_len'])}</p>
<audio controls preload="none" src="{esc(c['rel'])}"></audio>
<p class="what">{esc(c['what'])}</p><p class="lbl">{lbl}</p><ul>{look}</ul>
<p class="rule"><b>{std}:</b> {esc(c['rule'])}</p></div></section>"""
good = [c for c in picks["clips"] if c["kind"] == "good"]; bad = [c for c in picks["clips"] if c["kind"] == "bad"]
gs=[c for c in picks["clips"] if c["kind"]=="gs"]; bs=[c for c in picks["clips"] if c["kind"]=="bs"]; gl=[c for c in picks["clips"] if c["kind"]=="gl"]; bl=[c for c in picks["clips"] if c["kind"]=="bl"]
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Every Call Counts — Call Examples</title><style>
:root{{--bg:#f6f4ef;--ink:#1d1d1b;--mute:#5d5a52;--card:#fff;--good:#1f7a4a;--bad:#b3261e;--line:#e3dfd5}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
main{{max-width:980px;margin:0 auto;padding:32px 16px 60px}} h1{{font-size:32px;margin:0 0 4px}} .sub{{color:var(--mute);margin:0 0 18px}}
h2{{margin:40px 0 12px;font-size:24px;padding-bottom:6px;border-bottom:4px solid var(--line)}} h2.g{{border-color:var(--good)}} h2.b{{border-color:var(--bad)}}
.card{{display:flex;gap:16px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0;break-inside:avoid}}
.num{{flex:none;font-weight:700;font-size:15px;width:64px;height:56px;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff}}
.good .num{{background:var(--good)}} .bad .num{{background:var(--bad)}} .body{{flex:1;min-width:0}}
h3{{margin:0 0 2px;font-size:20px}} .meta{{margin:0 0 10px;color:var(--mute);font-size:14px}} audio{{width:100%;margin:0 0 10px}}
.what{{margin:0 0 6px}} .lbl{{margin:8px 0 2px;font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--mute)}}
ul{{margin:0 0 8px 20px;padding:0}} .rule{{margin:8px 0 0;font-size:16px;background:var(--bg);padding:8px 10px;border-radius:8px}}
.note{{background:#fff;border-left:4px solid var(--mute);padding:10px 14px;border-radius:6px;color:var(--mute);font-size:15px}}
@media (max-width:560px){{.card{{flex-direction:column}}}} @media print{{audio{{display:none}} body{{background:#fff}}}}
</style></head><body><main>
<h1>Every Call Counts — Call Examples</h1>
<p class="sub">November staff meeting &middot; real Valley Pawn calls, {esc(picks['range'])} &middot; picked from {esc(picks['reviewed'])} recorded calls</p>
<p class="note">Press play on any call. The same audio files are in the six folders next to this page and play on their own (double-click, or select and press the space bar). Long holds are cut short, and home addresses, names, phone and ID numbers are bleeped — everything else is exactly what was said.</p>
<h2 class="g">10 great calls — this is what going the extra mile sounds like</h2>
{''.join(card(c, i) for i, c in enumerate(good, 1))}
<h2 class="b">10 calls we never want to hear again</h2>
{''.join(card(c, i) for i, c in enumerate(bad, 1))}
<h2 class="g">Selling calls — what great sounds like</h2>
<p class="note">Slide 10: ask brand, model, condition, what's included and how much they need; give a range with the reason; set a time; and always offer the loan.</p>
{''.join(card(c, i) for i, c in enumerate(gs, 1))}
<h2 class="b">Selling calls — what we lose</h2>
{''.join(card(c, i) for i, c in enumerate(bs, 1))}
<h2 class="g">Loan calls — what great sounds like</h2>
<p class="note">Slide 6: verify, pull it up, read the dates, say where it stands, give the exact numbers to extend and to pick up, pin a day or send the app.</p>
{''.join(card(c, i) for i, c in enumerate(gl, 1))}
<h2 class="b">Loan calls — what we never say</h2>
{''.join(card(c, i) for i, c in enumerate(bl, 1))}
</main></body></html>"""
open(os.path.join(OUT, "Call Examples - Play List.html"), "w").write(page)
for c in picks["clips"]: print("%-55s %s" % (c["file"], mmss(c["play_len"])))
