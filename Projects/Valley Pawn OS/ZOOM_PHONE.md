# Zoom Phone — Store Lines & Extension Map

Built 2026-08-07. Reference for anything touching Zoom Phone (missed calls, voicemail, extensions).

## Account

- **Account:** Full Circle Finance Inc — Workplace Pro + Zoom Phone plan
- **Login:** jdavis@fcfpawn.com (Joshua is the Owner/Admin — can see every user's call history/voicemail
  from the admin console, not just his own)
- **Admin path:** zoom.us → left nav "Phone" → scroll sidebar to "Phone System Management" → "Users & Rooms"
  → click a user → "History" tab (has Voicemail / Call Result / Event columns and date-range + filters)
- **No Zoom Phone MCP connector exists** (checked connector registry 2026-08-07 — "Zoom for Claude" is
  meetings-only). Automation drives the admin web UI via Claude in Chrome instead.

## Extension / Line Map (updated 2026-08-21 — 3 of 5 stores LIVE on Zoom Phone; Culpeper/Roanoke staged)

| Store | Zoom user (login) | User Ext. | Queue / Ext. | Number | Live? |
|---|---|---|---|---|---|
| (admin only) | jdavis@fcfpawn.com (Joshua, Owner) | 800 | — | — (no calling plan since 2026-08-21) | n/a |
| Lexington | lexington@fcfpawn.com | 807 | Lexington Store Queue / 804 | (540) 461-8349 | LIVE |
| Harrisonburg | harrisonburg@fcfpawn.com | 802 | Harrisonburg Store Queue / 805 | (540) 574-4500 | LIVE |
| Waynesboro | waynesboro@fcfpawn.com | 803 | Waynesboro Store Queue / 806 | (540) 221-6346 | LIVE |
| Culpeper | culpeper@fcfpawn.com | 808 | Culpeper Store Queue / 810 | still on Verizon (540) 445-5510 | staged only |
| Roanoke | roanoke@fcfpawn.com | 809 | Roanoke Store Queue / 812 | still on Verizon (540) 562-0776 | staged only |

**Licenses (2026-08-21):** exactly 5 × US/CA Unlimited Calling Plan seats ($75/mo) on exts 802/803/807/808/809.
Joshua's ext 800 has NO calling plan (removed 2026-08-21 — admin-only account, not in any call path).

**Note:** Joshua's own Zoom user (ext 800) carries the Lexington store's public number — that's why every
Zoom voicemail notification email Joshua gets personally is actually a Lexington store call, not a call to
him personally. Harrisonburg and Waynesboro's voicemail notification emails go to their own store Gmail
inboxes (harrisonburg@fcfpawn.com / waynesboro@fcfpawn.com — see `store-credentials` skill), which nobody
reliably checks — this was the gap `zoom-voicemail-alert` was built to close.

Culpeper and Roanoke are expected to be added as Zoom Phone users soon ("will have them at 5 soon" per
Joshua 2026-08-07). When that happens no manual update is needed here for the automation to pick them up —
`zoom-voicemail-alert` re-reads the live Users & Rooms roster every run — but update this table for human
reference once their extensions are assigned.

## Automation

- **`zoom-voicemail-alert`** (Cowork scheduled task, SKILL.md at `~/Documents/Claude/Scheduled/zoom-voicemail-alert/`)
  — runs every 20 min, Mon–Sat 9am–7pm. Reads the live Users & Rooms roster, checks each store line's
  admin History tab (today only) for new missed-call/voicemail events, dedupes against a state file, checks
  whether the call was already returned (Step 3.5, added 2026-08-10), and posts a consolidated alert to
  Slack **#voicemails-missed-calls** so the store team knows to call the customer back. Silent when there's
  nothing new or everything was already called back. Self-heals nothing on a Zoom session logout — DMs
  Joshua instead of attempting a login, per safety policy on credential entry.
- Posts to Slack **#voicemails-missed-calls** (`C0BP4M3B99R` — updated 2026-08-10; the original channel
  `C0BND1NK65V` was archived same day and Joshua recreated the channel fresh under this new ID).
- **Dedupe state:** `~/Documents/Claude/Projects/Valley Pawn OS/.zoom_voicemail_alert_state.json` (moved
  here 2026-08-10 — `~/Documents/Claude/Scheduled/` is read-only in Cowork sessions, see CHANGELOG). Never
  scope a run beyond today's date range — today-only + this state file together are what prevent
  re-alerting on a prior day's calls.
