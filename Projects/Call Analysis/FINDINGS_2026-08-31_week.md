# What the phones actually said — week of Aug 31–Sep 6, 2026

**Scope:** 321 recorded calls across Harrisonburg, Waynesboro and Lexington (Culpeper and Roanoke
are still on Verizon and record nothing — no number in here is a company number). 256 of those
calls ran longer than 20 seconds and were read in full. This is not a keyword count; every call
in that set was read.

**Why this document exists:** the first automated weekly read said 68% of calls were about
"other" and that customers were mostly asking for things we don't have. Both were artifacts of a
narrow keyword list. Reading the calls says something quite different, and more useful.

---

## The one-paragraph version

The phone is not a sales line right now — it is a collections and loan-servicing desk, and it is
good at that job. Where it loses money is the buy side: people call wanting to sell us things,
and we routinely decline to put any number on it, take no name, set no appointment, and hand
control of the follow-up to the customer. Across the week, **every caller who was quoted a number
committed to coming in; almost none of the callers who weren't quoted did.** That is the single
most repeatable pattern in the data and it is worth real money.

---

## 1. Quoting a number is what gets people in the door

This showed up independently in all six reading passes, without being looked for.

| | Result |
|---|---|
| Callers given a specific number | Nearly all stated they were coming in, often naming a time |
| Callers told "I'd have to see it" / "text me photos" | Almost none committed; no name or number taken |

Representative:
- A caller with an Excalibur crossbow was given a conditional $160 — *"it's just a rough
  estimate"* — and said he'd come by before six. That is the model: hedge the number, still give
  the number.
- A caller with nine Nintendo Switch games was told *"it all depends on the game."* Staff never
  asked a single title. Call ended with no day named.
- A caller with three Makita drills and a saw was **sitting in our parking lot** — *"I'm in the
  red Chrysler 200 sitting outside your door"* — and was asked to text photos instead, because
  the employee was working alone.

**Action:** a standing rule that no sell-side call ends without either a conditional range or a
booked time, and that a name and callback number is captured every time we can't quote.

## 2. We capture nothing when the answer is "no"

Not once in 256 calls did anyone take a name and number for a follow-up when we didn't have the
item. Not once was another store's stock offered — we have five locations.

Things people called for and we didn't have: gas push mower, non-gaming laptop under $800 (16",
not HP), Porter Cable angle grinder, aluminum trekking poles, graded basketball cards, Xbox
Series X, large road cases.

One caller wanted specific graded cards (a Jordan patch, two Kobes, a LeBron) for Labor Day
weekend; they're tied up as loan collateral. He asked *us* to call *him* back Monday. That
callback exists only in a transcript.

**Action:** a want-list. Name, number, item, at every store. It costs nothing and it is the
cheapest inventory signal in the business.

## 3. The biggest single miss of the week: the gold coins

A caller offered **five half-ounce US gold coins** (~2.5 oz gold). He was quoted *"very very
roughly around 4,500"* — the employee's own words were *"I'm kind of spitballin' here"* and
afterward, to the customer, *"I was a little bit on the low end because I wasn't sure if they
were the 21 karat or not."* The customer's response: *"that's way way way too low… I was offered
around 10,000."*

From his description (Marion Anderson, early 1980s) these are almost certainly American Arts
Commemorative Series gold medallions — a standard, identifiable half-ounce item.

**Action:** no precious-metal quote over the phone without the spot-price sheet in hand, full
stop. This is the exact failure the melt-calculation policy exists to prevent.

## 4. The phone-payment gap is costing collections

Repeatedly across the week, customers with past-due loans asked to pay by phone and were told no.
Answers were inconsistent store to store and shift to shift — some staff offered the app or the
website, some just said come in. In two separate calls the app itself failed: *"there must be
something wrong with the app."*

One customer was driving 35+ miles to hand over a payment we could have taken remotely.

**Action:** one answer, everywhere, and fix or replace the app payment path. Every one of these
is a past-due account staying past-due a few more days.

## 5. The "silence" question — measured, and my first answer was wrong

35% of recordings (112 of 321) captured no conversation. I first checked Zoom's `accepted_by`
field and reported that **zero of 273 inbound calls went unanswered**. That number is real but
**I drew the wrong conclusion from it, and the correction matters.**

