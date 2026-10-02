#!/usr/bin/env python3
# Culpeper & Roanoke close 5 PM on Saturdays — 2026-10-01 (Joshua; first affected Saturday 10/3/2026).
# Rule: any store open 6 days a week closes at 5:00 PM on Saturday. Today = Culpeper & Roanoke.
# Mirrors _vp_hours_patch_2026-10-01_roanoke_wed.py: backs up each file to <file>.bak-pre-sat5-20261001,
# then applies exact replacements (global with expected count, or segment-scoped). Mac-side lane only.
# Run with --dry to report without writing.
import shutil, os, sys
BASE = os.environ.get("VP_PROJ", "/Users/joshuadavis/Documents/Claude/Projects")
SUF = ".bak-pre-sat5-20261001"
DRY = "--dry" in sys.argv
OLD_FOOTER = "Culpeper & Roanoke: Mon–Sat 10am–6pm. Harrisonburg, Waynesboro & Lexington: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."
NEW_FOOTER = "Culpeper & Roanoke: Mon–Fri 10am–6pm, Sat 10am–5pm. Harrisonburg, Waynesboro & Lexington: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."

# (relative path, [(old, new, expected_count)])
edits = [
    ("Refine Social Media/vp_social_publisher.py", [
        ('"hours": "Mon-Sat 10am-6pm, closed Sunday"', '"hours": "Mon-Fri 10am-6pm, Sat 10am-5pm, closed Sunday"', 2),
    ]),
    ("Refine Social Media/vp_social/config.py", [
        ('"hours": "Mon-Sat 10am-6pm, closed Sun"', '"hours": "Mon-Fri 10am-6pm, Sat 10am-5pm, closed Sun"', 2),
    ]),
    ("Refine Social Media/vp_social/plan.py", [
        ("Hours: Culpeper & Roanoke Mon-Sat 10-6; ", "Hours: Culpeper & Roanoke Mon-Fri 10-6, Sat 10-5; ", 1),
        ("closed Wed & Sun; nobody closes at 5. ", "closed Wed & Sun; only Culpeper & Roanoke close at 5, and only on Saturday. ", 1),
    ]),
    ("Refine Social Media/SOCIAL_SYSTEM_SPEC.md", [
        ("hours facts (Culpeper & Roanoke Mon–Sat 10–6; ", "hours facts (Culpeper & Roanoke Mon–Fri 10–6, Sat 10–5; ", 1),
        ("closed Wed & Sun; nobody closes at 5)", "closed Wed & Sun; only Culpeper & Roanoke close at 5, and only on Saturday)", 1),
    ]),
    ("Refine Social Media/PILLAR_OVERLAY.md", [
        ('bad claims ("seven days a week," "closes at 5pm," "Dixie Pawn")',
         'bad claims ("seven days a week," "closes at 5pm" for any store/day other than\n   Culpeper & Roanoke on Saturday, "Dixie Pawn")', 1),
    ]),
    ("Refine Social Media/LAUNCH_CAMPAIGNS.md", [(OLD_FOOTER, NEW_FOOTER, 1)]),
    ("Gold and Silver Markeitng/LAUNCH_CONTENT.md", [(OLD_FOOTER, NEW_FOOTER, 1)]),
    ("Gold and Silver Markeitng/pawn-loan-explained-page.md", [(OLD_FOOTER, NEW_FOOTER, 1)]),
    ("Gold and Silver Markeitng/STRATEGY.md", [
        ("Culpeper & Roanoke: Mon–Sat 10am–6pm; Harrisonburg", "Culpeper & Roanoke: Mon–Fri 10am–6pm, Sat 10am–5pm; Harrisonburg", 1),
        ("(closed Wed & Sun). No store closes at 5pm.", "(closed Wed & Sun). Only the 6-day stores (Culpeper & Roanoke) close at 5pm, and only on Saturday.", 1),
    ]),
    ("Gold and Silver Markeitng/generate_store_pages.py", [
        ('"STORE_HOURS_LINE": "Monday–Saturday, 10:00 AM – 6:00 PM · Closed Sunday"',
         '"STORE_HOURS_LINE": "Monday–Friday 10:00 AM – 6:00 PM · Saturday 10:00 AM – 5:00 PM · Closed Sunday"', 2),
    ]),
    ("Ai Optimized Marketing/AI-Search-GEO/content/faq-page.md", [
        ("- **Culpeper & Roanoke:** Monday–Saturday, 10:00 AM – 6:00 PM (the stores open Wednesdays).",
         "- **Culpeper & Roanoke:** Monday–Friday, 10:00 AM – 6:00 PM; Saturday, 10:00 AM – 5:00 PM (the stores open Wednesdays). Closed Sunday.", 1),
    ]),
    ("Ai Optimized Marketing/AI-Search-GEO/content/city-answer-snippets.md", [
        ("It's the only Valley Pawn location open on Wednesdays (Mon–Sat, 10 AM–6 PM).",
         "It's one of two Valley Pawn locations open on Wednesdays (Mon–Fri 10 AM–6 PM, Sat 10 AM–5 PM).", 1),
        ("Open Mon–Sat, 10 AM–6 PM. Call or text (540) 562-0776",
         "Open Mon–Fri 10 AM–6 PM, Sat 10 AM–5 PM. Call or text (540) 562-0776", 1),
    ]),
    ("Ai Optimized Marketing/AI-Search-GEO/llms.txt", [
        ("(540) 445-5510 - Mon-Sat 10am-6pm (open Wednesdays).", "(540) 445-5510 - Mon-Fri 10am-6pm, Sat 10am-5pm (open Wednesdays).", 1),
        ("(540) 562-0776 - Mon-Sat 10am-6pm (open Wednesdays).", "(540) 562-0776 - Mon-Fri 10am-6pm, Sat 10am-5pm (open Wednesdays).", 1),
        ("- Culpeper & Roanoke: Monday-Saturday 10:00 AM - 6:00 PM (closed Sunday).",
         "- Culpeper & Roanoke: Monday-Friday 10:00 AM - 6:00 PM, Saturday 10:00 AM - 5:00 PM (closed Sunday).", 1),
        ("- No Valley Pawn store closes at 5:00 PM.", "- Only the 6-day stores (Culpeper & Roanoke) close at 5:00 PM, and only on Saturday.", 1),
    ]),
    ("Ai Optimized Marketing/AI-Search-GEO/schema/valley-pawn-schema.html", [
        ("The Culpeper and Roanoke stores are open Monday through Saturday, 10:00 AM to 6:00 PM.",
         "The Culpeper and Roanoke stores are open Monday through Friday, 10:00 AM to 6:00 PM, and Saturday, 10:00 AM to 5:00 PM.", 1),
    ]),
    ("Human Resources/vp_hiring_posts.json", [
        ("doors close at 6 PM so there are no late retail nights", "doors close by 6 PM so there are no late retail nights", 1),
    ]),
]

