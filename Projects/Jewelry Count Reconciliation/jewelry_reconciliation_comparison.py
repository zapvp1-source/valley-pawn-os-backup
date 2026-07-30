#!/usr/bin/env python3
"""
jewelry_reconciliation_comparison.py — Jewelry Count Reconciliation, Valley Pawn
2026-07-29

Compares Bravo's "jewelry-count-audit" pipeline output (pieces SOLD per store,
per day, from the "Claude Sold Inv Details" Sold Inventory report) against the
manager's handwritten AM/PM physical jewelry count sheet posted daily as
photos in #end-of-day.

WHY THIS SHAPE (v1 design decision — see STATUS.md "Reconciliation Logic
Design (2026-07-29)" for full reasoning):

  The EOD paper ledger does NOT record "pieces sold" directly. It records a
  physical head-count of jewelry in the case at open (AM) and close (PM),
  broken out by category (Rings, Bracelets, Necklaces, Earrings, Pendants).
  The net change (AM - PM) reflects (pieces sold) MINUS (pieces bought/taken
  in) that day. Bravo's sold-count report only has the sold side.

  v1 heuristic (this script): flag when
      (AM_total - PM_total)  vs.  Bravo_sold_total
  differ by more than the tolerance (default 5 pieces). On a day with heavy
  buy volume this heuristic can throw a false-positive flag (physical count
  drop is smaller than sold count, because bought pieces backfilled the
  case) — that is a KNOWN v1 limitation, not a silent failure. It is exactly
  the loss-prevention signal Joshua asked for: if physical count moved LESS
  than sales alone should have moved it (i.e. AM-PM smaller than sold, past
  tolerance) that means fewer pieces are missing from the case than the
  register says walked out for cash-value reasons unaccounted by buys —
  worth a manual look either way. v2 should pull a "pieces bought" count
  from Bravo (separate saved report) to net this out precisely and remove
  the false-positive risk on big-buy days.

INPUT (per store per day):
  bravo_sold_total   — int, from summing jewelry-category rows in the
                       jewelry-count-audit CSV (see count_jewelry_sold()).
  am_counts          — dict of category -> int, from the EOD photo (read via
                       Claude-in-Chrome vision pass — no MCP tool can pull
                       Slack file bytes directly, see STATUS.md).
  pm_counts          — same shape as am_counts.
  sheet_date         — the handwritten DATE on the count sheet itself. This
                       can legitimately differ from the Slack post date
                       (managers sometimes photograph a prior day's sheet
                       late, or the sheet is a running multi-day ledger) —
                       ALWAYS compare against sheet_date, never assume the
                       Slack message timestamp is the count date. Flag
                       (not silently correct) any date mismatch.

TOLERANCE: ±5 pieces (per expert-board decision, 2026-07-27, applied
  company-wide as MVP; category-level tolerances are a v2 improvement).
"""
from pathlib import Path
import csv

TOLERANCE = 5

JEWELRY_CATEGORIES = {
    "Bracelet","Diamond","Diamond & Stone Necklace","Diamond Necklace",
    "Gent's Diamond Cluster Ring","Gent's Diamond Fashion Ring","Gent's Gold Ring",
    "Gent's Silver & Stone Ring","Gent's Silver Ring","Gent's Silver-Diamond Ring",
    "Gent's Stone Ring","Gent's Wristwatch","Gold Box Chain","Gold Bracelet",
    "Gold Chain","Gold Charm","Gold Earrings","Gold Figaro Bracelet","Gold Necklace",
    "Gold Pendant","Gold Rope Chain","Gold-Diamond & Stone Bracelet",
    "Gold-Diamond & Stone Earrings","Gold-Diamond & Stone Pendant",
    "Gold-Diamond Bracelet","Gold-Diamond Earrings","Gold-Diamond Scrap",
    "Gold-Diamond-Stone Brooch","Gold-Misc.","Gold-Multi-Diamond Pendant",
    "Gold-Scrap","Gold-Stone Bracelet","Gold-Stone Earrings","Gold-Stone Misc.",
    "Gold-Stone Pendant","Lady's Diamond Cluster Ring","Lady's Diamond Engagement Ring",
    "Lady's Diamond Fashion Ring","Lady's Diamond Solitaire Ring",
    "Lady's Diamond Wedding Band","Lady's Diamond Wedding Set","Lady's Gold Ring",
    "Lady's Gold Wedding Band","Lady's Platinum Diamond Fashion",
    "Lady's Platinum-Diamond Solitaire","Lady's Silver & Stone Ring","Lady's Silver Ring",
    "Lady's Silver Wedding Band","Lady's Silver-Diamond Ring","Lady's Stone & Diamond Ring",
    "Lady's Stone Ring","Lady's Wristwatch","Pin/Brooch","Pocket Watch",
    "Silver Bangle Bracelet","Silver Box Chain","Silver Bracelet","Silver Brooch",
    "Silver Chain","Silver Charm","Silver Charm Bracelet","Silver Earrings",
    "Silver Herringbone Chain","Silver ID Bracelet","Silver Link Bracelet",
    "Silver Necklaces","Silver Pendant","Silver Rope Bracelet","Silver Rope Chain",
    "Silver-Diamond & Stone Earrings","Silver-Diamond Bracelet","Silver-Diamond Earrings",
    "Silver-Diamond Pendant","Silver-Misc.","Silver-Scrap","Silver-Stone Bracelet",
    "Silver-Stone Earrings","Silver-Stone Misc.","Silver-Stone Pendant",
    "Stone Necklace","Unisex Gold Ring","Unisex Gold Wedding Band",
    "Unisex Gold-Diamond Wedding Band","Unisex Silver & Stone Ring","Unisex Silver Ring",
    "Unisex Stone Ring","Unisex Wristwatch","Watch Band",
    "Lady's Diamond Anniversary Ring","Lady's Gold-Diamond Anniversary Ring",
}

