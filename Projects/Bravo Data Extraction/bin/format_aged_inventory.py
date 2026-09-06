#!/usr/bin/env python3
"""
Deterministic formatter for the #aged-inventory-review Slack post.

WHY THIS EXISTS (2026-09-05):
The aged-inventory table was hand-rendered in free text by the model on every
Monday run. That drifted: 2026-08-10 lost its header row and gained a stray
code fence; 2026-08-31 posted a 1-of-5-store table with NO header row, an
unbalanced fence, and the store's Inventory Balance ($123,029.24) printed in
the Total Aged $ column. Rule 18 (added 2026-08-31) stops an INCOMPLETE post.
Nothing stopped a MALFORMED or MIS-MAPPED one. This script is that gate.

CONTRACT:
  - stdout  = the exact Slack message body, ready to post verbatim. Nothing else.
  - exit 0  = validated, complete, arithmetically self-consistent. Post it.
  - exit 2  = validation failed. stdout is EMPTY. Post NOTHING to the channel.
              stderr carries the reasons (for the run log / Joshua DM only).
  - exit 1  = usage / unexpected error. Post nothing.

Never post anything this script did not print.

Usage:
  format_aged_inventory.py --pipeline-date 2026-09-06 --post-date 2026-09-07 \
      [--output-dir "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output"]
"""

import argparse
import csv
import datetime as dt
import os
import sys

STORES = [
    ("CUL", "Culpeper"),
    ("HAR", "Harrisonburg"),
    ("LEX", "Lexington"),
    ("ROA", "Roanoke"),
    ("WAY", "Waynesboro"),
]

DEFAULT_OUTPUT_DIR = (
    "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/output"
)

# Column layout — matches the canonical 2026-08-03 post exactly.
W_NAME, W_MONEY, W_PCT = 13, 14, 8
SEP = " ".join(["-" * W_NAME, "-" * W_MONEY, "-" * W_PCT,
                "-" * W_MONEY, "-" * W_PCT, "-" * W_MONEY, "-" * W_PCT])

# Aged = 1yr-18mo, 18mo-2yr, 2yr-3yr, >3yr  (columns 6..9)
AGED_COLS = (6, 7, 8, 9)
COST_COL = 2
MIN_FILE_BYTES = 500


def money(raw):
    """'$21,334.42' -> 21334.42 ; '' / '-' / None -> 0.0"""
    if raw is None:
        return 0.0
    s = str(raw).strip().replace("$", "").replace(",", "").replace(" ", "")
    if s in ("", "-", "--"):
        return 0.0
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1]
    try:
        v = float(s)
    except ValueError:
        raise ValueError("unparseable money value %r" % (raw,))
    return -v if neg else v


def parse_store_csv(path):
    """Return dict(aged_jewelry, aged_merch, inv_balance) or raise ValueError."""
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        rows = list(csv.reader(fh))

    found = {}
    for row in rows:
        if not row:
            continue
        label = row[0].strip().rstrip(":").lower()
        if label in ("jewelry", "mfg. goods", "mfg goods", "subtotals"):
            found[label] = row

    for need in ("jewelry", "subtotals"):
        if need not in found:
            raise ValueError("missing '%s' row" % need)
    merch_row = found.get("mfg. goods") or found.get("mfg goods")
    if merch_row is None:
        raise ValueError("missing 'Mfg. Goods' row")

    def widest(row, idx):
        return money(row[idx]) if idx < len(row) else 0.0

    aged_j = sum(widest(found["jewelry"], i) for i in AGED_COLS)
    aged_m = sum(widest(merch_row, i) for i in AGED_COLS)
    inv_bal = widest(found["subtotals"], COST_COL)

    if inv_bal <= 0:
        raise ValueError("Subtotals Cost (inventory balance) is %.2f — no data" % inv_bal)
    if aged_j < 0 or aged_m < 0:
        raise ValueError("negative aged dollars (J=%.2f GM=%.2f)" % (aged_j, aged_m))
    if (aged_j + aged_m) > inv_bal * 1.0001:
        raise ValueError(
            "aged total $%.2f exceeds inventory balance $%.2f" % (aged_j + aged_m, inv_bal)
        )
    return {"aged_jewelry": aged_j, "aged_merch": aged_m, "inv_balance": inv_bal}


def fmt_money(v):
    return ("$" + format(v, ",.2f")).rjust(W_MONEY)


def fmt_pct(v):
    return (format(v, ".2f") + "%").rjust(W_PCT)


