#!/usr/bin/env python3
"""build_warehouse.py -- one queryable store for everything already pulled from Bravo (built 2026-11-27).

READ ONLY against the pipeline: reads Bravo Data Extraction/output and Deep KPI analysis, never writes there.
Full rebuild every run (idempotent). Builds in a temp folder, then swaps the finished file in.
Usage: build_warehouse.py [--out /path/to/bravo_warehouse.sqlite] [--tmp /tmp/dir]
"""
import csv, io, os, re, sys, sqlite3, datetime, shutil, tempfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(PROJ, "Bravo Data Extraction", "output")
DEEP = os.path.join(PROJ, "Deep KPI analysis")
STORES = ("CUL", "HAR", "LEX", "ROA", "WAY")

def money(s):
    s = (s or "").replace("$", "").replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"): s = "-" + s[1:-1]
    try: return float(s)
    except ValueError: return None

def iso(s):
    m = re.match(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})", s or "")
    return f"{m[3]}-{int(m[1]):02d}-{int(m[2]):02d}" if m else None

def read(path, delim=","):
    try:
        txt = open(path, encoding="utf-8-sig", newline="").read()
    except (OSError, UnicodeDecodeError):
        try: txt = open(path, encoding="cp1252", newline="").read()
        except OSError: return [], []
    rd = [r for r in csv.reader(io.StringIO(txt), delimiter=delim) if any(c.strip() for c in r)]
    if not rd: return [], []
    return [h.strip() for h in rd[0]], rd[1:]

def col(hdr, row, name):
    try: return row[hdr.index(name)].strip()
    except (ValueError, IndexError): return ""

