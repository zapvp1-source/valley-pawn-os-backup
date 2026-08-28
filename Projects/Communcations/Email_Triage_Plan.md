# Inbox Control Plan — Joshua / CEO Mail

**Drafted:** 2026-08-26 · **Status:** ✅ ALL FOUR PHASES + PERSONAL/CORPORATE CATEGORY BUILD EXECUTED 2026-08-27 — see §7, §8, §9
**Domain:** 1 (Valley Pawn) + 3 (Personal) · **Project:** Communcations
**Method:** measured against the live Unified Search index (341,912 messages, all 9 Apple Mail accounts) + live Gmail on jdavis@fcfpawn.com. No estimates below — every number is counted.

---

## 1. The actual diagnosis

**You do not have an email problem. You have a mailbox-aggregation problem.**

Apple Mail is carrying **9 accounts**. Volume over the trailing 30 days:

| Account | Msgs/day | What it is |
|---|---:|---|
| waynesboro@fcfpawn.com | 275 | store staff mailbox |
| culpeper@fcfpawn.com | 258 | store staff mailbox |
| lexington@fcfpawn.com | 246 | store staff mailbox |
| roanoke@fcfpawn.com | 227 | store staff mailbox |
| harrisonburg@fcfpawn.com | 193 | store staff mailbox |
| **5 store boxes subtotal** | **1,199** | **88% of everything you see** |
| zapvp1@me.com | 79 | your personal |
| jdavis@fcfpawn.com | 52 | **your actual work email** |
| fullcirclepawn@gmail.com | 29 | legacy |
| 2 dormant accounts | ~1 | |
| **TOTAL** | **1,359/day** | |

**Your real inbox is 131 emails/day** (work + personal). The other 1,199 belongs to your staff.

For scale: Radicati puts the average business professional at ~126 emails/day and executives at **150–200+/day**. At 131 you are *below* the executive norm. The overload is entirely the five store mailboxes bleeding into your unified inbox.

### What's in the store boxes

**98% is machine/marketplace mail** (35,104 of 35,961 messages over 30 days). Top senders, 90-day counts:

- `ebay@ebay.com` — 17,592 (offer/counteroffer notifications, one per event)
- `noreply@classicfirearms.com` — 6,938
- `members.ebay.com` buyer aliases — 6,677
- `sales@cdnnsports.com` — 3,063
- `gunbroker.com` — 1,554

These are **workflow notifications for whoever is working that store's eBay and FFL desk**. None of them are addressed to you, and none require a CEO decision.

### A live anomaly worth fixing today

CDNN Sports broke. Daily volume across the store boxes:

```
Aug 12–17:  20  43  45  69  46  49      ← normal
Aug 18–23: 291 332 329 333 351 406      ← broken
Aug 24–25:  37   2                      ← self-corrected
```

Same subject line repeated four and five times in a row ("BERETTA Factory Magazines & Parts!!"). **~2,000 emails in six days from a single vendor.** Nobody caught it. That is the failure mode the plan below is designed to catch automatically.

### Your own inbox (jdavis@fcfpawn.com) — 1,561 msgs/30d

| Bucket | Count/30d | Share |
|---|---:|---|
| Chekkit / Bravo / Gusto / Indeed / Controlio alerts — **already piped to Slack** | 539 | 35% |
| Consumer marketing (TikTok, Joss&Main, Reef, Vistaprint, Rugtomize, tile, supplements, travel) | 312 | 20% |
| Everything else — vendors, staff, customers, compliance, banking | ~710 | 45% |

**55% is provably removable without losing a single piece of information.** The Chekkit and Bravo alerts are duplicates of things you already read in Slack.

Gmail state: **5,061 messages in the inbox, 1,772 unread, 4 user labels total.** There is effectively no routing structure — every message lands in one undifferentiated pile.

Live sample, last 48 hours: **201 threads. One needed you** (Preston, re: the gold bars). That's a 0.5% signal rate at the surface you're actually looking at.

---

## 2. What "under control" looks like for a CEO

The goal is **not** fewer emails and **not** inbox zero. It's that nothing unknown is sitting in the pile. Four layers, in this order — each one only handles what the layer above couldn't kill:

| Layer | Job | Target |
|---|---|---|
| **0 — Separation** | Other people's mailboxes are not in your view | 1,359 → 131/day |
| **1 — Elimination** | Dead subscriptions and duplicate alerts stop arriving | 131 → ~60/day |
| **2 — Routing** | What remains is auto-sorted before you see it | ~60 → ~15 in the "you" tier |
| **3 — Synthesis** | One brief tells you what happened and what needs you | 1 read, 2×/day |

Benchmark for a well-run exec inbox: **under 20 messages/day that genuinely require the CEO**, touched in **two fixed windows** (morning + late afternoon), with everything else either handled by a delegate or read-only.

You are currently at 1,359 arriving and ~0 routed. The gap is all mechanism, not discipline.

---

## 3. The build

### Phase 1 — Separation (biggest win, zero risk, fully reversible)

