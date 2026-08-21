# bald-rock-15-day-contract — run 2026-08-21 — FAILED at Step 2 (Guesty login)

## Outcome
Could not complete. Blocked at Step 2 (pull candidate reservations from Guesty) — never reached
DocuSign classification, SEND, REMIND, or VERIFY phases. Per the task's hard constraint ("If
Guesty login fails, DM Joshua immediately and stop — never send partial contracts under
uncertainty"), the run stopped here. Zero contracts, reminders, or age-verification requests were
sent this run.

## What was done before the blocker
- Loaded `enterprise-map` (Domain 2 — Real Estate) and `bald-rock-property` skill per protocol.
- Reviewed `Life OS/REAL_ESTATE_OS.md` and `Life OS/OPEN_ITEMS_REGISTER.md` — no new blockers
  found there relevant to this run (existing open items: DocuSign corrected-PDF template upload
  still pending Joshua's one-time Touch ID login; age-verification manual-ask step already
  standing per 2026-08-07 decision, consistent with this task's Step 6).
- Window computed: 2026-08-21 → 2026-09-05 inclusive.

## The actual failure — Guesty login via Google SSO hangs indefinitely
Attempted `https://app.guesty.com/reservations` login via "Sign in with Google" → account chooser
→ `jdavis@fcfpawn.com` (Google Workspace SSO, matches `bald-rock-property` skill's documented
login method) **three separate full attempts**, each with the same failure mode:

1. Click "Sign in with Google" on `app.guesty.com/auth/login` → reaches Google's account chooser
   (`accounts.google.com/v3/signin/accountchooser`) showing "Joshua Davis — jdavis@fcfpawn.com".
2. Click that account → Google issues an OAuth authorization code, redirects to
   `login.guesty.com/oauth2/v1/authorize/callback?...code=...`.
3. Guesty's login page (Okta-hosted, `login.guesty.com`) shows **"Verifying your credentials..."**
   with an animating ellipsis that cycles indefinitely — confirmed still cycling after 60+
   seconds of continuous waiting, never resolves to either success or an error message.
4. Navigating directly to `app.guesty.com/reservations` afterward always lands back on
   `app.guesty.com/auth/login` — confirming no session was ever established, not just a slow
   redirect.

This was reproduced identically on 3 separate attempts (fresh account-chooser click each time,
fresh OAuth code each time). Not a one-off network blip — looks like a genuine hang on Guesty/
Okta's side of the credential-verification step, or a device/fingerprint trust check that never
completes in this sandboxed browser environment.

## What this means for candidate data
**None pulled.** Never reached the Guesty reservations list, so there is no candidate roster for
this run — no SEND/REMIND/VERIFY classification was possible for any guest with a check-in
2026-08-21 through 2026-09-05.

## Recommended next steps for the next session (or Joshua)
1. Try the login again fresh — this could be transient (Okta risk-based auth having an off day).
2. If it hangs again 2-3 times in a row, treat as a real outage: check Guesty's status page, and
   check whether `jdavis@fcfpawn.com`'s Google Workspace session/2FA state changed recently
   (a forced re-auth or device-trust reset on Google's side could be the actual trigger, given the
   hang happens right after Google hands back the OAuth code, before Guesty's own session forms).
3. If Joshua is available, ask him to try the same login manually once — if it also hangs for him
   this is confirmed a Guesty/Okta-side issue, not a browser-automation-detection issue.
4. Once login is confirmed working, immediately re-run this task from Step 1 — nothing was sent
   this run, so there is no de-dup risk in re-running clean.

## Companion note
Unrelated to this failure, but flagged for whoever picks this up next: the Open Items Register
still shows the 2026-08-07 row "Bald Rock DocuSign contract bug fix — corrected PDFs staged but
NOT yet uploaded to live DocuSign templates, needs Joshua's one-time Touch ID login." Worth
checking whether that's since been resolved, since it would affect what actually gets sent once
Guesty access is restored.
