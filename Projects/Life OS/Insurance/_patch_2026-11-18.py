import json

path = "INSURANCE_REGISTRY.json"
with open(path) as f:
    d = json.load(f)

today = "2026-11-18"

def find(pid):
    for p in d["policies"]:
        if p.get("id") == pid:
            return p
    raise KeyError(pid)

# --- RE-BALDROCK-STR: final policy document delivered 11/17 ---
p = find("RE-BALDROCK-STR")
p["policy_number"] = "PIV301688"
p["premium_notes"] = (p.get("premium_notes","") +
    " FINAL POLICY NUMBER PIV301688 confirmed 11/17/2026 via Proper Insurance Policy Delivery email "
    "(supersedes binder ref PIV20260922140051, which remains the binder/quote reference). "
    "Total Cost of Insurance $6,507.19 and $10,000 property deductible both reconfirmed on the issued policy.")
p["open_issues"] = [
    "FINAL (per 11/17/2026 Policy Delivery, supersedes the earlier generic 30-day list): pool depth-marker photos "
    "(at least 4 pool sides, max depth indicated) due 12/17/2026 — required for underwriting to continue coverage.",
    "Waiver language requirement: Proper's underwriter requires waiver language in the rental agreement for any of: "
    "hot tubs, bicycles, boats/watercraft, exercise equipment, sauna, bunk beds, a loft accessed by ladder, or "
    "swimming in a natural body of water. Need to confirm which of these amenities Bald Rock actually offers and "
    "that the rental agreement's waiver language covers them (Joshua's call, recommend involving a lawyer per Proper's own note).",
    "Cancel Homesite 39168908 pro-rata eff 11/9 — still Joshua's own action, unconfirmed as done.",
    "Optional $50/yr squatters coverage declined on application - Joshua's call.",
    "Update named insured paperwork when deed moves to Farming Infinity Mountains LLC (no premium change per Rikki).",
]
p["documents"].append(
    "Gmail 1a1ebd42a73882a2 (11/17/2026 11:25pm ET, Reed Newman/Proper Account Services): Proper Insurance Policy "
    "Delivery — PIV301688.pdf attached (final issued policy, not just the EPI/binder)."
)
p["status"] = p["status"] + (
    " UPDATE 2026-11-18 (insurance-inbox-watch): final issued policy document (PIV301688) delivered 11/17 11:25pm ET "
    "— this is the actual policy, not just the EPI/binder. Confirms Total Cost of Insurance $6,507.19 and $10,000 "
    "property deductible. One underwriting condition remains open with a hard date: pool depth-marker photos due "
    "12/17/2026 (see open_issues) — the earlier mortgagee-contact and pool-fence asks are no longer repeated in this "
    "final delivery, so treat those as satisfied."
)
p["last_verified"] = today

# --- RE-RICHMOND-817: Joshua sent bind instruction 11/17 ---
p = find("RE-RICHMOND-817")
p["status"] = p["status"] + (
    " UPDATE 2026-11-18 (insurance-inbox-watch): Joshua sent the bind instruction to Howard Baker 11/17 3:35pm ET "
    "(thread 1a145f65c8f27040) — bind the 817 Richmond standalone LRO policy in Farming Infinity, LLC's name per "
    "the 10/16 quote ($3,505.31/yr, $10K deductible), effective 11/17/2026, DuPont Community Credit Union staying "
    "on as mortgagee; once bound, delete Loc 5 from IK29P109337 (VP-PKG) and send the return premium. No reply from "
    "Howard yet as of this run (11/18 6:44am scan) — awaiting his bind confirmation and declarations page. This "
    "resolves the prior 'waiting on FirstCash' blocker: Joshua decided to proceed without further waiting."
)
p["last_verified"] = today

# --- VP-WC: carrier's promised EOD 11/17 written confirmation did not arrive ---
p = find("VP-WC")
p["status"] = p["status"] + (
    " UPDATE 2026-11-18 (insurance-inbox-watch, 6:44 AM slot): checked thread 1a1833478fccbeb6 for Christine Ayala's "
    "promised 'end of day 11/17' formal $0-balance/good-standing written confirmation — it has NOT arrived as of "
    "this run. Payment itself remains confirmed RECEIVED (her 11/16 10:00am message); this is only the formal "
    "paperwork still outstanding, not a new payment or cancellation risk. Not time-critical; will keep checking."
)
p["last_verified"] = today

# --- GAP-UMBRELLA: active movement on both legs 11/17 ---
p = find("GAP-UMBRELLA")
p["status"] = p["status"] + (
    " UPDATE 2026-11-18 (insurance-inbox-watch): ACTIVE MOVEMENT on both legs as of 11/17. COMMERCIAL LEG: Joshua "
    "emailed Howard Baker (cc Laura Sullins) 11/17 6:21pm ET asking to also schedule his 3 rental properties — "
    "282 Bald Rock, 14300 Woods Walk, 148 Hardinberry (all on commercial-premises liability forms, so his personal "
    "umbrella won't reach them) — under the commercial umbrella quote (thread 1a1eaad52df058f7). PERSONAL LEG: RLI "
    "quote PUPSUB-0800183 narrowed 11/17 to 1 residential property (844 Cypress Crossing, $300K liability) + 4 "
    "vehicles/2 drivers, $3M and $5M both with/without $1M excess UM/UIM; RLI (Shelly Rowley) confirmed the auto "
    "underlying minimum is $500,000/$500,000/$50,000 split (CSL may not satisfy it — still needs RLI's written "
    "confirmation either way) — Joshua is moving Progressive to $500K CSL at the 11/28 renewal to try to meet it. "
    "RLI (Melissa Alejandro) sent Joshua a self-service portal link to finalize the property change himself "
    "(thread 1a1ebdf7a34f65b5, 11/17 11:37pm ET) — this is now waiting on Joshua's own portal action, not a broker reply."
)
p["last_verified"] = today

with open(path, "w") as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("patched OK")