# Store -> #end-of-day poster mapping. Confirmed 2026-07-29 by reading each
# store's photographed sheet header ("END OF DAY: <STORE>") directly via a
# browser vision pass — all 5 stores confirmed. NOTE: this is who currently
# posts for each store, not a guarantee — personnel/channel membership can
# change. If a new poster name shows up who isn't in this map, don't guess:
# read that day's sheet header before scoring, and update this map once
# confirmed.
STORE_POSTER_MAP = {
    "Benjie Moore": "ROA",   # Roanoke
    "Walker Tapley": "HAR",  # Harrisonburg
    "Uriah": "LEX",          # Lexington
    "Chadd": "WAY",          # Waynesboro
    "Sandi Cole": "CUL",     # Culpeper
}


def count_jewelry_sold(csv_path):
    """Sum jewelry-category rows in a jewelry-count-audit CSV. Returns
    (total, per_category dict)."""
    per_category = {}
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cat = row.get("Category", "").strip()
            if cat in JEWELRY_CATEGORIES:
                per_category[cat] = per_category.get(cat, 0) + 1
    return sum(per_category.values()), per_category


def reconcile(store, date, bravo_sold_total, am_counts, pm_counts,
              sheet_date=None, tolerance=TOLERANCE):
    am_total = sum(am_counts.values())
    pm_total = sum(pm_counts.values())
    net_change = am_total - pm_total  # positive = net pieces left the case

    result = {
        "store": store,
        "date": date,
        "bravo_sold_total": bravo_sold_total,
        "am_total": am_total,
        "pm_total": pm_total,
        "net_change": net_change,
        "diff": net_change - bravo_sold_total,
        "flag": abs(net_change - bravo_sold_total) > tolerance,
        "date_mismatch": bool(sheet_date and sheet_date != date),
    }
    return result


def format_slack_message(results):
    lines = ["*Jewelry Count Reconciliation — daily results*"]
    for r in results:
        icon = "🚩" if r["flag"] or r["date_mismatch"] else "✅"
        lines.append(
            f"{icon} *{r['store']}* {r['date']}: Bravo sold={r['bravo_sold_total']}, "
            f"AM={r['am_total']}, PM={r['pm_total']}, net={r['net_change']} "
            f"(diff={r['diff']:+d})"
            + (" ⚠️ sheet date mismatch" if r["date_mismatch"] else "")
        )
    return "\n".join(lines)


if __name__ == "__main__":
    # Smoke-test with real data pulled 2026-07-29: WAY, 2026-07-28, 0 jewelry sold.
    csv_path = "/mnt/user-data/uploads/Projects/Bravo Data Extraction/output/2026-07-28_to_2026-07-28_WAY_jewelry-count-audit.csv"
    total, per_cat = count_jewelry_sold(csv_path)
    print(f"WAY 2026-07-28 jewelry sold: {total} ({per_cat})")

    # Real AM/PM read (via browser vision pass) for ROA, sheet dated 7/26/26,
    # message posted 2026-07-28 -- illustrates the date-mismatch flag.
    r = reconcile(
        store="ROA", date="2026-07-28",
        bravo_sold_total=0,  # placeholder -- ROA jewelry-count-audit not yet pulled
        am_counts={"Rings": 374, "Bracelets": 111, "Necklaces": 146, "Earrings": 77, "Pendants": 143},
        pm_counts={"Rings": 375, "Bracelets": 113, "Necklaces": 150, "Earrings": 78, "Pendants": 144},
        sheet_date="2026-07-26",
    )
    print(r)
    print(format_slack_message([r]))