def build_row(name, aged_j, aged_m, inv_bal):
    total = aged_j + aged_m
    return " ".join([
        name.ljust(W_NAME),
        fmt_money(aged_j), fmt_pct(aged_j / inv_bal * 100.0),
        fmt_money(aged_m), fmt_pct(aged_m / inv_bal * 100.0),
        fmt_money(total),  fmt_pct(total / inv_bal * 100.0),
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline-date", required=True,
                    help="date stamped on the CSVs (PART1 run date)")
    ap.add_argument("--post-date", required=True,
                    help="date shown in the Slack header")
    ap.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = ap.parse_args()

    problems, data = [], {}

    for code, name in STORES:
        path = os.path.join(
            args.output_dir,
            "%s_%s_aged-inventory-summary.csv" % (args.pipeline_date, code),
        )
        if not os.path.exists(path):
            problems.append("%s: CSV not found (%s)" % (name, os.path.basename(path)))
            continue
        if os.path.getsize(path) < MIN_FILE_BYTES:
            problems.append("%s: CSV is only %d bytes — truncated/empty export"
                            % (name, os.path.getsize(path)))
            continue
        try:
            data[code] = parse_store_csv(path)
        except Exception as exc:
            problems.append("%s: %s" % (name, exc))

    if problems:
        sys.stderr.write(
            "WITHHOLD — aged-inventory post not emitted (%d of 5 stores valid).\n"
            % len(data)
        )
        for p in problems:
            sys.stderr.write("  - %s\n" % p)
        sys.stderr.write("Post NOTHING to #aged-inventory-review this run.\n")
        return 2

    # Sort highest -> lowest by Total Aged %.
    ranked = sorted(
        STORES,
        key=lambda s: (data[s[0]]["aged_jewelry"] + data[s[0]]["aged_merch"])
        / data[s[0]]["inv_balance"],
        reverse=True,
    )

    lines = [
        "Store".ljust(W_NAME) + " " + "Jewelry".rjust(W_MONEY) + " " + "J%".rjust(W_PCT)
        + " " + "Gen Merch".rjust(W_MONEY) + " " + "GM%".rjust(W_PCT)
        + " " + "Total".rjust(W_MONEY) + " " + "Tot%".rjust(W_PCT),
        SEP,
    ]
    for code, name in ranked:
        d = data[code]
        lines.append(build_row(name, d["aged_jewelry"], d["aged_merch"], d["inv_balance"]))

    t_j = sum(d["aged_jewelry"] for d in data.values())
    t_m = sum(d["aged_merch"] for d in data.values())
    t_b = sum(d["inv_balance"] for d in data.values())
    lines.append(SEP)
    lines.append(build_row("TOTAL", t_j, t_m, t_b))

    # Arithmetic self-check: every Total cell must equal J + GM to the cent.
    for code, name in STORES:
        d = data[code]
        tot = d["aged_jewelry"] + d["aged_merch"]
        if abs(tot - (d["aged_jewelry"] + d["aged_merch"])) > 0.005:
            sys.stderr.write("WITHHOLD — %s total does not reconcile.\n" % name)
            return 2
        if tot >= d["inv_balance"]:
            sys.stderr.write(
                "WITHHOLD — %s aged total is not less than its inventory balance; "
                "the Total column is almost certainly carrying the wrong figure.\n" % name
            )
            return 2

    best = min(ranked, key=lambda s: (data[s[0]]["aged_jewelry"] + data[s[0]]["aged_merch"])
               / data[s[0]]["inv_balance"])
    worst = ranked[0]

    def tot_pct(code):
        d = data[code]
        return (d["aged_jewelry"] + d["aged_merch"]) / d["inv_balance"] * 100.0

    try:
        pretty = dt.datetime.strptime(args.post_date, "%Y-%m-%d").strftime("%B %-d, %Y")
    except ValueError:
        pretty = args.post_date

    fence = "```"
    msg = (
        ":bar_chart: _Aged Inventory Review — %s_\n"
        "_Inventory Aged Over 1 Year (Cost Basis)_\n"
        "_Ranked by Total Aged %% of Inventory_\n"
        "\n"
        "%s%s\n%s%s\n"
        ":trophy: Cleanest book: %s (%.2f%%).  :hammer_and_wrench: "
        "Needs the most attention: %s (%.2f%%)."
    ) % (
        pretty,
        fence, "", "\n".join(lines), fence,
        best[1], tot_pct(best[0]),
        worst[1], tot_pct(worst[0]),
    )

    # Fence hygiene: exactly two fences, nothing after the closing block but the trophy line.
    if msg.count(fence) != 2:
        sys.stderr.write("WITHHOLD — code fences unbalanced in generated message.\n")
        return 2

    sys.stdout.write(msg + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # never emit a half-built message
        sys.stderr.write("WITHHOLD — formatter error: %s\n" % exc)
        sys.exit(1)
