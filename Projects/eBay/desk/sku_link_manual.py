#!/usr/bin/env python3
"""Write reviewed Bravo numbers to SKU (2026-11-24; residual matches checked by eye against Bravo's eBay-marked items).
Only empty SKUs; skips a number already on another live listing. Ledger engine/ledger.jsonl. Usage: [--apply]"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "engine")); sys.path.insert(0, HERE)
import ebay_common as ec, desk_core as dc
from xml.sax.saxutils import escape
M = {"Culpeper": {"920082388061":"VP4033624","398443784275":"VP4024928","920097427600":"VP4033837","398363464853":"VP4024293","398257738891":"VP4029334",
 "398260905935":"VP4031971","398370757701":"VP4032436","398264464111":"VP4028400","398264473829":"VP4027903","398264522352":"VP4026216",
 "920024738251":"VP4033150","920027080706":"VP4032242","920027093411":"VP4032241","920027779249":"VP4031988","920131323599":"VP4034060",
 "398387695829":"VP4028438","398387713701":"VP4031977","398387737196":"VP4031976","398387740516":"VP4031975","398387745606":"VP4031974",
 "398387954679":"VP4031973","398387981933":"VP4031972","398278730026":"VP4030129","920033763965":"VP4032546","920149552580":"VP4034051",
 "920149864536":"VP4033166","920149876746":"VP4033165","920150049121":"VP4026337","398305219837":"VP4031740","920165816170":"VP4034273",
 "920168513158":"VP4034220","398314263430":"VP4032217"},
 "Roanoke": {"306644339361":"GP2005740"},
 "Waynesboro": {"800833896135":"VAP033758","800856308832":"VAP033984","800856308878":"VAP033983","800860349668":"VAP032463","800860351349":"VAP032465",
 "800860363979":"VAP032705","800856970948":"VAP032649","800857004530":"VAP032708","800868700933":"VAP032274","800868802619":"VAP030807",
 "800897797592":"VAP034451","800508951779":"VAP029474","800508951928":"VAP029476","800508951938":"VAP029478","800548737480":"VAP031891"},
 "Harrisonburg": {"800845278493":"VA5021342","800123750148":"VA5019021","800764651289":"VA5020475","387902916408":"SLM000564","800817566404":"VA5020770"},
 "Lexington": {"158278894417":"VA1054631"}}
apply = "--apply" in sys.argv; run_id = time.strftime("%Y%m%d-%H%M%S") + "-skulink-reviewed"; ok = fail = skip = 0
for store, m in M.items():
    live = {i["ItemID"]: i for i in ec.active_items(ec.token_for(store))}
    used = {i["SKU"].strip().upper() for i in live.values() if i["SKU"].strip()}
    for iid, b in m.items():
        it = live.get(iid)
        if not it or it["SKU"].strip() or b in used: skip += 1; continue
        used.add(b)
        if not apply: ok += 1; continue
        good, err = ec.revise(ec.token_for(store), iid, "<SKU>%s</SKU>" % escape(b))
        ec.ledger_append({"run_id": run_id, "store": store, "ItemID": iid, "action": "sku_set", "before": "", "after": b, "source": "reviewed-residual", "ok": good, "err": [e[1] for e in err][:1] if not good else []})
        ok += good; fail += (not good)
        if not good: print("FAIL", store, iid, err[:1])
        time.sleep(0.2)
print("run_id=%s %s=%d failed=%d skipped=%d" % (run_id, "applied" if apply else "would apply", ok, fail, skip))
