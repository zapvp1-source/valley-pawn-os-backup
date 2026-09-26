#!/usr/bin/env python3
"""email_analytics_weekly.py — native replacement for the Cowork task `email-analytics-weekly`
(Friday 03:30 ET). Same six steps as the SKILL, same sheet, same 5-line post, no Claude session.

WHY (2026-09-25): the Cowork run failed 9/25 because its every step is Python executed through the
Control_your_Mac connector, which does not exist in scheduled sessions. The Python was always the
real work (Scheduled/_shared/brevo_helper.py + sheets_helper.py); this just runs it directly.

Steps (from the SKILL, incl. the 2026-08-21 correction: north star = calls+texts per 1,000):
  1 pull sent campaigns from Brevo    2 diff vs the master sheet (NEW / STALE<=14d / FROZEN)
  3 per-link UTM bucketing            4 upsert rows (atomic; helper raises -> nothing written)
  5 trends: this send vs trailing-4 weekly avg   6 post exactly 5 lines to #email-campiagns
Guardrails kept: never lead with open rate; flag a metric only after 2+ bad weeks; tel:/sms: clicks
come only from the /c and /t redirect buckets; runtime is seconds.

  email_analytics_weekly.py            run (writes sheet, posts Slack)
  email_analytics_weekly.py --render   read Brevo + sheet, print the rows and the post, write nothing
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.expanduser("~/Documents/Claude/Scheduled/_shared"))

AGENT = "email-analytics-weekly"
OS_DIR = os.environ.get("VP_OS_DIR") or os.path.expanduser("~/Documents/Claude/Projects/Valley Pawn OS")
BIN = os.path.join(OS_DIR, "bin")
SHEET = "1EPj22S1zzbSm4B_mRZ4y8TEXXpiCj6YM_75TmVV4d2o"
TAB = "Email Campaign Performance"
CHANNEL = "C0APR5WUL2Z"   # #email-campiagns (sic — the channel really is spelled that way)
SHEET_URL = "https://docs.google.com/spreadsheets/d/%s" % SHEET
STATE = os.path.join(OS_DIR, "fleet", "email_analytics_state.json")
LEDGER = os.path.join(OS_DIR, "fleet", "FAILURE_LEDGER.md")
HEADERS = ["campaign_id", "send_date", "send_dow", "send_time", "campaign_name", "category", "theme",
           "recipients", "opens", "open_pct", "clicks", "click_pct", "unsubs", "unsub_pct", "clicks_per_1k",
           "calls_clicks", "texts_clicks", "directions_clicks", "primary_cta_clicks", "calls_texts_per_1k",
           "last_synced_at", "notes"]
EPOCH = dt.date(1899, 12, 30)   # Google Sheets serial-date origin (the sheet stores dates as serials)


def pct(a, b):
    return round(100.0 * a / b, 3) if b else 0


def per_1k(a, b):
    return round(1000.0 * a / b, 3) if b else 0


def parse_sent(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def serial(d):
    return (d.date() - EPOCH).days


def categorize(name):
    m = re.match(r"\s*(W\d+)\b", name)
    if m:
        return m.group(1), re.sub(r"^\s*W\d+\s*[—-]\s*", "", name).split(" — ")[0].strip()
    if "We Buy Gold" in name or "[Master" in name:
        return "Monthly", re.sub(r"^Valley Pawn\s*[—-]\s*", "", name).strip()
    if "Spotlight" in name:
        return "Weekly", "Store Spotlight"
    if "Giveaway" in name:
        return "Giveaway", name.split(" — ")[0].strip()
    return "Other", name.split(" — ")[0].strip()


def sheet_date(v):
    """send_date cell -> date. Serial number, ISO string, or blank."""
    try:
        f = float(v)
        return EPOCH + dt.timedelta(days=int(f))
    except (TypeError, ValueError):
        pass
    try:
        return dt.date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def build_row(b, c, existing):
    cid = int(c["id"])
    full = b.get_email_campaign(cid)
    stats = (full.get("statistics") or {}).get("campaignStats") or []
    tot = {}
    for st in stats:
        for k in ("sent", "delivered", "uniqueViews", "uniqueClicks", "unsubscriptions"):
            tot[k] = tot.get(k, 0) + int(st.get(k) or 0)
    buckets = b.utm_content_bucketed_clicks(cid) or {}
    calls = sum(v for k, v in buckets.items() if k.endswith("_call"))
    texts = sum(v for k, v in buckets.items() if k.endswith("_text"))
    dirs = sum(v for k, v in buckets.items() if k.endswith("_map"))
    cta = int(buckets.get("primary_cta", 0))
    sent_at = parse_sent(c["sentDate"])
    rec = tot.get("sent", 0)
    old = existing.get(cid, {})
    cat, theme = categorize(c.get("name", ""))
    row = {
        "campaign_id": cid,
        "send_date": old.get("send_date") or serial(sent_at),
        "send_dow": old.get("send_dow") or sent_at.strftime("%a"),
        "send_time": old.get("send_time") if old.get("send_time") not in (None, "") else round(
            (sent_at.hour * 3600 + sent_at.minute * 60) / 86400.0, 6),
        "campaign_name": c.get("name", ""),
        "category": old.get("category") or cat,
        "theme": old.get("theme") or theme,
        "recipients": rec,
        "opens": tot.get("uniqueViews", 0), "open_pct": pct(tot.get("uniqueViews", 0), rec),
        "clicks": tot.get("uniqueClicks", 0), "click_pct": pct(tot.get("uniqueClicks", 0), rec),
        "unsubs": tot.get("unsubscriptions", 0), "unsub_pct": pct(tot.get("unsubscriptions", 0), rec),
        "clicks_per_1k": per_1k(tot.get("uniqueClicks", 0), rec),
        "calls_clicks": calls, "texts_clicks": texts, "directions_clicks": dirs, "primary_cta_clicks": cta,
        "calls_texts_per_1k": per_1k(calls + texts, rec),
        "last_synced_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "notes": old.get("notes") or "",
    }
    return row, sent_at


def weekly_rows(rows):
    out = []
    for r in rows:
        cat = str(r.get("category", ""))
        if not (cat.startswith("W") or cat == "Weekly"):
            continue
        d = sheet_date(r.get("send_date"))
        if not d:
            continue
        try:
            out.append((d, r))
        except Exception:
            pass
    out.sort(key=lambda x: x[0], reverse=True)
    return out


def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def arrow(cur, avg, higher_good=True):
    if avg == 0:
        return "→"
    ch = (cur - avg) / avg
    if abs(ch) <= 0.05:
        return "→"
    good = ch > 0 if higher_good else ch < 0
    return "↑" if good else "↓"


def compose(rows, today):
    wk = weekly_rows(rows)
    week_of = (today - dt.timedelta(days=today.weekday())).isoformat()
    head = ":bar_chart: Email — Week of %s" % week_of
    if not wk:
        return None, "no weekly rows"
    d0, r0 = wk[0]
    trail = [r for _, r in wk[1:5]]
    def avg(k):
        vals = [fnum(r.get(k)) for r in trail]
        return sum(vals) / len(vals) if vals else 0.0
    ct, ct_avg = fnum(r0.get("calls_texts_per_1k")), avg("calls_texts_per_1k")
    di, di_avg = fnum(r0.get("directions_clicks")), avg("directions_clicks")
    cta, cta_avg = fnum(r0.get("primary_cta_clicks")), avg("primary_cta_clicks")
    un, un_avg = fnum(r0.get("unsub_pct")), avg("unsub_pct")
    age = (today - d0).days
    lines = [head]
    if age > 8:
        lines.append("Lead movement: no weekly send since %s (%d days) — the cadence is the story this week." % (d0.isoformat(), age))
    else:
        deltas = [("calls+texts per 1,000", ct, ct_avg, True), ("directions clicks", di, di_avg, True),
                  ("unsubscribe rate", un, un_avg, False)]
        name, cur, av, hg = max(deltas, key=lambda x: abs(x[1] - x[2]) / (x[2] or 1))
        lines.append("Lead movement: %s %s — %s vs trailing avg %s (%s, %s)" % (
            name, arrow(cur, av, hg), fmt(cur), fmt(av), r0.get("theme") or r0.get("category"), d0.isoformat()))
    lines.append("Calls+texts per 1,000: %s (avg %s) %s" % (fmt(ct), fmt(ct_avg), arrow(ct, ct_avg)))
    # KPI #2/#3: unsub only if it breached 0.5% twice; otherwise directions
    breach = [fnum(r.get("unsub_pct")) >= 0.5 for _, r in wk[:2]]
    if len(breach) == 2 and all(breach):
        lines.append("Unsubscribe rate: %.2f%% — above the 0.5%% red line two sends running" % un)
    else:
        lines.append("Directions clicks: %s (avg %s) %s" % (fmt(di), fmt(di_avg), arrow(di, di_avg)))
    # recommendation: the best-performing theme over the trailing 8 weekly sends, tied to numbers
    pool = [(fnum(r.get("calls_texts_per_1k")), r.get("theme") or r.get("category")) for _, r in wk[:8]]
    if age > 8:
        best = max(pool) if pool else (0, "Store Spotlight")
        rec = "Resume the weekly send — %s has been the strongest theme (%s calls+texts per 1,000)." % (best[1], fmt(best[0]))
    else:
        by_theme = {}
        for v, t in pool:
            by_theme.setdefault(t, []).append(v)
        ranked = sorted(((sum(v) / len(v), t) for t, v in by_theme.items()), reverse=True)
        if ranked and ranked[0][1] != (r0.get("theme") or r0.get("category")) and ranked[0][0] > ct:
            rec = "Next send: go back to %s — it averages %s calls+texts per 1,000 vs %s for this week's %s." % (
                ranked[0][1], fmt(ranked[0][0]), fmt(ct), r0.get("theme") or r0.get("category"))
        elif ct >= ct_avg:
            rec = "Keep %s in rotation — it is holding at or above the trailing average; test one stronger call-to-action line next." % (r0.get("theme") or r0.get("category"))
        else:
            rec = "This week's %s came in under the trailing average — alternate back to the best theme next send rather than repeating it." % (r0.get("theme") or r0.get("category"))
    lines.append("Recommendation for next send: " + rec)
    lines.append(":link: " + SHEET_URL)
    return "\n".join(lines), None


def fmt(v):
    return ("%.1f" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)


def ledger(sentence):
    row = "| %s (native) | %s | %s | NEEDS_HUMAN: no | OPEN |\n" % (
        dt.datetime.now().strftime("%Y-%m-%d %H:%M ET"), AGENT, sentence)
    try:
        open(LEDGER, "a").write(row)
    except OSError:
        pass


def main():
    render = "--render" in sys.argv
    from brevo_helper import BrevoClient
    from sheets_helper import SheetsClient
    today = dt.date.today()
    b, s = BrevoClient(), SheetsClient()
    try:
        sent = b.list_email_campaigns(status="sent")
        rows = s.read_as_dicts(SHEET, TAB)
    except Exception as e:
        print("read failed:", type(e).__name__, str(e)[:200])
        if not render:
            ledger("The weekly email analytics could not read Brevo or the master sheet (%s)." % type(e).__name__)
        return 1
    existing = {}
    for r in rows:
        try:
            existing[int(float(r.get("campaign_id")))] = r
        except (TypeError, ValueError):
            pass
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=14)
    todo = []
    for c in sent:
        try:
            cid, when = int(c["id"]), parse_sent(c["sentDate"])
        except (KeyError, ValueError, TypeError):
            continue
        if cid not in existing:
            todo.append(("NEW", c))
        elif when >= cutoff:
            todo.append(("STALE", c))
    upserts = []
    for kind, c in todo:
        row, _ = build_row(b, c, existing)
        upserts.append(row)
        print("%-5s %s %s recipients=%s calls+texts/1k=%s" % (kind, row["campaign_id"], row["campaign_name"][:50],
                                                             row["recipients"], row["calls_texts_per_1k"]))
    merged = {int(float(r["campaign_id"])): dict(r) for r in rows if str(r.get("campaign_id", "")).strip()}
    for u in upserts:
        merged[u["campaign_id"]] = u
    post, why = compose(list(merged.values()), today)
    if render:
        print("=== RENDER ONLY — %d row(s) would be upserted ===" % len(upserts))
        print(post or ("(no post: %s)" % why))
        return 0
    if upserts:
        try:
            res = s.upsert_by_key(SHEET, TAB, "campaign_id", [{h: u.get(h, "") for h in HEADERS} for u in upserts])
            print("sheet:", res)
        except Exception as e:
            print("upsert failed:", type(e).__name__, str(e)[:200])
            ledger("The weekly email analytics could not update the master sheet (%s); nothing was written." % type(e).__name__)
            return 1
    if not post:
        ledger("The weekly email analytics had no weekly campaign rows to summarize (%s)." % why)
        return 1
    env = dict(os.environ, VP_TASK=AGENT)
    p = subprocess.run(["/usr/bin/python3", os.path.join(BIN, "vp_slack.py"), "post", CHANNEL, post],
                       capture_output=True, text=True, timeout=60, env=env)
    if p.returncode != 0:
        err = (p.stderr or p.stdout).strip()
        print("post failed:", err[:200])
        if "guard" not in err.lower() and "dry" not in err.lower():
            ledger("The weekly email analytics summary was built but the Slack post did not go through.")
        return 1
    json.dump({"last_run": today.isoformat(), "upserted": len(upserts)}, open(STATE, "w"))
    print("posted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
