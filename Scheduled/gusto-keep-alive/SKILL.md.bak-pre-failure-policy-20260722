---
name: gusto-keep-alive
description: Keep the Gusto session alive by pinging every 30 minutes.
---

This is an automated Gusto session keep-alive task. Your goal is to ensure the Gusto session stays active indefinitely so that other scheduled tasks (like daily clock-in checks and weekly timekeeping analysis) can run without user involvement.

Steps:
1. Run a quick system check — echo a timestamp to confirm the session is responsive.
2. Open Chrome and navigate to https://app.gusto.com using Claude in Chrome tools.
3. Wait for the page to load, then read the page to determine the current state:
   - If you land on the Gusto dashboard (e.g., URL contains "payroll_admin" or page shows "Home | Valley Pawn"), the session is alive. Log a confirmation and you're done.
   - If you land on a login/sign-in page (URL contains "login.gusto.com" or page shows "Sign In"), the session has expired. Proceed to step 4.
4. Re-authenticate via Google SSO:
   a. Click "Sign in with Google" on the Gusto login page.
   b. Wait for the Google account chooser to load.
   c. Select the jdavis@fcfpawn.com account.
   d. If a consent/continue screen appears, click "Continue".
   e. Wait for redirect back to Gusto dashboard.
   f. Confirm you're now on the Gusto dashboard.
5. Log a short confirmation message with the current date/time and session status.

Important notes:
- This task runs autonomously every 2 hours. Do NOT ask for user input.
- If Google SSO fails or requires a password, log the error clearly so it can be investigated later.
- Do not take any write actions in Gusto — this is purely a session keep-alive.
- Success criteria: The Gusto dashboard is accessible at the end of the task.