# Roster — seed snapshot, pulled live from Gusto 2026-09-05

> **STATUS: SEED / REFERENCE ONLY. Do NOT wire any scheduled task to this file yet.**
> This is a point-in-time snapshot taken during the HR department review. It has no refresh
> mechanism, so it starts going stale the moment someone is hired or leaves. Phase 1 of
> `Human Resources/HR_DEPARTMENT_REVIEW_AND_AUTOMATION_PLAN_2026-09-05.md` replaces it with
> `ROSTER.json`, regenerated daily from the Gusto API — that file, not this one, becomes the
> single source of truth every HR task reads.
>
> Until then this file exists for one purpose: **to show that the five hand-typed rosters
> currently living inside task and skill files disagree with Gusto and with each other**, and to
> give any session a correct list to check against.
>
> Source: Gusto MCP `list_employees(terminated=false)` + `list_departments` + `list_pay_schedules`
> + `list_time_off_requests`, company `15bc2823-564f-4c1a-8464-9b0e7d79d3e8`. Read-only pull.

## Active employees — 18

Gusto's `department` field is the store. Titles are verbatim from Gusto.

### Culpeper (4)
| Name | Title | Rate | FLSA | Hired | PTO bal |
|---|---|---|---|---|---|
| Sandra "Sandi" Cole | Manager | $56,160 / yr | Exempt | 2022-11-28 | **−40.0 h** |
| Robert Swagger | Sales and Loan Representative | $17.00 / hr | Nonexempt | 2026-04-20 | 0 |
| Joshua Burnett | Sales and Loan Representative | $18.00 / hr | Nonexempt | **2026-09-03** | 0 |
| *(Bridgett "Bree" Grayson — appears in the Culpeper department list and in July time-off history but is NOT in the active-employee list; treat as departed and confirm)* | | | | | |

### Harrisonburg (3)
| Name | Title | Rate | FLSA | Hired | PTO bal |
|---|---|---|---|---|---|
| Logan Dean | Manager | $20.00 / hr | Nonexempt | **2026-08-31** | 0 |
| Walker Tapley | Sales and Loan Associate | $20.00 / hr | Nonexempt | 2025-11-24 | 0 |
| Michael Chambers | Sales and Loan Representative | $16.50 / hr | Nonexempt | 2026-08-03 | 0 |

### Lexington (1)
| Name | Title | Rate | FLSA | Hired | PTO bal |
|---|---|---|---|---|---|
| Uriah Tiglao | Manager | $15.00 / hr | Nonexempt | 2025-09-22 | 0 |

### Roanoke (2)
| Name | Title | Rate | FLSA | Hired | PTO bal |
|---|---|---|---|---|---|
| George "Benjie" Moore | Manager | $24.00 / hr | Nonexempt | 2023-10-27 | 40.0 h |
| Joseph Epperly | Sales and Loan Representative | $17.00 / hr | Nonexempt | 2026-07-23 | 0 |

### Waynesboro (2)
| Name | Title | Rate | FLSA | Hired | PTO bal |
|---|---|---|---|---|---|
| Chadd McClintic | Manager | $24.25 / hr | Nonexempt | 2023-03-13 | 40.0 h |
| Martin Dowden | Sales and Loan Associate | $21.50 / hr | Nonexempt | 2023-09-30 | 24.0 h |

### Corporate Support (6) / Marketing (1)
| Name | Title | Rate | FLSA | Hired | Note |
|---|---|---|---|---|---|
| Joshua Davis | Chief Executive Officer | $75,000 / yr | **Salaried Nonexempt** | 2022-01-24 | 2% shareholder; classification open (§L6 of the plan) |
| Hillary Davis | "Cheif Support Officer" *(spelling error in Gusto)* | $1,153.84 / wk | **Salaried Nonexempt** | 2023-04-04 | classification open (§L6) |
| Preston Peters | Market Manager | $90,000 / yr | Exempt | 2021-02-09 | everyone below store level reports to him |
| Madison Davis | Administrative Assistant | **$50.00 / week** | Nonexempt | 2026-01-02 | see §L5 — 40.00 h recorded on the 9/3 payroll breakdown |
| Savannah Davis | Social Media Manager (dept: Marketing) | **$50.00 / week** | Nonexempt | 2026-01-02 | see §L5 |
| Kennedy Davis | Gold Sorter | $12.00 / hr | Salaried Nonexempt | 2026-01-01 | **minor per Gusto DOB — see §L4** |
| Audrey Davis | Gold Sorter | $25.00 / week | Salaried Nonexempt | 2026-01-01 | **minor per Gusto DOB — see §L4** |

**Reporting line:** every store employee's `manager_uuid` is Preston Peters; Preston reports to
Joshua. Hillary reports to Joshua. The four family/corporate roles have no manager set.

**Pay schedule:** one active schedule — "every Friday", weekly, 52 periods, anchor 2021-02-12,
auto-pilot OFF (payroll is submitted by hand every week).

**Approved upcoming time off (as of this pull):** Chadd McClintic 9/8–9/14 (Waynesboro's manager
out the same week as the 9/10 bonus cycle and 9/11 payroll); Walker Tapley 9/26; Sandi Cole
11/9–11/14. Martin Dowden 9/2–9/6 was approved and is now in the past.

## The five conflicting rosters this replaces

Each of these is hand-typed inside a task or skill file and none is currently correct:

| Where | What it says | How it's wrong vs Gusto |
|---|---|---|
| `daily-clockin-check` (task **and** a duplicate copy in the skill of the same name) | a 9-row name → `companyMemberUuid` crosswalk | missing Logan Dean, Michael Chambers, Joseph Epperly, Joshua Burnett; Culpeper PATH-B roster names Martin Dowden at Culpeper (he is Waynesboro) |
| `weekly-timekeeping-analysis` | static store map | closest to correct, but predates the 8/31 and 9/3 hires |
| `chekkit-unanswered-alert` | per-store DM roster | same drift |
| `daily-dress-code-check` | exclusion list | excludes the Davis family + Sandi + Preston; no longer matches who is actually on camera |
| `valley-pawn-context` Employee Directory | Andrew, Nelson, Emma, Cris … | names that are not in Gusto's active list at all; missing four current employees |

Nothing in this file has been wired into any of them. Re-pointing each task to the Phase-1
`ROSTER.json` happens the next time that task is touched, per the additive rule.

## Provisioning gaps this snapshot exposes

Two people were hired in the last week and there is no record in the Open Items Register or
CHANGELOG that either was provisioned in Slack, Chekkit, or Bravo, or sent the policy-signature
pack:

- **Logan Dean** — Harrisonburg, Manager, hired 2026-08-31
- **Joshua Burnett** — Culpeper, Sales and Loan Representative, hired 2026-09-03

Both are `onboarding_completed` in Gusto (payroll side is done). The Phase-2 `hr-new-hire-detector`
exists precisely to catch this class; until it is built, this needs a manual pass — and it is
blocked on the Gusto browser session (SMS-MFA since 9/1) for the e-signature half.
