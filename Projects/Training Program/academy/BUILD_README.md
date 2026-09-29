# Valley Pawn Academy: building SCORM packages

`build_scorm.py` turns each lesson JSON (format: `LESSON_SPEC.md`) into a **SCORM 1.2** zip that TalentLMS can import and score. It uses only the Python standard library. It also needs `node` on the PATH for the JavaScript checks. If node is missing, the build still runs and the JS checks are skipped with a notice.

## Build

```bash
cd "Training Program/academy"
python3 build_scorm.py --all                          # every lessons/*/*.json (L1-L8 and M), then validate
python3 build_scorm.py lessons/L2/03_drawer_balancing.json   # one lesson (updates its entry in the index)
python3 build_scorm.py --all --skip-validate          # build only
python3 build_scorm.py --validate-only                # re-check the zips already in dist/
```

The exit code is 0 only when every package validates.

Output in `academy/dist/`:

| Path | What it is |
|---|---|
| `<id>_<slug>.zip` | The package you upload to TalentLMS (Add unit, then SCORM). Example: `L2-03_drawer_balancing.zip` |
| `preview/<id>/index.html` | The same package unzipped. Open it in a browser to preview (standalone mode, nothing is recorded) |
| `manifest_index.json` | One row per package: file, title, level, order, question count, pass %, whether it has a video, clip and Floor Check, plus any `media_notes` and `spec_warnings` |

The slug is the lesson filename without its `NN_` prefix.

## Add a lesson

1. Write `lessons/L<level>/<nn>_<slug>.json` to `LESSON_SPEC.md`. Extra top-level keys such as `production_notes` are allowed; they are ignored. `sources` and `production_notes` are never shipped to learners.
2. Run `python3 build_scorm.py lessons/L<level>/<nn>_<slug>.json`.
3. Read the `spec:` lines. They are warnings, not failures. Some examples:
   - a question with **no correct option** is dropped from the package;
   - a missing `why` shows no explanation for that option;
   - key points outside 3 to 6 items, fewer than 4 scenario questions, or a question count outside 6 to 8.
4. Open `dist/preview/<id>/index.html` and click through it.
5. Upload the zip to TalentLMS.

## How media is resolved

All media lives under `academy/media/`:

- **Video:** `"video": {"file": "joshua_welcome.mp4"}` resolves to `academy/media/joshua_welcome.mp4`. If the file exists, it is copied into the package as `media/<name>` and played with `<video>`. If it doesn't exist, the build falls back to the narrated slide deck and prints a `media:` note. It never fails.
- **Video URL:** `"video": {"url": "..."}` is used as given. YouTube and Vimeo links embed in an iframe; anything else plays in `<video>`. The learner needs internet access for these.
- **Call clip:** `"call_clip": {"file": "clips/X.m4a"}` resolves to `academy/media/clips/X.m4a`. A bare filename is also looked for in `media/clips/`. If the clip exists, the build transcodes it with ffmpeg to **MP3 (mono, 64 kbps, 44.1 kHz, metadata stripped)** and packages it under a neutral name, `media/<lessonId>_call.mp3` (the source filenames carry internal tags and never ship). TalentLMS's CDN would not stream the AAC `.m4a` originals (the player sat at 0:00). The player uses `<audio controls preload="metadata">` with `<source type="audio/mpeg">`. Clips longer than 3:00 show their length ("4 min call") under the caption. Transcodes are cached in the system temp folder, so rebuilds are fast. If the clip is missing or ffmpeg isn't installed, the Listen step is dropped (nothing is shown to the learner about it).
- A clip `caption` that starts with `TODO` is never shown to learners.
- A video file is packaged as `media/<lessonId>_video.<ext>`.

## Voiceover (ElevenLabs)

`voice.py` (standard library only) makes professional narration with ElevenLabs text-to-speech. The builder embeds it. For each lesson it narrates:

