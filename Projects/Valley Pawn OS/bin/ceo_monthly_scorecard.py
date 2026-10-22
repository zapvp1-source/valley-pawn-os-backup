#!/usr/bin/env python3
"""ceo_monthly_scorecard.py [YYYY-MM] [--render] — native `ceo-monthly-scorecard` (3rd 12:00 ET; wave 3 second pass, 2026-10-20).
Reads PUBLISHED month-end output only — never Bravo, never QBO, never a pull. Posts ONLY to #ceo-briefs (C0C06PWLQCR).

DETERMINISTIC (code, not the model): the COMPANY and BY STORE blocks, from Valley Pawn OS/monthly-analytics/<M> Monthly
Analytics.md (the monthly-analytics-report working file: same-month / YTD / T12M, current vs prior) and MoM against the
prior month's EOM net revenue in Bonus Program/data/history.json (the same figures the 10/3 post used: CUL 63,307 vs
61,998 = +2.1%, company 230,722 vs 233,039 = -1.0%). Gate E: all five stores in the working file, else HOLD.
MODEL (bin/vp_ai.py, claude-sonnet-5-5): THE TREND / FINANCIAL / OPERATIONS / PEOPLE / MARKETING / COMPLIANCE / DECISIONS /
STILL OPEN / WATCH, in the 10/3 layout (fleet/state/w3b_reference/ceo_monthly_2026-09.txt), from the HARVEST below only.
  Gate A: the weekly scorecard is never a source (not harvested). Gate B: the prompt forbids hardening ranges and pairing a
  figure with a percentage from different posts. Coverage floor: every "Month in Review" post of the month's close in the 15
  recap channels + #company-performance, #new-customers, #employee-performance, #scrap-rankings are harvested.
  Gate C: hires / separations come from Gusto ONLY — Communcations/ceo-scorecard/data/eom/<M>_people.json
  ({"active_at_month_end": n, "hires": [...], "separations": [...]} written by a Gusto-connected run). Absent = the PEOPLE
  block carries no hire/separation numbers (withheld, Rule 18) and the run is marked people_withheld in STATUS.
  Gate D (Joshua's DM contradiction scan) has no bot path (the bot cannot read Joshua's own DM) — STATUS says so.
  Bonus / Amazon allocation / gun audit always go in STILL OPEN with their close dates; never estimated.
Dedupe: a "VALLEY PAWN — <MONTH YEAR>" post already in #ceo-briefs (bot must be a member) = stop.
Writes: STATUS-<M>.md, MONTH-<M>.html (one printable page), LAST_MONTH.json carry-forward (live only).
--render: everything except the post / carry-forward; the post goes to fleet/test_output/.
"""
import datetime as dt
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import w3b_lib as L  # noqa: E402
import vp_people  # noqa: E402  fleet-wide rule 2026-10-21: current staff only, never a Davis

TASK = "ceo-monthly-scorecard"
CH = "C0C06PWLQCR"
CEO = os.path.join(L.PROJ, "Communcations", "ceo-scorecard")
REF = os.path.join(L.OS_DIR, "fleet", "state", "w3b_reference", "ceo_monthly_2026-09.txt")
HISTORY = os.path.join(L.PROJ, "Bonus Program", "data", "history.json")
HARVEST = {"C0B26GD8D2R": "company-performance", "C0BHF9NM0BH": "new-customers", "C0ATTLPQHR8": "employee-performance",
           "C05EHBH4G67": "scrap-rankings", "C0B08RS2BMK": "loan-review", "C04N24STDP1": "layaway-review",
           "C04NGH4FF35": "aged-inventory-review", "C0B17894S2Y": "first-payment-default", "C0AN6TNA4ES": "timekeeping-summary",
           "C0B1K4WK2HZ": "weekly-returns-summary", "C0B3R9B3S8H": "daily-funds-reconcilation", "C0B8WR95N31": "pawn-walks",
           "C04NDE52U2G": "google-reviews", "C0BMRC2LN3D": "social-media", "C0APR5WUL2Z": "email-campiagns", "C0ASE9C0GQ0": "website",
           "C0BCEESUANM": "ai-marketing", "C0ANVN5KX4Y": "ebay-performance", "C0APY6TE604": "blog-posts", "C07CPN020G0": "monthly-gun-audit"}
