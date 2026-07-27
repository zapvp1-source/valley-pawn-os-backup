#!/usr/bin/env python3
# Waynesboro 6-day hours patch — 2026-07-23. Backs up each file to <file>.bak-2026-07-23 then applies exact replacements.
import shutil, os, sys

BASE_SCHED = "/Users/joshuadavis/Documents/Claude/Scheduled"
BASE_PROJ = "/Users/joshuadavis/Documents/Claude/Projects"

def seg(text, start_anchor, end_anchor):
    i = text.index(start_anchor)
    j = text.index(end_anchor, i) if end_anchor else len(text)
    return i, j

edits = []  # (path, [(old, new)]) plain global-unique replacements
edits.append((f"{BASE_SCHED}/daily-clockin-check/SKILL.md", [
    ("keep ONLY Culpeper employees",
     "keep ONLY Culpeper and Waynesboro employees"),
    ("Only Culpeper is open on Wednesdays — Harrisonburg, Waynesboro, Lexington, and Roanoke are closed.",
     "Only Culpeper and Waynesboro are open on Wednesdays — Harrisonburg, Lexington, and Roanoke are closed."),
]))
edits.append((f"{BASE_SCHED}/chekkit-unanswered-alert/SKILL.md", [
    ("only Culpeper can have countable misses (the other four were closed)",
     "only Culpeper and Waynesboro can have countable misses (the other three were closed)"),
]))
edits.append((f"{BASE_SCHED}/vp-ai-search-health-check/SKILL.md", [
    ("Mon–Sat 10am–6pm (ONLY store open Wednesdays)",
     "Mon–Sat 10am–6pm (open Wednesdays)"),
    ("(540) 221-6346 — Mon,Tue,Thu,Fri,Sat 10am–6pm (closed Wed & Sun)",
     "(540) 221-6346 — Mon–Sat 10am–6pm (closed Sun)"),
]))
edits.append((f"{BASE_SCHED}/vp-website-deals-weekly/SKILL.md", [
    ("Every store closes at 6 PM (never 5); Culpeper is the only store open Wednesday.",
     "Every store closes at 6 PM (never 5); Culpeper and Waynesboro are the only stores open Wednesday."),
    ("Prefer email? Our subscribers get these deals first every Thursday. Mon, Tue, Thu, Fri & Sat 10 AM–6 PM (Culpeper also Wed). What's Right Is Right.",
     "Prefer email? Our subscribers get these deals first every Thursday. Culpeper & Waynesboro: Mon–Sat 10 AM–6 PM. Harrisonburg, Lexington & Roanoke: Mon, Tue, Thu, Fri & Sat 10 AM–6 PM (closed Wed & Sun). All stores closed Sunday. What's Right Is Right."),
]))
edits.append((f"{BASE_PROJ}/Refine Social Media/vp_social_publisher.py", [
    ("# no Valley Pawn store is open 7 days -- Culpeper is closed Sunday; all\n# other stores are closed Wednesday AND Sunday).",
     "# no Valley Pawn store is open 7 days -- Culpeper & Waynesboro are closed Sunday\n# only; the other three stores are closed Wednesday AND Sunday)."),
    ("(Culpeper closed Sun; others closed Wed+Sun)",
     "(Culpeper & Waynesboro closed Sun; others closed Wed+Sun)"),
]))
edits.append((f"{BASE_PROJ}/Refine Social Media/LAUNCH_CAMPAIGNS.md", [
    ("Culpeper: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun).",
     "Culpeper & Waynesboro: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."),
]))
edits.append((f"{BASE_PROJ}/Gold and Silver Markeitng/LAUNCH_CONTENT.md", [
    ("Culpeper: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun).",
     "Culpeper & Waynesboro: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."),
]))
edits.append((f"{BASE_PROJ}/Gold and Silver Markeitng/pawn-loan-explained-page.md", [
    ("Culpeper: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun).",
     "Culpeper & Waynesboro: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."),
]))
edits.append((f"{BASE_PROJ}/Gold and Silver Markeitng/STRATEGY.md", [
    ("Culpeper: Mon–Sat 10am–6pm; all others: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)",
     "Culpeper & Waynesboro: Mon–Sat 10am–6pm; all others: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)"),
]))
edits.append((f"{BASE_PROJ}/Ai Optimized Marketing/AI-Search-GEO/content/faq-page.md", [
    ("- **Culpeper:** Monday–Saturday, 10:00 AM – 6:00 PM (the only store open Wednesdays).",
     "- **Culpeper & Waynesboro:** Monday–Saturday, 10:00 AM – 6:00 PM."),
    ("- **Waynesboro, Harrisonburg, Lexington, Roanoke:** Monday, Tuesday, Thursday, Friday, Saturday, 10:00 AM – 6:00 PM. Closed Wednesday and Sunday.",
     "- **Harrisonburg, Lexington, Roanoke:** Monday, Tuesday, Thursday, Friday, Saturday, 10:00 AM – 6:00 PM. Closed Wednesday and Sunday.\n- All stores closed Sunday."),
]))
edits.append((f"{BASE_PROJ}/Ai Optimized Marketing/AI-Search-GEO/content/city-answer-snippets.md", [
    ("Open Mon, Tue, Thu, Fri, Sat, 10 AM–6 PM. Call or text (540) 221-6346",
     "Open Mon–Sat, 10 AM–6 PM. Call or text (540) 221-6346"),
]))

