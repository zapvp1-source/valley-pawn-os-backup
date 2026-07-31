#!/usr/bin/env python3
"""
jewelry_reconciliation_comparison.py — Jewelry Count Reconciliation, Valley Pawn
v2, 2026-07-30

Compares Bravo's jewelry-pieces-sold count for a day against the manager's
handwritten AM/PM physical jewelry count sheet posted in Slack #end-of-day.

================================ WHY v2 ================================
v1 compared Bravo's FULL jewelry category list (~90 categories, including
wristwatches, scrap, brooches, bullion) against a paper sheet that only counts
FIVE buckets: Rings, Bracelets, Necklaces, Earrings, Pendants.

That is an apples-to-oranges comparison and it systematically invents
mismatches. Caught live on 2026-07-29 at Culpeper: the store sold a gold
bracelet AND a TAG Heuer wristwatch. v1 would have counted 2 pieces sold
against a case that only dropped by 1 — a phantom flag. The watch was never in
the counted case to begin with.

v2 maps each Bravo category into one of the five sheet buckets, and ignores
anything that does not belong to a bucket (watches, scrap, bullion, brooches,
loose diamonds, misc). It then compares PER BUCKET as well as in total, which
is a much stronger check: on 2026-07-29 Culpeper matched exactly at the bucket
level (bracelets 119 -> 118, everything else unchanged, one bracelet sold).

================================ WHAT A FLAG MEANS =====================
The paper count is a PHYSICAL headcount, so (AM - PM) = pieces sold MINUS
pieces bought/taken in that day. Bravo's number is sold-only. On a heavy buy
day the case can shrink less than sales alone predict and throw a flag that is
not shrinkage. A flag means "worth a look," NOT "theft." Say it that way.

v3 improvement: pull a Bravo pieces-bought count and net it out.
"""
import csv
import re

TOLERANCE = 5           # per expert-board decision 2026-07-27; applies to the total
BUCKET_TOLERANCE = 3    # tighter per-bucket tolerance — a single bucket drifting
                        # is a sharper signal than the total, which can self-cancel

# The five buckets the paper sheet actually counts, in sheet order.
SHEET_BUCKETS = ["Rings", "Bracelets", "Necklaces", "Earrings", "Pendants"]


# Canonical jewelry categories, taken empirically from the distinct Category
# values in Bravo's own "Aged Jewelry Sales" saved report output (all 5 stores,
# full year, pulled 2026-07-29). This set is the GATE: a category must appear
# here before it is even considered for a sheet bucket.
#
# Why a gate and not just word-matching: on the first live test, plain substring
# matching put a STIHL CHAINSAW into Necklaces because "Chainsaw" contains
# "chain". Bravo has ~1,000 non-jewelry categories and several collide with
# jewelry words (Chainsaw/chain, Earmuffs/ear, Ring Light/ring). Gating on the
# known jewelry set removes that entire class of error.
JEWELRY_CATEGORIES = {
    "Bracelet", "Diamond", "Diamond & Stone Necklace", "Diamond Necklace",
    "Gent's Diamond Cluster Ring", "Gent's Diamond Fashion Ring", "Gent's Gold Ring",
    "Gent's Silver & Stone Ring", "Gent's Silver Ring", "Gent's Silver-Diamond Ring",
    "Gent's Stone Ring", "Gent's Wristwatch", "Gold Box Chain", "Gold Bracelet",
    "Gold Chain", "Gold Charm", "Gold Earrings", "Gold Figaro Bracelet", "Gold Necklace",
    "Gold Pendant", "Gold Rope Chain", "Gold-Diamond & Stone Bracelet",
    "Gold-Diamond & Stone Earrings", "Gold-Diamond & Stone Pendant",
    "Gold-Diamond Bracelet", "Gold-Diamond Earrings", "Gold-Diamond Scrap",
    "Gold-Diamond-Stone Brooch", "Gold-Misc.", "Gold-Multi-Diamond Pendant",
    "Gold-Scrap", "Gold-Stone Bracelet", "Gold-Stone Earrings", "Gold-Stone Misc.",
    "Gold-Stone Pendant", "Lady's Diamond Cluster Ring", "Lady's Diamond Engagement Ring",
    "Lady's Diamond Fashion Ring", "Lady's Diamond Solitaire Ring",
    "Lady's Diamond Wedding Band", "Lady's Diamond Wedding Set", "Lady's Gold Ring",
    "Lady's Gold Wedding Band", "Lady's Platinum Diamond Fashion",
    "Lady's Platinum-Diamond Solitaire", "Lady's Silver & Stone Ring", "Lady's Silver Ring",
    "Lady's Silver Wedding Band", "Lady's Silver-Diamond Ring", "Lady's Stone & Diamond Ring",
    "Lady's Stone Ring", "Lady's Wristwatch", "Pin/Brooch", "Pocket Watch",
    "Silver Bangle Bracelet", "Silver Box Chain", "Silver Bracelet", "Silver Brooch",
    "Silver Chain", "Silver Charm", "Silver Charm Bracelet", "Silver Earrings",
    "Silver Herringbone Chain", "Silver ID Bracelet", "Silver Link Bracelet",
    "Silver Necklaces", "Silver Pendant", "Silver Rope Bracelet", "Silver Rope Chain",
    "Silver-Diamond & Stone Earrings", "Silver-Diamond Bracelet", "Silver-Diamond Earrings",
    "Silver-Diamond Pendant", "Silver-Misc.", "Silver-Scrap", "Silver-Stone Bracelet",
    "Silver-Stone Earrings", "Silver-Stone Misc.", "Silver-Stone Pendant",
    "Stone Necklace", "Unisex Gold Ring", "Unisex Gold Wedding Band",
    "Unisex Gold-Diamond Wedding Band", "Unisex Silver & Stone Ring", "Unisex Silver Ring",
    "Unisex Stone Ring", "Unisex Wristwatch", "Watch Band",
    "Lady's Diamond Anniversary Ring", "Lady's Gold-Diamond Anniversary Ring",
}


