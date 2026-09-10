# Phase 0 — the one thing only Joshua can do (~3 minutes, once, forever)

> ✅ **DONE 2026-09-09.** Grant complete (3 scopes on the cached token), both APIs enabled on project 284722922565, and `jdavis@fcfpawn.com` added as **Viewer** on GA4 property 353209303 (the property owner is `fullcirclepawn@gmail.com`; without this the Data API returns 403 PERMISSION_DENIED even with the right scopes). `ga4_pull.py --check` and `gsc_pull.py --check` both return OK. Everything below is kept for the record / re-run instructions.

**What it unlocks:** every website number stops being screen-scraped out of the GA4 web UI by a
browser four times a week, and Search Console data (organic = ~70% of the site's traffic) becomes
available for the first time. After this, the weekly #website post can show **calls, texts and
directions clicks by store** instead of only "key events: 15".

**Not a service account.** `Scheduled/_shared/sheets_helper.py` records that the fcfpawn.com
Workspace org blocks service-account key downloads (`iam.disableServiceAccountKeyCreation`). The
existing, already-working pattern is a cached OAuth refresh token authorized as Joshua — this just
re-runs that consent with two extra **read-only** scopes added. Nothing that works today breaks:
the new grant is a superset of the current one, so `email-analytics-weekly` and everything else
using `sheets_helper.py` keeps working untouched.

---

## Step 1 — enable two APIs (2 minutes)

Go to <https://console.cloud.google.com/apis/library> and make sure the project selector at the top
says **valley-pawn-automation**. Then search for and click **Enable** on each:

1. **Google Analytics Data API**
2. **Google Search Console API**

Direct links (they respect the selected project):
- <https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com>
- <https://console.cloud.google.com/apis/library/searchconsole.googleapis.com>

## Step 2 — approve the grant (1 minute)

In Terminal, paste this one line:

```
python3 "/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin/google_grant.py"
```

A browser window opens. **Sign in as `jdavis@fcfpawn.com`** and click **Allow**. The window says
"you can close this tab" when it's done, and the script prints the scopes it now holds.

## Step 3 — confirm (10 seconds)

```
cd "/Users/joshuadavis/Documents/Claude/Projects/Website/analytics/bin"
python3 ga4_pull.py --check && python3 gsc_pull.py --check
```

Expected: two `OK —` lines with real session/click counts. If `ga4_pull.py --check` prints
`Lead events seen: NONE`, that is a separate, useful finding — it means the contact-bar click
events stopped firing on the live site, and the weekly health audit should be pointed at it.

---

### What is being requested, precisely

| Scope | Why | Can it change anything? |
|---|---|---|
| `analytics.readonly` | Read GA4 property 353209303 (sessions, channels, pages, lead events by store) | No — read only |
| `webmasters.readonly` | Read Search Console for thevalleypawn.com (clicks, impressions, positions, coverage issues) | No — read only |
| `spreadsheets` | Already granted; carried forward so existing Sheets jobs keep working | Unchanged from today |

### If something goes wrong

- **"access_denied" / wrong account** — sign out of other Google accounts first, or use a fresh
  browser profile, then re-run. The account must be the one that owns GA4 + Search Console
  (`jdavis@fcfpawn.com`; `fullcirclepawn@gmail.com` is the GA4 owner on some days — if `--check`
  reports no property access, re-run and approve with that account instead).
- **"API not enabled"** — Step 1 didn't take on the right project; re-check the project selector.
- **Rollback** — the previous token is saved as
  `~/.config/valley-pawn/google-oauth-token.json.bak-pre-analytics-grant`; restoring that file
  puts everything back exactly as it was.

### Until this is done

Every script degrades cleanly instead of failing: `ga4_pull.py` and `gsc_pull.py` exit 1 with this
file's name in the message, and `weekly-analytics-summary` falls back to the Chrome scrape it has
always used. Nothing breaks by waiting — it just stays slower, browser-dependent, and blind to
leads and search.
