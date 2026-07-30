# Enterprise File Organization Plan
## iCloud Drive + Google Drive → Business / Real Estate / Personal

**Prepared:** July 29, 2026 · **Designed by:** Fable (this session) · **Status:** PLAN ONLY — nothing has been moved, renamed, or deleted.
**Execute with:** any model, in phases below. Each phase is independent, reversible, and verifiable.

---

## 1. Executive Summary

Both clouds get the **same three-section skeleton** so filing is predictable no matter where you are:

```
00 Inbox  ·  01 Business  ·  02 Real Estate  ·  03 Personal  ·  99 Archive
```

Each section has exactly **one system of record**:

| Section | Lives primarily in | Why |
|---|---|---|
| **01 Business** | Google Drive (jdavis@fcfpawn.com My Drive) | Shareable with Preston/CPA; Workspace account; automations already there |
| **02 Real Estate** | Google Drive (My Drive) | Lender/attorney/CPA sharing; already has Real Estate & Leases folder |
| **03 Personal** | iCloud Drive | Personal Apple ID; keeps family/health/ID docs OFF the business Workspace account |
| Store operations | Valley Pawn Drive (shared drive) | **Unchanged — frozen.** It's the ops/automation landing zone, organized by workflow, and it works |

The mirrored skeleton means a business PDF that lands in iCloud still has an obvious slot (iCloud `01 Business/...`) — it just gets swept to Google Drive on the quarterly sweep, and vice versa. One map, everywhere.

---

## 2. Current State (audited July 29, 2026)