SPEC_6 = '{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"], "opens": "10:00", "closes": "18:00"}'
SPEC_5_ROA_OLD = '{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Thursday","Friday","Saturday"], "opens": "10:00", "closes": "18:00"}'
SPEC_NEW = ('{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "10:00", "closes": "18:00"},\n'
            '    {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday"], "opens": "10:00", "closes": "17:00"}')
SAT6 = '"Fri": "10am-6pm", "Sat": "10am-6pm", "Sun": "Closed"'
SAT5 = '"Fri": "10am-6pm", "Sat": "10am-5pm", "Sun": "Closed"'
CLOSE_LINE = '"close": "18:00",'
CLOSE_LINE_NEW = '"close": "18:00",\n      "close_by_weekday": {\n        "5": "17:00"\n      },'

# (relative path, segment start anchor, segment end anchor, [(old, new)]) — each old must occur exactly once in the segment
seg_edits = [
    ("Ai Optimized Marketing/AI-Search-GEO/schema/valley-pawn-schema.html", '"name": "Valley Pawn - Culpeper"', "</script>", [(SPEC_6, SPEC_NEW)]),
    ("Ai Optimized Marketing/AI-Search-GEO/schema/valley-pawn-schema.html", '"name": "Valley Pawn - Roanoke"', "</script>", [(SPEC_5_ROA_OLD, SPEC_NEW)]),
    ("Refine Social Media/audit_2026-06-22/canonical_nap.json", '"full_name": "Valley Pawn - Culpeper"', '"google_maps_canonical"',
     [('"hours": "Mon-Sat 10am-6pm, Closed Sun"', '"hours": "Mon-Fri 10am-6pm, Sat 10am-5pm, Closed Sun"'), (SAT6, SAT5)]),
    ("Refine Social Media/audit_2026-06-22/canonical_nap.json", '"full_name": "Valley Pawn - Roanoke"', '"google_maps_canonical"',
     [('"hours": "Mon-Sat 10am-6pm. Closed Sun"', '"hours": "Mon-Fri 10am-6pm, Sat 10am-5pm. Closed Sun"'), (SAT6, SAT5)]),
    ("Valley Pawn OS/fleet/missed_call_text_config.json", '"CUL": {', '"webhook"', [(CLOSE_LINE, CLOSE_LINE_NEW)]),
    ("Valley Pawn OS/fleet/missed_call_text_config.json", '"CUL": {', '"HAR": {', [('"hours_text": "Mon-Sat 10am-6pm"', '"hours_text": "Mon-Fri 10am-6pm, Sat 10am-5pm"')]),
    ("Valley Pawn OS/fleet/missed_call_text_config.json", '"ROA": {', '"webhook"', [(CLOSE_LINE, CLOSE_LINE_NEW)]),
    ("Valley Pawn OS/fleet/missed_call_text_config.json", '"ROA": {', '"WAY": {', [('"hours_text": "Mon-Sat 10am-6pm"', '"hours_text": "Mon-Fri 10am-6pm, Sat 10am-5pm"')]),
    ("Valley Pawn OS/fleet/missed_call_text_config.json", '"_exclude_note"', '"messages"',
     [('Re-sync when staff change.",', 'Re-sync when staff change.",\n  "_close_by_weekday_note": "2026-10-01 (Joshua): optional per-store map of weekday (0=Mon..6=Sun, as a string) -> closing time, overriding \\"close\\" for that day. CUL and ROA (the 6-day stores) close 17:00 on Saturday. Read by missed_call_text.during_hours (also texting_scorecard) and chekkit_ai_responder.store_open.",')]),
]

