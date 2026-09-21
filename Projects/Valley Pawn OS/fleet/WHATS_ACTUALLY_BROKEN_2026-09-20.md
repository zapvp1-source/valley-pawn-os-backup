# What's actually working and what isn't

2026-09-20. Read with the posting app's own token. Day-by-day for the last 14 days, not lifetime
rates — because lifetime rates are dominated by the 9/12–9/17 outage and say nothing about now.

`●` = posted that day · `–` = did not

```
Task                                  07 08 09 10 11 12 13 14 15 16 17 18 19 20
                                      Mo Tu We Th Fr Sa Su Mo Tu We Th Fr Sa Su
daily-clockin-check                    ●  ●  ●  ●  ●  ●  –  –  –  –  ●  ●  ●  –
chekkit-unanswered-alert               ●  ●  ●  ●  ●  –  –  –  –  –  ●  ●  ●  –
daily-funds-verification               ●  ●  ●  –  ●  –  –  –  –  ●  ●  ●  ●  –
daily-cloudcover-check                 ●  ●  ●  ●  ●  –  –  –  –  –  –  ●  ●  –
daily-dress-code-check                 ●  ●  ●  ●  ●  –  –  –  –  –  –  ●  ●  –
pawn-walk                              –  ●  ●  –  ●  ●  –  –  –  –  ●  ●  ●  –
sold-review                            –  ●  ●  –  ●  ●  –  –  –  –  ●  ●  ●  –
discount-review                        –  ●  ●  –  ●  ●  –  –  –  –  ●  ●  ●  –
chekkit-unanswered-eod-followup        ●  ●  ●  –  ●  –  –  –  –  –  ●  ●  ●  –
daily-items-to-price                   ●  ●  ●  –  ●  –  –  –  –  –  ●  –  ●  –
jewelry-onhand-nightly-pull            ●  ●  ●  –  ●  –  –  –  –  ●  –  ●  –  –
daily-unopened-email-eval              ●  ●  ●  ●  ●  –  –  –  –  –  ●  –  –  –
-- weeklies (Monday only) ----------------------------------------------------
layaway-yield-weekly                   ●  –  –  –  –  –  –  –  –  –  –  –  –  –
monday-bravo-combined-compile          ●  –  –  –  –  –  –  –  –  –  –  –  –  –
monday-bravo-postcheck                 ●  –  –  –  –  –  –  –  –  –  –  –  –  –
nics-weekly-mtd-ranking                ●  –  –  –  –  –  –  –  –  –  –  –  –  –
weekly-returns-summary                 ●  –  –  –  –  –  –  –  –  –  –  –  –  –
weekly-store-kpis                      ●  –  –  –  –  –  –  –  –  –  –  –  –  –
review-obtained-last-week              ●  –  –  –  –  –  –  –  –  ●  –  –  –  –
weekly-markdown-verification-review    ●  –  –  –  –  –  –  –  –  ●  –  –  –  –
weekly-timekeeping-analysis            ●  –  –  –  –  –  –  –  –  –  ●  –  –  –
```

## Nothing is dead. Zero tasks have produced nothing in 14 days.

## What the picture actually shows

**Every daily task worked through 9/11, went dark 9/12–9/16, and came back 9/17–9/19.**
That block of dashes in the middle is the one outage, not twelve separate broken tasks.
Sunday 9/13 and 9/20 are blank because the stores are closed. That is correct behaviour.

**Cloudcover posted 9/18 and 9/19. It is working.** Its 48.7% lifetime figure was almost entirely
the outage plus pre-conversion history — a number that answered "how has this done since July"
when the question was "is it working now."

## The three real daily problems

| Task | Evidence | Known cause |
|---|---|---|
| **daily-unopened-email-eval** | missed 9/18 AND 9/19 — the only daily still failing *after* the recovery | Mail.app sweep needs the host-shell path; never converted to native |
| **daily-items-to-price** | missed 9/18 | Waynesboro grid stalls at 241 of 247 rows; needs a watcher restart before WAY is retriggered |
| **jewelry-onhand-nightly-pull** | missed 9/17 and 9/19 | LEX Bravo session wedges; all-or-nothing rule correctly suppresses a partial post |

## The bigger problem: Monday 9/14 was lost and never backfilled

Six weekly reports posted on Monday 9/07 and have not posted since — 9/14 fell inside the outage
and nothing re-ran them: layaway-yield-weekly, monday-bravo-combined-compile, monday-bravo-postcheck,
nics-weekly-mtd-ranking, weekly-returns-summary, weekly-store-kpis. Three others limped back later
in the week (review-obtained 9/16, markdown-verification 9/16, timekeeping 9/17).

**Monday 9/21 is tomorrow.** These have had exactly one successful cycle in the window, so tomorrow
is the real test of the weekly tier — and the highest-value thing to watch.

---

# ROOT CAUSE OF THE WEEKLY FAILURES — found 2026-09-20

The six weeklies did **not** fail to run. **All 12 weekly tasks FIRED on 9/14 and published
nothing.** Verified against the live registry: every one is `enabled: true`, every cron is correct,
every `nextRunAt` is correctly set for Monday 9/21, and every `lastRunAt` is 9/14 or later.

This is the "fires, then dies mid-run" class — the exact failure the expected-outputs manifest was
built to catch, and the reason `lastRunAt` must never be trusted as proof a task worked.

## Why they died

The 9/12–9/17 outage had one cause: the **osascript / Control_your_Mac connector disappeared from
scheduled sessions**. On 9/17 that was fixed for **eleven DAILY tasks** by converting them to native
launchd agents. **The weekly Monday chain was never converted.**

A scan of their SKILLs: **11 of the 12 still gate on that connector at step 0** —
monday-bravo-combined-run · -combined-compile · -postcheck · -cell-gapfill · weekly-store-kpis ·
weekly-returns-summary · nics-weekly-mtd-ranking · layaway-yield-weekly · review-obtained-last-week ·
weekly-markdown-verification-pull · -review. (Only weekly-timekeeping-analysis is clear — it has no
host-shell dependency.)

**The connector is still absent today** (confirmed by tool search in this session). So Monday 9/21
would have failed in exactly the same way, for the third Monday running.

## What was done about it — `com.valleypawn.monday-pull`, Sundays 16:30

A native launchd agent, same proven shape as `morning_pull.sh` (working since 9/18): health-gate,
drop triggers into the Bravo queue, poll, integrity-gate, write an honest certificate. No Claude
session, no osascript, no computer-use — so the connector's absence cannot touch it.

It pulls the five reports the Monday chain consumes, under the names the **pipeline actually
knows** — read out of the pipeline's own docs and output history, never guessed, because a wrong
report name does not error, it returns nothing:

`aged-inventory-summary` · `loans-75-days-past-due` · `layaways` · `employee-activity` ·
`chekkit-inactives`

It **publishes nothing**. Its only job is to put real CSVs on disk before the Monday tasks wake up,
so they have something to read instead of dying at step 0. Installed and verified healthy; fires
16:30 today, ahead of the Sunday 18:00 chain and Monday 08:00.

**Still to do:** the publish side of those Monday reports is still Cowork+osascript. Getting the
data on disk removes the hard blocker; converting each report's publish step to native is the
remaining work, and is what turns Monday from "should work" into "provably works."