DDL = """
CREATE TABLE source_files(file TEXT PRIMARY KEY, dataset TEXT, store TEXT, d1 TEXT, d2 TEXT, rows INT, complete INT, note TEXT);
CREATE TABLE inventory_snapshot(snap_date TEXT, store TEXT, item_no TEXT, status TEXT, category TEXT, description TEXT, cost REAL, price REAL, since_date TEXT);
CREATE TABLE unpriced_snapshot(snap_date TEXT, store TEXT, item_no TEXT, status TEXT, category TEXT, source_type TEXT, description TEXT, location TEXT, cost REAL, item_date TEXT);
CREATE TABLE item_sales(store TEXT, item_no TEXT, sold_date TEXT, category TEXT, description TEXT, cost REAL, tag_price REAL, sold_price REAL, source TEXT, complete INT, file TEXT);
CREATE TABLE intake_items(store TEXT, d1 TEXT, d2 TEXT, ticket_kind TEXT, category TEXT, description TEXT, amount REAL, associate TEXT, file TEXT);
CREATE TABLE buy_items(store TEXT, ticket_no TEXT, category TEXT, description TEXT, amount REAL, win_start TEXT, win_end TEXT, file TEXT);
CREATE TABLE loan_items(store TEXT, ticket_no TEXT, disposition TEXT, disposition_date TEXT, due_date TEXT, pull_date TEXT, customer TEXT, amount REAL, age_days INT, category TEXT, description TEXT, last_payment TEXT, win_start TEXT, win_end TEXT, pulled TEXT, source TEXT, file TEXT);
CREATE TABLE layaway_snapshot(snap_date TEXT, store TEXT, layaway_no TEXT, status TEXT, last_payment TEXT, next_due TEXT, due_date TEXT, customer TEXT, amount REAL, age_days INT);
CREATE TABLE sales_ledger(store TEXT, sold_date TEXT, item_no TEXT, description TEXT, area TEXT, location TEXT, margin_pct REAL, discount_pct REAL, price_sold REAL, cost REAL, associate TEXT, channel TEXT, qty INT, file TEXT);
CREATE TABLE ticket_items(kind TEXT, store TEXT, ticket_no TEXT, category TEXT, description TEXT, disposition TEXT, disposition_date TEXT, due_date TEXT, pull_date TEXT, customer TEXT, amount REAL, age_days INT, written_date TEXT, last_payment TEXT, pulled TEXT, file TEXT);
CREATE TABLE ledger_files(file TEXT PRIMARY KEY, store TEXT, d1 TEXT, d2 TEXT, lines INT, cost REAL, price_sold REAL, report_total_cost REAL, ties INT, used INT);
CREATE TABLE eom_report(file TEXT PRIMARY KEY, store TEXT, d1 TEXT, d2 TEXT, full_month INT, pulled TEXT, inv_start REAL, inv_buys_qty REAL, inv_buys_amt REAL, inv_expirations_qty REAL, inv_expirations_amt REAL, returns_cost REAL, vendor_amt REAL, transfers_in REAL, transfers_out REAL, cos_qty REAL, cos_amt REAL, shrink_qty REAL, shrink_amt REAL, refined_qty REAL, refined_amt REAL, inv_end_qty REAL, inv_end REAL, loan_start REAL, lb_new_qty REAL, lb_new_amt REAL, lb_redeemed_qty REAL, lb_redeemed_amt REAL, lb_expired_qty REAL, lb_expired_amt REAL, loan_end_qty REAL, loan_end REAL, new_loans_n REAL, new_loans_amt REAL, buys_n REAL, buys_amt REAL, redemptions_n REAL, redemptions_principal REAL, instore_interest REAL, instore_fees REAL, instore_misc REAL, expired_buys_n REAL, expired_buys_amt REAL, net_sales REAL, sales_total REAL, cogs REAL, sales_profit REAL);
CREATE TABLE item_master(store TEXT, item_no TEXT, status TEXT, status_date TEXT, category TEXT, source TEXT, type TEXT, description TEXT, location TEXT, serial_no TEXT, sku TEXT, last_sold_to TEXT, customer TEXT, vendor TEXT, invoice_no TEXT, cost REAL, price REAL, last_sold_price REAL, date_to_inventory TEXT, inventory_age REAL, sale_price REAL, qty REAL, reference_no TEXT, last_ticket_no TEXT, manufacturer TEXT, model TEXT, jewelry_weight TEXT, metal_type TEXT, metal_purity TEXT, metal_weight TEXT, quality TEXT, win_start TEXT, win_end TEXT, file TEXT);
CREATE INDEX ix_im ON item_master(store,item_no);
CREATE INDEX ix_im_t ON item_master(store,last_ticket_no);
CREATE INDEX ix_ledger ON sales_ledger(store,item_no,sold_date);
CREATE INDEX ix_ticket ON ticket_items(store,ticket_no);
CREATE INDEX ix_snap ON inventory_snapshot(store,item_no,snap_date);
CREATE INDEX ix_sales ON item_sales(store,item_no,sold_date);
CREATE INDEX ix_buy ON buy_items(store,ticket_no);
CREATE INDEX ix_loan ON loan_items(store,ticket_no);
"""
VIEWS = """
CREATE VIEW v_item_origin AS SELECT i.store, i.item_no, i.status, i.status_date, i.category, i.source, i.type, i.last_ticket_no, CASE WHEN i.last_ticket_no GLOB '*-[0-9][0-9]' THEN substr(i.last_ticket_no,1,length(i.last_ticket_no)-3) ELSE i.last_ticket_no END ticket_no, i.date_to_inventory, i.cost, i.price, i.last_sold_price, i.customer, CASE WHEN i.date_to_inventory IS NOT NULL AND i.status IN ('SOLD','REFINED','SHRINK','DEFUNCT') THEN CAST(julianday(i.status_date)-julianday(i.date_to_inventory) AS INT) END days_in_inventory FROM item_master i;
CREATE VIEW v_eom_month AS SELECT substr(d1,1,7) month, e.* FROM eom_report e WHERE full_month=1 AND file=(SELECT MAX(file) FROM eom_report x WHERE x.store=e.store AND x.d1=e.d1 AND x.d2=e.d2);
CREATE VIEW v_tieout_sales AS SELECT e.store, e.month, ROUND(-e.cos_amt - COALESCE(e.returns_cost,0),2) eom_cost_net_returns, l.lines ledger_lines, l.cost ledger_cost, ROUND(l.cost - (-e.cos_amt - COALESCE(e.returns_cost,0)),2) diff, CASE WHEN l.cost IS NULL THEN 'no ledger' WHEN ABS(l.cost - (-e.cos_amt - COALESCE(e.returns_cost,0)))<0.015 THEN 'ties' ELSE 'unverified' END status FROM v_eom_month e LEFT JOIN (SELECT store, substr(sold_date,1,7) month, COUNT(*) lines, ROUND(SUM(cost),2) cost FROM sales_ledger GROUP BY 1,2) l ON l.store=e.store AND l.month=e.month;
CREATE VIEW v_inventory_latest AS SELECT * FROM inventory_snapshot WHERE snap_date=(SELECT MAX(snap_date) FROM inventory_snapshot);
CREATE VIEW v_item_first_seen AS SELECT store,item_no,MIN(since_date) since_date,MIN(snap_date) first_snap,MAX(snap_date) last_snap FROM inventory_snapshot GROUP BY store,item_no;
CREATE VIEW v_sales_with_age AS SELECT s.*, f.since_date, CAST(julianday(s.sold_date)-julianday(f.since_date) AS INT) days_to_sell
  FROM item_sales s LEFT JOIN v_item_first_seen f ON f.store=s.store AND f.item_no=s.item_no;
CREATE VIEW v_coverage AS SELECT dataset,store,COUNT(*) files,MIN(d1) first_day,MAX(d2) last_day,SUM(rows) rows,SUM(complete=0) partial_files FROM source_files GROUP BY dataset,store;
CREATE VIEW v_sales_coverage_by_month AS SELECT store,substr(sold_date,1,7) month,source,COUNT(*) lines,ROUND(SUM(cost),2) cost,ROUND(SUM(sold_price),2) sold FROM item_sales GROUP BY 1,2,3;
"""