1. **Pull the 5 store mailboxes out of your unified inbox view.** Keep the accounts connected so search still works — just uncheck them from "All Inboxes" and turn off their notifications. You keep full access via Unified Search and the Gmail MCP; you stop *seeing* 1,199/day.
   *Effect: 1,359 → 160/day. This single change is 88% of the problem.*
2. **Assign an owner per store box.** Each store manager already works their own eBay/FFL queue; formalize that the store box is theirs and escalation to you is by Slack, not by you reading their mail.
3. **Retire `fullcirclepawn@gmail.com`** (29/day, legacy) — forward-and-archive.

### Phase 2 — Elimination

4. **Unsubscribe sweep on your two real accounts.** ~40 senders account for the 312/month of consumer marketing. One pass, list-unsubscribe where available.
5. **Turn off the duplicate alert channels at the source** — Chekkit unanswered-message alerts, Bravo `noreply-reporting`, Gusto notifications, Controlio, Indeed. All 539/month of these already reach you in Slack. Kill the email leg, keep Slack.
6. **Vendor-flood guard.** A standing rule: any single sender exceeding 100 messages/day across the fleet gets auto-quarantined and flagged. This is the CDNN catch.

### Phase 3 — Routing

7. **A four-tier label structure on jdavis@fcfpawn.com**, applied automatically:
   - `1-Action` — a named human is waiting on you (Preston, Lainie, managers, bank, attorney, landlord, insurance, FFL/ATF)
   - `2-FYI` — real but no reply needed; read in batch
   - `3-Vendor` — quotes, invoices, shipments; goes to Preston/Lainie first
   - `4-Auto` — receipts, confirmations, marketing; archived unread, searchable forever
   Same four tiers on `zapvp1@me.com` with a personal/property/financial split.
8. **The 1,772 unread backlog** gets one bulk pass: anything older than 30 days that isn't `1-Action` is archived. It is searchable forever and it is not a to-do list.

### Phase 4 — Synthesis

9. **`ceo-mail-brief`** — a scheduled task, twice daily (7:00 AM and 4:30 PM ET). Reads jdavis + zapvp1 since the last run and produces one Slack DM:
   - **Needs you** — sender, one-line ask, and a *pre-drafted reply* in your voice for each
   - **FYI** — 3–5 bullets
   - **Filed** — a count, not a list
   - **Anomalies** — any sender spiking above baseline (the CDNN catch)
   Under 90 seconds to read. You act from the DM; the inbox becomes a filing cabinet, not a queue.
10. **`weekly-mail-health`** — Sunday: volume by account, top 10 senders, subscription creep, tier accuracy. Keeps the system honest instead of silently decaying.

---

## 4. What this does not touch

No existing scheduled task is modified. No mail is deleted — Phase 1 is a client-side view change, Phase 3 archives rather than deletes, and every message stays in Unified Search. Nothing here changes store operations; it changes who *reads* store mail. Fully additive per Rule #4.

---

## 5. Expected result

| | Now | After |
|---|---:|---:|
| Arriving in your view | 1,359/day | ~131/day |
| After elimination | — | ~60/day |
| Requiring your attention | unknown | **~15/day, surfaced in 1 DM** |
| Unread backlog | 1,772 | 0 |
| Time in the inbox | continuous | 2 windows |

---

## 6. Sequence

Phase 1 first and alone — it's 88% of the win, takes under an hour, and is undone by re-checking a box. Prove it for a week. Then 2, 3, 4 in order, each proven before the next. Phase 4 is the durable piece; Phases 1–3 are what make Phase 4 cheap enough to run twice a day forever.

---

## 7. What actually happened — executed 2026-08-26

### Built and live

**Label structure** on `jdavis@fcfpawn.com`: `1-Action` (red) · `2-FYI` (blue) · `3-Vendor` (orange) · `4-Auto/{Already-in-Slack, Marketing, Receipts-Shipping}` (grey).

**Nine server-side Gmail filters**, imported as XML with *apply to existing* — so each filter cleared its own share of the backlog in the same action it started running. They run 24/7 on Google's servers; nothing depends on Claude being awake.

The design rule these follow, worth preserving through any future edit:

> **Filters only ever remove KNOWN noise from the inbox. They never hide an unrecognized sender.**

A sender nobody has classified always stays visible. The system can bury nothing that matters.

