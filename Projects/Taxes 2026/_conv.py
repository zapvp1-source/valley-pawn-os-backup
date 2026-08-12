import json, glob, os, sys
pat = "/var/folders/6k/_z_8cvwd09v5v4cglg57t9_c0000gn/T/claude-hostloop-plugins/*/projects/*/*/tool-results/*.json"
fs = sorted(glob.glob(pat), key=os.path.getmtime, reverse=True)[:8]
out = os.path.expanduser("~/Documents/Claude/Projects/Taxes 2026/_raw")
os.makedirs(out, exist_ok=True)
for f in fs:
    try:
        d = json.load(open(f))
    except Exception:
        continue
    txt = ""
    if isinstance(d, list):
        for b in d:
            if isinstance(b, dict) and b.get("type") == "text":
                txt += b.get("text", "")
    if len(txt) < 5000:
        continue
    head = txt[:400].lower()
    if "1120-s" in head or "full circle" in head:
        nm = "REQ_1120S.md"
    elif "1040" in head or "davis" in head:
        nm = "REQ_1040.md"
    else:
        nm = "REQ_" + os.path.basename(f)[:12] + ".md"
    p = os.path.join(out, nm)
    open(p, "w").write(txt)
    print("wrote", p, len(txt))