def eom_parse(path):
    """One End of Month export (xlsx, or the csv some older pulls were converted to) -> dict of month figures.
    On Inventory Base / Loan Base lines the first qty,amount pair is the report's LAST DAY and the second pair is the MONTH."""
    rows = []
    if path.lower().endswith(".xlsx"):
        import openpyxl
        ws = openpyxl.load_workbook(path, data_only=True, read_only=True).active
        for r in ws.iter_rows(values_only=True):
            rows.append([x for x in r if x not in (None, "")])
    else:
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            for r in csv.reader(fh): rows.append([x for x in r if x != ""])
    def num(x):
        if isinstance(x, (int, float)): return float(x)
        try: return float(str(x).replace(",", "").replace("$", ""))
        except ValueError: return None
    def lab(r):
        if not r: return ""
        if str(r[0]).strip() == "-" and len(r) > 1: return "-" + str(r[1]).strip()
        return str(r[0]).strip()
    def nums(r):
        out = []
        for x in r[(2 if str(r[0]).strip() == "-" else 1):]:
            v = num(x)
            if v is None: break
            out.append(v)
        return out
    def find(label, after=0, exact=True):
        for i in range(after, len(rows)):
            l = lab(rows[i])
            if (l == label) if exact else l.startswith(label): return i
        return -1
    def m4(label, after=0, exact=True):
        i = find(label, after, exact)
        if i < 0: return (None, None)
        n = nums(rows[i])
        if len(n) >= 4: return (n[2], n[3])
        if len(n) == 2: return (None, n[1])
        return (None, None)
    def last(label, after=0, exact=True):
        i = find(label, after, exact)
        if i < 0: return None
        n = nums(rows[i])
        return n[-1] if n else None
    def at(label, k, after=0):
        i = find(label, after)
        if i < 0: return None
        n = nums(rows[i])
        return n[k] if len(n) > k else None
    rng = None
    for r in rows[:12]:
        for x in r:
            m = re.match(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*-\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$", str(x))
            if m:
                g = [int(v) for v in m.groups()]
                rng = (datetime.date(g[2], g[0], g[1]).isoformat(), datetime.date(g[5], g[3], g[4]).isoformat())
    if not rng: return None
    d = {"d1": rng[0], "d2": rng[1]}
    ib = find("Inventory Base"); lb = find("Loan Base"); pa = find("Pawn Activity"); ist = find("In-Store Txns"); sa = find("Sales Activity")
    if min(ib, lb, pa, ist, sa) < 0: return None
    d["inv_start"] = m4("Starting Inventory Base", ib, False)[1]
    d["inv_buys_qty"], d["inv_buys_amt"] = m4("Buys, Bought Loans, Trade-Ins", ib)
    d["inv_expirations_qty"], d["inv_expirations_amt"] = m4("Expirations", ib)
    d["returns_cost"] = m4("Returns (Cost of Sales)", ib)[1]
    d["vendor_amt"] = m4("Vendor Purchase/Return", ib)[1]
    d["transfers_in"] = m4("Transfers In", ib)[1]
    d["transfers_out"] = m4("-Transfers Out", ib)[1]
    d["cos_qty"], d["cos_amt"] = m4("-Sales (Cost of Sales)", ib)
    d["shrink_qty"], d["shrink_amt"] = m4("-Shrinkage", ib)
    d["refined_qty"], d["refined_amt"] = m4("-Refined (Cost of Sales)", ib)
    d["inv_end_qty"], d["inv_end"] = m4("Ending Inventory Base", ib, False)
    d["loan_start"] = m4("Starting Loan Base", lb, False)[1]
    d["lb_new_qty"], d["lb_new_amt"] = m4("New Loans", lb)
    d["lb_redeemed_qty"], d["lb_redeemed_amt"] = m4("-Redeemed Loans", lb)
    d["lb_expired_qty"], d["lb_expired_amt"] = m4("-Expired Loans", lb)
    d["loan_end_qty"], d["loan_end"] = m4("Ending Loan Base", lb, False)
    d["new_loans_n"] = at("New Loans", 0, pa); d["new_loans_amt"] = at("New Loans", 1, pa)
    d["buys_n"] = at("Buys", 0, pa); d["buys_amt"] = at("Buys", 1, pa)
    d["redemptions_n"] = at("Redemptions", 0, ist); d["redemptions_principal"] = at("Redemptions", 1, ist)
    d["instore_interest"] = at("In-Store Subtotal", 3, ist); d["instore_fees"] = at("In-Store Subtotal", 4, ist); d["instore_misc"] = at("In-Store Subtotal", 5, ist)
    d["expired_buys_n"] = at("Expired Buys / Trade-Ins", 0, ist); d["expired_buys_amt"] = at("Expired Buys / Trade-Ins", 1, ist)
    d["net_sales"] = last("Net Sales Subtotal", sa); d["sales_total"] = last("Sales Total", sa)
    d["cogs"] = last("-COGS", sa); d["sales_profit"] = last("Sales Revenue (Profit)", sa)
    return d

EOM_COLS = ["inv_start", "inv_buys_qty", "inv_buys_amt", "inv_expirations_qty", "inv_expirations_amt", "returns_cost", "vendor_amt", "transfers_in", "transfers_out", "cos_qty", "cos_amt", "shrink_qty", "shrink_amt", "refined_qty", "refined_amt", "inv_end_qty", "inv_end", "loan_start", "lb_new_qty", "lb_new_amt", "lb_redeemed_qty", "lb_redeemed_amt", "lb_expired_qty", "lb_expired_amt", "loan_end_qty", "loan_end", "new_loans_n", "new_loans_amt", "buys_n", "buys_amt", "redemptions_n", "redemptions_principal", "instore_interest", "instore_fees", "instore_misc", "expired_buys_n", "expired_buys_amt", "net_sales", "sales_total", "cogs", "sales_profit"]

def load_eom(db, names, reg):
    """All End of Month exports. Parsed figures are cached by file size and mtime (xlsx parsing is the slow part)."""
    cpath = os.path.join(PROJ, "Bravo Warehouse", "cache", "eom_cache.json")
    try: cache = json.load(open(cpath))
    except Exception: cache = {}
    new = {}
    for f in names:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})_([A-Z]{3})_end-of-month\.(xlsx|csv)$", f)
        if not m or m.group(2) not in STORES: continue
        p = os.path.join(OUT, f); st_ = os.stat(p); key = f"{st_.st_size}:{int(st_.st_mtime)}"
        c = cache.get(f)
        if c and c.get("key") == key: d = c.get("d"); new[f] = c
        else:
            try: d = eom_parse(p); new[f] = {"key": key, "d": d}
            except Exception as e: d = None   # not cached, so a later build retries it
        if not d or d.get("cos_amt") is None or not d.get("inv_end") or not d.get("loan_end"):
            reg(f, "eom", m.group(2), d["d1"] if d else None, d["d2"] if d else None, 0, 0, "unreadable or structurally empty"); continue
        d1 = datetime.date.fromisoformat(d["d1"]); d2 = datetime.date.fromisoformat(d["d2"])
        full = int(d1.day == 1 and d1.strftime("%Y-%m") == d2.strftime("%Y-%m") and (d2 + datetime.timedelta(1)).day == 1)
        db.execute("INSERT INTO eom_report VALUES(" + ",".join("?" * (6 + len(EOM_COLS))) + ")", [f, m.group(2), d["d1"], d["d2"], full, datetime.date.fromtimestamp(st_.st_mtime).isoformat()] + [d.get(k) for k in EOM_COLS])
        reg(f, "eom", m.group(2), d["d1"], d["d2"], 1, 1, "full month" if full else "")
    try:
        os.makedirs(os.path.dirname(cpath), exist_ok=True)
        with open(cpath + ".tmp", "w") as fh: json.dump(new, fh)
        os.replace(cpath + ".tmp", cpath)
    except Exception: pass