def bucket_for(category: str):
    """Map a Bravo Category to one of the five sheet buckets, or None if the
    count sheet does not track it.

    Two stages: (1) the category must be a known jewelry category, (2) it must
    fall into one of the five counted buckets. Watches, scrap, bullion, brooches
    and loose stones are real jewelry but are NOT on the sheet — they live in the
    safe or the scrap bin, not the counted case — so they return None.

    Order matters: 'Silver Charm Bracelet' must land in Bracelets not Pendants,
    and 'Earrings' contains the substring 'ring', so earrings are tested before
    rings.
    """
    c = (category or "").strip()
    if c not in JEWELRY_CATEGORIES:
        return None
    low = c.lower()

    # Jewelry, but never part of the AM/PM counted case.
    if re.search(r"scrap|bullion|wristwatch|pocket watch|watch band|brooch|misc", low):
        return None
    if low == "diamond":         # loose stone, not a finished piece
        return None

    if "bracelet" in low or "bangle" in low:
        return "Bracelets"
    if "earring" in low:         # before 'ring' — 'Earrings' contains 'ring'
        return "Earrings"
    if "ring" in low or "wedding band" in low or "solitaire" in low:
        return "Rings"
    if "necklace" in low or "chain" in low:
        return "Necklaces"
    if "pendant" in low or "charm" in low:
        return "Pendants"

    return None


def count_jewelry_sold(csv_path):
    """Count sold pieces from a jewelry-count-audit / jewelry-margin-sold CSV,
    bucketed to match the paper sheet.

    Returns (total, per_bucket dict, ignored list) where `ignored` holds
    (category, description) for jewelry-ish items deliberately excluded, so the
    write-up can mention them instead of them vanishing silently.
    """
    per_bucket = {b: 0 for b in SHEET_BUCKETS}
    ignored = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cat = (row.get("Category") or "").strip()
            b = bucket_for(cat)
            if b:
                per_bucket[b] += 1
            elif cat in JEWELRY_CATEGORIES:
                # Real jewelry, deliberately not on the sheet (watch, scrap,
                # brooch, loose stone). Surfaced so it is visible rather than
                # silently dropped.
                ignored.append((cat, (row.get("Description") or "").strip()))
    return sum(per_bucket.values()), per_bucket, ignored