Then I measured the audio itself rather than inferring from the transcripts:

| | mean volume | peak | detected silence |
|---|---|---|---|
| The 8 longest "silent" recordings | −17 to −34 dB | near 0 dB | mostly **zero** |

**They are not silent at all.** They are loud, continuous audio, full length, with almost no gaps
— and Whisper transcribes none of it as speech. Loud + continuous + unintelligible to a speech
model is what **music or a repeating tone** looks like. The recorded greeting also plays a median
of 2 times and up to 8 times in these files, versus once in a normal call.

The shape of it:

- **Inbound: 103 of 273 silent (38%). Outbound: 9 of 48 (19%).**
- By store: **Waynesboro 44%**, Harrisonburg 35%, Lexington 26%.
- Median length 56s; 18 of them run over two minutes, the longest 4m33s.

**The likely explanation, and why "zero unanswered" was misleading:** if the recording begins when
the *queue* answers — not when a person picks up — then `accepted_by` is populated on every
inbound call whether or not a human ever took it. That would make "0 unanswered" an artifact of
how the queue answers, not evidence that we caught every call. A caller who waits through the
greeting and hold music and hangs up would produce exactly what we're seeing: full-length, loud,
no speech, greeting repeating.

**If that's right, roughly a third of inbound calls may be abandoning in the queue** — which is a
far more expensive problem than hold time, and the opposite of what I told you first.

**Two ways to settle it, both underway:** three sample recordings have been saved for a listen
(anyone will recognise their own hold music in seconds), and the Zoom app needs the
`phone:read:list_call_logs:admin` scope added, which unlocks Zoom's own per-call disposition and
queue wait/abandon data. That's the authoritative source and it is currently the one thing this
pipeline can't see.

## 6. What customers actually asked about

Roughly half to two-thirds of substantive calls were existing-loan servicing — payments, payoffs,
due dates, extensions, "please don't sell my item." That side is handled well: the grace-period
and late-fee explanations were clear, reassuring and consistent, and outbound collection calls
produced payment commitments and genuine thanks.

Real demand signals on the merchandise side:
- **Gaming consoles are the number-one draw**, in every batch, both directions (people buying
  them from us and selling them to us). PS5, PS5 Pro, PS4, Xbox Series X, Switch games.
- **Power tools and outdoor equipment**, both directions — and on the same day we told a buyer we
  had no mower, we told a seller we didn't want his because they're out of season.
- **Firearms process questions** — FFL transfers, background-check status — several per week.
  Three calls in one batch were customers waiting on delayed checks.
- Precious metals barely appeared in some batches at all, which is worth comparing against what
  we spend marketing them.

## 7. Conduct on recorded lines

These are on company recordings and should be handled privately, not in a channel:

- Staff speculating on a customer's criminal activity after a voicemail beep.
- Staff narrating a management departure to a customer, and mocking another customer by name.
  That caller said *"I'm gonna quit coming in there."*
- Staff telling an upset customer, repeatedly, *"this is coming from the owner and the general
  manager… this isn't my decision."*
- A ~14-minute call in which an employee appraised an item using a consumer AI chatbot on the
  phone with the customer, then passed on it.
- Loan payoff amounts given to third parties who called on a customer's behalf.
- A customer accused of pawning something that wasn't his — a gift from his mother — who called
  back, was put on hold mid-complaint, and ended up apologizing to *us*. He bought anyway. We
  kept him by luck.

## 8. Data quality notes

- **Store labels are wrong on some calls** — several tagged Waynesboro have staff answering
  "Valley Pawn Lexington." Per-store call metrics can't be trusted until routing/tagging is
  checked.
- **Direction is wrong on some calls** — inbound-tagged records that are plainly outbound
  voicemails we left.
- Two customers in the same day asked whether we were open Labor Day, and several more asked
  about the Wednesday closure. That's a Google/Facebook hours gap, not a phone problem.

---

## The short list

1. Never end a sell-side call without a number or a booked time — and capture a name either way.
2. Start a want-list at every store for things we didn't have.
3. No precious-metal quote by phone without the spot sheet.
4. One consistent phone-payment answer; fix the app path.
5. Pull the Zoom queue hold/abandon report.
6. Handle the conduct items privately with the people involved.