- **Callback verification:** since 2026-08-10 the task cross-references each candidate missed call against
  the store's Outbound call log for that day. If the store already placed a later call to the same number
  that Connected, the row is suppressed from the alert instead of nagging about a callback that already
  happened.
- **`zoom-voicemail-eod-review`** (Cowork scheduled task, SKILL.md at
  `~/Documents/Claude/Scheduled/zoom-voicemail-eod-review/`, built 2026-08-12) — daily close-out companion.
  Runs once a day (cron `45 17 * * *`, actual dispatch ~5:52 PM local due to the platform's few-minute
  scheduling jitter — Joshua asked for 5:45 PM specifically, flagging in case exact timing matters). Unlike
  the intraday task, it is stateless: it re-pulls EVERY missed call/voicemail from that day (not just new
  ones since the last state-file checkpoint) and re-runs the same staff-callback / customer-reconnected
  resolution check against the full day's Outbound+Inbound rows. Posts to the same
  **#voicemails-missed-calls** channel EVERY run — either the list of still-outstanding callbacks, or an
  explicit all-clear — since it's meant to be the definitive end-of-day record, not a silent-when-nothing
  event alert like the intraday task. Does not read or write the intraday task's dedupe state file; the two
  are fully independent so a bug in one can't silently break the other. Same session-expired and failure
  DM policy as `zoom-voicemail-alert`. Note: channel was renamed `#voicemails-missed-calls` ->
  `#voicemails-calls-missed` by Joshua on 2026-08-13; channel ID `C0BP4M3B99R` unchanged so no task update
  was needed, but this doc's channel name references should be read as historical.

## Admin Console Audit — 2026-08-13

Full audit of the 3 live Zoom Phone lines (Harrisonburg, Waynesboro, Lexington) via Users & Rooms, Phones &
Devices, Call Queues, and Auto Receptionists. Prompted by Joshua asking for a settings health check across
the 3 store phone lines. Findings and actions:

**FIXED (live, safe, non-customer-facing) — 911 emergency address was wrong for 2 of 3 stores.**
Harrisonburg's and Waynesboro's Zoom users were both defaulting to the Zoom account's company address
(125 Walker St, Lexington) for E911 — meaning a 911 call placed from either store's phone would have sent
dispatch to Lexington, ~30-40 miles from the actual caller. Added and activated a Personal Emergency
Address for each: Harrisonburg -> 1790 E Market St, Harrisonburg, VA 22801; Waynesboro -> 1321 W Broad St,
Waynesboro, VA 22980 (both verified/geocoded by Zoom on save). Lexington's own line was already correct
(it legitimately is the company address). No customer-facing or reversibility risk — this only corrects
911 routing to the true location, done without waiting for confirmation per standing autonomy preference.

