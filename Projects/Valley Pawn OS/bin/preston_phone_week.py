#!/usr/bin/env python3
"""preston_phone_week.py — weekly Preston Phone Brief (native, added 2026-11-16, additive).

Joshua 2026-11-16: "a weekly task ... seeing what Preston is talking about to the group via Zoom calls as well as
if Preston is on the phone less like we are trying to accomplish."

Runs AFTER the Monday Phone & Text Review (call_week_grade.py, 02:30) and reads only what that job already wrote —
it never calls Zoom and never re-transcribes:
  Call Analysis/week_<mon>/recordings_index.json, call_history.json, grades/<id>.json, Zoom Call Pipeline transcripts.

  1. LOAD     every recorded call on Preston's Zoom line (ext 813) + every store-line call to/from his cell
              (540-836-4200), deduped by call id.
  2. TREND    calls and talk minutes per week on both, from every week folder on disk (history since 10/5).
  3. TAG      each call (Claude, cached per call in week_<mon>/preston/<id>.json): who he talked to, topic, and
              whether the store could have handled it without him (and what would have let them).
  4. WRITE    one-page brief (numbers + trend + themes + "could have been handled without Preston" + customer-service
              issues raised in team calls), HTML + PDF, copied to Drive › Call Reviews.
  5. DELIVER  3–5 plain lines through fleet/outbox (ops bot DM to Joshua only — it names staff). One CHANGELOG line.

  preston_phone_week.py                 last Mon–Sun (waits for that week's review to finish; exits 0 if not yet)
  preston_phone_week.py --since 2026-11-09 --until 2026-11-15 --render    build everything, no DM / CHANGELOG
Idempotent: a week that has already been delivered is skipped (week_<mon>/preston/_delivered.json).
"""
import argparse, collections, datetime as dt, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import call_week_grade as cwg  # reuse: et(), to_pdf(), drive_copy(), ask_rows(), paths, MODEL  (import has no side effects)

ET, CA, FLEET, OS_DIR, PIPE = cwg.ET, cwg.CA, cwg.FLEET, cwg.OS_DIR, cwg.PIPE
TASK = "preston-phone-week"
JOSHUA = cwg.JOSHUA
ZOOM_NUM, CELL_NUM, PEXT = "+15402024200", "+15408364200", "813"
STORE_EXT = {k: v for k, v in cwg.EXT.items() if v != "PRE"}
WHO = ["store staff", "job candidate", "vendor or bank", "customer", "Joshua Davis (owner)", "personal or unknown", "voicemail or no conversation"]
TOPICS = ["deal or price approval", "loan or policy question", "cash, funds or bank", "schedule, call-out or coverage",
          "coaching or HR", "hiring interview", "IT, phones or equipment", "compliance, firearms or police",
          "customer problem escalated", "inventory, transfers or scrap", "personal or other"]
LINE_START = dt.date(2026, 10, 5)   # Zoom line adoption week (Preston Time Review/STATUS.md)
CELL_BASELINE = [("Sep 21", 100, 559), ("Sep 28", 49, 276), ("Oct 5", 56, 372), ("Oct 12", 81, 487)]  # T-Mobile bill, STATUS.md 10/23


def log(m):
    print(dt.datetime.now(ET).strftime("%H:%M:%S"), m, flush=True)