ORDER = ["CUL", "HAR", "LEX", "ROA", "WAY"]


def tables(md):
    out, cur = {}, None
    for line in md.splitlines():
        m = re.match(r"^### (\S+)\s*$", line)
        if m:
            cur = m.group(1); out[cur] = {}; continue
        if cur and line.startswith("| ") and not line.startswith("| Store") and not line.startswith("|---"):
            c = [x.strip().strip("*") for x in line.strip("|").split("|")]
            try:
                out[cur][c[0]] = {"inv": float(c[1]), "loans": float(c[2]), "sales": float(c[3]), "scrap": float(c[4]),
                                  "psc": float(c[5]), "net": float(c[6])}
            except (ValueError, IndexError):
                pass
        elif cur and line.startswith("#"):
            cur = None
    return out


def arrow(p):
    return ("▲%.1f%%" % p) if p >= 0 else ("▼%.1f%%" % -p)


def pct(a, b):
    return (a - b) * 100.0 / b if b else 0.0


def header(period, t, prev):
    cur, pri = t["same-month-current"], t["same-month-prior"]
    yc, yp, tc, tp = t["ytd-current"], t["ytd-prior"], t["t12m-current"], t["t12m-prior"]
    gt = cur["GT"]
    prev_tot = sum(prev.values()) if prev else None
    _, _, _, label = L.months(period)
    month = label.split()[0]
    lines = [":bar_chart: VALLEY PAWN — %s" % label.upper(), "", "COMPANY",
             "Net revenue $%s · MoM %s · YoY %s" % (format(round(gt["net"]), ","), arrow(pct(gt["net"], prev_tot)) if prev_tot else "n/a",
                                                    arrow(pct(gt["net"], pri["GT"]["net"]))),
             "Total sales $%s %s YoY · Pawn service charges $%s %s YoY" % (format(round(gt["sales"]), ","), arrow(pct(gt["sales"], pri["GT"]["sales"])),
                                                                          format(round(gt["psc"]), ","), arrow(pct(gt["psc"], pri["GT"]["psc"]))),
             "Loan balance $%s %s YoY · Inventory $%s %s YoY" % (format(round(gt["loans"]), ","), arrow(pct(gt["loans"], pri["GT"]["loans"])),
                                                                 format(round(gt["inv"]), ","), arrow(pct(gt["inv"], pri["GT"]["inv"]))),
             "Year to date $%s %s · Trailing 12 months $%s %s" % (format(round(yc["GT"]["net"]), ","), arrow(pct(yc["GT"]["net"], yp["GT"]["net"])),
                                                                  format(round(tc["GT"]["net"]), ","), arrow(pct(tc["GT"]["net"], tp["GT"]["net"]))),
             "", "BY STORE (ranked on %s net revenue)" % month]
    ranked = sorted(ORDER, key=lambda s: -cur[s]["net"])
    for i, s in enumerate(ranked, 1):
        mom = arrow(pct(cur[s]["net"], prev[s])) if prev and prev.get(s) else "n/a"
        lines.append("%d. %s — $%s · MoM %s / YoY %s · loans $%s" % (i, L.NAMES[s], format(round(cur[s]["net"]), ","), mom,
                                                                    arrow(pct(cur[s]["net"], pri[s]["net"])), format(round(cur[s]["loans"]), ",")))
    facts = {"company": {k: round(v, 2) for k, v in gt.items()}, "prior_year": {k: round(v, 2) for k, v in pri["GT"].items()},
             "ytd": round(yc["GT"]["net"], 2), "ytd_prior": round(yp["GT"]["net"], 2), "t12m": round(tc["GT"]["net"], 2),
             "stores": {s: {"net": cur[s]["net"], "prior_year_net": pri[s]["net"], "prev_month_net": (prev or {}).get(s),
                            "loans": cur[s]["loans"], "loans_prior_year": pri[s]["loans"], "inv": cur[s]["inv"]} for s in ORDER}}
    return "\n".join(lines), facts, ranked


SYSTEM = ("You write Joshua Davis's one-page monthly CEO scorecard for Valley Pawn. You use ONLY the facts and posts given. "
          "Never estimate. Never harden a range into a precise number. A dollar figure and a percentage in one sentence must "
          "come from the SAME dated post. Never present a mid-month figure as month-end — label it 'at <date>'. Never name "
          "software, systems, files, channels, tasks or automations. Withhold rather than caveat. Name only current employees, "
          "and never name anyone with the last name Davis.")
