# Personal OS — Master Reference

**Created:** 2026-08-07 · **Domain 3 of 3** in the Life Map (`Life OS/LIFE_MAP.md`)
**Mission:** Joshua's own life — health, personal finances, family, personal tax exposure — kept
separate from Full Circle Finance Inc / Valley Pawn and tracked so a new session doesn't have to
be re-briefed from zero.

This is the thinnest of the three domain files today because the least amount of prior work has
been consolidated here — most personal-domain material exists in project folders but was never
indexed centrally. Treat this as a scaffold to extend, same pattern as `bald-rock-property` was
when it started.

---

## Quick Map

| If the task involves... | Go to |
|---|---|
| Health, medical records, labs, symptoms, doctors | Health section below → `Health Optimization` project folder |
| Personal money, bank accounts, personal taxes, Cypress Crossing finances | Personal Finance section below + `Real Estate OS` (Cypress Crossing) |
| Family (Hillary, other family members) | Family section below *(TODO — thin)* |
| Personal travel | *(TODO)* |
| Anything for Valley Pawn or Full Circle Finance Inc | **Wrong file** — go to `Valley Pawn OS/BUSINESS_OS.md` instead |

---

## People

- **Joshua Davis** — jdavis@fcfpawn.com (business/Workspace), zapvp1@me.com (personal iCloud).
  Owner, Full Circle Finance Inc DBA Valley Pawn.
- **Hillary Davis** — Joshua's wife. Joint owner of 844 Cypress Crossing Trail (see
  `Real Estate OS`). Confirm her role/involvement in other personal-domain matters as it surfaces
  — not yet documented here.

---

## Health

**`Health Optimization`** project folder — an active, deep personal health investigation, now with a
running automation layer (built 2026-09-06; full design in `HEALTH_OS_AUTOMATION_PLAN.md`).

**Start here, in this order — do not re-derive from raw data:**
1. `STATUS.md` — live pipeline health, every open thread with its verified status, and what's unfolded
2. `Master_Findings_Index.md` — the sourced case file, every abnormal value traced to a source + date
3. `TARGETED_TRACK.md` — the settled 3-track plan (night events / RUQ-gallbladder / CV prevention)
4. `Open_Tests_Tracker.md` — every test and records request the boards called for, with status + age
5. `CHANGELOG.md` — what changed and when

Supporting: `BOARD_CONSENSUS_June2026.md` + `Board_A/Board_B` (Joshua ran an expert-panel process on
his own case — conventional vs heterodox, the same pattern he wants for technical decisions);
`Data_Coverage_Ledger.md` (what is fully extracted vs. not — read before claiming anything is missing);
`Case_Summary_SOURCED.md` / `One_Page_Doctor_Summary.*` (physician-facing); `In_Network_Doctors_and_Tests.md`
(FHCP HMO options + referral rules).

### The case in one line
A REM-state-triggered vasomotor / small-fiber process at night (hot feet → body, out of REM, all night,
**non-tachycardic** — HR stays flat), plus an independent daytime RUQ / hyperkinetic-gallbladder problem,
on an insulin-resistance substrate, with Lp(a) 245 / ApoB 105 cardiovascular prevention as the background
job. Most dangerous things are excluded (see the index's "what this is NOT" list — don't re-open them).
The June 2026 board's single strongest recommendation — one bundled blood draw (Fabry α-Gal A, TTR gene,
SPEP + free light chains, copper/ceruloplasmin, B6, smear + retic) — **still had no evidence of being
ordered as of 2026-09-06.**

### Automation (all additive, all host-side)
| Piece | Cadence | What it does |
|---|---|---|
| launchd `com.healthos.oura-import` | 8:30 AM daily | Runs `oura/run_daily_v5.sh`. Live db on LOCAL disk at `~/Library/Application Support/HealthOS/oura.db`; only a 23 MB `.gz` backup + `oura_latest.json` go in the synced folder. |
| Cowork `oura-daily-import` | ~8:53 AM | Verifier/fallback only — reads `oura_latest.json`, re-runs the script if launchd didn't. |
| Cowork `health-episode-capture` | 9:15 AM daily | Reads Joshua's notes-to-self (his own number / zapvp1@me.com) and the **"Health Log" Apple Note**, logs episodes to `Episode_Log.csv`, and auto-cross-checks that night's hypnogram, HR, temp, SpO2, HRV. Silent when there's nothing. |
| Cowork `health-records-intake` | 9 PM daily | Files anything dropped in `_inbox/` into `records/<year>/`, parses lab values into `All_Lab_Results_MASTER.csv`, scans mail for result notices. |
| Cowork `health-weekly-digest` | Sunday 9 AM | Plain-language DM: episode nights vs baseline, what was logged, new records, open tests aging past 30 days. Also runs the case-file drift check. |
| `scripts/night_signature.py` | with each run | Scores EVERY night (1,176 back to Oct 2022) against its own trailing 30-night baseline → `Nights_Ledger.csv` + `Nights_Summary.md`. |

