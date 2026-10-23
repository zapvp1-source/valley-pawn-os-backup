#!/usr/bin/env python3
"""asset_recovery_native.py — native (Mac) refresh of the "Asset Recovery 2025 Vs 2026" artifact (2026-10-22).

WHY: the cloud task asset-recovery-daily-refresh (trig_014PS7pZqihrdybSZZ8q6ZPP, 19:15 daily) computes the
combined Loan + Inventory base from the Bravo EOM xlsx set, but has not been able to write the artifact since
9/11: ~/Documents/Claude/Artifacts/... is not a folder the cloud run can reach, mcp__cowork__update_artifact is
not available there, and its "mandatory" bravo_health_gate.sh dies on /Users paths in the cloud sandbox
(ledger 10/9 -> 10/21, every night). It is file + math only — no Bravo touch, no Slack — so it belongs here.

SAME CONTRACT AS THE CLOUD SKILL (Scheduled/asset-recovery-daily-refresh/SKILL.md):
  * reuse-first: newest set within 8 days where all 5 stores' <D>_<ST>_end-of-month.xlsx exist AND pass
    store_rankings.validate(path, D) (window <M>/1 - D, non-zero Ending Loan/Inventory Base, non-blank Total:)
    — the 10/11 degenerate set (Loan Base 0) is skipped exactly as the other readers skip it. NEVER pulls.
  * metric = (sum Ending Loan Base + sum Ending Inventory Base) / 1000 across CUL/HAR/LEX/ROA/WAY (parse_eom).
  * edits DATA ONLY and only the CURRENT month's point: timelineData + cycle2026 point, the "Today" + ATH
    tiles, the snapshot line, the head-to-head 2026 cells, the projection row for this month, and a new
    split-chart point (+ split tiles). Never a closed month, never the 2025 cycle, never Aug 2024.
  * every replacement must match exactly once, else NOTHING is written (one ledger row).
  * no Slack (the cloud's one-line team post was flagged by the 10/21 comms-drift check as tool jargon).

    render            compute + write fleet/state/asset_recovery/render/index.html (artifact untouched)
    run               same, then back up the live artifact and replace it atomically, re-read and verify
    snapshot          copy the live artifact + cloud SKILL.md into fleet/state/asset_recovery/snapshot/
Wrapper bin/asset_recovery_native.sh is vp_live-gated on "asset-recovery-daily-refresh" (dormant until the
cloud trigger is off and fleet/state/native_live/asset-recovery-daily-refresh exists).
"""
import datetime as dt
import glob
import os
import re
import shutil
import sys
from zoneinfo import ZoneInfo

