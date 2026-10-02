#!/usr/bin/env python3
# Roanoke open Wednesdays patch — 2026-10-01 (Joshua). Mac-side text/config files only.
# Mirrors _vp_hours_patch_2026-07-23.py: backs up each file to <file>.bak-pre-roanokewed-20261001,
# then applies exact replacements (global-unique or segment-scoped). Code files (vp_lib.sh,
# daily_audit_digest.py, run_daily_sold_review.py, ebay_ship_alert.py, recent_truth.py,
# fleet/missed_call_text_config.json) were patched by hand in the same session.
import shutil, os, sys
BASE = os.environ.get("VP_PROJ", "/Users/joshuadavis/Documents/Claude/Projects")
SUF = ".bak-pre-roanokewed-20261001"
OLD_OTHERS = "Culpeper: Mon–Sat 10am–6pm. All other stores: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."
NEW_FOOTER = "Culpeper & Roanoke: Mon–Sat 10am–6pm. Harrisonburg, Waynesboro & Lexington: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)."
CLOSED5 = "Mon, Tue, Thu, Fri, Sat 10am-6pm, closed Wed & Sun"

edits = []
edits.append(("Refine Social Media/vp_social_publisher.py", [
    ("# no Valley Pawn store is open 7 days -- Culpeper is closed Sunday; all\n# other stores are closed Wednesday AND Sunday).",
     "# no Valley Pawn store is open 7 days -- Culpeper & Roanoke are closed Sunday\n# only; the other three stores are closed Wednesday AND Sunday)."),
    ("(Culpeper closed Sun; others closed Wed+Sun)", "(Culpeper & Roanoke closed Sun; others closed Wed+Sun)"),
]))
edits.append(("Refine Social Media/vp_social/plan.py", [
    ("Hours: Culpeper Mon-Sat 10-6; all others \"\n              \"Mon/Tue/Thu/Fri/Sat 10-6, closed Wed & Sun;",
     "Hours: Culpeper & Roanoke Mon-Sat 10-6; Harrisonburg, Waynesboro & Lexington \"\n              \"Mon/Tue/Thu/Fri/Sat 10-6, closed Wed & Sun;"),
]))
edits.append(("Refine Social Media/SOCIAL_SYSTEM_SPEC.md", [
    ("hours facts (Culpeper Mon–Sat 10–6; others Mon/Tue/Thu/Fri/Sat\n10–6, closed Wed & Sun;",
     "hours facts (Culpeper & Roanoke Mon–Sat 10–6; Harrisonburg, Waynesboro & Lexington Mon/Tue/Thu/Fri/Sat\n10–6, closed Wed & Sun;"),
]))
edits.append(("Refine Social Media/LAUNCH_CAMPAIGNS.md", [(OLD_OTHERS, NEW_FOOTER)]))
edits.append(("Gold and Silver Markeitng/LAUNCH_CONTENT.md", [(OLD_OTHERS, NEW_FOOTER)]))
edits.append(("Gold and Silver Markeitng/pawn-loan-explained-page.md", [(OLD_OTHERS, NEW_FOOTER)]))
edits.append(("Gold and Silver Markeitng/STRATEGY.md", [
    ("Culpeper: Mon–Sat 10am–6pm; all others: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)",
     "Culpeper & Roanoke: Mon–Sat 10am–6pm; Harrisonburg, Waynesboro & Lexington: Mon, Tue, Thu, Fri & Sat 10am–6pm (closed Wed & Sun)"),
]))
edits.append(("Ai Optimized Marketing/AI-Search-GEO/content/faq-page.md", [
    ("- **Culpeper:** Monday–Saturday, 10:00 AM – 6:00 PM (the only store open Wednesdays).",
     "- **Culpeper & Roanoke:** Monday–Saturday, 10:00 AM – 6:00 PM (the stores open Wednesdays)."),
    ("- **Waynesboro, Harrisonburg, Lexington, Roanoke:** Monday, Tuesday, Thursday, Friday, Saturday, 10:00 AM – 6:00 PM. Closed Wednesday and Sunday.",
     "- **Harrisonburg, Waynesboro, Lexington:** Monday, Tuesday, Thursday, Friday, Saturday, 10:00 AM – 6:00 PM. Closed Wednesday and Sunday."),
]))
edits.append(("Ai Optimized Marketing/AI-Search-GEO/content/city-answer-snippets.md", [
    ("Open Mon, Tue, Thu, Fri, Sat, 10 AM–6 PM. Call or text (540) 562-0776",
     "Open Mon–Sat, 10 AM–6 PM. Call or text (540) 562-0776"),
    ("(note Culpeper = Wednesdays)", "(note Culpeper & Roanoke = Wednesdays)"),
]))
edits.append(("Ai Optimized Marketing/AI-Search-GEO/llms.txt", [
    ("(540) 445-5510 - Mon-Sat 10am-6pm (only store open Wednesdays).",
     "(540) 445-5510 - Mon-Sat 10am-6pm (open Wednesdays)."),
    ("(540) 562-0776 - Mon, Tue, Thu, Fri, Sat 10am-6pm.",
     "(540) 562-0776 - Mon-Sat 10am-6pm (open Wednesdays)."),
    ("- Culpeper: Monday-Saturday 10:00 AM - 6:00 PM (closed Sunday).",
     "- Culpeper & Roanoke: Monday-Saturday 10:00 AM - 6:00 PM (closed Sunday)."),
    ("- Waynesboro, Harrisonburg, Lexington, Roanoke: Monday, Tuesday, Thursday, Friday, Saturday 10:00 AM - 6:00 PM (closed Wednesday and Sunday).",
     "- Harrisonburg, Waynesboro, Lexington: Monday, Tuesday, Thursday, Friday, Saturday 10:00 AM - 6:00 PM (closed Wednesday and Sunday)."),
    ("Culpeper is the only store open on Wednesday.", "Culpeper and Roanoke are the stores open on Wednesday."),
]))
edits.append(("Ai Optimized Marketing/AI-Search-GEO/schema/valley-pawn-schema.html", [
    ("The Culpeper store is open Monday through Saturday, 10:00 AM to 6:00 PM. The Waynesboro, Harrisonburg, Lexington, and Roanoke stores are open Monday, Tuesday, Thursday, Friday, and Saturday, 10:00 AM to 6:00 PM, and are closed Wednesday and Sunday. Culpeper is the only store open on Wednesdays.",
     "The Culpeper and Roanoke stores are open Monday through Saturday, 10:00 AM to 6:00 PM. The Harrisonburg, Waynesboro, and Lexington stores are open Monday, Tuesday, Thursday, Friday, and Saturday, 10:00 AM to 6:00 PM, and are closed Wednesday and Sunday. Culpeper and Roanoke are the stores open on Wednesdays."),
]))
edits.append(("Human Resources/vp_hiring_posts.json", [
    ("hiring a Retail Sales Associate.\\n\\nEvery Sunday off, closed Wednesdays, home by 6 every night.",
     "hiring a Retail Sales Associate.\\n\\nEvery Sunday off, home by 6 every night."),
]))

