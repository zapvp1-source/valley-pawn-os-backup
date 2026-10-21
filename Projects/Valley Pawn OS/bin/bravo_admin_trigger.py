#!/usr/bin/env python3
"""
bravo_admin_trigger.py — drop a Bravo System-Configuration admin job and wait for it.

Hands-free path for the two write cells in Bravo Data Extraction/reports/StoreConfigAdmin.ahk:
  employee-status  set an employee's Bravo login status (TERMINATED / CURRENT / UNKNOWN)
  store-hours      set a store's "Store Hours" text

Runs from either the Mac or a Cowork Linux session (pass --base to the mounted
Projects path). It writes the trigger atomically, polls results/<id>.result.json,
prints the cell outcome and the plain-text note the handler wrote, and exits
0 only when the handler reported status=success.

Examples
  # Offboard (the normal case). Default mode is PROBE (read-only) — pass --live to change anything.
  bravo_admin_trigger.py employee-status --store ROA --name "JACOB COX" --status TERMINATED --live
  # Store hours
  bravo_admin_trigger.py store-hours --store WAY --hours "Mon - Fri: 10am - 6pm | Sat: 10am - 5pm | Sun: Closed" --live
  # Read-only check of what Bravo currently shows
  bravo_admin_trigger.py store-hours --store HAR

Contention: the watcher serialises triggers itself (atomic claim), so this needs
no foreground guard. It will simply queue behind an in-flight pull.
"""
import argparse, json, os, sys, time, datetime, re

DEFAULT_BASE = os.path.expanduser("~/Documents/Claude/Projects")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cell", choices=["employee-status", "store-hours"])
    ap.add_argument("--store", required=True, help="3-letter store code: CUL HAR LEX ROA WAY")
    ap.add_argument("--name", help="employee as shown in Bravo's tree, e.g. 'JACOB COX'")
    ap.add_argument("--status", default="TERMINATED", help="TERMINATED | CURRENT | UNKNOWN")
    ap.add_argument("--hours", help="exact Store Hours text (max 100 chars, no double quotes)")
    ap.add_argument("--live", action="store_true", help="actually edit + save (default is read-only probe)")
    ap.add_argument("--dryedit", action="store_true", help="employee-status only: Edit, pick status, Cancel — saves nothing")
    ap.add_argument("--base", default=DEFAULT_BASE, help="Projects folder (mounted path in a Linux session)")
    ap.add_argument("--timeout", type=int, default=1500, help="seconds to wait for the result (default 25 min)")
    ap.add_argument("--no-wait", action="store_true")
    a = ap.parse_args()

    store = a.store.upper()
    if store not in ("CUL", "HAR", "LEX", "ROA", "WAY"):
        sys.exit("bad store code")
    mode = "live" if a.live else ("dryedit" if a.dryedit else "probe")
    if a.cell == "employee-status":
        if not a.name:
            sys.exit("--name is required")
        if '"' in a.name or "~" in a.name:
            sys.exit("name may not contain quotes or ~")
        params = f"store={store}~name={a.name.upper().strip()}~status={a.status.upper()}~mode={mode}"
        slug = "empstat"
    else:
        hours = a.hours or ""
        if a.live and not hours:
            sys.exit("--hours is required with --live")
        if '"' in hours or "~" in hours or len(hours) > 100:
            sys.exit("hours may not contain quotes or ~, max 100 chars")
        params = f"store={store}~hours={hours}~mode={mode}"
        slug = "hours"

    bde = os.path.join(a.base, "Bravo Data Extraction")
    trig_dir, res_dir, log_dir = (os.path.join(bde, d) for d in ("triggers", "results", "logs"))
    if not os.path.isdir(trig_dir):
        sys.exit(f"triggers folder not found: {trig_dir}")

    now = datetime.datetime.now().astimezone()
    tid = f"{slug}-{store}-{now.strftime('%Y%m%d-%H%M%S')}"
    body = {"id": tid, "requested_at": now.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "reports": [{"name": a.cell, "stores": [store], "date": params}]}
    tmp = os.path.join(trig_dir, f".{tid}.json.tmp")
    final = os.path.join(trig_dir, f"{tid}.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(body, f)
    os.replace(tmp, final)
    print(f"dropped {final}\n  {a.cell} {params}")
    if a.no_wait:
        return 0

    res = os.path.join(res_dir, f"{tid}.result.json")
    crash = os.path.join(res_dir, f"{tid}.crash.json")
    t0 = time.time()
    while time.time() - t0 < a.timeout:
        if os.path.exists(res) or os.path.exists(crash):
            break
        time.sleep(10)
    else:
        print(f"TIMEOUT after {a.timeout}s — still queued or running. Check {log_dir}/{tid}.log")
        return 2
    if os.path.exists(crash):
        print("CRASH:", open(crash, encoding="utf-8-sig", errors="replace").read()[:800]); return 1
    r = json.load(open(res, encoding="utf-8-sig"))
    ok = False
    for c in r.get("cells", []):
        print(f"{c.get('report')} {c.get('store')}: {c.get('status')}  {c.get('error','')}")
        ok = ok or (c.get("status") == "success")
        op = c.get("output_path", "")
        # translate a Windows Y:\ or UNC path back to the mounted base
        m = re.search(r"Bravo Data Extraction[\\/](.*)$", op)
        if m:
            local = os.path.join(bde, m.group(1).replace("\\", "/"))
            if os.path.exists(local):
                print("---- note ----"); print(open(local, encoding="utf-8", errors="replace").read().strip())
    for e in r.get("errors", []):
        print("ERROR:", e)
    print("log:", os.path.join(log_dir, f"{tid}.log"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
