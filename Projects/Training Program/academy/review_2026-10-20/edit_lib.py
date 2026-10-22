"""Tiny helpers for precise, asserted edits to Academy lesson JSONs."""
import json, glob, os, sys, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lessons")
_cache = {}
_touched = set()

def path_of(lid):
    lvl, order = lid.split("-")
    folder = "M" if lvl == "M" else "L" + lvl[1:]
    hits = glob.glob(os.path.join(ROOT, folder, f"{int(order):02d}_*.json"))
    assert len(hits) == 1, (lid, hits)
    return hits[0]

def load(lid):
    if lid not in _cache:
        _cache[lid] = json.load(open(path_of(lid), encoding="utf-8"))
    return _cache[lid]

def save_all():
    for lid in sorted(_touched):
        d = _cache[lid]
        with open(path_of(lid), "w", encoding="utf-8") as f:
            f.write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    return sorted(_touched)

LEARNER_FIELDS = ("heading", "bullets", "say", "key_points", "prompt", "text", "why",
                  "caption", "listen_for", "objectives", "title", "gate", "floor_check")

def _walk(obj, fn, key=None):
    """Apply fn(key, string) -> string to every learner-facing string."""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k == "sources" or k == "production_notes":
                continue
            obj[k] = _walk(v, fn, k)
        return obj
    if isinstance(obj, list):
        return [_walk(x, fn, key) for x in obj]
    if isinstance(obj, str) and key in LEARNER_FIELDS:
        return fn(key, obj)
    return obj

def replace_everywhere(lid, old, new, expect=None):
    """Replace in all learner-facing fields; assert the number of occurrences."""
    d = load(lid)
    n = [0]
    def fn(k, s):
        c = s.count(old)
        if c:
            n[0] += c
            return s.replace(old, new)
        return s
    _walk(d, fn)
    if expect is not None:
        assert n[0] == expect, f"{lid}: expected {expect} of {old!r}, found {n[0]}"
    else:
        assert n[0] > 0, f"{lid}: {old!r} not found"
    _touched.add(lid)
    return n[0]

def slide(lid, i):
    return load(lid)["slides"][i - 1]

def q(lid, i):
    return load(lid)["quiz"]["questions"][i - 1]

def set_field(lid, obj, key, old, new):
    """obj[key] must equal old exactly (or contain old if old is a substring flag)."""
    cur = obj[key]
    if isinstance(cur, list):
        assert old in cur, f"{lid}: {old!r} not in list {key}"
        cur[cur.index(old)] = new
    else:
        assert old in cur, f"{lid}: {old!r} not in {key}: {cur!r}"
        obj[key] = cur.replace(old, new, 1)
    _touched.add(lid)

def say(lid, i, old, new):
    set_field(lid, slide(lid, i), "say", old, new)

def bullet(lid, i, old, new):
    set_field(lid, slide(lid, i), "bullets", old, new)

def bullet_sub(lid, i, old, new):
    s = slide(lid, i)
    hits = [b for b in s["bullets"] if old in b]
    assert len(hits) == 1, f"{lid} slide {i}: {old!r} matched {len(hits)} bullets"
    s["bullets"][s["bullets"].index(hits[0])] = hits[0].replace(old, new, 1)
    _touched.add(lid)

def add_bullet(lid, i, text, after=None):
    s = slide(lid, i)
    if after is None:
        s["bullets"].append(text)
    else:
        idx = [n for n, b in enumerate(s["bullets"]) if after in b]
        assert len(idx) == 1
        s["bullets"].insert(idx[0] + 1, text)
    _touched.add(lid)

def set_bullets(lid, i, new_list):
    slide(lid, i)["bullets"] = list(new_list)
    _touched.add(lid)

def kp(lid, old, new):
    set_field(lid, load(lid), "key_points", old, new)

def kp_sub(lid, old, new):
    d = load(lid)
    hits = [k for k in d["key_points"] if old in k]
    assert len(hits) == 1, f"{lid}: kp {old!r} matched {len(hits)}"
    d["key_points"][d["key_points"].index(hits[0])] = hits[0].replace(old, new, 1)
    _touched.add(lid)

def opt(lid, qi, text_sub):
    qq = q(lid, qi)
    hits = [o for o in qq["options"] if text_sub in o["text"]]
    assert len(hits) == 1, f"{lid} Q{qi}: option {text_sub!r} matched {len(hits)}"
    return hits[0]

def correct(lid, qi):
    qq = q(lid, qi)
    hits = [o for o in qq["options"] if o.get("correct")]
    assert len(hits) == 1
    return hits[0]

def set_opt(lid, qi, text_sub, text=None, why=None, why_sub=None):
    o = opt(lid, qi, text_sub)
    if text is not None:
        o["text"] = text
    if why is not None:
        o["why"] = why
    if why_sub is not None:
        old, new = why_sub
        assert old in o["why"], f"{lid} Q{qi}: {old!r} not in why {o['why']!r}"
        o["why"] = o["why"].replace(old, new, 1)
    _touched.add(lid)

def set_prompt(lid, qi, old, new):
    set_field(lid, q(lid, qi), "prompt", old, new)

def replace_question(lid, qi, newq):
    load(lid)["quiz"]["questions"][qi - 1] = newq
    _touched.add(lid)

def add_question(lid, newq):
    load(lid)["quiz"]["questions"].append(newq)
    _touched.add(lid)

def delete_question(lid, qi):
    del load(lid)["quiz"]["questions"][qi - 1]
    _touched.add(lid)

def top(lid, key, old, new):
    set_field(lid, load(lid), key, old, new)

def set_top(lid, key, value):
    load(lid)[key] = value
    _touched.add(lid)

def add_source(lid, text):
    load(lid)["sources"].append(text)
    _touched.add(lid)

def drop_source_containing(lid, sub):
    d = load(lid)
    before = len(d["sources"])
    d["sources"] = [s for s in d["sources"] if sub not in s]
    _touched.add(lid)
    return before - len(d["sources"])

def show(lid, what=None, i=None):
    d = load(lid)
    if what == "slide":
        print(json.dumps(d["slides"][i - 1], indent=1, ensure_ascii=False))
    elif what == "q":
        print(json.dumps(d["quiz"]["questions"][i - 1], indent=1, ensure_ascii=False))
    elif what == "kp":
        print(json.dumps(d["key_points"], indent=1, ensure_ascii=False))
    elif what:
        print(json.dumps(d.get(what), indent=1, ensure_ascii=False))
    else:
        print(json.dumps({k: v for k, v in d.items() if k not in ("slides", "quiz")}, indent=1, ensure_ascii=False))