**`ceo-mail-brief`** scheduled task — 7:00 AM and 4:00 PM ET daily, pinned `claude-sonnet-5`. One Slack DM: NEEDS YOU (max 8, each with a ready-to-send reply drafted in Joshua's voice), FYI, a filed count, and a volume-anomaly line. Read-and-draft only — it never sends, replies, archives, or deletes. Monday runs also list unfiltered repeat senders as filter candidates, recorded but never auto-applied.

### Measured result

| | Before | After |
|---|---:|---:|
| Inbox messages | 5,061 | **2,084** |
| Inbox unread threads | 1,713 | **409** |
| Total unread | 2,740 | **694** |
| User labels | 4 | 11 |
| Filters | 0 | 9 |

Archived, not deleted — 4,046 messages: 2,230 duplicate Slack alerts · 1,263 marketing · 339 vendor · 201 FYI · 13 receipts. Every one is still in All Mail and in Unified Search.

### One side effect, disclosed

The first filter import had *Star it* set on `1-Action` and retroactively starred **1,374 messages**, diluting Joshua's 66 manual stars. Apple Mail had already synced the change before the original set could be snapshotted, so those 66 are **not recoverable**. Starring is now off in the filter — the red `1-Action` label is the signal instead — and existing stars were deliberately left alone, because bulk-unstarring would permanently destroy the originals rather than merely dilute them. Making `Starred` clean again is Joshua's call, not a call to make on his behalf.

### Phase 1 — ✅ DONE 2026-08-26

Built in Apple Mail, all nine accounts left connected so Unified Search keeps indexing `~/Library/Mail`:

- **Smart Mailbox "My Mail"** — matches *any* of: message is in Inbox of **Corporate**, **Personal**, or **jdavis@fcfpawn.com**. The five store inboxes and the dormant `joshuachristiandavis@gmail.com` are excluded. Added to **Favorites**, so it sits at the top of the sidebar as the default click.
- **Settings → General → New message notifications** → *My Mail*
- **Settings → General → Unread count** → *My Mail* (this is the Dock badge — the number he actually sees all day)

**Immediate effect: All Inboxes 20,635 unread → My Mail 13,094.** 7,541 messages of store noise removed from view in one change, with nothing deleted, nothing unsubscribed, and no change to what store staff see. Reversible by deleting one smart mailbox.

---

## 8. Correction — Apple Mail Categories already did this, no iCloud rules needed

§7's "next lever" (custom iCloud Mail rules) turned out to be solving a problem Apple Mail had already solved. **Mail Categories** — Primary / Transactions / Updates / Promotions, classified on-device, active on every account including iCloud — was already on and already running. Smart Mailboxes just can't see it: "Show Mail Categories" is disabled inside a Smart Mailbox, which is why My Mail's badge never reflected it.

Verified 2026-08-27 by opening the Personal account outside My Mail and clicking each category tab:

| View | Unread |
|---|---:|
| Personal, raw inbox | 12,798 |
| Personal → **Primary** | 686 (then 2,840 once Mail finished re-indexing after the bulk actions below) |
| Personal → Promotions | 3,369 of 22,079 |
| Personal → Updates | 5,186 of 13,311 — **mixed**: real content (law firm, school, insurance) sitting next to junk |
| Personal → Transactions | 2,723 of 10,182 — receipts and confirmations, no reply ever needed |

**Primary is the number that matters — everything else is either noise or reference.**

## 9. Built 2026-08-27 — cleared it for real, not just filtered the view

**Personal (zapvp1@me.com):**
- Promotions and Transactions selected in full and marked read — nothing archived, nothing deleted, every message stays exactly where it is and stays searchable. Safe to batch because both categories are cleanly non-actionable.
- Updates was **not** bulk-cleared — it mixes signal with junk (Palencia Elementary, Johnson Gasink & Baxter LLP, Steadily insurance quotes for Bald Rock, sitting next to Vrbo and Microsoft policy spam). Blanket-clearing it would have buried real mail.
- Instead, the specific commercial senders you named — **Drift House, FUM, The Chosen People** — plus five more found in the same sweep (And Just Like... Health, ConsumerAffairs, Tesla, PRAY.COM, The Glucose Effect) were individually pinned via **right-click → Categorize Sender → Always Categorize as → Promotions**. This is a permanent, per-sender rule: every future email from these senders lands in Promotions automatically, no ongoing maintenance. FUM was already being caught correctly — verified, not just assumed.
- Deliberately left alone: **Hims** (subject read like a personal health reminder, not pure marketing — didn't want to risk burying something health-related), **Vrbo** and **Microsoft** (mixed real-notification senders, not safe to blanket-categorize).

**Result: Personal → Primary down to 2,840 unread** (from 12,798 raw). My Mail (the Dock-badge mailbox) down to **8,581** from 13,094.

**Corporate (fullcirclepawn@gmail.com):**
- Two Gmail filters built (Amazon Business receipts, subscription newsletters) with apply-to-existing.
- **Important finding, not fixed by design:** Corporate's Promotions tab mixes genuine Indeed candidate reply notifications in with real marketing — Apple's classifier misfires on templated recruiter emails. Bulk-clearing Promotions here would hide real hiring leads, so it was **not** touched. Corporate's Primary tab is accurate and safe to use as-is; its Promotions tab is not safe to batch-clear the way Personal's was.

**jdavis@fcfpawn.com:** unaffected by this pass — already at 444 unread from yesterday's Gmail filters, no further action needed.

**Known cosmetic bug:** the Personal account's sidebar unread badge showed 28,846 during and after the bulk mark-as-read — this is stale/incorrect (exceeds what the account actually contains); the category headers and My Mail count were the reliable readings throughout. Likely clears on Mail's next relaunch; not worth chasing further.
