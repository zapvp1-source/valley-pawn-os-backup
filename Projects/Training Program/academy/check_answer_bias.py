#!/usr/bin/env python3
"""Measure answer-length bias across all lesson quizzes.
For every non-true/false question: is the correct option the (strictly) longest?
Also reports ties-for-longest, key_points counts, and giveaway words."""
import json, glob, re, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
tot = longest = tie = 0
per = []
flags = []
absol = [0, 0]  # options using always/never/only: [correct, wrong]
for f in sorted(glob.glob("lessons/*/*.json")):
    d = json.load(open(f))
    ln = lt = 0
    for i, q in enumerate(d["quiz"]["questions"]):
        if q["type"] == "truefalse":
            continue
        opts = q["options"]
        L = [len(o["text"]) for o in opts]
        c = [k for k, o in enumerate(opts) if o["correct"]]
        if len(c) != 1:
            flags.append(f"{d['id']} q{i+1}: {len(c)} correct options")
            continue
        c = c[0]
        tot += 1; lt += 1
        m = max(L)
        if L[c] == m and L.count(m) == 1:
            longest += 1; ln += 1
        elif L[c] == m:
            tie += 1
        for k, o in enumerate(opts):
            t = o["text"].lower()
            if re.search(r"\ball of the above\b|\bnone of the above\b", t):
                flags.append(f"{d['id']} q{i+1}: all/none of the above")
            if re.search(r"\b(always|never|only)\b", t):
                absol[0 if k == c else 1] += 1
    per.append((d["id"], ln, lt, len(d.get("key_points", []))))
print(f"Non-true/false questions: {tot}")
print(f"Correct option strictly longest: {longest} ({100*longest/max(tot,1):.1f}%)")
print(f"Correct option tied for longest: {tie}")
print(f"Options using always/never/only: correct {absol[0]}, wrong {absol[1]} (should not be all on wrong answers)")
if "-v" in sys.argv:
    for p in per:
        print(f"  {p[0]:6} longest {p[1]}/{p[2]}  key_points={p[3]}")
for x in flags:
    print("FLAG", x)