# Segment-scoped edits: (path, seg_start_anchor, seg_end_anchor, [(old, new)])
seg_edits = [
    (f"{BASE_PROJ}/Refine Social Media/vp_social_publisher.py",
     '"Waynesboro": {"address"', '"Harrisonburg": {"address"',
     [('"hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun"',
       '"hours": "Mon-Sat 10am-6pm, closed Sunday"')]),
    (f"{BASE_PROJ}/Refine Social Media/audit_2026-06-22/canonical_nap.json",
     '"full_name": "Valley Pawn - Waynesboro"', '"full_name": "Valley Pawn - Harrisonburg"',
     [('"hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm. Closed Wed, Sun"',
       '"hours": "Mon-Sat 10am-6pm. Closed Sun"'),
      ('"Mon": "10am-6pm", "Tue": "10am-6pm", "Wed": "Closed",',
       '"Mon": "10am-6pm", "Tue": "10am-6pm", "Wed": "10am-6pm",')]),
    (f"{BASE_PROJ}/Gold and Silver Markeitng/generate_store_pages.py",
     '"STORE_CITY": "Waynesboro"', '"STORE_CITY": "Harrisonburg"',
     [('"STORE_HOURS_LINE": "Mon, Tue, Thu, Fri & Sat 10:00 AM – 6:00 PM · Closed Wednesday & Sunday"',
       '"STORE_HOURS_LINE": "Monday–Saturday 10:00 AM – 6:00 PM · Closed Sunday"')]),
]

report = []
def backup(path):
    b = path + ".bak-2026-07-23"
    if not os.path.exists(b):
        shutil.copy2(path, b)

ok = True
for path, reps in edits:
    try:
        with open(path, encoding="utf-8") as f: t = f.read()
        new_t = t
        for old, new in reps:
            n = new_t.count(old)
            if n == 0:
                report.append(f"MISS  {path} :: {old[:60]!r}"); ok = False; continue
            new_t = new_t.replace(old, new)
            report.append(f"OK({n}) {os.path.basename(os.path.dirname(path))}/{os.path.basename(path)} :: {old[:55]!r}")
        if new_t != t:
            backup(path)
            with open(path, "w", encoding="utf-8") as f: f.write(new_t)
    except Exception as e:
        report.append(f"ERROR {path} :: {e}"); ok = False

for path, sa, ea, reps in seg_edits:
    try:
        with open(path, encoding="utf-8") as f: t = f.read()
        i, j = seg(t, sa, ea)
        segment = t[i:j]
        new_seg = segment
        for old, new in reps:
            n = new_seg.count(old)
            if n != 1:
                report.append(f"SEGMISS({n}) {path} :: {old[:55]!r}"); ok = False; continue
            new_seg = new_seg.replace(old, new)
            report.append(f"SEG-OK {os.path.basename(path)} :: {old[:55]!r}")
        if new_seg != segment:
            backup(path)
            with open(path, "w", encoding="utf-8") as f: f.write(t[:i] + new_seg + t[j:])
    except Exception as e:
        report.append(f"ERROR {path} :: {e}"); ok = False

print("\n".join(report))
print("RESULT:", "ALL-OK" if ok else "HAS-MISSES")