PROMPT = """Write the sections AFTER the BY STORE block of the {label} scorecard, in exactly this layout and with these caps
(reference = last month's real page; match its tone, density and caps, not its numbers):
:chart_with_upwards_trend: THE TREND (3 bullets) · :moneybag: FINANCIAL (3) · :gear: OPERATIONS (3) · :busts_in_silhouette: PEOPLE (3)
· :mega: MARKETING (3) · :shield: COMPLIANCE (2) · :white_check_mark: DECISIONS FOR THIS MONTH (5 numbered, each "— <owner>")
· :hourglass_flowing_sand: STILL OPEN · :warning: WATCH (3) · then ONE closing line on last month's decisions.

REFERENCE PAGE:
{ref}

THE COMPANY / BY STORE BLOCK ALREADY WRITTEN (do not repeat it; you may cite its numbers):
{head}

FACTS (exact): {facts}

PEOPLE (Gusto): {people}

LAST MONTH'S DECISIONS (say how many closed, using only evidence in the posts): {decisions}

STILL OPEN must always include: bonus qualifiers and payout — closes the 10th; Amazon store spend allocation — the 6th;
gun audit — deadline the 15th, reported the 16th; plus anything the posts say has not closed.

MONTH-END POSTS (channel, date, text):
{posts}

Return ONLY the sections, starting with ':chart_with_upwards_trend: THE TREND'."""


_NAME_RX = re.compile(r"[*_]([A-Z][a-zA-Z'.-]+(?: [A-Z][a-zA-Z'.-]+){1,2})[*_]\s*\(|\b([A-Z][a-zA-Z'.-]+ [A-Z][a-zA-Z'.-]+) \((?:CUL|HAR|LEX|ROA|WAY)")
_METRIC_WORDS = {"Revenue", "Sales", "Total", "Net", "Retail", "Loans", "Loan", "Inventory", "Store", "Stores", "Company",
                 "Gold", "Silver", "Scrap", "Service", "Charges", "Pawn", "Layaway", "Layaways", "Review", "Month", "Week",
                 "Average", "Gross", "Profit", "Buys", "Fees", "Past", "Due", "Aged", "Email", "Reviews", "Google"}
_NOT_NAMES = {"Valley Pawn", "Retail Sales", "Company Total", "Store Performance", "Employee Sales", "Month In Review"}


_KNOWN = {}


def known_people():
    """Everyone Bravo has ever listed (BRAVO_USERS incl. TERMINATED + every employee-activity CSV label on disk)
    -> {lowercase full name: name}. The former-staff side of the line checks (2026-10-21)."""
    if _KNOWN:
        return _KNOWN
    import glob
    names = []
    try:
        names += [u.get("name") or "" for u in json.load(open(vp_people.BRAVO_USERS_PATH)).get("users", [])]
    except (OSError, ValueError):
        pass
    out_dir = os.path.join(L.PROJ, "Bravo Data Extraction", "output")
    for f in glob.glob(os.path.join(out_dir, "*employee-activity*.csv")):
        try:
            for ln in open(f, encoding="latin-1"):
                m = re.match(r"^[A-Z0-9]+ - ([^,]+)", ln)
                if m:
                    names.append(m.group(1).strip())
        except OSError:
            pass
    for n in names:
        if len(n.split()) >= 2:
            _KNOWN[" ".join(n.lower().split())] = n
    return _KNOWN


def former_named(ln):
    """A known person (ever in Bravo) named in this line who is not reportable now, else None."""
    low = " ".join(ln.lower().split())
    for k, n in known_people().items():
        if k in low and not vp_people.is_reportable(n):
            return n
    return None


