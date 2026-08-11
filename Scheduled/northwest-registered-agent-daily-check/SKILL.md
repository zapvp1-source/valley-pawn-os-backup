---
name: northwest-registered-agent-daily-check
description: Daily check of Northwest Registered Agent portal for new notices; downloads and files them to Google Drive, posts summary + links to #registered-agent Slack channel
model: claude-sonnet-5
---

You are checking Northwest Registered Agent (the registered agent service for Joshua's business entities — Full Circle Finance Inc DBA Valley Pawn, Farming Infinity LLC, Farming Infinity Mountains LLC, Farming Infinity Virginia LLC, and any other entities on the account) for new notices, downloading them, filing them in Google Drive, and reporting to Slack. This is a fully autonomous daily task — do not ask Joshua for anything, do not wait for approval, just do it and report the result.

STEP 1 — Log in and check for new documents
- Load Chrome MCP tools first via ToolSearch: query "select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__read_network_requests,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__find"
- Navigate to https://www.northwestregisteredagent.com/login (it will auto-redirect through SSO to https://accounts.northwestregisteredagent.com/#/dashpanel using the saved Chrome session/credentials — do NOT ask Joshua to log in, do NOT type credentials, the session persists). If it ever demands manual 2FA or credentials you don't have, stop and send Joshua a single plain-language Slack DM (channel ID D03BHQH5VGT) explaining the portal needs his attention — do not post this failure to any team channel.
- Go to Documents (https://accounts.northwestregisteredagent.com/#/documents). Clear any "Unread" filter (click Filters > Clear Filters) so you see the FULL document list, not just unread — Northwest sometimes marks documents Read without them having been filed yet. Compare against what's already filed in the Drive "Registered Agent" folder (Step 3) to determine what's actually new.

STEP 2 — Download any document not yet filed
- For each document in the portal not already present (by filename) in the Drive "Registered Agent" folder: open its detail page, click Download, and capture the resulting presigned S3 URL via read_network_requests (urlPattern "amazonaws"). Then use the workspace bash tool to curl each URL into a local folder (e.g. an "outputs/Northwest Registered Agent - <date>" folder) so the file lands in this session's shared outputs directory.
- Some documents (rare) come back as an image (e.g. PNG) rather than PDF — that's fine, keep the original format, just file it with a matching filename.

STEP 3 — File into Google Drive
- The permanent home for these documents is the Google Drive folder "Registered Agent" (folder ID: 1WAYRYy2OXJXaVBYagpTrBys4ZYExUVn0 — this is a Drive-for-Desktop synced folder under Computers > My Mac > Desktop > Registered Agent, so anything filed here also lands on Joshua's Desktop automatically).
- First check what's already in that folder (Google Drive search_files tool, query: parentId = '1WAYRYy2OXJXaVBYagpTrBys4ZYExUVn0') to avoid re-filing duplicates.
- To upload new files: in the same Chrome tab, navigate to https://drive.google.com/drive/folders/1WAYRYy2OXJXaVBYagpTrBys4ZYExUVn0, click "New" then the "File upload" menu item, then use the `find` tool to locate the resulting file input element (query like "input type=file element for file upload"), then call `file_upload` with that element's ref and the absolute path(s) to the downloaded file(s) in this session's outputs folder (NOT the sandbox /sessions/... path — use the real macOS path form, e.g. under ".../local_.../outputs/..."). Do NOT try to pass file content inline via the Drive API's create_file tool with base64 — that is far too token-expensive for these files; the browser file_upload approach is the only efficient path. Wait a few seconds and confirm via screenshot that the upload(s) completed ("N uploads complete").
- After uploading, search_files again to grab the shareable viewUrl for each newly filed document — you'll need these for the Slack post.

STEP 4 — Summarize and post to Slack
- Use the Slack MCP tool (slack_send_message) to post to channel C0BMN275FD4 (#registered-agent).
- If there ARE new documents: state what's new (entity, document type, date received), whether anything looks time-sensitive (state annual report/franchise tax due notice, compliance deficiency, or — most importantly — service of process/lawsuit), then link the Drive "Registered Agent" folder and each newly filed document's Drive viewUrl. Flag anything urgent at the top of the message.
- If there is nothing new since the last check: a single brief line, e.g. "Northwest Registered Agent checked {date} — no new notices, portal and Drive folder are in sync."
- Keep the post concise — this is a daily status ping, not a report. Write in plain sentences, not bullet lists.

STEP 5 — Escalation
- If you find a service-of-process/lawsuit notice, or anything with a deadline inside the next 5 days, ALSO send Joshua a direct Slack DM (channel ID D03BHQH5VGT) flagging it specifically — time-sensitive legal/compliance items should not rely on him seeing the channel post.

Do not modify or delete anything in the Northwest Registered Agent portal itself — read-only there. Only add files to Drive, never delete or overwrite existing ones. Do not send failure notices to any team channel or store manager — only to Joshua's DM (D03BHQH5VGT), and only for the failure/2FA case described above.