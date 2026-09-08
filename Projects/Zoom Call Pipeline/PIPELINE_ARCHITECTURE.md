# Zoom Call Pipeline — one ingest, two consumers

**Created:** 2026-09-07 · **Domain:** 1 (Full Circle Finance Inc DBA Valley Pawn)

Zoom Phone automatic call recording has been on company-wide since 2026-08-21, inbound and
outbound, retention indefinite. Live lines: **Harrisonburg (ext 802), Waynesboro (803), Lexington
(807)**. Culpeper and Roanoke are still on Verizon and record nothing.

This folder is the **shared ingest layer**. It pulls recordings once, transcribes them once, decides
what kind of call each one is, and routes it. Two completely separate consumers read from it:

```
                    Zoom Phone recordings
                             │
                   zoom_ingest.py  (pull → transcribe locally → classify)
                             │
              ┌──────────────┴──────────────┐
              │                             │
      EMPLOYEE calls                 CUSTOMER calls
   (store↔Preston, store↔mgr)      (everyone else)
              │                             │
   Preston Knowledge Base            Call Analysis
   → sourced KB entries              → aggregate demand + service metrics
   → #preston-claude verify          → its own Slack channel
```

**Why one pipeline and not two:** two Zoom auth paths, two transcription passes and two sets of
credentials for the same audio is waste and a second thing to break. One ingest, one auth, one
Whisper pass.

**Why two consumers and never one system:** they have opposite privacy requirements. The knowledge
base is *durable and queryable by store staff* — it must never contain customer data. The call
analysis *is about customers* — so it must never persist an individual customer's words. Merging
them would force the weaker rule on both.

---

## ⚠️ MEASURED RESULT (2026-09-07): the employee-call vein is essentially empty

The premise of routing employee calls to the Preston knowledge base was that store↔Preston phone
traffic — the judgment that never reaches Slack — would be captured here. **Measured against the
full 2026-08-21 → 2026-09-07 window, with Preston's cell in the roster, it is not:**

| | count |
|---|---|
| Total recordings | **793** |
| Customer calls | **792** |
| **Employee calls** | **1** |
| Inbound / outbound | 668 / 125 |

The single employee call (2026-08-29, outbound, 14m42s to Preston) is real and was classified
correctly — the mechanism works. There simply is almost no store↔Preston traffic on the recorded
lines. The explanation is straightforward: managers call Preston **cell-to-cell**, which Zoom never
sees, and two of the five stores (Culpeper, Roanoke) are not on Zoom Phone at all.

**Consequence — do not treat call recordings as the knowledge-capture channel.** One call every
two-and-a-half weeks will not build a knowledge base. The Slack harvest (219 sourced entries) plus
the weekly verification loop remains the knowledge engine. Adding manager cell numbers to the
roster will NOT fix this: it only helps when a manager dials Preston *from the store line*, and the
125 outbound calls show they overwhelmingly do not.

The employee route stays in place because it costs nothing and occasionally catches a real one (a
15-minute call is worth having). It is a bonus, not a pipeline.

**What this data IS good for is the customer analysis** — 792 real calls in 17 days, ~46/day
across three stores. That side is fully viable and is where the value of this pipeline sits.

## The classification step is the privacy boundary

`zoom_ingest.py` classifies every call by matching the external party's number against
`internal_roster.json` (Preston, store managers, the five store lines, Joshua, Hillary).

- **Match → EMPLOYEE call.** Transcript is kept. It can become a knowledge-base entry.
- **No match → CUSTOMER call.** Transcript is processed and **deleted the same run.** Only
  structured, non-identifying facts survive.

Everything downstream depends on this being right, so it fails **closed**: an unknown number, a
blocked number, or a number the roster can't resolve is treated as a CUSTOMER call. Misclassifying
an employee call as a customer call costs one lost knowledge entry. The reverse would put a
customer's conversation into a knowledge base store staff can query. Those are not symmetric
mistakes.

## Customer transcripts are ephemeral — by design, not by policy

The strong move here is not "scrub the PII." Redaction on free-form speech is best-effort and
leaks — a first name, a street, an unusual item, and a transcript is re-identifiable.

So customer call transcripts **are never written to disk in readable form and never persist past
the run that created them.** The transcript exists in memory, gets reduced to a structured record,
and is discarded. What persists is:

