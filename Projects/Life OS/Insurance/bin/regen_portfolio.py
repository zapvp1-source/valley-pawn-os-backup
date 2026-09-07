#!/usr/bin/env python3
"""Regenerate INSURANCE_PORTFOLIO.md from INSURANCE_REGISTRY.json.

The portfolio file is a VIEW. Never hand-edit it — edit the registry and re-run:
    python3 "Life OS/Insurance/bin/regen_portfolio.py"
"""
import json
import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REG = HERE / "INSURANCE_REGISTRY.json"
OUT = HERE / "INSURANCE_PORTFOLIO.md"

DOMAIN_ORDER = ["1", "2", "3"]
DOMAIN_TITLES = {
    "1": "DOMAIN 1 — Full Circle Finance Inc DBA Valley Pawn",
    "2": "DOMAIN 2 — Real Estate",
    "3": "DOMAIN 3 — Personal",
}


def money(v):
    if v is None:
        return "—"
    if isinstance(v, (int, float)):
        return f"${v:,.0f}" if float(v).is_integer() else f"${v:,.2f}"
    return str(v)


def flat(d, indent="  "):
    """Render a dict of limits/deductibles as bullet lines."""
    lines = []
    for k, v in (d or {}).items():
        label = k.replace("_", " ")
        if isinstance(v, dict):
            inner = "; ".join(f"{ik.replace('_',' ')} {money(iv) if isinstance(iv,(int,float)) else iv}"
                              for ik, iv in v.items())
            lines.append(f"{indent}- **{label}:** {inner}")
        elif isinstance(v, list):
            lines.append(f"{indent}- **{label}:** {', '.join(str(x) for x in v)}")
        else:
            lines.append(f"{indent}- **{label}:** {money(v) if isinstance(v,(int,float)) else v}")
    return lines


def main():
    reg = json.loads(REG.read_text())
    meta = reg.get("meta", {})
    pols = reg["policies"]
    today = datetime.date.today().isoformat()

    L = []
    A = L.append
    A("# Insurance Portfolio — All Domains")
    A("")
    A(f"**GENERATED {today} from `INSURANCE_REGISTRY.json` — do not hand-edit.**")
    A("Update the registry, then run `Life OS/Insurance/bin/regen_portfolio.py`.")
    A("Ownership authority: `Life OS/ENTITY_STRUCTURE.md`. Claims: `CLAIMS.md`. Broker history: `BROKER_PIPELINE.md`.")
    A("")

    # Renewal calendar
    A("## RENEWAL CALENDAR (next 18 months)")
    A("")
    A("| Date | Line | Entity | Carrier | Policy # | Premium |")
    A("|---|---|---|---|---|---|")
    dated = [p for p in pols if p.get("renewal_date")]
    for p in sorted(dated, key=lambda x: str(x["renewal_date"])):
        A(f"| {p['renewal_date']} | {p['line'].split(' - ')[0][:60]} | {p.get('entity_named_insured') or '—'} "
          f"| {p.get('carrier') or '—'} | {p.get('policy_number') or '—'} | {money(p.get('premium_annual'))} |")
    A("")

    # Open exposures
    A("## OPEN COVERAGE ISSUES (every open_issue in the registry)")
    A("")
    for p in pols:
        issues = p.get("open_issues") or []
        if not issues:
            continue
        A(f"**{p['id']} — {p['line'].split(' - ')[0][:70]}**")
        A("")
        for i in issues:
            A(f"- {i}")
        A("")

    # Per-domain detail
    for dk in DOMAIN_ORDER:
        group = [p for p in pols if str(p.get("domain", "")).strip().startswith(dk)]
        if not group:
            continue
        A(f"## {DOMAIN_TITLES[dk]}")
        A("")
        for p in group:
            A(f"### {p['id']} — {p['line']}")
            A("")
            A(f"- **Named insured (entity):** {p.get('entity_named_insured') or '—'}")
            if p.get("named_insured_on_policy"):
                A(f"- **Named insured (as written on policy):** {p['named_insured_on_policy']}")
            A(f"- **Scope:** {p.get('insured_property_or_scope') or '—'}")
            A(f"- **Carrier:** {p.get('carrier') or '—'}"
              + (f" · **Program/MGA:** {p['program_or_mga']}" if p.get("program_or_mga") else ""))
            A(f"- **Broker:** {p.get('broker') or '—'}"
              + (f" · {p['broker_contact']}" if p.get("broker_contact") else ""))
            A(f"- **Policy #:** {p.get('policy_number') or '—'} · **Term:** "
              f"{p.get('term_start') or '?'} → {p.get('term_end') or '?'} · **Renews:** {p.get('renewal_date') or '—'}")
            A(f"- **Premium:** {money(p.get('premium_annual'))}"
              + (f" — {p['premium_notes']}" if p.get("premium_notes") else ""))
            if p.get("payment_method"):
                A(f"- **Payment:** {p['payment_method']}")
            if p.get("key_limits"):
                A("- **Key limits:**")
                L.extend(flat(p["key_limits"], "  "))
            if p.get("deductibles"):
                A("- **Deductibles:**")
                L.extend(flat(p["deductibles"], "  "))
            for m in (p.get("mortgagee_or_AI") or []):
                A(f"- **{m.get('role','Interest')}:** {m.get('name')}")
            A(f"- **Status:** {p.get('status') or '—'}")
            if p.get("documents"):
                A("- **Documents:** " + " · ".join(p["documents"]))
            A(f"- **Last verified:** {p.get('last_verified') or '—'} — source: {p.get('source') or '—'}")
            A("")

    if meta.get("not_reachable_this_pass"):
        A("## KNOWN DATA GAPS (sources not reachable at last build)")
        A("")
        for g in meta["not_reachable_this_pass"]:
            A(f"- {g}")
        A("")

    OUT.write_text("\n".join(L) + "\n")
    print(f"wrote {OUT} ({len(L)} lines, {len(pols)} policies)")


if __name__ == "__main__":
    main()