def ledger(sentence):
    with open(os.path.join(FLEET, "FAILURE_LEDGER.md"), "a") as f:
        f.write("| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), TASK, sentence))


def num(s):
    d = "".join(c for c in str(s or "") if c.isdigit())
    return "+1" + d[-10:] if len(d) >= 10 else ""


def roster():
    names = {}
    try:
        for p in json.load(open(os.path.join(PIPE, "internal_roster.json")))["people"]:
            for n in p["numbers"]:
                names[num(n)] = p["name"].replace("Valley Pawn — ", "").replace(" (store line)", " store")
    except Exception:
        pass
    try:
        for e in json.load(open(os.path.join(OS_DIR, "hr", "ROSTER.json")))["employees"]:
            if e.get("phone") and num(e["phone"]) not in names:
                names[num(e["phone"])] = e.get("name") or e.get("preferred")
    except Exception:
        pass
    return names


def week_of(t):
    d = t.date()
    return d - dt.timedelta(days=d.weekday())


# ---------------------------------------------------------------- 2. trend (all weeks on disk)
def is_zoom(x):
    return PEXT in (x.get("caller_ext_number"), x.get("callee_ext_number")) or ZOOM_NUM in (x.get("caller_did_number"), x.get("callee_did_number"))


def is_cell(x):
    return CELL_NUM in (num(x.get("caller_did_number")), num(x.get("callee_did_number")), num(x.get("caller_number")), num(x.get("callee_number")))


def trend(until):
    rows = {}
    for f in glob.glob(os.path.join(CA, "week_*", "call_history.json")):
        if "regrade" in f:
            continue
        try:
            for x in json.load(open(f)):
                rows[x.get("id")] = x
        except Exception:
            continue
    seen, agg = set(), collections.defaultdict(collections.Counter)
    for x in rows.values():
        t = cwg.et(x.get("start_time") or "")
        if not t:
            continue
        k = x.get("call_id") or x.get("id")
        if k in seen:
            continue
        z, c = is_zoom(x), is_cell(x)
        if not (z or c):
            continue
        seen.add(k)
        w = week_of(t)
        if w < LINE_START or w > until:
            continue
        dur = (x.get("duration") or 0) / 60.0
        a = agg[w]
        a["calls"] += 1; a["min"] += dur
        if dur > 0:
            a["talked"] += 1
        out = x.get("caller_ext_number") == PEXT or x.get("caller_did_number") == ZOOM_NUM
        a["out" if out else "in"] += 1
        if t.hour >= 18 or t.hour < 9 or t.weekday() == 6:
            a["after_min"] += dur
    hist = [{"week": w.isoformat(), "calls": a["calls"], "talked": a["talked"], "minutes": round(a["min"]), "inbound": a["in"],
             "outbound": a["out"], "after_hours_min": round(a["after_min"])} for w, a in sorted(agg.items())]
    json.dump(hist, open(os.path.join(CA, "preston_phone_history.json"), "w"), indent=1)
    return hist


# ---------------------------------------------------------------- 1. load the week's Preston calls
def week_calls(d, since, until):
    idx = json.load(open(os.path.join(d, "recordings_index.json")))
    grades = {}
    for f in glob.glob(os.path.join(d, "grades", "*.json")):
        try:
            grades[os.path.basename(f)[:-5]] = json.load(open(f))
        except Exception:
            pass
    tx = {}
    for f in glob.glob(os.path.join(cwg.TX, "2026-*", "*.json")):
        tx[os.path.basename(f)[:-5]] = f
    names = roster()
    pick, seen = [], {}
    for r in idx:
        t = cwg.et(r.get("date_time") or "")
        if not t or not (since <= t.date() <= until):
            continue
        mine = PEXT in (str(r.get("owner_ext")), str(r.get("accepted_ext")))
        other = num(r.get("other_number"))
        cell = other == CELL_NUM or (other == ZOOM_NUM and not mine)
        if not (mine or cell):
            continue
        key = r.get("call_id") or r["id"]
        if key in seen:
            if mine:
                pick[seen[key]] = None   # keep Preston's own leg
            else:
                continue
        g = grades.get(r["id"]) or {}
        text = ""
        if r["id"] in tx:
            try:
                text = (json.load(open(tx[r["id"]])).get("transcript") or "").strip()
            except Exception:
                pass
        store_leg = STORE_EXT.get(str(r.get("accepted_ext"))) or STORE_EXT.get(str(r.get("owner_ext")))
        pick.append({"id": r["id"], "t": t, "dir": r.get("direction"), "dur": int(r.get("duration_s") or 0),
                     "line": "zoom" if mine else "cell", "other_l4": other[-4:],
                     "known": names.get(other) or (cwg.NAMES.get(store_leg, "") + " store" if (cell and store_leg) else ""),
                     "type": g.get("type", ""), "summary": g.get("summary", ""), "flags": g.get("flags") or [], "quote": g.get("quote", ""),
                     "transcript": text})
        seen[key] = len(pick) - 1
    return [p for p in pick if p], len(idx)


# ---------------------------------------------------------------- 3. tag (cached)
SYS = ("You read machine transcripts of phone calls made or taken by Preston Peters, Market Manager over Valley Pawn's 5 Virginia "
       "pawn stores (Culpeper, Harrisonburg, Lexington, Roanoke, Waynesboro). The business goal is for the stores to need Preston on "
       "the phone LESS. IMPORTANT: Joshua Burnett is a Culpeper store employee (store staff), NOT the owner; the owner is Joshua Davis — only tag a call as the owner when the known name says Joshua Davis. Stores should handle routine questions themselves using the written policy, the Ask Valley Pawn / Ops Agent "
       "knowledge base, Bravo POS, and their own authority (manager transaction limits were raised 10/8). Be factual; use only the "
       "transcript and summary; never invent names or facts. Return JSON only.")


def tag(calls, d):
    cdir = os.path.join(d, "preston"); os.makedirs(cdir, exist_ok=True)
    todo = []
    for c in calls:
        f = os.path.join(cdir, c["id"] + ".json")
        if os.path.exists(f):
            try:
                c["tag"] = json.load(open(f)); continue
            except Exception:
                pass
        words = len(c["transcript"].split())
        if words < 12 or c["type"] in ("silent_or_unintelligible", "voicemail_outbound"):
            c["tag"] = {"who": "voicemail or no conversation", "name": c["known"], "topic": "personal or other", "store": "",
                        "gist": c["summary"] or "No conversation.", "store_could_handle": False, "what_would_let_them": "", "service_issue": ""}
            json.dump(c["tag"], open(f, "w")); continue
        todo.append(c)
    for i in range(0, len(todo), 10):
        batch = todo[i:i + 10]
        parts = []
        for n, c in enumerate(batch, 1):
            parts.append("=== CALL %d | %s | %s | %ds | line=%s | other ...%s %s\nGRADER SUMMARY: %s\nTRANSCRIPT: %s" % (
                n, c["t"].strftime("%a %m/%d %I:%M %p"), c["dir"], c["dur"], c["line"], c["other_l4"],
                ("(known: %s)" % c["known"]) if c["known"] else "", c["summary"], c["transcript"][:3500]))
        prompt = ("For each call return one JSON object, in a JSON array, with keys:\n"
                  "call (int), who (one of %s), name (first+last of the other person if clear from known/transcript, else empty), "
                  "store (Culpeper|Harrisonburg|Lexington|Roanoke|Waynesboro|empty), topic (one of %s), "
                  "gist (one plain sentence: what was discussed and decided), "
                  "store_could_handle (true only if a trained store manager could have resolved this WITHOUT Preston using written policy, "
                  "the knowledge base, Bravo or their own authority; false for real judgment calls, approvals above their authority, "
                  "coaching Preston initiated, hiring interviews, and vendors), "
                  "what_would_let_them (if store_could_handle: the specific fix — e.g. 'knowledge-base entry on X', 'policy line on Y', "
                  "'training on Z', 'Bravo permission for W'; else empty), "
                  "service_issue (if the call reveals a customer-service problem at a store — rude handling, a customer left waiting, a "
                  "policy broken with a customer, a complaint — one plain sentence; else empty).\n\n%s"
                  ) % (json.dumps(WHO), json.dumps(TOPICS), "\n\n".join(parts))
        try:
            got = cwg.ask_rows(prompt, SYS, d, "preston%d" % i)
        except Exception as e:
            log("tag batch %d failed: %s" % (i, e)); continue
        by = {int(g.get("call", 0)): g for g in got if isinstance(g, dict)}
        for n, c in enumerate(batch, 1):
            g = by.get(n)
            if not g:
                continue
            if g.get("who") not in WHO:
                g["who"] = "personal or unknown"
            k = c["known"]
            if k and "Davis" not in k and "store" not in k and k != "Preston Peters":
                g["who"] = "store staff"; g["name"] = g.get("name") or k
            elif g["who"] == "Joshua Davis (owner)" and "Joshua Davis" not in k:
                g["who"] = "store staff" if g.get("store") else "personal or unknown"
            if g.get("topic") not in TOPICS:
                g["topic"] = "personal or other"
            c["tag"] = g
            json.dump(g, open(os.path.join(cdir, c["id"] + ".json"), "w"), indent=1)
    return [c for c in calls if c.get("tag")], [c for c in calls if not c.get("tag")]


# ---------------------------------------------------------------- 4. write
def mins(cs):
    return round(sum(c["dur"] for c in cs) / 60.0)


def numbers(tagged):
    talk = [c for c in tagged if c["tag"]["who"] != "voicemail or no conversation"]
    by_who = collections.Counter(); by_who_m = collections.Counter()
    by_topic = collections.Counter(); by_topic_m = collections.Counter()
    people = collections.Counter(); people_m = collections.Counter()
    for c in talk:
        g = c["tag"]
        by_who[g["who"]] += 1; by_who_m[g["who"]] += c["dur"] / 60.0
        by_topic[g["topic"]] += 1; by_topic_m[g["topic"]] += c["dur"] / 60.0
        if g["who"] == "store staff":
            nm = g.get("name") or c["known"] or ("%s (unnamed)" % g.get("store") if g.get("store") else "unnamed staff")
            people[nm] += 1; people_m[nm] += c["dur"] / 60.0
    staff = [c for c in talk if c["tag"]["who"] == "store staff"]
    could = [c for c in staff if c["tag"].get("store_could_handle")]
    return {"talk": talk, "staff": staff, "could": could, "by_who": by_who, "by_who_m": by_who_m, "by_topic": by_topic,
            "by_topic_m": by_topic_m, "people": people, "people_m": people_m}


def narrative(since, until, N, hist):
    calls = [{"when": c["t"].strftime("%a %I:%M %p"), "min": round(c["dur"] / 60.0, 1), "who": c["tag"]["who"], "name": c["tag"].get("name", ""),
              "store": c["tag"].get("store", ""), "topic": c["tag"]["topic"], "gist": c["tag"].get("gist", ""),
              "could_handle": bool(c["tag"].get("store_could_handle")), "fix": c["tag"].get("what_would_let_them", ""),
              "service_issue": c["tag"].get("service_issue", "")} for c in N["talk"]]
    facts = {"staff_calls": len(N["staff"]), "staff_calls_store_could_handle": len(N["could"]),
             "minutes_store_could_handle": mins(N["could"]), "by_who": dict(N["by_who"]), "by_topic": dict(N["by_topic"])}
    prompt = ("EXACT COUNTS (use these, never recount): %s\n\n" % json.dumps(facts)) + ("Week %s to %s. Preston's phone trend by week (his Zoom line + store calls to his cell): %s\n\nEvery call this week, already tagged:\n%s\n\n"
              "Write for Joshua (CEO, not technical, reads on his phone). Plain words, short. Return JSON with keys:\n"
              "headline: one sentence — is Preston on the phone more or less than last week and the 4-week average, and the main reason.\n"
              "themes: 3-5 objects {head, body} — what Preston and the team actually talked about this week, with counts/minutes and names.\n"
              "offload: up to 5 objects {head, body} — repeat questions the stores could have handled without him, grouped, each with the "
              "specific fix (knowledge-base entry, policy line, training, permission) and which store/person.\n"
              "service: up to 4 objects {head, body} — customer-service problems at the stores that surfaced in these team calls (empty list if none).\n"
              "actions: exactly 3 short sentences — the three things that would cut Preston's phone time next week.\n"
              "Use only the data given. Never invent numbers; use the counts in the data.") % (
        since, until, json.dumps(hist[-6:]), json.dumps(calls))
    try:
        txt, stop, _ = cwg._ask_meta(prompt, SYS, 12000)
        m = re.search(r"\{.*\}", txt, re.S)
        return json.loads(m.group(0), strict=False)
    except Exception as e:
        log("narrative failed: %s" % e)
        return None


def esc(x):
    return (str(x) if x is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def html_doc(since, until, N, hist, nar, untagged):
    nar = nar or {}
    tw = next((h for h in hist if h["week"] == since.isoformat()), {"calls": 0, "minutes": 0, "talked": 0, "after_hours_min": 0})
    prior = [h for h in hist if h["week"] < since.isoformat()][-4:]
    avg = round(sum(h["minutes"] for h in prior) / len(prior)) if prior else None
    last = prior[-1]["minutes"] if prior else None
    def bl(items):
        return "".join("<li><b>%s</b> %s</li>" % (esc(i.get("head", "")), esc(i.get("body", ""))) for i in (items or [])) or "<li>None this week.</li>"
    trows = "".join("<tr><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>" % (
        dt.date.fromisoformat(h["week"]).strftime("%b %d"), h["calls"], h["talked"], h["minutes"], h["after_hours_min"]) for h in hist[-8:])
    mx = max([h["minutes"] for h in hist[-8:]] + [1])
    bars = "".join("<div class='bar'><span class='lab'>%s</span><span class='b' style='width:%d%%'></span><span class='v'>%d min</span></div>" % (
        dt.date.fromisoformat(h["week"]).strftime("%b %d"), int(80 * h["minutes"] / mx), h["minutes"]) for h in hist[-8:])
    who = "".join("<tr><td>%s</td><td>%d</td><td>%d</td></tr>" % (esc(k), v, round(N["by_who_m"][k])) for k, v in N["by_who"].most_common())
    top = "".join("<tr><td>%s</td><td>%d</td><td>%d</td></tr>" % (esc(k), v, round(N["by_topic_m"][k])) for k, v in N["by_topic"].most_common())
    ppl = "".join("<tr><td>%s</td><td>%d</td><td>%d</td></tr>" % (esc(k), v, round(N["people_m"][k])) for k, v in N["people"].most_common(8))
    cell_base = " · ".join("%s %d calls / %d min" % b for b in CELL_BASELINE)
    note = (" · %d calls could not be read" % len(untagged)) if untagged else ""
    return """<html><head><meta charset='utf-8'><style>
body{font-family:Calibri,Helvetica,Arial,sans-serif;font-size:10pt;color:#222;margin:0.5in 0.7in}
h1{color:#2D1A5E;font-size:18pt;margin:0} .brand{color:#0099DD;font-weight:bold;font-size:9pt} .sub{color:#595959;font-size:9.5pt;margin-bottom:6pt}
h2{color:#0099DD;font-size:11.5pt;margin:10pt 0 3pt} table{border-collapse:collapse;margin:3pt 0} td,th{border:1px solid #999;padding:2pt 6pt;font-size:9pt}
th{background:#2D1A5E;color:#fff} ul{margin:2pt 0 2pt 14pt;padding:0} li{margin:0 0 3pt 0} b{color:#2D1A5E}
.top{background:#F2F0F8;border-left:4px solid #2D1A5E;padding:6pt 8pt;margin:6pt 0} .foot{color:#595959;font-size:8pt;margin-top:8pt}
.kpi{display:inline-block;margin-right:18pt} .kpi b{font-size:16pt;display:block} .grid{display:flex;gap:14pt;flex-wrap:wrap}
.bar{font-size:8.5pt;margin:1pt 0} .lab{display:inline-block;width:44pt} .b{display:inline-block;height:9pt;background:#0099DD;vertical-align:middle} .v{margin-left:4pt}
</style></head><body>
<div class='brand'>VALLEY PAWN</div><h1>Preston Phone Brief</h1>
<div class='sub'>%s – %s · every recorded call on Preston's Zoom line and every store call to his cell · For Joshua only%s</div>
<div class='top'><b>%s</b></div>
<div><span class='kpi'><b>%d min</b>on the phone this week</span><span class='kpi'><b>%s</b>last week</span><span class='kpi'><b>%s</b>4-week average</span>
<span class='kpi'><b>%d of %d</b>staff calls the store could have handled</span><span class='kpi'><b>%d min</b>after 6 PM / before 9 AM / Sunday</span></div>
<h2>THREE THINGS THAT WOULD CUT HIS PHONE TIME NEXT WEEK</h2><ol>%s</ol>
<h2>TREND (minutes per week)</h2>%s
<h2>WHAT PRESTON AND THE TEAM TALKED ABOUT</h2><ul>%s</ul>
<h2>COULD HAVE BEEN HANDLED WITHOUT PRESTON</h2><ul>%s</ul>
<h2>CUSTOMER-SERVICE ISSUES RAISED IN TEAM CALLS</h2><ul>%s</ul>
<div class='grid'>
<div><h2>WHO HE TALKED TO</h2><table><tr><th></th><th>Calls</th><th>Min</th></tr>%s</table></div>
<div><h2>TOPICS</h2><table><tr><th></th><th>Calls</th><th>Min</th></tr>%s</table></div>
<div><h2>STAFF WHO CALLED MOST</h2><table><tr><th></th><th>Calls</th><th>Min</th></tr>%s</table></div>
</div>
<h2>WEEK BY WEEK</h2><table><tr><th>Week of</th><th>Calls</th><th>Connected</th><th>Minutes</th><th>After-hours min</th></tr>%s</table>
<div class='foot'>Before the Zoom line, his cell bill showed: %s (all callers). Store calls to his cell are counted above from the store side; calls between his cell and staff or candidate cell phones are not recorded by Zoom.
Topics come from machine transcripts; play the audio in Zoom (Phone → Recordings) before acting. Per-call tags: Call Analysis/week_%s/preston/.</div>
</body></html>""" % (since.strftime("%b %d"), until.strftime("%b %d, %Y"), esc(note), esc(nar.get("headline", "")),
                     tw["minutes"], ("%d min" % last) if last is not None else "–", ("%d min" % avg) if avg is not None else "–",
                     len(N["could"]), len(N["staff"]), tw.get("after_hours_min", 0),
                     "".join("<li>%s</li>" % esc(t) for t in (nar.get("actions") or [])), bars, bl(nar.get("themes")), bl(nar.get("offload")),
                     bl(nar.get("service")), who, top, ppl, trows, esc(cell_base), since.isoformat())


# ---------------------------------------------------------------- 5. deliver
def deliver(since, until, nar, N, hist, out, drive_dst, render):
    tw = next((h for h in hist if h["week"] == since.isoformat()), {"minutes": 0, "calls": 0})
    prior = [h for h in hist if h["week"] < since.isoformat()][-4:]
    avg = round(sum(h["minutes"] for h in prior) / len(prior)) if prior else None
    lines = ["Preston Phone Brief for %s – %s: %d calls, %d min on the phone (last week %s, 4-week avg %s)." % (
        since.strftime("%b %d"), until.strftime("%b %d"), tw["calls"], tw["minutes"],
        ("%d" % prior[-1]["minutes"]) if prior else "–", ("%d" % avg) if avg is not None else "–")]
    lines.append("• %d of %d staff calls the store could have handled without him." % (len(N["could"]), len(N["staff"])))
    for t in ((nar or {}).get("actions") or [])[:2]:
        lines.append("• " + str(t))
    lines.append("PDF: " + (("Google Drive › My Drive › Call Reviews › " + os.path.basename(drive_dst)) if drive_dst else out))
    txt = "\n".join(lines)
    if render:
        print("=== DM (render only)\n" + txt); return
    stamp = dt.datetime.now(ET).strftime("%Y%m%d-%H%M%S")
    tpath = os.path.join(FLEET, "outbox", "%s-joshua-%s.txt" % (TASK, stamp))
    os.makedirs(os.path.dirname(tpath), exist_ok=True)
    open(tpath, "w").write(txt)
    json.dump({"channel": JOSHUA, "file": tpath}, open(tpath[:-4] + ".json", "w"))
    with open(os.path.join(OS_DIR, "CHANGELOG.md"), "r+") as f:
        body = f.read(); f.seek(0)
        f.write("## %s (preston phone brief, native)\n\n- preston-phone-week: %s–%s, %d calls / %d min, %d of %d staff calls offloadable; DM'd to Joshua\n\n%s" % (
            dt.datetime.now(ET).strftime("%Y-%m-%d"), since, until, tw["calls"], tw["minutes"], len(N["could"]), len(N["staff"]), body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since"); ap.add_argument("--until"); ap.add_argument("--render", action="store_true"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.since and a.until:
        since, until = dt.date.fromisoformat(a.since), dt.date.fromisoformat(a.until)
    else:
        since, until = cwg.last_week()
    d = os.path.join(CA, "week_%s" % since.isoformat())
    done = os.path.join(d, "preston", "_delivered.json")
    if os.path.exists(done) and not (a.render or a.force):
        log("already delivered for %s" % since); return 0
    st = os.path.join(d, "review_status.json")
    if not os.path.exists(st) or not os.path.exists(os.path.join(d, "recordings_index.json")):
        log("weekly phone review for %s not finished yet — will try again at the next slot" % since)
        if dt.datetime.now(ET).hour >= 13 and not a.render:
            ledger("The Preston phone brief for the week of %s could not run because that week's phone review was not finished by 1 PM." % since)
        return 0
    hist = trend(until)
    calls, _ = week_calls(d, since, until)
    log("preston calls this week: %d" % len(calls))
    tagged, untagged = tag(calls, d)
    if untagged:
        tagged2, untagged = tag(untagged, d)   # one retry: cached calls skipped
        tagged += tagged2
    N = numbers(tagged)
    nar = narrative(since, until, N, hist)
    if nar is None:
        nar = narrative(since, until, N, hist)
    tagn = "%s_%s" % (since.strftime("%b%d"), until.strftime("%b%d"))
    html_path = os.path.join(d, "Preston_Phone_Brief_%s.html" % tagn)
    pdf_path = os.path.join(d, "Preston_Phone_Brief_%s.pdf" % tagn)
    open(html_path, "w").write(html_doc(since, until, N, hist, nar, untagged))
    have_pdf = cwg.to_pdf(html_path, pdf_path)
    out = pdf_path if have_pdf else html_path
    drive_dst = None
    if have_pdf and not a.render:
        try:
            drive_dst = cwg.drive_copy(pdf_path)
        except Exception as e:
            log("drive copy failed: %s" % e)
    if nar is None or len(untagged) > 0.1 * max(len(calls), 1):
        ledger("The Preston phone brief for the week of %s was built but not sent: %d of %d calls could not be read%s." % (
            since, len(untagged), len(calls), "" if nar else " and the summary could not be written"))
        log("held: incomplete"); return 0
    deliver(since, until, nar, N, hist, out, drive_dst, a.render)
    if not a.render:
        json.dump({"since": since.isoformat(), "pdf": out, "drive": drive_dst, "calls": len(calls),
                   "at": dt.datetime.now(ET).isoformat(timespec="seconds")}, open(done, "w"), indent=1)
    log("done: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
