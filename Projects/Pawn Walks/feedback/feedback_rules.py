#!/usr/bin/env python3
"""
feedback_rules.py — apply what the stores taught us to today's valuations (hook for run_daily_intake.py).

Inputs (all written by feedback_ingest.py from #pawn-walks feedback, or hand-editable):
  manager_comps.json   model-key -> {value, date, by}      a value Preston/Joshua stated for that model
  item_overrides.json  "STORE|DESC|PAID" -> {...}           an item they cleared ("all good", half-back, qty)
  calibration.json     flag accuracy; category_tuning raises the bar for categories we keep getting wrong
  feedback_rules.json  knobs (allowances, keyword lists, expiry days)
Plus the Bravo intake history itself (serial numbers seen on earlier intake = reloan).

Every rule is additive on top of value_item(): it only ever (a) replaces a value with a
manager-stated one, (b) adds a documented allowance, (c) multiplies by a quantity that the
description states, (d) moves an item from FLAGS to a VERIFY list with a reason, or (e) tags a
reloan. Each change is recorded in r['fb_notes'] so the spreadsheet shows why.
All functions fail soft: any exception leaves the item exactly as the engine valued it.
"""
from __future__ import annotations
import csv, glob, json, os, re, datetime, collections

HERE      = os.path.dirname(os.path.abspath(__file__))
PW_DIR    = os.path.dirname(HERE)
BRAVO_OUT = os.environ.get("VP_BRAVO_OUTPUT",
            "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output/")
CFG       = os.path.join(HERE, "feedback_rules.json")
COMPS     = os.path.join(HERE, "manager_comps.json")
OVERRIDES = os.path.join(HERE, "item_overrides.json")
CALIB     = os.path.join(HERE, "calibration.json")
STATE     = os.path.join(HERE, "ingest_state.json")
SERIAL_IX = os.path.join(HERE, "serial_index.json")

FLAG_MARGIN, BULLION_FLAG, TARGET, BULLION_TARGET = 0.30, 0.25, 0.50, 0.25
_SERIAL = re.compile(r"SERIAL\s*(?:NUMBER|NO\.?|#)\s*:?\s*([A-Z0-9][A-Z0-9-]{2,})")
_SERIAL_JUNK = {"NA", "N/A", "NONE", "UNKNOWN", "UNK", "NOT", "NUMBER", "N-A", "NSN", "XXX", "000", "123", "1234", "NONE-", "N/A-"}
_QTY_DESC = re.compile(r"\b(?:QUANTITY|QTY)\s*(?:OF|:|#|-)?\s*(\d{1,3})\b|\(\s*(\d{1,3})\s*(?:PCS|PIECES|EA|COUNT|CT)\s*\)|\bX\s?(\d{1,3})\b|\b(\d{1,3})\s*(?:PCS|PIECES|COINS|ROUNDS|BARS)\b")
# Bravo writes the power TYPE as "CORDLESS - BATTERY OPERATED"; only "W/ BATTERY", "2 BATTERIES",
# "BATTERY AND CHARGER" mean a battery came with the tool. "NO CHARGER" means none did.
_BATT = re.compile(r"\b(\d)\s*(?:X\s*)?BATTER")
_HAS_BATT = re.compile(r"\bW/\s*\d?\s*BATTER|\bWITH\s*\d?\s*BATTER|\b\d\s*BATTERIES|BATTERY AND CHARGER|BATTERIES AND CHARGER|BATTERY & CHARGER|INCLUDES? BATTER")
_HAS_CHG = re.compile(r"(?<!NO )(?<!WITHOUT )CHARGER(?! NOT)")
_HAS_CASE = re.compile(r"\b(W/|WITH|INCLUDES?|INCL\.?)\s*(HARD |SOFT |ORIGINAL )?(CASE|BOX)\b|CASE INCLUDED")

def _j(p, d):
    try:
        return json.load(open(p))
    except Exception:
        return d

def _cfg():
    return _j(CFG, {})

def _norm(s):
    return re.sub(r"\s+", " ", (s or "").upper().strip())

def _recompute(r, note):
    """Recompute margin / flag / overpay / meets from r['value'] (keeps engine semantics)."""
    val, cost = r.get("value"), r.get("cost") or 0
    r["margin"] = ((val - cost) / val) if (val and val > 0) else None
    trusted = r.get("conf") in ("high", "medium")
    r["trusted"] = 1 if trusted else 0
    thr = BULLION_FLAG if r.get("is_bullion") else FLAG_MARGIN
    tgt = BULLION_TARGET if r.get("is_bullion") else TARGET
    cat_thr = r.get("_cat_flag_margin")
    if cat_thr is not None:
        thr = min(thr, cat_thr)
    r["flag"] = 1 if (trusted and r["margin"] is not None and r["margin"] < thr) else 0
    r["overpay"] = 1 if (trusted and val is not None and cost > val) else 0
    r["meets"] = 1 if (trusted and r["margin"] is not None and r["margin"] >= tgt) else 0
    r.setdefault("fb_notes", []).append(note)