report, ok = [], True
cache = {}
def load(rel):
    if rel not in cache:
        p = os.path.join(BASE, rel); cache[rel] = [open(p, encoding="utf-8").read(), None]
        cache[rel][1] = cache[rel][0]
    return cache[rel]

for rel, reps in edits:
    c = load(rel)
    for o, n, exp in reps:
        k = c[1].count(o)
        if k != exp:
            report.append("MISS(%d!=%d) %s :: %r" % (k, exp, rel, o[:60])); ok = False; continue
        c[1] = c[1].replace(o, n); report.append("OK(%d) %s :: %r" % (k, rel, o[:50]))
for rel, sa, ea, reps in seg_edits:
    c = load(rel); t = c[1]
    i = t.index(sa); j = t.index(ea, i); seg = t[i:j]; ns = seg
    for o, n in reps:
        k = ns.count(o)
        if k != 1:
            report.append("SEGMISS(%d) %s [%s] :: %r" % (k, rel, sa[:25], o[:50])); ok = False; continue
        ns = ns.replace(o, n); report.append("SEG-OK %s [%s] :: %r" % (rel, sa[:25], o[:40]))
    c[1] = t[:i] + ns + t[j:]

print("\n".join(report)); print("RESULT:", "ALL-OK" if ok else "HAS-MISSES")
if ok and not DRY:
    for rel, (orig, new) in cache.items():
        if new != orig:
            p = os.path.join(BASE, rel); b = p + SUF
            if not os.path.exists(b): shutil.copy2(p, b)
            open(p, "w", encoding="utf-8").write(new)
            print("WROTE", rel)
elif not ok:
    print("Nothing written (fix misses first).")
