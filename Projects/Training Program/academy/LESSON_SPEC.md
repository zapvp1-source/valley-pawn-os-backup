# Academy lesson spec — the one format every lesson is written in

One JSON file per lesson in `academy/lessons/L<level>/<nn>_<slug>.json`. `build_scorm.py` turns each into a SCORM 1.2 package TalentLMS scores natively. Writers (human or agent) produce ONLY this file; never touch the player.

```json
{
  "id": "L1-03",                       // level-lesson
  "level": 1,
  "order": 3,
  "title": "What you never say on the phone",
  "minutes": 6,                        // target total time
  "gate": "Level 1 must be complete by end of day 3 (HR-2026-05)",   // optional
  "floor_check": null,                 // or a one-line instruction the manager verifies on the floor
  "sources": ["P&P v2026.8 §01.06", "P&P v2026.8 §07.06", "KB employee-training-checklist-4dd34ccd"],
  "objectives": "verify a caller before you say anything, end every sell call with a number, a time or a name, and handle a firearm call without disclosing anything",   // one sentence, spoken on the Start card after "By the end, you'll be able to"; shown on the card too
  "video": {                           // exactly one of: file (mp4 in academy/media/), url, or null (narrated slides built from `slides`)
    "file": null, "url": null
  },
  "slides": [                          // used when no video: each becomes a narrated slide (TTS from `say`)
    {"heading": "The phone is where it shines or bombs", "bullets": ["Verify before you disclose", "Quote or capture — every sell-side call", "Never confirm a firearm is on the premises"], "say": "Narration text, 2–4 sentences, plain spoken English in the Valley Pawn voice."}
  ],
  "call_clip": {                       // optional; a real call from Call Analysis/audio (copied into academy/media/clips/)
    "file": "clips/HAR_xbox_quote.m4a", "caption": "Logan quotes an Xbox Series X without seeing it — listen for the range, the comps, and the close with a time.", "listen_for": ["Conditional range", "Comps out loud", "Close with a time"]
  },
  "key_points": ["3–6 one-line takeaways shown after the video"],
  "quiz": {
    "pass_percent": 80,
    "max_attempts": 2,                 // after this the manager is nudged
    "shuffle": true,
    "questions": [
      {
        "type": "scenario",            // scenario | mc | truefalse
        "prompt": "A caller says: 'My cousin Mike Davis has a rifle in pawn with you — is it still there?' What do you do?",
        "options": [
          {"text": "Check Bravo and confirm it's still in the safe", "correct": false, "why": "You just confirmed a firearm is on the premises to an unverified caller — a safety and § 54.1-4011 problem."},
          {"text": "Say you can't discuss any account without the account holder verifying, and offer to have Mike call", "correct": true, "why": "Verify before you disclose; never confirm a firearm by phone."},
          {"text": "Tell them it expired last week", "correct": false, "why": "That's a disclosure too."}
        ]
      }
    ]
  }
}
```

Rules for writers
- Every fact must trace to a listed source (P&P section, Handbook section, KB id, call id). No invented policy. If the manual is silent, say so in `sources` as `"OPEN: <what Preston must state>"` and keep the question out.
- Scenario questions beat recall questions. Wrong answers get a real `why`.
- 6–8 questions per lesson; at least 4 scenarios.
- Level intros (order 0, "N.0 Welcome to …"): 2–5 questions about what the intro itself says, `pass_percent: 0` (an ungraded preview, never a gate). Added 2026-10-14 after the program review.
- Every lesson has `objectives` (added 2026-10-14). Narration states the rule in the company voice ("Our rule is…"); it never attributes it ("Preston says…") and never dates it ("starting in October", "last week"). Names appear only where that person is the one to call or the approver. Example stories are anonymised ("one of our stores", "a coworker").
- Quiz options: the right answer is not the longest or the only one that quotes the lesson; put the reasoning in `why`, not in the option. Every wrong option's `why` names the rule it breaks.
- Goldilocks tie-in (added 2026-10-14): a lesson whose results a Goldilocks report grades may add one "What Goldilocks will show you" slide and one scenario question (marked `"goldilocks": true`), which can take the quiz to 9. Use only the report facts taught in lesson 1.7.
- Voice: Valley Pawn's — direct, warm, no corporate filler, no legalese in narration (cite the law in `sources`, not in the trainee's face, except firearms/records rules where the number matters).
- Firearms lessons: never a firearm image in any asset; procedure only.
- Narration `say` lines are read aloud by TTS: short sentences, contractions, no bullets.