seg_edits = [
    ("Refine Social Media/vp_social_publisher.py", '"Roanoke": {"address"', "}\n\n",
     [('"hours": "%s"' % CLOSED5, '"hours": "Mon-Sat 10am-6pm, closed Sunday"')]),
    ("Refine Social Media/vp_social/config.py", '"Roanoke":      {"address"', "\n}",
     [('"hours": "%s"' % CLOSED5, '"hours": "Mon-Sat 10am-6pm, closed Sun"')]),
    ("Refine Social Media/audit_2026-06-22/canonical_nap.json", '"full_name": "Valley Pawn - Roanoke"', '"google_maps_canonical"',
     [('"hours": "Mon, Tue, Thu, Fri, Sat 10am-6pm. Closed Wed, Sun"', '"hours": "Mon-Sat 10am-6pm. Closed Sun"'),
      ('"Mon": "10am-6pm", "Tue": "10am-6pm", "Wed": "Closed",', '"Mon": "10am-6pm", "Tue": "10am-6pm", "Wed": "10am-6pm",')]),
    ("Gold and Silver Markeitng/generate_store_pages.py", '"STORE_CITY": "Roanoke"', "\n]",
     [('"STORE_HOURS_LINE": "Mon, Tue, Thu, Fri & Sat 10:00 AM – 6:00 PM · Closed Wednesday & Sunday"',
       '"STORE_HOURS_LINE": "Monday–Saturday, 10:00 AM – 6:00 PM · Closed Sunday"'),
      ('"STORE_OPEN_DAYS_SCHEMA": \'["Monday","Tuesday","Thursday","Friday","Saturday"]\'',
       '"STORE_OPEN_DAYS_SCHEMA": \'["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]\'')]),
]

report, ok = [], True
def backup(p):
    b = p + SUF
    if not os.path.exists(b): shutil.copy2(p, b)
def write(p, t, nt):
    if nt != t:
        backup(p); open(p, "w", encoding="utf-8").write(nt)

for rel, reps in edits:
    p = os.path.join(BASE, rel)
    t = open(p, encoding="utf-8").read(); nt = t
    for o, n in reps:
        c = nt.count(o)
        if c == 0: report.append("MISS  %s :: %r" % (rel, o[:60])); ok = False; continue
        nt = nt.replace(o, n); report.append("OK(%d) %s :: %r" % (c, rel, o[:50]))
    write(p, t, nt)
for rel, sa, ea, reps in seg_edits:
    p = os.path.join(BASE, rel)
    t = open(p, encoding="utf-8").read()
    i = t.index(sa); j = t.index(ea, i); seg = t[i:j]; ns = seg
    for o, n in reps:
        c = ns.count(o)
        if c != 1: report.append("SEGMISS(%d) %s :: %r" % (c, rel, o[:50])); ok = False; continue
        ns = ns.replace(o, n); report.append("SEG-OK %s :: %r" % (rel, o[:50]))
    write(p, t, t[:i] + ns + t[j:])
print("\n".join(report)); print("RESULT:", "ALL-OK" if ok else "HAS-MISSES")