def _to_verify(r, reason):
    if r.get("flag") or r.get("overpay"):
        r["flag"], r["overpay"] = 0, 0
        r["verify"] = reason
        r.setdefault("fb_notes", []).append("VERIFY: " + reason)

# ── model key (same rule as feedback_ingest.model_key; duplicated so each file stands alone) ─
def model_key(desc):
    d = _norm(desc)
    if re.search(r"\d\s*(DWT|GRAMS?|\bG\b|OZT?)\b|\b\d{1,2}K[- ]?[YWR]?/?G\b|SILV-?925|STERLING", d):
        return None
    d = re.split(r",", d, 1)[0]
    d = re.sub(r"\bSERIAL\s*(NUMBER|NO\.?|#)?\s*[A-Z0-9-]*", " ", d)
    d = re.sub(r"\bMODEL\b", " ", d)
    d = re.sub(r"[^A-Z0-9/.\- ]", " ", d)
    d = re.sub(r"\s+", " ", d).strip(" -")
    toks = d.split()
    if len(toks) < 2:
        return None
    if not any(any(c.isdigit() for c in t) for t in toks) and len(toks[0]) < 3:
        return None
    return d

# ── serial index: serial -> sorted list of intake dates it appeared on ─────────
def _serial_index(upto: datetime.date, lookback_days: int) -> dict:
    ix = _j(SERIAL_IX, {"files": {}, "serials": {}})
    files, serials = ix.setdefault("files", {}), ix.setdefault("serials", {})
    changed = False
    for f in glob.glob(os.path.join(BRAVO_OUT, "*_intake-detail.csv")):
        b = os.path.basename(f)
        m = re.match(r"(\d{4}-\d{2}-\d{2})(?:_to_(\d{4}-\d{2}-\d{2}))?_([A-Z]{3})_", b)
        if not m:
            continue
        d = m.group(2) or m.group(1)
        try:
            mt = os.path.getmtime(f)
        except OSError:
            continue
        if files.get(b) == mt:
            continue
        files[b] = mt
        changed = True
        try:
            with open(f, newline="", encoding="utf-8-sig") as fh:
                for row in csv.DictReader(fh):
                    desc = _norm(row.get("Full Description") or row.get("FullDescription"))
                    sm = _SERIAL.search(desc)
                    if sm and sm.group(1) not in _SERIAL_JUNK:
                        lst = serials.setdefault(sm.group(1), [])
                        if d not in lst:
                            lst.append(d)
                            lst.sort()
        except Exception:
            pass
    if changed:
        try:
            tmp = SERIAL_IX + ".tmp"
            json.dump(ix, open(tmp, "w"))
            os.replace(tmp, SERIAL_IX)
        except Exception:
            pass
    return serials

# ── the hook ──────────────────────────────────────────────────────────────────
def apply(valued: list, date: datetime.date) -> list:
    """Mutates and returns `valued`. Never raises."""
    try:
        return _apply(valued, date)
    except Exception as ex:                      # fail soft — engine output stands
        for r in valued:
            r.setdefault("fb_notes", [])
        return valued