**URGENT, NOT FIXED (requires physical in-store action) — Harrisonburg has ZERO working phones right now.**
Both of Harrisonburg's Grandstream WP822 wireless handsets (`Harrisonburg wireless`, `Harrisonburg wireless
2`, ext 802) show **Offline** in Phones & Devices with "Factory reset needed for provisioning" — a
provisioning failure, not a simple network blip. No remote reboot/factory-reset action exists in the admin
console for these devices (checked the device row's "More Actions" menu — only Bind Provision Template /
Unassign are available). This is 100% consistent with the missed-call flood in #voicemails-calls-missed on
2026-08-12 (an EOD sweep found dozens of unresolved Harrisonburg/Waynesboro/Lexington missed calls with
**zero outbound calls logged all day on any of the 3 lines**) and 2026-08-13 morning (5-6 repeat missed
calls in under an hour, several numbers calling back 2-3x). **Someone needs to physically power-cycle /
factory-reset both Harrisonburg WP822 handsets in-store** (per Zoom's own device note, a triggered factory
reset completes in a few minutes via zero-touch provisioning once power/network is restored) — this cannot
be done remotely. Logged as an open item — see Life OS/OPEN_ITEMS_REGISTER.md.

**Other findings, not fixed (recommendations only, business-preference / build calls, not silent fixes):**
- No Call Queues exist on the account (0 configured) — all 3 stores run as plain "User" extensions with
  Simultaneous ring across 2 devices and a 30-second max wait before falling to voicemail, no hold/overflow.
  A proper Call Queue per store (multi-agent ring, hold music, configurable overflow) would handle burst
  volume far better than a 2-device user extension, especially relevant given the Harrisonburg outage
  showed there's no fallback path today when the store's phones are down.
- Lexington's desk phone (`Lexington 2`, Poly VVX250) is flagged **End of Life** by Zoom — still online and
  working today, but a similar unannounced failure to Harrisonburg's is a real risk; worth proactively
  budgeting a replacement before it fails rather than after.
- Harrisonburg's user Time Zone is set to `(GMT-7:00) Pacific Time` — should be Eastern. Affects how call
  history/voicemail timestamps display in the admin console (the underlying call time itself is UTC-based
  and unaffected). Not editable from the field shown on the Profile tab; needs a follow-up look at where
  this is actually set.
- A "Main Auto Receptionist" (ext 801) exists with zero numbers assigned to it — appears to be an unused
  default, not routing any store's calls. Harmless as-is but worth confirming it's not a forgotten
  half-finished setup.
- 2026-08-12 EOD review's "zero outbound calls logged on any of the 3 lines all day" is unexplained beyond
  Harrisonburg (which had no working phones to call FROM either). Waynesboro and Lexington's phones were
  online that day — worth a follow-up with those two stores on whether callbacks are happening off-platform
  (personal cell, invisible to this audit) or genuinely not happening.

## Timezone Fix + Call Queue Buildout — 2026-08-13 (same day, follow-up to the audit above)

Joshua approved two of the audit's open recommendations same-day: "fix the timezone" and, after seeing the
proposed Call Queue design, "yes build it."

**Timezone bug — FIXED (both affected users).** Root cause: Harrisonburg's and Waynesboro's Zoom user
Time Zone field was never set ("No option selected"), silently inheriting the account default (Pacific)
instead of the account's real Eastern location. Not editable from Phone System Management > Users & Rooms
> Profile (display-only there) — the actual field lives at User Management > Users > [click the user's
display name, not "Edit"] > Profile > Time Zone. Set both to "(GMT-4:00) Eastern Time (US and Canada)":
Harrisonburg (Walker Tapley) and Waynesboro (Chadd McClintic).

**Call Queues — BUILT, all 3 stores, not yet live (see cutover note below).** Design: one Call Queue per
store, replacing the fragile single-user/2-device extension model that has no overflow path (this is what
left Harrisonburg with zero fallback during its hardware outage). Each queue:
- Member: the store's existing Zoom user (so no device re-provisioning needed)
- Business Hours: Custom Hours, Mon/Tue/Thu/Fri/Sat 10:00 AM–6:00 PM, Wed/Sun off — matches real store hours
- Call Distribution: Simultaneous (Zoom default, unchanged)
- Music on Hold: Default (Zoom default, unchanged)
- Max Wait Time: 1 minute (Zoom default, unchanged)
- Overflow: Leave Voicemail to Current Extension (Zoom default, unchanged)

| Queue | Ext. | Member |
|---|---|---|
| Lexington Store Queue | 804 | lexington@fcfpawn.com (Ext.807) |
| Harrisonburg Store Queue | 805 | harrisonburg@fcfpawn.com |
| Waynesboro Store Queue | 806 | waynesboro@fcfpawn.com |

**Cutover status — ALL 3 STORES LIVE (2026-08-14).** Joshua approved testing Lexington first, then
approved cutting over Harrisonburg and Waynesboro same-session once Lexington proved out. All three
reassigned via Number Management > Phone Numbers > row's "..." menu > Assign > Type=Call Queue > select
the store's queue > Save:
- Lexington (540) 461-8349: Joshua Davis-Ext.800 → Lexington Store Queue-Ext.804
- Harrisonburg (540) 574-4500: harrisonburg@fcfpawn.com-Ext.802 → Harrisonburg Store Queue-Ext.805
- Waynesboro (540) 221-6346: waynesboro@fcfpawn.com-Ext.803 → Waynesboro Store Queue-Ext.806

**Verified live with real call-log data (not just config), 2026-08-14:** found actual answered customer
calls on all 3 lines showing "Forwarded by [Store] Store Queue Ext.XXX" → Event "Ring to Member" → Call
Result "Answered" — full ring-to-answer path confirmed working, not just number routing. All 6 store
phones (2 per store) confirmed Online in Phones & Devices.

**RESOLVED (2026-08-14) — Lexington migrated off Joshua's personal Zoom account.** Historical context:
Ext.800 (jdavis@fcfpawn.com) was simultaneously Joshua's personal owner/admin account AND the account
Lexington's 2 physical store phones were registered under — which made Joshua's personal cell ring for
Lexington store calls. Joshua approved the dedicated-account fix (incl. a 4th Zoom Phone license,
$15/mo, purchased via Plan Management). Zero-downtime migration executed same day:

1. Created `lexington@fcfpawn.com` Zoom user (Zoom Meetings Basic + Zoom Phone, **Ext.807**).
2. Added Ext.807 as 2nd member of Lexington Store Queue (queue rang both during transition).
3. Unassigned both physical phones from Ext.800, reassigned to Ext.807 one at a time.
4. Activation: the Zoom invite went to the lexington@ Gmail mailbox (NOT an alias of jdavis@ — it's a
   separate mailbox; a Google "suspicious login" challenge also had to be cleared via the admin console's
   per-user Security > Login challenge > "Turn off for 10 mins" before Joshua could get in). Joshua
   activated the account 2026-08-14.
5. Removed Ext.800 from the queue — verified members list now shows ONLY lexington@ Ext.807
   (Receive Calls: On). Joshua's personal devices are no longer in any store call path.

Post-migration device status (Phones & Devices, 2026-08-14): Poly VVX250 **Online** (provisioned
Aug 14); Grandstream WP822 cordless **Offline — "Factory reset needed for provisioning"** — needs a
power-cycle at the store, then factory reset + reprovision if it doesn't recover (same procedure as
Harrisonburg's WP822s). Desk phone carries the queue in the interim. Cosmetic note: the lexington@ Zoom
user's display name shows "Joshua Davis" (from account creation) — can be renamed to "Lexington Store"
in User Management for clarity.

**Not independently verifiable from available data:** hold music playback and in-queue wait time. Zoom's
Call History table only exposes total call Duration, not queue hold/ring time, and Call Queues have no
History/Analytics tab on this plan. Routing itself is proven live (above); the queues' Music-on-Hold and
Max-Wait settings are confirmed unchanged from build (Default hold music, 1-min max wait) but can't be
evidenced from logs — would require a live test call to hear directly.

## Roster expansion spotted — Culpeper + Roanoke provisioned, NOT yet live (found 2026-08-14 ~4:30 PM ET)

A `zoom-voicemail-alert` run found 2 new rows in Users & Rooms that didn't exist as of the 2026-08-13 audit:

| Store | Zoom user | Ext. | Package | Number(s) | Desk Phone(s) |
|---|---|---|---|---|---|
| Culpeper | culpeper@fcfpawn.com | 808 | Zoom Phone Basic | -- (none assigned) | -- (none paired) |
| Roanoke | roanoke@fcfpawn.com | 809 | Zoom Phone Basic | -- (none assigned) | -- (none paired) |

Both show User Status Active / Activation Status Activated, but **no external phone number and no desk
phone are assigned to either** — Culpeper's Profile tab still has an unset "Area Code" field, and both
still show the stale `(GMT-7:00) Pacific Time` default (the same Time Zone bug fixed for Harrisonburg/
Waynesboro on 2026-08-13 — see above — has not yet been applied here). History tab confirms zero call
data for either extension over the trailing week. **Conclusion: these are stub accounts mid-setup, not
live customer-facing lines yet** — matches Joshua's 2026-08-07 comment that Culpeper/Roanoke were coming
"soon." `zoom-voicemail-alert` will keep checking both every run (Step 1's fresh-roster design) and will
naturally start finding real call data once a number + Call Queue are built for them, no task edit needed.
Worth a manual look next time Joshua is doing Zoom admin work: assign a number, fix the Time Zone field,
and build a Call Queue for each (mirroring the Harrisonburg/Waynesboro/Lexington pattern above) before
going live, so the same day-one gaps don't recur.

## 2026-08-21 — Licenses right-sized, Culpeper/Roanoke staged, call recording ON, caller-ID incident

**Licenses right-sized to 5 seats.** Joshua: "we only need 5 numbers, we only have 5 stores." Plan
Management edited to 5 × US/CA Unlimited Calling Plan ($75/mo). Calling plan REMOVED from Joshua's ext 800
(More Actions → Remove All Packages) — his account is admin-only now, no calling plan, no store call path.
The 5 plans sit on 802 (Harrisonburg), 803 (Waynesboro), 807 (Lexington), 808 (Culpeper), 809 (Roanoke).
Culpeper/Roanoke users were created the Lexington way (Unassigned/free Meetings Basic + Zoom Phone), NOT
Workplace Pro — a near-miss $50.97/mo Workplace Pro checkout was caught and closed unordered.

**Culpeper + Roanoke fully staged, NOT live — Verizon untouched (HARD RULE).** Queues built: Culpeper
Store Queue ext 810, Roanoke Store Queue ext 812, both with "NOT LIVE" descriptions and NO numbers
assigned. Business hours set correctly per store: Culpeper Mon–Sat 10–6 (only store open Wednesday); all
other stores Mon/Tue/Thu/Fri/Sat 10–6, Wed+Sun off. Grandstream WP822 cordless phones ordered on Amazon
2026-08-15 (~$96 ea, AMEX 2003) shipped to each store; managers notified. Cutover = a future explicit
step (port/point the Verizon number at the queue) ONLY on Joshua's word — do not touch the Verizon lines.

**Automatic call recording ON company-wide (inbound + outbound).** Enabled at account level and verified
per-line via each extension's Policy tab (aria-checked on all 6 lines). Legal recording disclaimer
accepted by Joshua himself. Retention: "Auto delete data after retention duration" is OFF — recordings
keep indefinitely until manually deleted. Plan: listen to Monday's recordings of Lexington's sub-15-second
calls before deciding on Call Screening for spam.

**Spam controls.** "Block calls without caller ID" enabled account-wide (see incident below). Call-log
analysis confirmed neighbor-spoofing robocalls at Lexington (7 of 11 answered calls ≤15s, scattered
spoofed VA-local numbers) — blocklists are useless against spoofing; Call Screening is the candidate fix,
decision pending after recording review.

**INCIDENT (2026-08-15→21, resolved): Lexington couldn't dial out.** Error: "We cannot complete your
call, your service does not support calling to this destination." Inbound fine. Root cause: enabling
"Block calls without caller ID" account-wide while ext 807 was the ONLY live extension with no Outbound
Caller ID configured (802/803 had their queue numbers set; 807 was created during the account migration
and the field was never set). Fix: 807 Profile → Outbound Caller ID → Lexington Store Queue
(540) 461-8349 — verified persisted after reload; block setting left ON.
**STANDING RULE: every live user extension MUST have Outbound Caller ID set to its store queue number.
808/809 currently have none (their queues have no numbers yet) — setting it is a MANDATORY step in the
Culpeper/Roanoke cutover checklist, before go-live.**

## 2026-08-26 — Recording announcement softened to "training purposes" script

Joshua reported the legally-mandated recording announcement ("this call is being recorded") was scaring
callers off, and asked either to silence it entirely or soften the wording. Recommended softening rather
than full silence — Virginia is one-party consent, so Valley Pawn's own knowledge suffices for VA-based
calls, but callers phoning in from two-party-consent states (e.g. MD, PA) make a fully silent recording
a real legal exposure. Joshua confirmed: "ok, letrs get it done and see how it goes."

**Change made (Account Settings → Phone → Automatic Call Recording → Inbound/Outbound audio
notifications → "recording has started" prompt → Edit → Add Audio → Text to Speech):** replaced Zoom's
default recording announcement with a custom TTS asset —

> "This call may be recorded for quality assurance and training purposes."

Asset name: **Inbound Recording Notice - Training Purposes** (English US, Matthew-Male voice, saved under
Personal Audios). "Press 1 to provide consent to be recorded" left OFF (Zoom's UI has a habit of toggling
this checkbox on stray clicks near the Edit dropdown — always screenshot-verify it's unchecked before Save
unless an IVR consent gate is actually wanted).

**Update (same day, follow-up):** Joshua then said outbound calls don't need the announcement at all —
"we are calling from virginia and the employees already know we are recording for training purposes."
Turned OFF both "when the recording has started" and "when the recording is stopped" prompts for
**Outbound** only. Zoom required accepting a liability disclaimer to disable the prompt ("you are solely
responsible for complying with applicable consent laws... required to indemnify Zoom against any
violation caused by you") — accepted per Joshua's explicit instruction and stated legal reasoning (VA
one-party consent + staff already informed = no notice legally required on calls Valley Pawn initiates).
Saved and confirmed.

**Final state:** Inbound = softened "training purposes" TTS prompt plays to callers. Outbound = no
recording announcement at all.

**Not done / no action needed:** the "before attempting to connect" prompt was left off on Inbound
(unchanged from prior state — was never enabled).

**Next:** per Joshua, "see how it goes" on the inbound wording — no further action queued unless he
reports it's still deterring callers, in which case the fallback is disabling the inbound "started" prompt
entirely too.