def main():
    out = os.path.join(PROJ, "Bravo Warehouse", "bravo_warehouse.sqlite")
    tmpdir = None
    a = sys.argv[1:]
    if "--out" in a: out = a[a.index("--out") + 1]
    if "--tmp" in a: tmpdir = a[a.index("--tmp") + 1]
    tmpdir = tmpdir or tempfile.mkdtemp(prefix="bravo_wh_")
    os.makedirs(tmpdir, exist_ok=True)
    tmp = os.path.join(tmpdir, "build.sqlite")
    if os.path.exists(tmp): os.remove(tmp)
    db = sqlite3.connect(tmp); db.executescript(DDL)
    names = sorted(os.listdir(OUT))
    def reg(f, ds, st, d1, d2, n, complete=1, note=""):
        db.execute("INSERT OR REPLACE INTO source_files VALUES(?,?,?,?,?,?,?,?)", (f, ds, st, d1, d2, n, complete, note))
    def meta_ok(f, n):
        p = os.path.join(OUT, f + ".meta")
        if not os.path.isfile(p): return 1, ""
        m = dict(l.strip().split("=", 1) for l in open(p, encoding="utf-8-sig") if "=" in l)
        return (1, "") if str(n) == m.get("expected", str(n)) else (0, f"rows {n} vs Bravo {m.get('expected')}")
    sold_days = set()
    pat_day = re.compile(r"^(\d{4}-\d{2}-\d{2})_([A-Z]{3})_(.+)$")
    pat_rng = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:_to_|\.\.)(\d{4}-\d{2}-\d{2})_([A-Z]{3})_(.+)$")
    for f in names:
        m = pat_rng.match(f); d1 = d2 = st = cell = None
        if m: d1, d2, st, cell = m.groups()
        else:
            m = pat_day.match(f)
            if m: d1, st, cell = m.groups(); d2 = d1
        if not m or st not in STORES: continue
        p = os.path.join(OUT, f)
        if cell == "instock-all.tsv":
            h, b = read(p, "\t")
            if "Number" not in h: continue
            ok, note = meta_ok(f, len(b)); reg(f, "inventory_snapshot", st, d1, d2, len(b), ok, note)
            if not ok: continue
            db.executemany("INSERT INTO inventory_snapshot VALUES(?,?,?,?,?,?,?,?,?)", [(d1, st, col(h, r, "Number"), col(h, r, "Status"), col(h, r, "Category"), col(h, r, "Description"), money(col(h, r, "Cost")), money(col(h, r, "Price")), iso(col(h, r, "Date"))) for r in b])
        elif cell == "items-to-price.csv":
            h, b = read(p)
            if "Number" not in h: continue
            reg(f, "unpriced_snapshot", st, d1, d2, len(b))
            db.executemany("INSERT INTO unpriced_snapshot VALUES(?,?,?,?,?,?,?,?,?,?)", [(d1, st, col(h, r, "Number"), col(h, r, "Status"), col(h, r, "Category"), col(h, r, "Type"), col(h, r, "Description"), col(h, r, "Location"), money(col(h, r, "Cost")), iso(col(h, r, "Date"))) for r in b])
        elif cell == "sold-discount-detail.csv":
            h, b = read(p)
            if "Number" not in h: continue
            reg(f, "item_sales", st, d1, d2, len(b))
            for r in b:
                sd = iso(col(h, r, "Date"))
                db.execute("INSERT INTO item_sales VALUES(?,?,?,?,?,?,?,?,?,?,?)", (st, col(h, r, "Number"), sd, col(h, r, "Category"), col(h, r, "Description"), money(col(h, r, "Cost")), money(col(h, r, "Price")), money(col(h, r, "Last Sold Price")), "sold-discount-detail", 1, f))
            dd = datetime.date.fromisoformat(d1)
            while dd <= datetime.date.fromisoformat(d2): sold_days.add((st, dd.isoformat())); dd += datetime.timedelta(1)
        elif cell == "intake-detail.csv":
            h, b = read(p)
            if "Ticket Kind" not in h: continue
            reg(f, "intake_items", st, d1, d2, len(b))
            db.executemany("INSERT INTO intake_items VALUES(?,?,?,?,?,?,?,?,?)", [(st, d1, d2, col(h, r, "Ticket Kind"), col(h, r, "Category"), col(h, r, "Full Description"), money(col(h, r, "Loan Amount")), col(h, r, "Associate"), f) for r in b])
        elif cell == "buys-from-public.csv":
            h, b = read(p)
            if "Ticket Number" not in h: continue
            reg(f, "buy_items", st, d1, d2, len(b))
            db.executemany("INSERT INTO buy_items VALUES(?,?,?,?,?,?,?,?)", [(st, col(h, r, "Ticket Number"), col(h, r, "Category"), col(h, r, "Full Description"), money(col(h, r, "Loan Amount")), d1, d2, f) for r in b])
        elif cell in ("loan-portfolio-2026.csv", "loan-reminders.csv") or cell.startswith("pm-loan-growth-p") and cell.endswith(".csv"):
            h, b = read(p)
            if "Ticket Number" not in h: continue
            src = cell.split(".")[0]
            ok, note = meta_ok(f, len(b)); reg(f, "loan_items:" + ("pm-loan-growth" if src.startswith("pm-") else src), st, d1, d2, len(b), ok, note)
            ws, we = (d1, d2) if src == "loan-portfolio-2026" else (None, None)
            def ai(x):
                try: return int(x)
                except ValueError: return None
            db.executemany("INSERT INTO loan_items VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [(st, col(h, r, "Ticket Number"), col(h, r, "Disposition"), iso(col(h, r, "Disposition Date")), iso(col(h, r, "Due Date")), iso(col(h, r, "Pull Date")), col(h, r, "Customer"), money(col(h, r, "Loan Amount")), ai(col(h, r, "Age")), col(h, r, "Category"), col(h, r, "Full Description"), iso(col(h, r, "Last Payment")), ws, we, d2 if src != "loan-portfolio-2026" else None, src, f) for r in b])
        elif cell == "layaway-detail-all-active.tsv":
            h, b = read(p, "\t")
            if "Layaway Number" not in h: continue
            reg(f, "layaway_snapshot", st, d1, d2, len(b))
            def ai(x):
                try: return int(x)
                except ValueError: return None
            db.executemany("INSERT INTO layaway_snapshot VALUES(?,?,?,?,?,?,?,?,?,?)", [(d1, st, col(h, r, "Layaway Number"), col(h, r, "Status"), iso(col(h, r, "Last Payment")), iso(col(h, r, "Next Due")), iso(col(h, r, "Due Date")), col(h, r, "Customer"), money(col(h, r, "Layaway Amount")), ai(col(h, r, "Age"))) for r in b])
    # ---- sales ledger: Bravo's built-in Sold Inventory report (cell sold-inventory). Ties to End of Month
    # "Sales (Cost of Sales)" net of returns (proven LEX 8/1-8/27/2026: 11,028.32). Each file's own Total line is
    # checked; a file that does not add up to its Total is not used. Longest windows win; a window that overlaps
    # one already loaded for the store is skipped.
    cand = []
    for f in names:
        m = pat_day.match(f)
        if not m or m.group(3) != "sold-inventory.csv" or m.group(2) not in STORES: continue
        st = m.group(2)
        try: raw = list(csv.reader(io.StringIO(open(os.path.join(OUT, f), encoding="utf-8-sig", errors="replace", newline="").read())))
        except OSError: continue
        rng = None; hdr = None; area = ""; lines = []; rep_total = None
        for r in raw:
            c = [x.strip() for x in r]
            if rng is None:
                for x in c:
                    mm = re.match(r"(\d{1,2}/\d{1,2}/\d{4}) - (\d{1,2}/\d{1,2}/\d{4})$", x)
                    if mm: rng = (iso(mm[1]), iso(mm[2]))
            if c and c[0] == "Business Date Sold": hdr = c; continue
            if hdr is None or not c or not c[0]: continue
            if c[0].startswith("Total:"): rep_total = money(c[hdr.index("Cost")]) if len(c) > hdr.index("Cost") else None; continue
            if c[0].startswith("Subtotal:") or c[0].startswith("Report printed"): continue
            sd = iso(c[0])
            if not sd:
                if not any(c[1:]): area = c[0]
                continue
            g = lambda k: (c[hdr.index(k)] if k in hdr and hdr.index(k) < len(c) else "")
            desc = g("Full Description"); q = re.match(r"Quantity (\d+) - ", desc)
            pct = lambda x: (float(x.replace("%", "").replace(",", "")) if x.replace("%", "").replace(",", "").replace(".", "").replace("-", "").isdigit() else None)
            lines.append((st, sd, g("Item Num"), desc, area, g("Location"), pct(g("Margin %")), pct(g("Discount %")), money(g("Price Sold")), money(g("Cost")), g("Associate"), g("Omni-Channel"), int(q[1]) if q else 1, f))
        if rng is None or hdr is None: continue
        cost = round(sum(x[9] or 0 for x in lines), 2); ps = round(sum(x[8] or 0 for x in lines), 2)
        ties = 1 if (rep_total is not None and abs(cost - rep_total) < 0.02) or (rep_total is None and not lines) else 0
        cand.append((rng[1] > rng[0], (datetime.date.fromisoformat(rng[1]) - datetime.date.fromisoformat(rng[0])).days, f, st, rng, lines, cost, ps, rep_total, ties))
    taken = {}
    for _, span, f, st, rng, lines, cost, ps, rep_total, ties in sorted(cand, key=lambda x: (-x[1], x[2])):
        overlap = any(not (rng[1] < a or rng[0] > b) for a, b in taken.get(st, []))
        used = 1 if ties and not overlap else 0
        db.execute("INSERT OR REPLACE INTO ledger_files VALUES(?,?,?,?,?,?,?,?,?,?)", (f, st, rng[0], rng[1], len(lines), cost, ps, rep_total, ties, used))
        if used:
            taken.setdefault(st, []).append(rng)
            db.executemany("INSERT INTO sales_ledger VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", lines)
            reg(f, "sales_ledger", st, rng[0], rng[1], len(lines), 1, "")
        elif not ties:
            reg(f, "sales_ledger", st, rng[0], rng[1], len(lines), 0, f"lines add to {cost} but report Total is {rep_total}")
    # ---- loans / buys written (cells loans-written, buys-written; FDP layout, count-checked by FwbRun)
    for f in names:
        m = pat_day.match(f)
        if not m or m.group(3) not in ("loans-written.csv", "buys-written.csv") or m.group(2) not in STORES: continue
        d2, st, cell = m.groups(); kind = "LOAN" if cell.startswith("loans") else "BUY"
        p = os.path.join(OUT, f); h, b = read(p)
        if "Ticket Number" not in h: continue
        ok, note = meta_ok(f, len(b))
        pulled = datetime.date.fromtimestamp(os.path.getmtime(p))
        reg(f, "ticket_items:" + kind, st, d2[:8] + "01", d2, len(b), ok, note)
        if not ok: continue
        for r in b:
            try: age = int(col(h, r, "Age"))
            except ValueError: age = None
            wd = (pulled - datetime.timedelta(age)).isoformat() if age is not None else None
            db.execute("INSERT INTO ticket_items VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (kind, st, col(h, r, "Ticket Number"), col(h, r, "Category"), col(h, r, "Full Description"), col(h, r, "Disposition"), iso(col(h, r, "Disposition Date")), iso(col(h, r, "Due Date")), iso(col(h, r, "Pull Date")), col(h, r, "Customer"), money(col(h, r, "Loan Amount")), age, wd, iso(col(h, r, "Last Payment")), pulled.isoformat(), f))
    # history pulls (cell sold-history, clipboard copy, count-checked). Used for days the daily feed does not cover.
    hist_days = set()
    for f in names:
        m = pat_rng.match(f)
        if not m or m.group(4) != "sold-history.tsv" or m.group(3) not in STORES: continue
        d1, d2, st, _ = m.groups()
        h, b = read(os.path.join(OUT, f), "\t")
        if "Number" not in h: continue
        ok, note = meta_ok(f, len(b)); n = 0
        if ok:
            for r in b:
                sd = iso(col(h, r, "Date"))
                if not sd or (st, sd) in sold_days: continue
                db.execute("INSERT INTO item_sales VALUES(?,?,?,?,?,?,?,?,?,?,?)", (st, col(h, r, "Number"), sd, col(h, r, "Category"), col(h, r, "Description"), money(col(h, r, "Cost")), money(col(h, r, "Price")), money(col(h, r, "Last Sold Price")), "sold-history", 1, f)); n += 1
        reg(f, "item_sales", st, d1, d2, n, ok, note)
        if ok:
            dd = datetime.date.fromisoformat(d1)
            while dd <= datetime.date.fromisoformat(d2): hist_days.add((st, dd.isoformat())); dd += datetime.timedelta(1)
    sold_days |= hist_days
    # history: the May 2025 - May 2026 sold pull (Deep KPI analysis). Used only for days the daily feed does not cover.
    for st in STORES:
        f = f"sold_inv_{st}_2025-05-17_to_2026-05-17.csv"; p = os.path.join(DEEP, f)
        if not os.path.isfile(p): continue
        h, b = read(p); n = 0
        for r in b:
            sd = iso(col(h, r, "Date"))
            if not sd or (st, sd) in sold_days or col(h, r, "Status") != "SOLD": continue
            db.execute("INSERT INTO item_sales VALUES(?,?,?,?,?,?,?,?,?,?,?)", (st, col(h, r, "Number"), sd, col(h, r, "Category"), col(h, r, "Description"), money(col(h, r, "Cost")), money(col(h, r, "Price")), money(col(h, r, "Last Sold Price")), "sold-history-2025-26", 1, f)); n += 1
        reg(f, "item_sales", st, "2025-05-17", "2026-05-17", n, 1, "one-time history pull 2026-05-17")
    # item master (cell item-master: saved report "Claude Item Master", every status, by status date; clipboard copy, count-checked).
    # One row per item as it stood when pulled: where it came from (source, type, last ticket), when it hit inventory, and how it ended.
    for f in names:
        m = pat_rng.match(f)
        if not m or m.group(4) != "item-master.tsv" or m.group(3) not in STORES: continue
        d1, d2, st, _ = m.groups()
        h, b = read(os.path.join(OUT, f), "\t")
        if "Last Ticket Number" not in h: continue
        ok, note = meta_ok(f, len(b)); n = 0
        if ok:
            for r in b:
                db.execute("INSERT INTO item_master VALUES(" + ",".join("?" * 34) + ")", (st, col(h, r, "Number"), col(h, r, "Status"), iso(col(h, r, "Date")), col(h, r, "Category"), col(h, r, "Source"), col(h, r, "Type"), col(h, r, "Description"), col(h, r, "Location"), col(h, r, "Serial Number"), col(h, r, "SKU Number"), col(h, r, "Last Sold To"), col(h, r, "Customer"), col(h, r, "Vendor"), col(h, r, "Invoice #"), money(col(h, r, "Cost")), money(col(h, r, "Price")), money(col(h, r, "Last Sold Price")), iso(col(h, r, "Date to Inventory")), money(col(h, r, "Inventory Age")), money(col(h, r, "Sale Price")), money(col(h, r, "Quantity")), col(h, r, "Reference Number"), col(h, r, "Last Ticket Number"), col(h, r, "Manufacturer"), col(h, r, "Model"), col(h, r, "Total Jewelry Weight"), col(h, r, "Metal Type/Color"), col(h, r, "Metal Purity"), col(h, r, "Metal Weight"), col(h, r, "Quality"), d1, d2, f)); n += 1
        reg(f, "item_master", st, d1, d2, n, ok, note)
    load_eom(db, names, reg)
    db.executescript(VIEWS)
    db.execute("CREATE TABLE build_info(built_at TEXT, note TEXT)")
    db.execute("INSERT INTO build_info VALUES(?,?)", (datetime.datetime.now().isoformat(timespec="seconds"), "full rebuild from pipeline output"))
    db.commit()
    cov = db.execute("SELECT * FROM v_coverage ORDER BY 1,2").fetchall()
    tie = db.execute("SELECT month,store,eom_cost_net_returns,ledger_lines,ledger_cost,diff,status FROM v_tieout_sales ORDER BY 1 DESC,2").fetchall()
    db.execute("VACUUM"); db.close()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    part = out + ".part"; shutil.copyfile(tmp, part); os.replace(part, out)
    with open(os.path.join(os.path.dirname(out), "COVERAGE.md"), "w") as fh:
        fh.write(f"# Bravo warehouse coverage\n\nBuilt {datetime.datetime.now():%Y-%m-%d %H:%M}. Regenerated on every build.\n\n| Dataset | Store | Files | First day | Last day | Rows | Partial files |\n|---|---|---|---|---|---|---|\n")
        for c in cov: fh.write("| " + " | ".join(str(x) for x in c) + " |\n")
        fh.write("\n## Sales check against End of Month, by store and month\n\nBravo's End of Month cost of sales less returns, against the sales ledger in the warehouse. Only months marked ties are safe for totals. Months with no End of Month file on disk are not listed.\n\n| Month | Store | End of Month cost | Ledger lines | Ledger cost | Difference | Status |\n|---|---|---|---|---|---|---|\n")
        for c in tie: fh.write("| " + " | ".join("" if x is None else str(x) for x in c) + " |\n")
    print(json.dumps({"out": out, "datasets": len(cov)}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