```json
{"date":"2026-09-08","store":"HAR","direction":"inbound","duration_s":94,
 "intent":"item_availability","category":"gaming_console","item":"PS5",
 "outcome":"not_in_stock","qualifying_questions_asked":false,"spam":false}
```

No name. No number. No quote. Nothing that points back to a person. That record answers every
question the analysis actually needs to answer, and it cannot leak a customer.

The audio itself stays in Zoom under existing access control. This pipeline never copies it
anywhere permanent.

## Transcription is local, always

Whisper runs on the Mac Studio (`whisper-cpp`; ffmpeg already present). **No call audio is ever
sent to a third-party transcription service.** That is not a preference — it is what makes the
whole thing defensible. If local transcription ever stops working, the pipeline stops. It does not
fall back to a cloud API.

## Access — LIVE as of 2026-09-07

Zoom Server-to-Server OAuth app **"Valley Pawn Ops Agent"**, activated, account-level, not published.
**Read-only scopes only:**

- `phone:read:call_recording:admin`
- `phone:read:list_call_recordings:admin`

Nothing in this pipeline can change a Zoom setting, delete a recording, or place a call. Note that
Zoom's scope search surfaces `phone:delete:call_recording:admin` and
`phone:update:call_recording:admin` *first* when you search "recording" — both were deliberately
left unchecked. The `:master` variants were also left off; those are for partner/reseller accounts
spanning sub-accounts and do not apply here.

Credentials live at `~/.vp_secrets/zoom_s2s.json`, mode 600, never in Slack, a report, or a task
file. The secret can be regenerated in the Zoom marketplace at any time — update that one file and
nothing else breaks.

## What the API actually returns (verified live 2026-09-01, not assumed)

Two things were wrong in the first implementation and are worth recording so nobody re-introduces
them:

**1. The recording's `owner` is the CALL QUEUE, not the store user.** A Waynesboro call comes back
with `owner.extension_number: 806` ("Waynesboro Store Queue") while `accepted_by.extension_number`
is `803` (the store user). Mapping only the user extensions made every single call resolve to
`UNK`. `EXT_TO_STORE` therefore maps **both** the user and queue extension for each store, and
resolution tries `accepted_by` first (most precise — it's whoever actually picked up), then
`owner`. An unanswered call has no `accepted_by` at all.

**2. The metadata carries the caller's real name.** Each record includes `caller_name` — carrier
CNAM, e.g. a full personal name on an inbound customer call. That is PII arriving *outside* the
audio, which the "transcripts are ephemeral" rule alone would not have caught. It is never read,
never stored, never logged. Do not "enrich" a customer record with it.

Volume reference: **58 recordings on a single Tuesday** across the three live stores
(HAR 29 / WAY 15 / LEX 14). A full backfill to the 8/21 recording go-live is on the order of
900–1,000 calls.

## Operational notes learned from the first real run

- **State checkpoints after every call**, not at the end of the run. A backfill is hundreds of
  calls and can be killed part-way; end-of-run checkpointing lost all progress and would have
  re-appended every record already written. Re-running a completed range is now a no-op
  (`skipped=N`).
- **`--limit N`** chunks a long backfill and keeps any single invocation short.
- Stale audio from a killed run is swept at startup — call audio must never linger on disk outside
  the run actively transcribing it.
- Roughly 1 call in 58 fails transcription (very short or silent recordings). It is logged as a
  warning and skipped, never retried against a cloud service.

## Layout

```
Zoom Call Pipeline/
├── PIPELINE_ARCHITECTURE.md   this file
├── zoom_ingest.py             pull → transcribe → classify → route
├── internal_roster.json       whose numbers count as EMPLOYEE (fail-closed)
├── state.json                 processed call ids, so nothing is done twice
├── out/employee/              transcripts KEPT → Preston KB consumer
└── out/customer/              structured records ONLY → Call Analysis consumer
```

## Legal note (recorded once, not re-litigated)

The inbound announcement says calls may be recorded *"for quality assurance and training
purposes"* — which is what both consumers are. Outbound carries no announcement, a considered
decision on 2026-08-26 (VA one-party consent; staff informed). The ephemeral-transcript design
above exists partly so that this new use adds essentially no data footprint beyond the recordings
Zoom already holds. Worth one lawyer's glance on the derived-data question; not a reason to wait.
