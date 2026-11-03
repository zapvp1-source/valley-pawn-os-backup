import sys, os, json
sys.path.insert(0, os.path.abspath('.'))
import voice
cfg = voice.load_config(require_key=True)
jv = cfg['joshua_voice']
c = dict(cfg, voice_id=jv['voice_id'], model_id=jv['model_id'], settings=jv['settings'])
S = [
 "Welcome to Valley Pawn Academy. This is how every one of us learns the job, the same way, in every store.",
 "It's eight levels, about seventy short lessons, five to ten minutes each. It starts with the rules, safety and your drawer, then loans, buying, gold, firearms, and selling.",
 "Each lesson walks you through it with voiceover, step by step, right at the store, on the clock.",
 "Then you do it for real. Your manager watches, and signs off your floor check.",
 "Every lesson ends with a short test. Miss a question, and it shows you why. Score eighty percent, and the next lesson unlocks.",
 "Level one is done by day three. Everyone starts this week, new hires and veterans alike. One standard, every store.",
]
out = os.path.abspath('../demo_video/intro_v3')
json.dump(S, open(os.path.join(out,'script.json'),'w'), indent=1)
for i,t in enumerate(S,1):
    a = voice.synthesize(voice.tts_text(t), c)
    open(os.path.join(out, f's{i}.mp3'),'wb').write(a)
    print(i, len(a))