def reconcile(store, date, bravo_per_bucket, am_counts, pm_counts,
              sheet_date=None, tolerance=TOLERANCE,
              bucket_tolerance=BUCKET_TOLERANCE):
    """Compare Bravo sold counts against the AM/PM physical count, per bucket
    and in total."""
    bravo_total = sum(bravo_per_bucket.values())
    am_total = sum(am_counts.values())
    pm_total = sum(pm_counts.values())
    net_change = am_total - pm_total          # positive = pieces left the case
    diff = net_change - bravo_total

    buckets = {}
    bucket_flags = []
    for b in SHEET_BUCKETS:
        am = am_counts.get(b)
        pm = pm_counts.get(b)
        if am is None or pm is None:
            buckets[b] = {"unreadable": True}
            continue
        b_net = am - pm
        b_sold = bravo_per_bucket.get(b, 0)
        b_diff = b_net - b_sold
        flagged = abs(b_diff) > bucket_tolerance
        buckets[b] = {"am": am, "pm": pm, "net": b_net, "sold": b_sold,
                      "diff": b_diff, "flagged": flagged, "unreadable": False}
        if flagged:
            bucket_flags.append(b)

    return {
        "store": store,
        "date": date,
        "bravo_sold_total": bravo_total,
        "bravo_per_bucket": dict(bravo_per_bucket),
        "am_total": am_total,
        "pm_total": pm_total,
        "net_change": net_change,
        "diff": diff,
        "buckets": buckets,
        "bucket_flags": bucket_flags,
        "flag": abs(diff) > tolerance or bool(bucket_flags),
        "date_mismatch": bool(sheet_date and sheet_date != date),
    }


# Store <-> #end-of-day poster map. Confirmed 2026-07-29 by reading each sheet's
# printed "END OF DAY: <STORE>" header. This is who CURRENTLY posts, not a
# guarantee — if an unknown name appears, read that day's header before scoring
# and update this map. (Seen posting but not yet mapped: "Bree", "Martin D.",
# "Preston Peters" — confirm from a sheet header before using.)
STORE_POSTER_MAP = {
    "Benjie Moore": "ROA",   # Roanoke
    "Walker Tapley": "HAR",  # Harrisonburg
    "Uriah": "LEX",          # Lexington
    "Chadd": "WAY",          # Waynesboro
    "Sandi Cole": "CUL",     # Culpeper
    "Sandi": "CUL",
}


def format_slack_message(results, date, missing_sheets=None, failed_pulls=None):
    lines = [f"*💎 Jewelry Count Reconciliation — {date}*", ""]
    for r in results:
        icon = "🚩" if (r["flag"] or r["date_mismatch"]) else "✅"
        lines.append(
            f"{icon} *{r['store']}* — sold {r['bravo_sold_total']} · "
            f"case moved {r['net_change']} · diff {r['diff']:+d}"
            + ("  ⚠️ sheet dated differently" if r["date_mismatch"] else "")
        )
        for b in r["bucket_flags"]:
            d = r["buckets"][b]
            lines.append(f"      • {b}: sold {d['sold']}, case moved {d['net']} ({d['diff']:+d})")
    if failed_pulls:
        lines.append("")
        lines.append("*Couldn't check — no sales data:* " + ", ".join(failed_pulls))
    if missing_sheets:
        lines.append("")
        lines.append("*Couldn't check — no count sheet posted:* " + ", ".join(missing_sheets))
    if not any(r["flag"] or r["date_mismatch"] for r in results) \
            and not failed_pulls and not missing_sheets:
        lines.append("")
        lines.append("All stores line up.")
    return "\n".join(lines)


if __name__ == "__main__":
    # Live check against real 2026-07-29 Culpeper data.
    path = ("/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/"
            "output/2026-07-29_to_2026-07-29_CUL_jewelry-count-audit.csv")
    total, per_bucket, ignored = count_jewelry_sold(path)
    print("CUL 2026-07-29 sold (bucketed):", total, per_bucket)
    print("  excluded as not-on-sheet:", ignored)

    r = reconcile(
        store="CUL", date="2026-07-29",
        bravo_per_bucket=per_bucket,
        am_counts={"Rings": 602, "Bracelets": 119, "Necklaces": 146,
                   "Earrings": 124, "Pendants": 247},
        pm_counts={"Rings": 602, "Bracelets": 118, "Necklaces": 146,
                   "Earrings": 124, "Pendants": 247},
        sheet_date="2026-07-29",
    )
    print()
    print("flag:", r["flag"], "| diff:", r["diff"], "| bucket flags:", r["bucket_flags"])
    for b, d in r["buckets"].items():
        print(f"  {b:<10} sold={d['sold']} net={d['net']} diff={d['diff']:+d}")
    print()
    print(format_slack_message([r], "2026-07-29",
                               missing_sheets=["HAR", "LEX", "ROA", "WAY"],
                               failed_pulls=["HAR", "LEX", "ROA", "WAY"]))
