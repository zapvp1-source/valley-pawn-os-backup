---
name: bald-rock-signing-status
description: Daily DocuSign signing status check for Bald Rock guests → posts to Slack
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are checking the DocuSign signing status for all upcoming guests at 282 Bald Rock Road (Mountain Luxury), Verona, VA 24482, and posting a summary to Slack.

## Property Info
- Guesty Listing ID: 68b59902faaa330013ede1f8
- DocuSign Account ID: 320a0ff8-3001-4e1a-93b4-4fc3004b1116
- Airbnb Template ID: cf0bdcb8-4476-4d69-a88c-ba6b605a6034
- VRBO Template ID: c264e23c-5ff7-47eb-b676-fc469048f331

## Steps

1. **Get DocuSign envelope status**: Use the DocuSign MCP tool `getEnvelopes` to list all envelopes for account `320a0ff8-3001-4e1a-93b4-4fc3004b1116`. Filter for envelopes from the last 90 days related to Bald Rock (look for emailSubject containing "Bald Rock" or "282 Bald Rock"). Check each envelope's status (sent, delivered, completed, declined, voided).

2. **Get upcoming Guesty reservations**: Use the Chrome MCP or Slack/Guesty tools to check reservations at listing `68b59902faaa330013ede1f8` that are confirmed and check-in is within the next 60 days. If you can access Guesty, navigate to app.guesty.com and use the Okta token from localStorage to call:
   `/api/reservations-reports?smartView=true&columns=checkIn+checkOut+confirmationCode+guest+source&filters={"status":{"@in":["confirmed"]},"listingId":{"@in":["68b59902faaa330013ede1f8"]}}&sort=checkIn&limit=20`

3. **Match envelopes to guests**: For each upcoming guest, determine if they have a DocuSign envelope and whether it is:
   - ✅ Signed (status: "completed")
   - ⏳ Awaiting signature (status: "sent" or "delivered")  
   - ❌ No envelope sent yet
   - ⚠️ Declined or voided

4. **Post to Slack**: Find the Slack channel related to Bald Rock / Airbnb / rental property (search for channels named "airbnb", "bald-rock", "rental", or "property"). Post a message formatted like:

```
🏡 *Bald Rock — Contract Signing Status* (as of [today's date])

✅ *Signed:*
• [Guest Name] — Check-in [date]

⏳ *Awaiting Signature:*
• [Guest Name] — Check-in [date] (sent [X] days ago)

❌ *No Contract Sent:*
• [Guest Name] — Check-in [date]

_Reply to this message or tag @Joshua to take action on pending items._
```

5. If no Bald Rock / rental channel exists, post to the most relevant general channel or DM Joshua Davis (zapvp1@me.com).

## Notes
- If DocuSign MCP is unavailable, note it in the Slack message and ask Joshua to check manually.
- Only include confirmed reservations with check-in dates in the future.
- Skip reservations where check-in is more than 60 days away (too early to worry).
- Always run at 9 AM daily.