def scrub_people(text, source):
    """2026-10-21 fleet-wide rule: drop any line that names a Davis or a person who is not current staff
    (bin/vp_people.py). Dropped names go to vp_people's local log only, never into the page."""
    out, dropped = [], []
    for ln in text.split("\n"):
        if vp_people.mentions_davis(ln):
            dropped.append((ln[:60], "Davis family")); continue
        if re.search(r"(?i)[*_]\s*(free1|system system|backup backup|approval sandi)", ln):
            dropped.append((ln[:60], "shared / service login")); continue
        bad = former_named(ln)
        for n in ([] if bad else [a or b for a, b in _NAME_RX.findall(ln)]):
            if n.upper().startswith(vp_people.SERVICE_PREFIXES):
                bad = n; break
            if n in _NOT_NAMES or n.split()[0] in L.NAMES.values() or n.split()[-1] in L.NAMES.values():
                continue
            if vp_people.resolve(n) is None and vp_people.is_davis(n) is False and _looks_person(n):
                bad = n; break
        if bad:
            dropped.append((bad, vp_people.reason(bad) or "not current")); continue
        out.append(ln)
    vp_people._log(source, dropped)
    return "\n".join(out)


def _looks_person(n):
    """Only treat 'First Last' as a person when it is shaped like the ranked lines (2-3 words, no digits/$)."""
    w = n.split()
    if set(w) & _METRIC_WORDS:
        return False
    return 2 <= len(w) <= 3 and not any(c.isdigit() for c in n) and all(x[:1].isupper() for x in w)


def harvest(period):
    _, first, last, label = L.months(period)
    month = label.split()[0]
    lo, hi = L.ts_of(last - dt.timedelta(days=3)), L.ts_of(last + dt.timedelta(days=4), end=True)
    posts, seen = [], []
    for ch, name in HARVEST.items():
        try:
            msgs = L.history(ch, lo, hi)
        except RuntimeError:
            continue
        keep = [m for m in msgs if month in L.text_of(m) or "Month in Review" in L.text_of(m)]
        if name in ("loan-review", "layaway-review", "aged-inventory-review", "daily-funds-reconcilation", "google-reviews") and not keep:
            keep = msgs[-2:]
        for m in keep:
            t = scrub_people(L.text_of(m).strip(), TASK).strip()
            if t:
                posts.append("[#%s %s] %s" % (name, dt.datetime.fromtimestamp(float(m["ts"]), L.ET).date(), t[:3500]))
                seen.append(name)
    return posts, sorted(set(seen))


PEOPLE_NOT_TRACKED = "• Hires / separations: not tracked yet"
_PEOPLE_NUM = re.compile(r"\b(hire|hired|hires|hiring|separation|separations|left|quit|terminat|departure|roster|headcount|on staff)", re.I)