**Data reality:** the full Oura history 2022→now IS available (924k HR points from 2022-10-02) — the old
"2022–2024 missing" note in the index was wrong and is corrected. **Glucose/CGM is stale since 4/28/2026**
— the Oura token needs the `metabolic` scope, which only Joshua can regenerate.

**Hard-won lessons, do not repeat:** never put the live Oura SQLite db back in the synced folder (it was
silently truncated 8/14 and 8/31 — years of history lost, restored from backup both times). Never run this
folder's work through the workspace Bash tool or a `/sessions/*/mnt/` path — that mount deadlocks; use
`mcp__Control_your_Mac__osascript`. Always open the Oura db read-only (`?mode=ro`), and `chat.db` copies
need `immutable=1`.

**Handling note:** sensitive personal medical material. Stay factual and sourced — verify against the data,
don't diagnose from metadata. Don't add speculative medical interpretation beyond what the findings
documents already say; genuine medical decisions are Joshua's to make with his doctors, not Claude's to
resolve. Never let Valley Pawn brand voice or business money touch anything here.

---

## Personal Finance

- **`Taxes 2026`** project folder is cross-domain (see `Life OS/LIFE_MAP.md` for why) — it holds
  personal-relevant material alongside FCF Inc material:
  - `Bank Statements/` subfolder
  - `Vehicle Purchase Docs/` subfolder
  - Cypress Crossing and Bald Rock capital-improvement evidence logs (detailed in `Real Estate
    OS` — Bald Rock is Farming Infinity Mountains LLC money (a single-member LLC that lands on
    Joshua's 1040, NOT FCF Inc), Cypress Crossing is personal money; both get substantiated
    the same way. Ownership authority: `Life OS/ENTITY_STRUCTURE.md`)
- **QBO:** two separate QuickBooks Online accounts exist per `qbo-context` —
  `jdavis@fcfpawn.com` (FCF Inc books, read-write) and the bookkeeper's account under
  `zapvp1@me.com` (**strictly read-only**). Neither is confirmed to be a *personal* (non-FCF-Inc)
  set of books — if Joshua asks for personal bookkeeping/P&L work, first confirm whether personal
  finances are tracked in QBO at all or need a different source (bank exports, etc.) before
  assuming QBO has the answer.
- **CPA:** Silverline Tax (Liana Motel, liana@silverline.tax; Jonathan, co-owner;
  219-365-9520) handles Full Circle Finance Inc's monthly management reports. **Not confirmed**
  whether Silverline also prepares Joshua & Hillary's personal 1040 — check before assuming.
- (G) **Gap:** no personal net-worth tracker, no personal cash-flow/runway view, no consolidated
  view of personal vs. business exposure. Natural next build if Joshua asks for one.

---

## Home / Office Equipment

- **UPS / surge protection — Mac Studio + monitors (home office):** CyberPower CP1500PFCLCD
  (PFC Sinewave series, 1500VA/1000W, pure sine wave, 12 outlets — 6 battery+surge, 6 surge-only).
  Chosen because Mac Studio's internal PSU uses active PFC and needs true/pure sine wave output
  (stepped-sine UPS units can cause buzzing or unexpected shutdowns on battery). Purchased
  2026-08-13 — retailer/order confirmation not yet on file; add if Joshua forwards the receipt.
  Purchase links researched: [Amazon](https://www.amazon.com/CyberPower-CP1500PFCLCD-Sinewave-Outlets-Mini-Tower/dp/B00429N19W),
  [Best Buy](https://www.bestbuy.com/product/cyberpower-pfc-sinewave-series-1500va-battery-back-up-system-black/JX8P9297PT),
  [Newegg](https://www.newegg.com/cyberpower-cp1500pfclcd-nema-5-15r/p/N82E16842102134).

---

## Family

*(TODO — thin section.)* Hillary Davis is the only family member documented so far (see People
above, via Cypress Crossing joint ownership). Add children, other family, or recurring
family-related tasks (school, events, etc.) here as they surface.

---

## Working rules for this domain

Same four hard rules as Valley Pawn (`valley-pawn-context` Rules #1–#4: act autonomously, never
ask Joshua to log in, check prior work before redoing, build additive) apply here too — Joshua's
"Claude does the work" preference is not scoped to the business, it's how he wants everything
handled. The one addition specific to this domain:

1. **Never let business money or business brand voice bleed into personal content, and vice
   versa.** A personal email to Joshua's doctor should never carry Valley Pawn branding. A
   personal expense should never land on FCF Inc's books without Joshua explicitly directing it.

---

## How to extend this file

This file is intentionally thin today. The single best move for any session working in the
personal domain: after finishing the task, add whatever you learned back into the relevant
section here (a new health finding's location, a new personal account, a new family fact) so the
next session doesn't start from zero the way this one did.