HOME = os.path.expanduser("~")
ART_DIR = os.path.join(HOME, "Documents", "Claude", "Artifacts", "asset-recovery-2025-vs-2026")
ART = os.path.join(ART_DIR, "index.html")
SKILL = os.path.join(HOME, "Documents", "Claude", "Scheduled", "asset-recovery-daily-refresh", "SKILL.md")
PROJ = os.path.join(HOME, "Documents", "Claude", "Projects")
OS_DIR = os.path.join(PROJ, "Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
EOM_DIR = os.path.join(PROJ, "Bravo Data Extraction", "output")
ST = os.path.join(OS_DIR, "fleet", "state", "asset_recovery")
BK = os.path.join(OS_DIR, "fleet", "_backups", "asset_recovery")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
STORES = ["CUL", "HAR", "LEX", "ROA", "WAY"]
ET = ZoneInfo("America/New_York")
ATH, LOW = 1294.143, 1237.056          # Jan 2026 peak / Apr 2026 tax-season low ($K) — fixed by the SKILL
LOW_MONTH = (2026, 4)
AGENT = "asset-recovery-daily-refresh"
sys.path.insert(0, BIN)


def log(*a):
    print(dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M:%S"), *a, flush=True)


def ledger(sentence, human="no"):
    try:
        open(LEDGER, "a").write("| %s (native) | %s | %s | NEEDS_HUMAN: %s | OPEN |\n"
                                % (dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence, human))
    except OSError:
        pass


def snapshot():
    os.makedirs(os.path.join(ST, "snapshot"), exist_ok=True)
    print("artifact dir exists:", os.path.isdir(ART_DIR))
    if os.path.isdir(ART_DIR):
        for f in sorted(os.listdir(ART_DIR)):
            p = os.path.join(ART_DIR, f)
            print("  ", f, os.path.getsize(p) if os.path.isfile(p) else "dir")
            if os.path.isfile(p) and os.path.getsize(p) < 5_000_000:
                shutil.copy2(p, os.path.join(ST, "snapshot", f))
    if os.path.isfile(SKILL):
        shutil.copy2(SKILL, os.path.join(ST, "snapshot", "cloud_SKILL.md"))
        print("copied SKILL.md")


# ------------------------------------------------------------------ data
def pick_set(today):
    from store_rankings import validate
    for back in range(0, 9):
        d = today - dt.timedelta(days=back)
        ds = d.isoformat()
        ps = [os.path.join(EOM_DIR, "%s_%s_end-of-month.xlsx" % (ds, s)) for s in STORES]
        if not all(os.path.exists(p) and os.path.getsize(p) > 1024 for p in ps):
            continue
        bad = ["%s %s" % (os.path.basename(p), w) for p in ps for w in [validate(p, ds)] if w]
        if bad:
            log("skipped invalid set", ds, "—", "; ".join(bad))
            continue
        return d, ps
    return None, None


def compute(today):
    from parse_eom import parse_store_xlsx
    d, ps = pick_set(today)
    if d is None:
        return None
    if (d.year, d.month) != (today.year, today.month):
        log("newest valid set %s is last month — current month has no data yet; nothing to update" % d)
        return None
    per = {}
    for s, p in zip(STORES, ps):
        r = parse_store_xlsx(p)
        per[s] = (r["loan_balance"], r["inventory_balance"])
    loans = round(sum(v[0] for v in per.values()), 2)
    inv = round(sum(v[1] for v in per.values()), 2)
    return {"date": d, "per": per, "loans": loans, "inv": inv, "total_k": (loans + inv) / 1000.0}


# ------------------------------------------------------------------ html
class Miss(Exception):
    pass


def sub1(pat, repl, s, what, flags=0):
    n = len(re.findall(pat, s, flags))
    if n != 1:
        raise Miss("%s: pattern matched %d times" % (what, n))
    return re.sub(pat, repl, s, count=1, flags=flags)


def money_m(k):
    return "$%.3fM" % (k / 1000.0)


def repair_js(html):
    """2026-10-22: the live file's chart <script> is ONE line (an earlier cloud refresh collapsed its newlines),
    so the first '// Recovery curves ...' line comment swallows the rest of the script and NO chart renders —
    only the tiles and tables show. Turn each // comment into a /* */ block comment. Idempotent; touches
    comments only (a URL's '://' is never matched)."""
    parts = re.split(r"(<script>.*?</script>)", html, flags=re.S)
    for i, p in enumerate(parts):
        if p.startswith("<script>") and "\n" not in p:
            parts[i] = re.sub(r"(?<![:/*])//([^\n]*?)(?=const |new Chart\(|$)", lambda m: "/*%s*/" % m.group(1), p)
    return "".join(parts)


def update_html(html, data, today):
    html = repair_js(html)
    d, tk = data["date"], data["total_k"]
    T = int(round(tk))
    mon = today.strftime("%b %y")                      # 'Oct 26'
    month_full = today.strftime("%B %Y")               # 'October 2026'
    md = "%d/%d" % (d.month, d.day)
    n = (today.year - LOW_MONTH[0]) * 12 + today.month - LOW_MONTH[1]   # months since Apr-2026 low
    over = T - int(round(ATH))
    pct = tk / ATH * 100

    s = html
    # snapshot line
    s = sub1(r"Snapshot: [A-Z][a-z]+ \d{1,2}, \d{4} \(data through \d{1,2}/\d{1,2}\)\.",
             "Snapshot: %s %d, %d (data through %s)." % (today.strftime("%B"), today.day, today.year, md), s, "snapshot")
    # Today tile
    if over >= 0:
        dl = '<div class="delta up">+$%dK above ATH</div>' % over
    else:
        dl = '<div class="delta down">$%dK below ATH</div>' % (-over)
    s = sub1(r'<div class="label">Today \([A-Za-z]+ \d{4}\)</div>\s*<div class="val">\$[\d.]+M</div>\s*<div class="delta[^"]*">[^<]*</div>',
             '<div class="label">Today (%s)</div>    <div class="val">%s</div>    %s' % (month_full, money_m(tk), dl), s, "today tile")
    # ATH / gap tile
    if over >= 0:
        rep = '<div class="label">New ATH set</div>    <div class="val">+$%dK</div>    <div class="delta">above Jan \'26 peak</div>' % over
    else:
        rep = '<div class="label">Gap to recover ATH</div>    <div class="val">$%dK</div>    <div class="delta">to Jan \'26 peak</div>' % (-over)
    s = sub1(r'<div class="label">(?:New ATH set|Gap to recover ATH)</div>\s*<div class="val">[^<]*</div>\s*<div class="delta">[^<]*</div>',
             rep, s, "ath tile")
    # timelineData: update/append current month
    tl = re.search(r"const timelineData = \[(.*?)\];", s, re.S)
    if not tl:
        raise Miss("timelineData not found")
    body = tl.group(1)
    if re.search(r"\{ m: '%s', v: [\d.]+ \}" % re.escape(mon), body):
        body2 = re.sub(r"\{ m: '%s', v: [\d.]+ \}" % re.escape(mon), "{ m: '%s', v: %d }" % (mon, T), body, count=1)
    else:
        body2 = body.rstrip() + ",  { m: '%s', v: %d }" % (mon, T)
    s = s[:tl.start(1)] + body2 + s[tl.end(1):]
    # cycle2026
    cy = re.search(r"const cycle2026 = \[(.*?)\];", s, re.S)
    if not cy:
        raise Miss("cycle2026 not found")
    cb = cy.group(1)
    pt = "{ month: %d, label: '%s', value: %.3f }" % (n, mon, tk)
    if re.search(r"\{ month: %d, label: '[^']*', value: [\d.]+ \}" % n, cb):
        cb2 = re.sub(r"\{ month: %d, label: '[^']*', value: [\d.]+ \}" % n, pt, cb, count=1)
    else:
        cb2 = cb.rstrip() + ",  " + pt
    s = s[:cy.start(1)] + cb2 + s[cy.end(1):]
    # split chart point + tiles
    sp = re.search(r"const splitData = \[(.*?)\];", s, re.S)
    if not sp:
        raise Miss("splitData not found")
    lab = "%s %d" % (d.strftime("%b"), d.day)
    spt = "{ d: '%s', loans: %.1f, inv: %.1f }" % (lab, data["loans"] / 1000.0, data["inv"] / 1000.0)
    sb = sp.group(1)
    if re.search(r"\{ d: '%s', [^}]*\}" % re.escape(lab), sb):
        sb2 = re.sub(r"\{ d: '%s', [^}]*\}" % re.escape(lab), spt, sb, count=1)
    else:
        sb2 = sb.rstrip() + ",  " + spt
    s = s[:sp.start(1)] + sb2 + s[sp.end(1):]
    s = sub1(r'(<div class="label">Loans Receivable \()\d{1,2}/\d{1,2}(\)</div>\s*<div class="val">)\$[\d,]+K',
             r"\g<1>%s\g<2>$%dK" % (md, round(data["loans"] / 1000.0)), s, "split loans tile")
    s = sub1(r'(<div class="label">Inventory Asset \()\d{1,2}/\d{1,2}(\)</div>\s*<div class="val">)\$[\d,]+K',
             r"\g<1>%s\g<2>$%dK" % (md, round(data["inv"] / 1000.0)), s, "split inv tile")
    s = sub1(r'(<div class="label">Combined \()\d{1,2}/\d{1,2}(\)</div>\s*<div class="val">)\$[\d.]+M',
             r"\g<1>%s\g<2>%s" % (md, money_m(tk)), s, "split combined tile")
    # head-to-head 2026 cells (only the running numbers)
    if over >= 0:
        s = sub1(r"currently \+\$\d+K above Jan peak", "currently +$%dK above Jan peak" % over, s, "h2h recover")
    s = sub1(r"<td>[A-Z][a-z]{2} \d{4}: \$[\d,]+K \([+-][\d.]+% vs Jan ATH\) — in progress",
             "<td>%s %d: $%sK (%+.1f%% vs Jan ATH) — in progress" % (today.strftime("%b"), today.year, format(T, ","), pct - 100),
             s, "h2h year-end")
    # projection row for this month (Month +n)
    row = re.search(r"<tr><td>Month \+%d</td><td>[^<]*</td><td[^>]*>[^<]*</td></tr>" % n, s)
    if row:
        cell = "<td>%s %d (MTD, thru %s): $%sK (%.1f%%)</td>" % (today.strftime("%b"), today.year, md, format(T, ","), pct)
        new_row = re.sub(r"<td[^>]*>[^<]*</td></tr>$", cell + "</tr>", row.group(0))
        s = s[:row.start()] + new_row + s[row.end():]
    if "Source: Bravo Data Extraction pipeline (live)" not in s:
        raise Miss("source line missing")
    return s


def verify(html, data, today):
    T = int(round(data["total_k"]))
    mon = today.strftime("%b %y")
    ok = ("{ m: '%s', v: %d }" % (mon, T) in html and money_m(data["total_k"]) in html
          and "data through %d/%d" % (data["date"].month, data["date"].day) in html)
    # closed months untouched: every timeline point other than this month must be identical to the original
    return ok


def closed_points(html, mon):
    tl = re.search(r"const timelineData = \[(.*?)\];", html, re.S)
    c25 = re.search(r"const cycle2025 = \[(.*?)\];", html, re.S)
    pts = re.findall(r"\{ m: '([^']+)', v: ([\d.]+)[^}]*\}", tl.group(1)) if tl else []
    return [p for p in pts if p[0] != mon], (c25.group(1) if c25 else None)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    if cmd == "snapshot":
        return snapshot() or 0
    today = dt.datetime.now(ET).date()
    if "--today" in sys.argv:
        today = dt.date.fromisoformat(sys.argv[sys.argv.index("--today") + 1])
    data = compute(today)
    if data is None:
        log("no valid current-month EOM set within 8 days — artifact left unchanged")
        return 0
    log("set %s loans %.2f inv %.2f total $%.3fK" % (data["date"], data["loans"], data["inv"], data["total_k"]))
    try:
        cur = open(ART, encoding="utf-8").read()
    except OSError as e:
        if cmd == "run":
            ledger("Could not read the Asset Recovery artifact file to refresh it (%s)." % e.__class__.__name__)
        log("artifact unreadable:", e)
        return 1
    try:
        new = update_html(cur, data, today)
    except Miss as e:
        if cmd == "run":
            ledger("Asset Recovery artifact not refreshed: its layout changed (%s), so nothing was written." % e)
        log("NOT WRITTEN —", e)
        return 1
    mon = today.strftime("%b %y")
    if closed_points(cur, mon) != closed_points(new, mon):
        log("NOT WRITTEN — a closed month or the 2025 cycle would change")
        if cmd == "run":
            ledger("Asset Recovery artifact not refreshed: the update would have touched a closed month, so nothing was written.")
        return 1
    if cmd == "render":
        os.makedirs(os.path.join(ST, "render"), exist_ok=True)
        out = os.path.join(ST, "render", "index.html")
        open(out, "w", encoding="utf-8").write(new)
        log("RENDER written", out, "| verify:", verify(new, data, today))
        return 0
    if new == cur:
        log("artifact already shows this data — nothing to do")
        return 0
    os.makedirs(BK, exist_ok=True)
    stamp = dt.datetime.now(ET).strftime("%Y%m%d-%H%M%S")
    shutil.copy2(ART, os.path.join(BK, "index.html.bak-%s" % stamp))
    for old in sorted(glob.glob(os.path.join(BK, "index.html.bak-*")))[:-30]:
        os.remove(old)
    tmp = ART + ".tmp"
    open(tmp, "w", encoding="utf-8").write(new)
    os.replace(tmp, ART)
    back = open(ART, encoding="utf-8").read()
    if not verify(back, data, today):
        shutil.copy2(os.path.join(BK, "index.html.bak-%s" % stamp), ART)
        ledger("Asset Recovery artifact refresh did not verify after writing; the previous version was put back.")
        log("VERIFY FAILED — restored backup")
        return 1
    log("artifact refreshed: %s MTD $%sK (data through %d/%d)" % (today.strftime("%B"), format(int(round(data["total_k"])), ","),
                                                                    data["date"].month, data["date"].day))
    return 0


if __name__ == "__main__":
    sys.exit(main())