- the Start card intro: "Welcome to *title*. This takes about *N* minutes, and there's a short test at the end.";
- every slide's `say`, after the learner-text cleaner, so it matches what ships;
- the key points.

The result screen stays silent.

**Why it's embedded:** TalentLMS's SCORM frame will not load `<audio>`/`<video>` media (verified live 2026-09-28). The MP3s go into `index.html` as one `<script type="application/json" id="voice-b64">` map (`{"intro": b64, "0": b64, ..., "keypoints": b64}`). The player decodes them with Web Audio (`decodeAudioData` into an `AudioBufferSourceNode`) on the same shared `AudioContext` as the call player. Any line that has no recording yet falls back to browser speech (slides only).

### 1. Setup (once)

Create `academy/.elevenlabs.json`. It is listed in `academy/.gitignore`. Never share, commit or upload it, and never paste the key into chat or Slack.

```json
{"api_key": "sk_...", "voice_id": "<from step 2>", "model_id": "eleven_multilingual_v2"}
```

`voice.py` never prints the key. If `voice_id` is left out, ElevenLabs' example voice "George" (`JBFqnCBsd6RMkjVDRZzb`) is used.

### 2. Choose a voice

```bash
python3 voice.py voices                 # name, voice_id, category, labels (accent, gender, age, use case)
python3 voice.py voices --search narration
```

Put the `voice_id` you like in `.elevenlabs.json`.

### 3. The flow

```bash
python3 voice.py estimate                         # billable characters per lesson (uncached lines only) + total
python3 voice.py sample --text "Welcome to Valley Pawn." --out media/voice/sample.mp3   # listen before you commit
python3 voice.py generate --lesson L1-01          # one lesson, then check it in the preview
python3 voice.py generate --all                   # everything that isn't cached yet
python3 build_scorm.py --all                      # embeds the cached MP3s; the build prints "voiceover: 7/7 lines embedded"
```

Then re-upload the changed zips to TalentLMS (`REPLACE_RUNBOOK.md`).

### Cost control: the cache

Every line is cached in `academy/media/voice/<sha1>.mp3`. The hash covers the voice, the model, the voice settings, the output format and the exact text sent. Only new or changed text is ever billed:

- Rebuilding costs nothing.
- Editing one slide's `say` re-bills that one line.
- Changing the voice, the model or the settings re-bills everything. Run `estimate` first.
- `build_scorm.py` never calls ElevenLabs. It only embeds what is already cached.

Old cache files are never deleted automatically. They are harmless.

### Request and behaviour

The request format was checked against https://elevenlabs.io/docs/api-reference/text-to-speech/convert on 2026-09-28:

- **Endpoint:** `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_64`
- **Header:** `xi-api-key`
- **Body:** `{"text", "model_id", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": true}}`
- **Voices:** `GET /v2/voices`, paginated

How errors are handled:

- **429 and 5xx:** retried with exponential backoff, honouring `Retry-After`.
- **401, 402, 403 or any quota/credits error:** a hard stop with a clear message, and nothing more is sent.

64 kbps mono keeps packages sane: about 8 KB per second of speech, and the whole course is about 3 hours.

### Pronunciation

`PRONUNCIATION` at the top of `voice.py` rewrites text **for TTS only**, never for what learners read. It turns "P&P" into "P and P", "§" into "section", "4473" into "forty-four seventy-three", "A&D" into "A and D", "FFL" into "F F L", "TCPA" into "T C P A", "GLBA" into "G L B A", "dwt" into "pennyweight", "Va. Code" into "Virginia Code" and "e.g." into "for example". Dollar amounts, "Bravo" and "eBay" are left alone. Tune it freely: only the lines it changes are re-billed.

## What gets embedded, and the learner-text cleaner

`index.html` embeds only learner fields: id, title, level label, minutes, gate, slides (heading, bullets, `say`, icon), call clip caption and listen-for list, key points, Floor Check, the quiz, and the packaged media paths. `sources`, `production_notes` and build data never ship.