def _apply(valued, date):
    cfg = _cfg()
    today = datetime.date.today()
    comps = _j(COMPS, {})
    overrides = _j(OVERRIDES, {})
    calib = _j(CALIB, {})
    tuning = (calib.get("category_tuning") or {})
    comp_days = int(cfg.get("manager_comp_days", 180))
    ov_days, gen_days = int(cfg.get("override_days", 180)), int(cfg.get("generic_override_days", 120))
    allow = cfg.get("accessory_allowance") or {}
    optic_re = re.compile(cfg.get("optic_keywords") or "OPTIC|SCOPE", re.I)
    serials = _serial_index(date, int(cfg.get("reloan_lookback_days", 400)))
    ds = date.isoformat()

    def fresh(d, days):
        try:
            return (today - datetime.date.fromisoformat(d)).days <= days
        except Exception:
            return False

    for r in valued:
        r.setdefault("fb_notes", [])
        desc = _norm(r.get("desc"))
        cat = (r.get("category") or "").strip()
        key = model_key(desc)
        src = str(r.get("source") or "")

        # category self-tuning (from calibration): severe-only threshold where we keep being wrong
        t = tuning.get(cat)
        if t and t.get("flag_margin") is not None:
            r["_cat_flag_margin"] = float(t["flag_margin"])

        # R1 — manager comp: a value Preston/Joshua stated for this model, still fresh
        c = comps.get(key) if key else None
        if c and fresh(c.get("date", ""), comp_days) and c.get("value"):
            r["value"], r["source"], r["conf"], r["comp_n"] = float(c["value"]), "MGR-COMP", "high", 1
            r["t3_range_lo"] = r["t3_range_hi"] = None
            _recompute(r, f"manager comp ${float(c['value']):,.0f} ({c.get('by','?')} {c.get('date','')})")

        # R2 — quantity stated in the description, per-unit sources only
        qm = _QTY_DESC.search(desc)
        if qm and r.get("qty") is None and r.get("value") and src.startswith(("COIN-", "BULLION", "MGR-COMP", "T3-EBAY", "COMP")):
            q = int(next(g for g in qm.groups() if g))
            if 2 <= q <= 50:
                r["value"] = round(r["value"] * q, 2)
                r["source"] = src + f"×{q}"
                _recompute(r, f"quantity {q} in description → value ×{q}")

        # R3 — accessory allowances (tools): batteries / chargers / case named in the description
        if r.get("group") == "Everything Else" and r.get("value") and not src.startswith("MGR-COMP") \
           and "BATTER" not in cat.upper() and "CHARGER" not in cat.upper():
            add, parts = 0.0, []
            if _HAS_BATT.search(desc):
                bm = _BATT.search(desc)
                nb = int(bm.group(1)) if bm else 1
                add += nb * float(allow.get("battery", 0)); parts.append(f"{nb} batt")
            if _HAS_CHG.search(desc):
                add += float(allow.get("charger", 0)); parts.append("charger")
            if _HAS_CASE.search(desc):
                add += float(allow.get("case", 0)); parts.append("case")
            if add > 0:
                r["value"] = round(r["value"] + add, 2)
                _recompute(r, f"+${add:,.0f} accessories ({', '.join(parts)})")

        # R4 — reloan tag: this serial number came through intake before
        sm = _SERIAL.search(desc)
        if sm and sm.group(1) not in _SERIAL_JUNK:
            prior = [d for d in serials.get(sm.group(1), []) if d < ds]
            if prior:
                r["reloan"] = 1
                r["reloan_first"] = prior[0]
                r["fb_notes"].append(f"reloan — first seen {prior[0]} ({len(prior)} prior)")

        # recompute flags once more if category tuning applies and nothing else touched the item
        if r.get("_cat_flag_margin") is not None and not any(n for n in r["fb_notes"] if not n.startswith("reloan")):
            _recompute(r, f"category tuned: flag only below {int(r['_cat_flag_margin']*100)}% ({t.get('why','')})")

        # R5 — cleared items: Preston already looked at this exact item (same store / desc / paid)
        okey = f"{r.get('store')}|{desc}|{(r.get('cost') or 0):.0f}"
        o = overrides.get(okey)
        if o and fresh(o.get("date", ""), gen_days if o.get("generic") else ov_days):
            why = ", ".join(o.get("reasons") or []) or "cleared"
            if r.get("flag") or r.get("overpay"):
                r["flag"], r["overpay"] = 0, 0
                r["fb_notes"].append(f"cleared by {o.get('by','?')} {o.get('date','')}: {why}")
            r["cleared"] = 1

        # R6 — firearm with an optic named: our comp is the bare gun; verify instead of flag
        if r.get("group") == "Guns" and optic_re.search(desc) and not src.startswith("MGR-COMP"):
            _to_verify(r, "optic attached — value and write up the optic separately")

    return valued

# ── message helpers for build_slack_message ───────────────────────────────────
def kind_label(r) -> str:
    base = "L" if (r.get("ticket_kind") == "LOAN") else "B"
    return "RL" if (base == "L" and r.get("reloan")) else base

def verify_lines(valued: list) -> list:
    v = [r for r in valued if r.get("verify")]
    if not v:
        return []
    out = ["", "*🔎 VERIFY (" + str(len(v)) + ")* — not counted as flags; needs a look at the counter"]
    for r in sorted(v, key=lambda x: (x.get("store", ""), -(x.get("cost") or 0)))[:10]:
        d = (r.get("desc") or "").strip()
        d = d[:41] + "…" if len(d) > 42 else d
        out.append(f"• {r.get('store','')} · {kind_label(r)} · ${r.get('cost',0):,.0f} · {d} — _{r['verify']}_")
    return out

