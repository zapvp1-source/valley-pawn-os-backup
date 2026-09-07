#!/usr/bin/env python3
"""
render_calendar.py — OBLIGATIONS.json -> COMPLIANCE_CALENDAR.md (+ horizon JSON for the weekly brief)

stdlib only. Never hand-edit COMPLIANCE_CALENDAR.md; edit OBLIGATIONS.json and re-run.

Usage:
  python3 render_calendar.py                 # writes COMPLIANCE_CALENDAR.md and state/horizon.json
  python3 render_calendar.py --horizon 120   # also prints the due-inside-N-days list (for the brief)
  python3 render_calendar.py --check         # exit 2 if any row is past-due or has status/evidence mismatch

Exit codes: 0 ok · 2 = register has past-due rows or integrity problems (used by compliance-weekly-brief)
"""
import json, sys, os, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # Projects/Compliance
REG = os.path.join(ROOT, "OBLIGATIONS.json")
OUT = os.path.join(ROOT, "COMPLIANCE_CALENDAR.md")
STATE = os.path.join(ROOT, "state")
TODAY = dt.date.today()

STATUS_ICON = {"current": "✅", "due": "🟡", "past-due": "🔴", "unknown": "⚪", "in-progress": "🔵", "blocked": "⛔", "closed": "➖"}
STORE_LABEL = {"culpeper": "Culpeper", "waynesboro": "Waynesboro", "harrisonburg": "Harrisonburg", "lexington": "Lexington", "roanoke": "Roanoke", "all": "All stores", "entity": "Entity"}


def load():
    with open(REG) as f:
        return json.load(f)


def parse(d):
    return dt.date.fromisoformat(d) if d else None


def days_to(d):
    return (parse(d) - TODAY).days if d else None


def effective_status(row):
    """Derive the display status: a 'current' row whose date has passed is past-due regardless of what the file says."""
    s = row.get("status", "unknown")
    dd = days_to(row.get("due"))
    if dd is not None and dd < 0 and s not in ("closed", "in-progress", "blocked"):
        return "past-due"
    if dd is not None and s == "current" and dd <= row.get("lead_days", 30):
        return "due"
    return s


def integrity_problems(row):
    probs = []
    if row.get("status") == "current" and not row.get("evidence"):
        probs.append("marked current with no evidence")
    if row.get("status") == "current" and not row.get("last_verified"):
        probs.append("marked current but never verified")
    return probs


def render(data):
    rows = data["obligations"]
    for r in rows:
        r["_status"] = effective_status(r)
        r["_days"] = days_to(r.get("due"))
        r["_probs"] = integrity_problems(r)

    dated = sorted([r for r in rows if r.get("due")], key=lambda r: r["due"])
    undated = [r for r in rows if not r.get("due")]
    past = [r for r in dated if r["_days"] < 0 and r["_status"] == "past-due"]
    h30 = [r for r in dated if 0 <= r["_days"] <= 30]
    h120 = [r for r in dated if 30 < r["_days"] <= 120]
    later = [r for r in dated if r["_days"] > 120]
    joshua = [r for r in rows if r.get("owner") == "joshua" and r["_status"] in ("due", "past-due", "blocked")]
    unknown = [r for r in rows if r["_status"] == "unknown"]
    probs = [(r["id"], p) for r in rows for p in r["_probs"]]

    def line(r):
        d = f"{r['due']} ({r['_days']:+d}d)" if r.get("due") else "no date"
        return f"| {STATUS_ICON.get(r['_status'], '?')} {r['_status']} | {d} | {STORE_LABEL.get(r.get('store'), r.get('store'))} | **{r['id']}** — {r.get('authority', '')} | {r.get('owner', '')} | {r.get('next_step', '')} |"

    hdr = "| Status | Due | Store | Obligation | Owner | Next step |\n|---|---|---|---|---|---|"

    out = []
    out.append("# COMPLIANCE CALENDAR — Full Circle Finance Inc DBA Valley Pawn")
    out.append(f"\n**Rendered {TODAY.isoformat()} from `OBLIGATIONS.json` by `bin/render_calendar.py`. Do not hand-edit — edit the register and re-render.**\n")
    out.append(f"Rows: {len(rows)} · 🔴 past-due {len(past)} · 🟡 due ≤30d {len(h30)} · ≤120d {len(h120)} · ⚪ unknown {len(unknown)} · integrity problems {len(probs)}\n")

    out.append("## 🔴 PAST DUE\n")
    out.append(hdr); out.extend(line(r) for r in past) if past else out.append("| — | — | — | none | — | — |")
    out.append("\n## 🟡 DUE IN THE NEXT 30 DAYS\n")
    out.append(hdr); out.extend(line(r) for r in h30) if h30 else out.append("| — | — | — | none | — | — |")
    out.append("\n## DUE IN 31–120 DAYS\n")
    out.append(hdr); out.extend(line(r) for r in h120) if h120 else out.append("| — | — | — | none | — | — |")
    out.append("\n## LATER\n")
    out.append(hdr); out.extend(line(r) for r in later)
    out.append("\n## ⚪ UNKNOWN STATUS — needs discovery (no evidence on disk)\n")
    out.append(hdr); out.extend(line(r) for r in unknown)
    out.append("\n## CONTINUOUS / UNDATED CONTROLS\n")
    out.append(hdr); out.extend(line(r) for r in undated)
    out.append("\n## STAGED FOR JOSHUA (money, signature, filing, or decision)\n")
    out.append(hdr); out.extend(line(r) for r in sorted(joshua, key=lambda r: r.get("due") or "9999"))
    if probs:
        out.append("\n## INTEGRITY PROBLEMS (status says one thing, evidence says another)\n")
        out.extend(f"- `{i}`: {p}" for i, p in probs)

    out.append("\n## By class\n")
    by = {}
    for r in rows:
        by.setdefault(r.get("class", "?"), []).append(r)
    for c in sorted(by):
        out.append(f"\n### {c} ({len(by[c])})\n")
        out.append(hdr)
        out.extend(line(r) for r in sorted(by[c], key=lambda r: r.get("due") or "9999"))

    out.append("\n---\n*Legend: ✅ current (evidence on disk, verified) · 🟡 due inside lead window · 🔴 past due · ⚪ unknown (never verified) · 🔵 in progress · ⛔ blocked on a Joshua touch.*\n")

    horizon = {
        "rendered": TODAY.isoformat(),
        "past_due": [r["id"] for r in past],
        "due_30": [r["id"] for r in h30],
        "due_120": [r["id"] for r in h120],
        "unknown": [r["id"] for r in unknown],
        "joshua_items": [{"id": r["id"], "due": r.get("due"), "next_step": r.get("next_step")} for r in joshua],
        "integrity_problems": probs,
    }
    return "\n".join(out) + "\n", horizon


def main():
    data = load()
    md, horizon = render(data)
    os.makedirs(STATE, exist_ok=True)
    with open(OUT, "w") as f:
        f.write(md)
    with open(os.path.join(STATE, "horizon.json"), "w") as f:
        json.dump(horizon, f, indent=2)
    if "--horizon" in sys.argv:
        print(json.dumps(horizon, indent=2))
    bad = horizon["past_due"] or horizon["integrity_problems"]
    print(f"rendered {OUT}: past_due={len(horizon['past_due'])} due_30={len(horizon['due_30'])} unknown={len(horizon['unknown'])} problems={len(horizon['integrity_problems'])}")
    if "--check" in sys.argv and bad:
        sys.exit(2)


if __name__ == "__main__":
    main()