Every learner-visible string goes through `learner_text()` at build time (the lesson JSONs are not changed):

- Internal references are removed: Master Plan, KB ids, POLICY_GAPS / CONDUCT_REVIEW / FINDINGS / TRAINING_PROGRAM_PLAN and other internal docs, "OPEN" / "TODO" / "see sources" sentences, production notes, v1/v2 numbering, "library:" tags, queue numbers.
- Call numbers in running text become "a real call" ("This is Call 204." becomes "This happened on a real call.").
- P&P and Handbook section numbers, HR/OB memo numbers and laws (e.g. "P&P §05.05", "Va. Code § 54.1-4011") are **kept inside the `why` explanations** and dropped from citation parentheses everywhere else (gate, slides, key points, prompts, options).
- After the build, the validator greps every `index.html` for the forbidden patterns (`FORBIDDEN_PATTERNS` in the builder) and fails the package on any hit.

Each slide gets a large line icon picked by keyword from its heading, then its bullets (`ICON_RULES`; no firearm imagery by design). The icons are an inline SVG sprite in brand colours.
- To publish media, drop the file in place and rebuild that lesson.
- Big videos make big zips. Check TalentLMS's upload limit before adding long mp4s.

The logo is `academy/assets/tlms_logo.png`, copied into every package as `logo.png`. The packages load nothing from a CDN or the internet; all CSS and JS is inline.

## What the learner sees