def footer_lines(valued: list, date: datetime.date) -> list:
    """One line when feedback was just ingested; a short accuracy line on Tuesdays."""
    out = []
    st = _j(STATE, {})
    lr = st.get("last_result") or {}
    try:
        ran_today = (st.get("last_run") or "")[:10] == datetime.date.today().isoformat()
    except Exception:
        ran_today = False
    if ran_today and (lr.get("new_lines") or 0) > 0:
        who = ", ".join(lr.get("by") or []) or "the stores"
        wd = ", ".join(lr.get("walk_dates") or [])
        parts = []
        if lr.get("comps_added"):
            parts.append(f"{lr['comps_added']} model value{'s' if lr['comps_added'] != 1 else ''} updated")
        if lr.get("overrides_added"):
            parts.append(f"{lr['overrides_added']} item{'s' if lr['overrides_added'] != 1 else ''} cleared")
        out.append("")
        out.append(f"🧠 _{who}'s feedback on the {wd or 'last'} walk is in: {lr['new_lines']} notes"
                   + (" → " + ", ".join(parts) if parts else "") + "._")
    reloans = sum(1 for r in valued if r.get("reloan") and (r.get("flag") or r.get("overpay")))
    if reloans:
        if not out:
            out.append("")
        out.append(f"_RL = reloan of an item we've written before — re-check value, condition and quantity every time._")
    cal = _j(CALIB, {})
    tot = cal.get("totals") or {}
    n = (tot.get("confirmed") or 0) + (tot.get("false") or 0)
    if datetime.date.today().weekday() == 1 and n >= 5 and cal.get("precision") is not None:
        if not out:
            out.append("")
        out.append(f"_Flag accuracy, last {cal.get('window_days', 90)} days: {tot.get('confirmed',0)} of {n} flags the stores reviewed were real overpays ({cal['precision']*100:.0f}%)._")
    return out

def excel_sheet(path: str, valued: list) -> bool:
    """Append a 'Feedback' tab: every item a rule touched, with the why. Fail soft."""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        wb = openpyxl.load_workbook(path)
        if "Feedback" in wb.sheetnames:
            del wb["Feedback"]
        ws = wb.create_sheet("Feedback")
        hdr = ["Store", "Kind", "Category", "Description", "Cost Paid", "Est Value", "Source", "Margin", "Flag?", "Verify", "What the feedback loop did"]
        for i, h in enumerate(hdr, 1):
            c = ws.cell(row=1, column=i, value=h)
            c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0D1B40")
        ri = 2
        for r in valued:
            if not r.get("fb_notes"):
                continue
            vals = [r.get("store"), kind_label(r), r.get("category"), r.get("desc"), r.get("cost"), r.get("value"),
                    r.get("source"), r.get("margin"), "⚑" if r.get("flag") else "", r.get("verify", ""), " | ".join(r["fb_notes"])]
            for ci, v in enumerate(vals, 1):
                ws.cell(row=ri, column=ci, value=v)
            ws.cell(row=ri, column=8).number_format = "0.0%"
            ws.cell(row=ri, column=5).number_format = '"$"#,##0.00'
            ws.cell(row=ri, column=6).number_format = '"$"#,##0.00'
            ri += 1
        cal = _j(CALIB, {})
        tot = cal.get("totals") or {}
        ri += 1
        ws.cell(row=ri, column=1, value=f"Flag accuracy — last {cal.get('window_days', 90)} days of store feedback").font = Font(bold=True)
        ws.cell(row=ri + 1, column=1, value="Real overpays"); ws.cell(row=ri + 1, column=2, value=tot.get("confirmed", 0))
        ws.cell(row=ri + 2, column=1, value="Not overpays"); ws.cell(row=ri + 2, column=2, value=tot.get("false", 0))
        ws.cell(row=ri + 3, column=1, value="Unclear"); ws.cell(row=ri + 3, column=2, value=tot.get("unclear", 0))
        ri += 5
        ws.cell(row=ri, column=1, value="By category").font = Font(bold=True)
        ws.cell(row=ri, column=2, value="Real"); ws.cell(row=ri, column=3, value="Not"); ws.cell(row=ri, column=4, value="Rule in force")
        tun = cal.get("category_tuning") or {}
        for cat, d in sorted((cal.get("by_category") or {}).items()):
            ri += 1
            ws.cell(row=ri, column=1, value=cat); ws.cell(row=ri, column=2, value=d.get("confirmed", 0))
            ws.cell(row=ri, column=3, value=d.get("false", 0))
            if cat in tun:
                ws.cell(row=ri, column=4, value=f"flag only below {int(tun[cat]['flag_margin']*100)}% — {tun[cat].get('why','')}")
        for col, w in zip("ABCDEFGHIJK", [7, 6, 22, 46, 10, 10, 26, 9, 6, 30, 60]):
            ws.column_dimensions[col].width = w
        wb.save(path)
        return True
    except Exception:
        return False
