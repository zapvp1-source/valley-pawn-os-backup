# Human Queue — the only list Joshua has to look at

Everything here is something Claude has verified it cannot do (MFA, device trust, a password only he knows, an OAuth consent, a legal signature). One row per item, deduped — a task that hits the same wall again does NOT add a row, it bumps `Last hit`. `fleet-guardian` surfaces this list in its single daily DM only when a row is new or older than 7 days. Anything a session can do itself must never land here.

| Added | Item (what to do, where, ~minutes) | Unblocks | Last hit | Status |
|---|---|---|---|---|
| 2026-09-08 | **Gusto — trust this browser once.** On the Mac Studio, Chrome → app.gusto.com → sign in with Google → enter the texted code → tick **Remember this device / Don't ask again**. ~3 min. | gusto-keep-alive, daily-clockin-check, weekly-timekeeping-analysis, vp-gusto-signature-chase, Logan Dean dismissal form | 2026-09-08 (hit again 18:56 + 21:30) | OPEN — surfaced 9/8 |
| 2026-09-08 | **WordPress.com connector — reconnect.** claude.ai → Settings → Connectors → WordPress.com → reconnect (OAuth consent). ~2 min. | vp-website-shop-weekly-report (failing every Monday since 8/25) | 2026-09-07 | OPEN |
| 2026-09-08 | **VSP eReceivables — sign in once and let Chrome save the password.** Portal rejected the saved password 9/6; it locks after 5 tries so Claude will not retry. ~3 min. | Monthly VSP/NICS fee balance check (none verified since 6/23) | 2026-09-06 | OPEN |
| 2026-09-08 | **Google Analytics/Search Console consent.** Run `Website/analytics/GOOGLE_API_SETUP.md` click-path once (re-consent the existing OAuth client with analytics + webmasters read scopes). ~3 min. | weekly-analytics-summary API path, GSC keyword tracking | 2026-09-05 | OPEN |