### iCloud Drive (~6,300+ files)
- **Companies/** (1,082 files) — 11 mixed folders: Full Circle Finance, Farming Infinity, J Davis Group, Tax Experts, Tax Experts MGMT, Voicerunners, 817 Richmond Rd, First Cash Lease, Gold 2024, 2024 FCF Anaylsis *(typo)*, 14300 Pics
- **Personal/** (5,154 files) — **six different tax folders** (`Taxes`, `Taxes 2022`, ` Taxes 2022` *(leading space)*, `2023 Taxes ` *(trailing space)*, ` Personal Tax 2023`, `2024 Taxes`, `Taxes Follow up 2`), plus Health, Important Docs, Florida Home Loan, Lender Info, Vehicles, Pictures, Car PICS, etc.
- **Minutes/** — already clean (Farming Infinity / Full Circle Finance / Prime IV)
- **Desktop - Joshua's iMac/** — old iMac backup with `$RECYCLE.BIN`, `Thumbs.db`, Office lock files, `Junk to Trash/`
- **Root** — ~10 loose files (work comp policy, general liability, Sales Tax.xlsx, pool application ×2, estimate, car comparison…) + leftover session junk (`_claude_scratch`, `_tmp_stage`, `_verify`, `_Cleanup Notes.md`)
- **Downloads/_Review for Deletion/** — 244 files parked since the April 27 cleanup, never triaged

### Google Drive — My Drive (jdavis@fcfpawn.com)
- Good bones already exist: Corporate Governance, Financial Records (Banking / P&L / Tax Documents), Human Resources, Marketing & Advertising, Operations, Real Estate & Leases (844 Cypress Crossing Trail), Vendor Contracts & Agreements, Farming Infinity — Entity Records
- **~55 loose files at root**, heavy duplication: `VP_BONUS_TARGETS_2026` ×4, `Kitchen_Appliance_Options` ×5, `Pool_Proposals_Comparison` ×3, plus test files (`_test.gdoc`, `test file 3.gdoc`)
- **Personal files mixed into the business account root**: kitchen appliances, pool proposals, landscape plan, UF Health records request, visit/procedure totals
- **Claude/** tree (mirror of the Mac's automation folders) — infrastructure, not documents

### Valley Pawn Drive (shared drive)
Operationally organized (Accounting Exports, Aged Inventory, Bookkeeping, FFL, Chekkit Invite Lists, Employee Productivity Reports, Weekly KPIS, Valley Pawn Plus, Cannabis Retail — Staunton, New Merch Program, Vendor Onboarding). **Working as designed. Not part of this reorg.**

### Prior work found (Rule #3)
- April 27, 2026 iCloud cleanup (`_Cleanup Notes.md`): ~340 loose files sorted into subfolders; internal hierarchies deliberately left for "a separate pass" — **this plan is that pass.**
- No other session or project is working file organization (Slack + Projects folder checked July 29). One concurrent session is running Bravo aged-jewelry diagnostics and filed one PDF to Real Estate & Leases today — no conflict, but execution must leave the Drive `Claude/` tree alone.

---

## 3. FROZEN ZONES — never rename, move, or delete (automation depends on these)

| Location | Item | Why frozen |
|---|---|---|
| Valley Pawn Drive | `Accounting Exports` (ID `1FzXIRPNZHaECOwfaKpQDMUTPRY3-d12_`) | QBO GL import pipeline |
| Valley Pawn Drive | `Aged Inventory` + subfolders (ID `1bFhkthaunjrygDIKLgpumhI5iqRGeBId`) | Weekly aged-inventory task |
| Valley Pawn Drive | `Bookkeeping` + `Bravo Exports` (ID `1zZyhJvmd_MPrx8jh9Y3-XpoWCDUp9XTA`) | QBO reference exports |
| Valley Pawn Drive | `Chekkit Invite Lists`, `Employee Productivity Reports`, `Weekly KPIS` | Scheduled tasks write here |
| Valley Pawn Drive | `Valley Pawn — Policies & Procedures` + Policies folder | `policy-lifecycle` skill target |
| Valley Pawn Drive | `Valley Pawn — Hiring Pipeline.gsheet`, `New Inventory Tracker` | hiring-inbox-watch, new-inv-intake/report |
| My Drive | **entire `Claude/` tree** (`Claude/Projects/Bravo Data Extraction/…` — logs, output, triggers, results, reports) | Live Bravo pipeline mirror — a diagnostic session was writing to it during this audit |
| My Drive | `.shortcut-targets-by-id`, `.tmp` (local sync artifacts) | Google Drive sync internals |
| Mac | `/Users/joshuadavis/Documents/Claude/**` (Projects, Scheduled, etc.) | All scheduled tasks + pipelines |
| iCloud | `Desktop` and `Documents` symlinks at iCloud root | macOS system links |

**Rule for the executing model:** if a folder is in this table, work AROUND it. Rule #4 — additive only.

---

## 4. Target Architecture

### 4a. Google Drive — My Drive (system of record: Business + Real Estate)

```
My Drive/
├── 00 Inbox/                          ← new files land here if unsure; swept weekly
├── 01 Business/
│   ├── Full Circle Finance (Valley Pawn)/
│   │   ├── 01 Corporate Governance/   ← existing folder moves in
│   │   ├── 02 Financial Records/      ← existing (Banking / P&L / Tax Documents)
│   │   ├── 03 Human Resources/        ← existing
│   │   ├── 04 Contracts & Vendors/    ← existing "Vendor Contracts & Agreements"
│   │   ├── 05 Marketing & Advertising/← existing
│   │   ├── 06 Operations/             ← existing
│   │   ├── 07 Insurance/              ← new (work comp, general liability, Lockton)
│   │   └── 08 Reports & Analysis/     ← loose VP_* reports, rankings, market analyses
│   ├── Farming Infinity/              ← existing "Farming Infinity — Entity Records"
│   ├── J Davis Group/
│   ├── Tax Experts/  (incl. Management subfolder)
│   ├── Voicerunners/
│   └── Prime IV/
├── 02 Real Estate/                    ← absorbs "Real Estate & Leases"
│   ├── 817 Richmond Rd — Staunton VA (Commercial)/
│   ├── 282 Bald Rock Rd — Verona VA (Rental)/
│   ├── 844 Cypress Crossing Trail — FL (Home)/   ← existing folder moves in
│   ├── Valley Pawn Store Leases/
│   │   ├── Culpeper/ · Waynesboro/ · Harrisonburg/ · Lexington/ · Roanoke/
│   └── _Prospects & Research/         ← acquisition targets, market analyses
├── 03 Personal/                       ← SLIM: Google-native (.gdoc/.gsheet) personal files only;
│   │                                     everything else migrates to iCloud 03 Personal
├── Claude/                            ← FROZEN (automation mirror)
└── 99 Archive/                        ← superseded versions, old test files
```

**Standard subfolders inside every entity folder** (create only as needed):
`01 Formation & Governance · 02 Minutes · 03 Tax Returns · 04 Financials · 05 Contracts & Leases · 06 Insurance · 07 Correspondence`

**Standard subfolders inside every property folder:**
`01 Purchase & Closing · 02 Deed & Title · 03 Financing · 04 Leases & Tenants · 05 Insurance · 06 Taxes & Assessments · 07 Improvements & Maintenance · 08 Photos`

### 4b. iCloud Drive (system of record: Personal)

```
iCloud Drive/
├── 00 Inbox/
├── 01 Business/                       ← renamed from "Companies"; same entity folders as Drive
│   ├── Full Circle Finance (Valley Pawn)/   (absorbs FCF Old, Gold 2024, 2024 FCF Analysis → its 04 Financials / 99 archive)
│   ├── Farming Infinity/
│   ├── J Davis Group/
│   ├── Tax Experts/  (absorbs "Tax Experts MGMT" as subfolder)
│   ├── Voicerunners/
│   ├── Prime IV/
│   └── Minutes stay WITH each entity (Minutes/Farming Infinity → 01 Business/Farming Infinity/02 Minutes, etc.)
├── 02 Real Estate/
│   ├── 817 Richmond Rd — Staunton VA (Commercial)/   ← from Companies/817 Richmond Rd
│   ├── 844 Cypress Crossing Trail — FL (Home)/       ← Florida Home Loan, Home Improvements, pool app, landscape
│   ├── 282 Bald Rock Rd — Verona VA (Rental)/
│   ├── 14300 [address TBD]/            ← from "14300 Pics"; executor confirms address from file contents
│   └── First Cash Lease/               ← executor confirms which property; file under it
├── 03 Personal/
│   ├── 01 Identification & Vital Records/  ← "Important Docs"
│   ├── 02 Taxes/
│   │   └── 2020/ 2021/ 2022/ 2023/ 2024/ 2025/   ← ALL six tax folders merged by year
│   ├── 03 Health/                      ← stays iCloud ONLY (never on the Workspace account)
│   ├── 04 Financial/                   ← Lender Info, Bank Application, QDRO
│   ├── 05 Vehicles/                    ← Vehicles + ATV title/receipt from iMac backup
│   ├── 06 Family/                      ← resume, family W-2 folders (names kept as-is)
│   ├── 07 Memberships & Travel/        ← Palencia Club, Sandals docs
│   └── 08 Photos/                      ← Pictures, Car PICS, 14300 Pics photos not deed-related
└── 99 Archive/
    ├── iMac Backup (2020)/             ← "Desktop - Joshua's iMac" minus junk
    └── _To Trash/                      ← junk staged for YOUR one-click delete (Claude can't empty trash)
```

---

## 5. Naming Conventions (apply to everything touched going forward)

1. **Folders:** Title Case, no leading/trailing spaces, no typos (`2024 FCF Anaylsis` → fixed), numbered prefixes (`01`–`99`) only at levels where scan order matters.
2. **Dated documents:** `YYYY-MM-DD Description.ext` (e.g. `2026-04-08 Lockton Welcome Letter.pdf`).
3. **Yearly/recurring docs:** `YYYY Description.ext` (e.g. `2024 J Davis Group Tax Return.pdf`).
4. **No duplicate suffixes:** `(1) (2) (3)` copies get deduped — newest version kept with clean name, older copies → `99 Archive`.
5. **Entity prefix on business docs** where the folder doesn't already say it: `FCF`, `JDG`, `FI`, `TE`, `VR`.
6. **Screenshots/scans renamed** to what they are (`IMG_2104.HEIC` → keep in Photos; documents get real names).

---

## 6. Execution Phases (run in order; each ends with a verification step)

| Phase | Scope | Est. effort | Risk |
|---|---|---|---|
| **1. Skeletons** | Create the `00/01/02/03/99` trees in both clouds. Zero moves. | Small | None — purely additive |
| **2. Google Drive root sweep** | Dedupe the ~55 loose My Drive files; file into new tree; test files → 99 Archive | Medium | Low |
| **3. Drive folder moves** | Move the 8 existing business folders under `01 Business/FCF`; `Real Estate & Leases` → `02 Real Estate` | Small | Low — Drive moves preserve file IDs & links |
| **4. iCloud Business + Real Estate** | `Companies` → `01 Business` restructure; extract 817/14300/First Cash → `02 Real Estate` | Medium | Low |
| **5. iCloud Personal consolidation** | Merge 6 tax folders by year; Important Docs → ID & Vital Records; Health/Family/Vehicles/Photos | Large (5,154 files) | Low — moves only, nothing deleted |
| **6. Junk staging** | iMac backup junk, Office lock files, session scratch (`_claude_scratch` etc.), `_Review for Deletion` triage list → `99 Archive/_To Trash` | Small | None — Joshua deletes, Claude never does |
| **7. Cross-cloud sweep** | Business/RE strays in iCloud → Drive; personal strays in Drive (incl. health .gdocs, exported) → iCloud | Medium | Low |
| **8. Verify + document** | File counts before/after per folder; write `FILING_GUIDE.md` at both roots; update valley-pawn-context Drive table + register in BUSINESS_OS.md (Rule 14); set up quarterly sweep scheduled task | Small | None |

**Ground rules for every phase:**
- **Nothing is ever deleted.** Junk goes to `99 Archive/_To Trash`; Joshua empties it from Finder/Drive.
- **Before/after manifest** per phase (file counts + top-level listing) saved to the project folder → any phase can be audited or reversed.
- **Frozen zones (Section 3) untouched.** Any file discovered inside one stays put.
- Phase = one session. If a session dies mid-phase, the manifest shows exactly where it stopped.

---

## 7. Items the executor resolves from file contents (no need to ask Joshua)

- **14300 Pics** — open a few files, identify the property address, name the folder properly.
- **First Cash Lease** — determine which property/entity; file accordingly.
- **`lor (7).pdf`** (iCloud Downloads) and root loose files — open, rename, file.
- **`_Review for Deletion` (244 files)** — produce a keep/toss shortlist (April notes already flag 4 keepers) rather than dumping it on Joshua raw.
- **Prime IV** — currently only minutes exist; entity folder created for future docs.

---

## 8. Governance (what keeps it clean long-term)

1. **The Inbox rule:** anything you can't file in 5 seconds goes to `00 Inbox` — never loose at root.
2. **Weekly sweep** added to an existing admin scheduled task (or new one, additive): empty both `00 Inbox` folders, dedupe any `(1)` copies that appeared.
3. **Filing guide** (`FILING_GUIDE.md`) at both roots — one page, the decision tree: *Business entity? → 01. Property? → 02. You/family? → 03. Store operations? → Valley Pawn Drive (don't file it here).*
4. **New entity or property = new folder from the standard template.** Never a new top-level section.
5. Registered in **BUSINESS_OS.md** so every future session inherits the map.

---

## 9. Expert Board Review (summary)

**Panel:** Records-management consultant (F500 filing systems) · Automation/SRE engineer · CPA-records & retention advisor.

- **Mirrored skeleton + one system of record per section** — chosen over "each cloud fully independent" (drifts back to mess) and over "everything in one cloud" (personal docs don't belong on the business Workspace account; automations can't leave Drive). 
- **Restructure by moving into a new tree, never delete** — chosen over in-place renames (harder to audit/reverse) and over automated deletion (irreversible; violates house rules).
- **Health documents live in iCloud only** — CPA/privacy call: keeps medical records off the company Google Workspace account.
- **Valley Pawn Drive excluded from the reorg** — SRE veto on touching the ops shared drive: it's organized by workflow, automations write there by folder ID, and it already works. "Just works" beats "matches the taxonomy."
- **Rejected:** big-bang single-session execution (too many files, no checkpoint) in favor of 8 verified phases.
