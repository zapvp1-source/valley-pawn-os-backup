#!/usr/bin/env python3
"""capex_drive_put.py <staging_dir> [--apply] | --list   (2026-10-23)

WHY: the quarterly capex sweep runs as a cloud scheduled task. It can READ the property folders through the
Google Drive connector, but the connector cannot replace an existing file's contents, so updated CAP GAIN
tracker workbooks and copied source documents could never land back in Drive (the old version of the task
relied on a Mac connector that no longer exists). This script is the write leg: the cloud run stages files in
  Projects/Taxes 2026/capex_sweeps/<YYYY-QN>/   with a manifest.json
and drops a host_queue job calling this script; vp-runner (which can write the Drive desktop-sync folder)
places them.

manifest.json = {"items": [{"src": "<file in staging dir>", "dest_rel": "02 Real Estate/<...>/<file>",
                            "mode": "replace_tracker" | "copy_new"}]}
SAFETY  * dest_rel must start with "02 Real Estate/" and its folder path must contain "cap gain" (any case)
        * replace_tracker: only .xlsx, destination must already exist; the old file is backed up to
          Projects/Taxes 2026/capex_sweeps/_backups/<stamp>__<name> first
        * copy_new: never overwrites (skipped if the name exists)
        * nothing is ever deleted; dry run unless --apply; result written to <staging_dir>/result.json
"""
import datetime as dt, json, os, shutil, sys
HOME = os.path.expanduser("~")
DRIVE = os.path.join(HOME, "Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive")
PROJ = os.path.join(HOME, "Documents/Claude/Projects")
STAGE_ROOT = os.path.join(PROJ, "Taxes 2026/capex_sweeps")
BACKUP = os.path.join(STAGE_ROOT, "_backups")

def list_folders():
    root = os.path.join(DRIVE, "02 Real Estate")
    print("drive root exists:", os.path.isdir(root))
    for dp, dn, fn in os.walk(root):
        if "cap gain" in dp.lower():
            print(dp.replace(DRIVE + "/", ""), "|", ", ".join(sorted(fn))[:400])
            dn[:] = []

def main():
    if "--list" in sys.argv:
        return list_folders()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__); sys.exit(2)
    sd = os.path.realpath(args[0] if os.path.isabs(args[0]) else os.path.join(STAGE_ROOT, args[0]))
    if not sd.startswith(os.path.realpath(STAGE_ROOT) + "/"):
        print("REFUSED: staging dir must be under", STAGE_ROOT); sys.exit(2)
    apply = "--apply" in sys.argv
    man = json.load(open(os.path.join(sd, "manifest.json")))
    out, stamp = [], dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for it in man.get("items", []):
        src = os.path.join(sd, os.path.basename(it["src"]))
        rel = it["dest_rel"].lstrip("/")
        dest = os.path.realpath(os.path.join(DRIVE, rel))
        r = {"src": it["src"], "dest_rel": rel, "mode": it.get("mode")}
        if not rel.startswith("02 Real Estate/") or "cap gain" not in os.path.dirname(rel).lower() \
           or not dest.startswith(os.path.realpath(DRIVE) + "/"):
            r["result"] = "REFUSED: destination outside a CAP GAIN folder"
        elif not os.path.isfile(src):
            r["result"] = "MISSING staged file"
        elif not os.path.isdir(os.path.dirname(dest)):
            r["result"] = "MISSING destination folder"
        elif it.get("mode") == "replace_tracker":
            if not dest.lower().endswith(".xlsx") or not os.path.isfile(dest):
                r["result"] = "REFUSED: replace_tracker needs an existing .xlsx"
            elif apply:
                os.makedirs(BACKUP, exist_ok=True)
                shutil.copy2(dest, os.path.join(BACKUP, stamp + "__" + os.path.basename(dest)))
                shutil.copy2(src, dest); r["result"] = "REPLACED (backup kept)"
            else:
                r["result"] = "WOULD REPLACE"
        elif it.get("mode") == "copy_new":
            if os.path.exists(dest):
                r["result"] = "SKIPPED: already exists"
            elif apply:
                shutil.copy2(src, dest); r["result"] = "COPIED"
            else:
                r["result"] = "WOULD COPY"
        else:
            r["result"] = "REFUSED: unknown mode"
        out.append(r); print(r["result"], "|", rel)
    json.dump({"ran": stamp, "apply": apply, "items": out}, open(os.path.join(sd, "result.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
