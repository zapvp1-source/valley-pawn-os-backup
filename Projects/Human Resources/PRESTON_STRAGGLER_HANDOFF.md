# Hiring Straggler Handoff — for Preston
**Prepared:** Thursday, 2026-09-03 · **Prepared by:** Claude for Joshua
**Automated outreach status: STOPPED.** The `indeed-applicant-outreach` task is disabled and all 5 Valley Pawn listings are Paused/Closed. Nothing is auto-contacting anyone. What's below is manual cleanup only.

---

## Bottom line
Outreach coverage is **complete**. Every applicant was contacted before the campaign stopped on **Aug 22**.

Evidence checked (not assumed):
- Indeed's **"New" bucket = 0** — nobody is sitting untouched
- **110 contact-log entries** spanning Aug 15, 16, 17, 21, 22
- Spot-checked **19 of 19** candidates currently in "Reviewing" — all present in the contact log
- Current pipeline: 213 total applications · 77 Reviewing · **99 Contacting** · 37 Interviewing · 178 Rejected (mostly auto-rejected on required screener questions)

**⚠️ Time-sensitive:** the interviews that got booked were for **Wed Aug 26** — that was **8 days ago**. Nobody has touched this since Aug 22, so those outcomes are unknown. Start there.

---

## GROUP 1 — Booked an interview, never confirmed it (11 people) ⬅ HIGHEST PRIORITY
These were offered or tentatively booked a slot but never confirmed. Their slots were on/around **Aug 26 and have passed.** Assume they need re-contacting from scratch, and expect some to have taken other jobs.

| Candidate | Store / Role | Email on file |
|---|---|---|
| Jasmine Lipes | Waynesboro — Sales & Loan Associate | hunnibfli2012@gmail.com |
| Sabrina Clark | Waynesboro — Sales & Loan Associate | sabrinaclarkamck5_y4a@indeedemail.com |
| Travis Reed | Waynesboro — Sales & Loan Associate | travisreed762_gr2@indeedemail.com |
| Jennifer Parrish | Waynesboro — Sales & Loan Associate | Jfaerogue31@outlook.com |
| Brittany Smith | Waynesboro — Sales & Loan Associate | brittanycsmith2017@gmail.com |
| Isaiah Abshire | Waynesboro — Sales & Loan Associate | (pull from Indeed) |
| Richard Marsh | Harrisonburg — Store Manager | richardmarsh383_e9p@indeedemail.com |
| Isom Bryant | Harrisonburg — Store Manager | isom.bryant@gmail.com |
| Joseph West Jr | Harrisonburg — Store Manager | josephwestjr9_y5i@indeedemail.com |
| Jaekwon Wayne | Harrisonburg — Sales & Loan Associate | (pull from Indeed) |
| Leila Eutsler | Harrisonburg — Sales & Loan Associate | (pull from Indeed) |

**Also confirm what happened with the two interviews that WERE confirmed for Wed Aug 26** (10:30 AM and 11:00 AM phone slots — Cameron Pearson and James Beverly, both Lexington). Did they happen? Calendar events `ki9n5kkft04fv68kjece56gf7c` and `ilgag3sla93poerb01j1dk17a0` on jdavis@fcfpawn.com.

---

## GROUP 2 — Text never reached them (9 people) ⬅ CALL THESE
Email and/or Indeed message delivered, but **every text attempt failed** (macOS Messages "error 22", retried and still failed). If they only check texts, they never heard from us.

| Candidate | Store / Role | Email on file |
|---|---|---|
| Jesse Saunders | Lexington — Sales & Loan Associate | jessesaunders28drb_98y@indeedemail.com |
| James Jones | Waynesboro — Sales & Loan Associate | jamey11238p7dc_67h@indeedemail.com |
| Michelle Foster | Waynesboro — Sales & Loan Associate | gmseashell19672_2sc@indeedemail.com |
| Christopher Dunn | Waynesboro — Store Manager | Ashleycouch717@gmail.com |
| Marinda Smalberger | Harrisonburg — Sales & Loan Associate | smalbergermarinda@gmail.com |
| McKenna Haines | Harrisonburg — Store Manager | hainesmckenna45673_4cc@indeedemail.com |
| Jazlyn Fink | Harrisonburg — Store Manager | j_fink0507@yahoo.com |
| Brian Heise | Harrisonburg — Store Manager | brianheise265@gmail.com |
| Andy Perez | Harrisonburg — Store Manager | Prezandy42@gmail.com |

> **Get phone numbers from the Indeed candidate record, not from this sheet.** The contact log's phone column is cross-contaminated between rows (the same number appears against three different people), so any number pulled from it can't be trusted. Open the applicant in Indeed and read the resume.

---

## What to say
Same approach that was used, minus the automation:
> "Hi {name}, this is Preston with Valley Pawn. We received your application for the {role} position at our {store} store. Joshua wanted to connect — is there a day and time that works for a quick call?"

Keep to **9:00 AM – 8:00 PM ET**.

---

## Known issues, for the record
1. **Text delivery "error 22"** — recurring macOS Messages failure on ~9 numbers. Root cause not diagnosed. Likely landlines or non-SMS-capable numbers. Worth checking whether these are VoIP/landline before assuming the tooling is at fault.
2. **Indeed in-app messaging can't be automated** — the composer is a React-controlled field that rejects programmatic input. Indeed messages that did go out were sent by other means; assume this channel needs a human.
3. **Local clocks were 19 days wrong** on 2026-09-03 (reported Aug 15). Fixed by requiring an external time source. Mentioned only because it's why outreach sat idle Aug 22 → Sept 3.
4. **Sponsorship windows expired as designed** (Aug 15–29, 15-day cap). That's why listings show Paused — nothing broke.

---

## To restart automated outreach later
1. Reopen whichever listings should be live (and re-sponsor — 15-day windows only, per standing rule)
2. Re-enable the `indeed-applicant-outreach` scheduled task
3. Click **Run now** once and approve the tool prompts, or the first run will do nothing
Full spec: `Valley Pawn OS/HIRING_OUTREACH.md`