def people_not_tracked(body):
    """2026-10-20 (Joshua): with no reliable hires/separations source on the Mac (Gusto people file absent), the PEOPLE block
    says "not tracked yet" instead of a number. Deterministic: drops any model bullet about hires/separations/roster counts
    that carries a digit, puts the fixed line first, keeps the 3-bullet cap."""
    lines = body.split("\n")
    try:
        i = next(k for k, ln in enumerate(lines) if "PEOPLE" in ln and ln.strip().startswith(":busts_in_silhouette:"))
    except StopIteration:
        return body
    j = i + 1
    while j < len(lines) and lines[j].strip().startswith("•"):
        j += 1
    keep = [ln for ln in lines[i + 1:j] if not (_PEOPLE_NUM.search(ln) and re.search(r"\d", ln))][:2]
    return "\n".join(lines[:i + 1] + [PEOPLE_NOT_TRACKED] + keep + lines[j:])


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    render = "--render" in sys.argv
    period = args[0] if args else L.prev_month()
    _, first, last, label = L.months(period)
    marker = "VALLEY PAWN — %s" % label.upper()
    if not render and L.already(CH, marker, 24 * 25):
        print("already posted:", marker)
        return 0
    wf = os.path.join(L.OS_DIR, "monthly-analytics", "%s Monthly Analytics.md" % period)
    if not os.path.exists(wf):
        L.ledger(TASK, "the %s CEO scorecard waited on the month's analytics, which are not in yet" % label) if not render else None
        print("HOLD: no working file", wf)
        return 3
    t = tables(open(wf).read())
    need = ("same-month-current", "same-month-prior", "ytd-current", "ytd-prior", "t12m-current", "t12m-prior")
    if any(w not in t or any(s not in t[w] for s in ORDER + ["GT"]) for w in need):
        L.ledger(TASK, "the %s CEO scorecard was held: the month's analytics are missing a store" % label) if not render else None
        print("HOLD: Gate E")
        return 3
    pm = (first - dt.timedelta(days=1)).strftime("%Y-%m")
    hist = json.load(open(HISTORY)) if os.path.exists(HISTORY) else {}
    prev = {s: v["net_revenue"] for s, v in (hist.get(pm) or {}).items()} or None
    head, facts, ranked = header(period, t, prev)
    pfile = os.path.join(CEO, "data", "eom", "%s_people.json" % period)
    people = json.load(open(pfile)) if os.path.exists(pfile) else None
    people_txt = json.dumps(people) if people else ("NOT AVAILABLE — do NOT state any hire, separation or roster count. Use only "
                                                   "hours / staffing facts from the posts for PEOPLE, at most 2 bullets (a fixed "
                                                   "first bullet is added in code).")
    lm = os.path.join(CEO, "LAST_MONTH.json")
    lmj = json.load(open(lm)) if os.path.exists(lm) else {}
    decisions = lmj.get("decisions") if lmj.get("month") == pm else lmj.get("prior_month_decisions") or lmj.get("decisions")
    try:
        posts, sources = harvest(period)
    except vp_people.RosterHold as e:
        L.ledger(TASK, "the %s CEO scorecard was held: the current-staff list could not be read (%s)" % (label, e)) if not render else None
        print("HOLD: roster", e)
        return 3
    body = L.ask(PROMPT.format(label=label, ref=open(REF).read(), head=head, facts=json.dumps(facts), people=people_txt,
                               decisions=json.dumps(decisions), posts="\n\n".join(posts)[:110000]), system=SYSTEM, max_tokens=9000).strip()
    if not people:
        body = people_not_tracked(body)
    body = "\n".join(ln for ln in body.split("\n") if not vp_people.mentions_davis(ln))   # never a Davis (2026-10-21)
    text = head + "\n\n" + body
    bad = [b for b in L.field_clean(text) if b not in ("sync",)]
    if bad:
        print("Rule 16 terms in draft:", bad)
    ok = L.post(TASK, CH, text, render)
    status = ["# STATUS — CEO Monthly Scorecard, %s (native%s)" % (label, " render" if render else ""),
              "Run: %s · %s" % (L.now().strftime("%Y-%m-%d %H:%M ET"), "rendered to fleet/test_output" if render else ("posted to #ceo-briefs" if ok is True else ("DRY RUN — diverted, not posted" if ok else "post FAILED"))),
              "", "## Sources harvested", ", ".join("#" + s for s in sources), "Working file: %s" % os.path.basename(wf),
              "MoM base: Bonus Program/data/history.json %s" % pm, "", "## Gates",
              "- A: weekly scorecard not read. B: enforced in the prompt. E: all five stores present in the working file.",
              "- C: %s" % ("Gusto people file used: " + os.path.basename(pfile) if people else "NO Gusto people file — PEOPLE line says 'Hires / separations: not tracked yet'"),
              "- D: not run — the ops bot cannot read Joshua's DM.", "- Rule 16 terms flagged: %s" % (bad or "none")]
    out_dir = L.TEST_OUT if render else CEO
    open(os.path.join(out_dir, "STATUS-%s%s.md" % (period, "-native-render" if render else "")), "w").write("\n".join(status) + "\n")
    page = "<!doctype html><html><head><meta charset='utf-8'><title>Valley Pawn — %s</title><style>@page{size:letter;margin:.5in}" \
           "body{font:11px/1.35 -apple-system,Helvetica,Arial,sans-serif;color:#111;white-space:pre-wrap}</style></head><body>%s</body></html>" % (
               html.escape(label), html.escape(re.sub(r":[a-z_]+: ?", "", text)))
    open(os.path.join(out_dir, "MONTH-%s%s.html" % (period, "-native-render" if render else "")), "w").write(page)
    if ok is True and not render:   # a guard-diverted post never overwrites the carry-forward
        json.dump({"month": period, "generated": L.now().date().isoformat(), "note": "native carry-forward", "company": facts["company"],
                   "stores": [{"rank": i + 1, "store": L.NAMES[s], "net_revenue": facts["stores"][s]["net"]} for i, s in enumerate(ranked)],
                   "decisions": [], "prior_month_decisions": decisions, "page_text": text}, open(lm, "w"), indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
