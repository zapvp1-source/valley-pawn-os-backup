# DELTA 2026-07-29 — Enterprise File Organization (merge into BUSINESS_OS.md)

## New: unified filing structure across iCloud Drive + Google Drive My Drive

Executed 2026-07-29 (plan + execution: Admin Assitant project, `FILE_ORGANIZATION_PLAN.md`).
Both clouds now share the same skeleton: `00 Inbox / 01 Business / 02 Real Estate / 03 Personal / 99 Archive`.

- **System of record:** Google Drive (jdavis My Drive) = Business + Real Estate · iCloud = Personal (health docs iCloud ONLY) · **Valley Pawn Drive = operations, untouched/frozen** (all automation folders unchanged).
- My Drive business folders (Corporate Governance, Financial Records, HR, Vendor Contracts, Marketing, Operations) moved under `01 Business/Full Circle Finance (Valley Pawn)/` as numbered subfolders 01–08. `Farming Infinity — Entity Records` → `01 Business/Farming Infinity`. `Real Estate & Leases` → `02 Real Estate` (emptied shell in `99 Archive`).
- iCloud `Companies` → `01 Business` (entities: FCF, Farming Infinity, J Davis Group, Tax Experts, Voicerunners, Prime IV). Properties extracted to `02 Real Estate`. `Personal` → `03 Personal` with numbered subfolders; six tax folders merged under `02 Taxes/[year]`. Old iMac backup → `99 Archive/iMac Backup (2020)`.
- **`FILING_GUIDE.md` at both cloud roots** — the decision tree every session should follow when saving user documents.
- `99 Archive/_To Trash` in both clouds = staged deletions awaiting Joshua's manual empty (incl. iCloud `_Review for Deletion`, 244 files).
- Manifests (before/after/error logs): `Projects/Admin Assitant/file-org-manifests/`.
- The Drive `Claude/` tree, Valley Pawn Drive, `~/Documents/Claude`, and all pipeline paths were NOT touched.

## Rule addition (Rule 10 extension)
When saving a business/real-estate/personal document for Joshua, file it per `FILING_GUIDE.md` — never loose at a cloud root. Unsure → `00 Inbox`.

## Open items
- `02 Real Estate/14300 (Address TBD) - Property Photos` (iCloud) — property address unconfirmed.
- `03 Personal/02 Taxes/Mixed - To Sort` + `Follow up 2 - To Sort` — per-file year sort pending.
- `00 Inbox` (iCloud) holds: 2025 personal tax extension PDF, `lor (7).pdf` — awaiting filing.


## ADDENDUM 2026-07-29 (later same day) — Mac Desktop integrated into filing structure

Joshua's Mac Desktop (~90 loose folders/files, never synced to either cloud) has been fully merged into the same `00 Inbox / 01 Business / 02 Real Estate / 03 Personal / 99 Archive` structure. Desktop is now clean except for `Claude`, `Claude Back Up` (session backups) and `data` (app data) — deliberately left untouched, not part of the filing scheme.

- **Full Circle Finance** (Desktop folder, 2,846 files) turned out to be a richer, more mature taxonomy than the GDrive structure built earlier the same day. Merged in wholesale; added two new top-level FCF categories that didn't exist yet: **`09 Compliance & Legal`** (Licensing & Permits, Entity Set Up Documents, IRS Form 843 Claims [COVID + Kwong Protective Claims], Case Files [Goldchaincase pawn dispute, Wells Fargo garnishment]) and **`10 Strategy & M&A`**.
- Real estate renovation/vendor clusters (Airbnb MGMT, Real Estate Improvements, 844 Cypress cluster — Anchient City/Pool Spec/Bathroom/Green Nest/appliances/photos) filed under the matching property in `02 Real Estate`.
- Personal health MyChart exports (7 date-range folders) → `03 Personal/03 Health/MyChart Exports/`. Tax Transcripts (individual 1040s) → `03 Personal/02 Taxes/Tax Transcripts (Desktop Import)/`.
- Banking statement folders (Wells Fargo, Best Egg, Dupont LOC) merged into `01 Business/.../02 Financial Records/Banking & Accounts/`.
- Two near-duplicate "Tax and Entity Set Up" folders found — kept the more complete one, trashed the fully-duplicate original.
- Three large ambiguous dump folders (Documents ~165 files, Spreadsheets ~22 files, Info ~15 items/subfolders) were bulk-filed into `00 Inbox/Desktop ... Import (Needs Sorting)` rather than guessed at file-by-file — safe holding, nothing lost, optional secondary sort later.
- **Response** dispute folder relocated intact (not opened/read) to `02 Real Estate/_Vendor Disputes & Legal (Unconfirmed Property)/` — needs Joshua to confirm which property before final filing.
- **Escalated to Joshua directly** (not silently filed): Wells Fargo Notice of Garnishment (now filed but flagged), two new IRS dishonored-payment transcript flags (TY2022, TY2023) found in the Desktop Tax Transcripts, on top of the already-known $39,274.54 TY2024 balance note.
- Junk/system files (fonts, web-scrape cache, RECYCLE.BIN, Office lock files, duplicate root files) staged to `99 Archive/_To Trash` per clouds, not deleted.
- Scripts/logs: `Projects/Admin Assitant/file-org-manifests/desktop_stage1.sh` through `desktop_final_cleanup.sh` + matching `.log` files.