The layout is responsive: the card uses the available width up to about 960 px, the page scrolls when content is taller than the frame (TalentLMS's desktop frame is 980×660), and the Back / Next / Continue bar is sticky at the bottom so the main button is always on screen. It works down to a 375 px phone. Keyboard: ← and → move, Enter continues, 1–4 or A–D answer a test question.

Before the test, a progress bar tracks these steps, and Back works on all of them:

1. **Start.** Title, minutes, question count, pass mark, and the `gate` deadline, with a **Voiceover: On/Off** toggle. With recorded voiceover, the intro line plays once the learner has interacted with the page (browsers block sound before that); a tap on "Start lesson" goes straight to slide 1.
2. **Learn** (or **Watch** for a video). The slides one at a time, each with its icon, a progress-dots row and a slide-in transition. **Voiceover** is **on by default** and starts on the first slide after the single "Start lesson" click (which satisfies browser autoplay rules). When the lesson has recorded ElevenLabs narration (see "Voiceover" below) that is what plays, with an animated "Speaking" indicator; when it ends, the Next button pulses gently. A slide with no recording falls back to the browser's speechSynthesis reading its `say` text (best English voice available: Samantha, Google US English, Microsoft Aria / Jenny / Guy, else the first en-US voice). Narration stops when the learner leaves the screen or plays the call, and an off choice is remembered on that device.
3. **Listen.** The call clip, its caption (plus its length if over 3 minutes), and a "listen for" checklist. Every box must be ticked before Continue. This step only appears when the clip exists. If the audio fails to load, a "try again" note appears.
4. **Key points.** Check-mark cards that animate in. With recorded voiceover, the key points are read too (with the toggle and indicator on this card).
5. **Floor Check.** "Your manager will verify this on the floor: ..." This step only appears if `floor_check` is set.
6. **Test.**
   - One question at a time, with "Question 3 of 8", a running score, and a coloured bar per question. If `shuffle` is true, the questions and options are shuffled; true/false keeps True before False.
   - Big lettered option buttons. After each answer the learner immediately sees green or red, a short encouraging line on a correct answer, the `why` for the option they picked, and, if they were wrong, the right answer with its `why`.
7. **Result.**
   - A pass is a score of `pass_percent` or better. It shows an animated score ring, "Lesson complete", "You earned points toward the leaderboard" (TalentLMS awards the points; no number is shown) and a confetti celebration.
   - A fail lists every missed question with explanations and offers **Retake**, which reshuffles.
   - Once attempts reach `max_attempts`, the result also says "Ask your manager to go through this lesson with you". Retake stays available.

## SCORM 1.2 behavior

- **Manifest:**
  - `imsmanifest.xml` sits at the zip root with `schema` set to `ADL SCORM` and `schemaversion` set to `1.2`.
  - It has one organization, one item and one resource (`type="webcontent"`, `adlcp:scormtype="sco"`, `href="index.html"`), with every file listed.
  - `adlcp:masteryscore` is set to `pass_percent`.
- **Finding the API:** the player looks for `window.API` up the parent frames (10 levels max), then in `opener` and `top.opener`.
- **Start:**
  - `LMSInitialize`.
  - `cmi.core.lesson_status` is set to `incomplete`, unless it's already `passed` or `completed`.
  - `cmi.core.exit` is set to `suspend`, then `LMSCommit`.
- **Test finished:**
  - `cmi.core.score.min` is set to 0, `score.max` to 100, and `score.raw` to the 0-100 score.
  - `cmi.core.lesson_status` is set to `passed` or `failed`.
  - `cmi.suspend_data` stores `{"a":attempts,"b":best,"p":everPassed}`.
  - Then `LMSCommit`.
  - Attempts carry across sessions through `suspend_data`.
  - **A learner who has already passed is never downgraded.** If they retake and score lower, the status stays `passed` and the raw score reported is their best.
- **Leaving** (`pagehide`, `beforeunload` or `unload`): `cmi.core.session_time` is set, then `LMSCommit` and `LMSFinish`, once only.
- **No LMS** (preview or file open): every call is only logged to the console as `[VPA] ...`. Nothing throws.

## Validation (runs after every build)

For each zip, the build checks the following:

- It parses `imsmanifest.xml` with an XML parser and checks the schema and version, the default organization, the item to resource link, `scormtype=sco` and `webcontent`.
- Every `<file>` in the manifest and every local `src` or `href` in `index.html` exists in the zip, as do the video and clip paths. No remote `src` or `href` is allowed.
- The player script is extracted and run through `node --check`.
- A node test loads the real player script with a fake SCORM API and the lesson's quiz data, then simulates:
  - all answers correct, which must give `passed`, raw 100, min 0, max 100, attempts 1 in `suspend_data`, and a commit and finish;
  - all answers wrong, which must give `failed` and raw 0;
  - attempts adding up from an earlier `suspend_data`;
  - shuffling that keeps each correct answer;
  - standalone mode with no API.
- When a call clip is present: it is `media/<lessonId>_call.mp3`, the file really is MPEG audio, and the player declares it as `audio/mpeg`. No `.m4a`/`.aac` ships, and every file under `media/` has a neutral name.
- The `voice-b64` block (when present) parses as JSON, its keys are `intro`, `keypoints` or a slide index that exists, and every entry is valid base64 that decodes to MP3 bytes (an ID3 tag or an MPEG frame sync).
- `index.html` has zero hits for the forbidden learner-text patterns (the `clip-b64` and `voice-b64` audio blocks are skipped) (Master Plan, KB and KB ids, POLICY_GAPS, OPEN, TODO, production, call numbers, v1/v2 numbering, internal doc names), no "coming soon", no `sources`, `production_notes` or build data, and only the learner fields listed above.

## Render check (optional, needs Playwright)

```bash
pip install playwright && python3 -m playwright install chromium
python3 render_check.py                 # L1-05, L3-06, L6-03 at 980x660 and 375x740
python3 render_check.py L1-05 --shots   # also saves PNGs to dist/screenshots/
```

It serves `dist/` on 127.0.0.1, loads each preview inside a host page that plays TalentLMS (an iframe of that size with a fake SCORM API), clicks through every screen and the whole test, and checks that the main button is on screen without scrolling on every screen, that html/body never clip, that there is no sideways scroll, and that the fake LMS got `passed` / 100. Results go to `dist/render_check.json`. If Playwright isn't installed it prints a skip notice.
