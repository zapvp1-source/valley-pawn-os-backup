---
name: bald-rock-auto-contract
description: Auto-send DocuSign contracts to Bald Rock guests 15 days before check-in
---

> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

You are automatically sending DocuSign rental contracts to upcoming guests at 282 Bald Rock Road (Mountain Luxury), Verona, VA 24482. Run this task every morning to catch any guests whose check-in is exactly 15 days away (or between 14-16 days to avoid missing a day).

## Property Info
- Guesty Listing ID: 68b59902faaa330013ede1f8
- DocuSign Account ID: 320a0ff8-3001-4e1a-93b4-4fc3004b1116
- Airbnb Template ID: cf0bdcb8-4476-4d69-a88c-ba6b605a6034
- VRBO Template ID: c264e23c-5ff7-47eb-b676-fc469048f331
- Owner email: zapvp1@me.com

## Steps

### 1. Get Today's Date
Note today's date. Identify the target window: guests with check-in between 14 and 16 days from today.

### 2. Fetch Upcoming Reservations from Guesty
Navigate to app.guesty.com in Chrome and use the Guesty API. Get the Okta Bearer token from localStorage:
```javascript
const storage = JSON.parse(localStorage.getItem('okta-token-storage') || '{}');
const token = storage.accessToken?.accessToken;
```

Then fetch reservations:
```
GET /api/reservations-reports?smartView=true&columns=checkIn+checkOut+confirmationCode+guest+guest.email+source&filters={"status":{"@in":["confirmed"]},"listingId":{"@in":["68b59902faaa330013ede1f8"]}}&sort=checkIn&limit=50
```

Filter for reservations where checkIn is 14-16 days from today.

### 3. Check if Contract Already Sent
For each reservation in the window, use the DocuSign MCP `getEnvelopes` tool to check if an envelope already exists for that guest. Search by guest name in the envelope list. Skip guests who already have an envelope (any status).

### 4. Send Contracts

**For VRBO guests** (source contains "vrbo" or "VRB-" in confirmation code):
- If `guest.email` is available, use DocuSign MCP `createEnvelope` with:
  - templateId: c264e23c-5ff7-47eb-b676-fc469048f331 (VRBO template)
  - recipient email: the guest's actual email
  - emailSubject: "Rental Agreement – 282 Bald Rock Road (Check-in [date])"

**For Airbnb guests** (source contains "airbnb"):
- Check if the guest has shared their email in the Guesty inbox conversation
- If email found: send DocuSign via `createEnvelope` with the Airbnb template
- If no email: send a Guesty inbox message asking for their email:
  "Hi [Name]! We're looking forward to welcoming you to Bald Rock on [check-in date]! Before your arrival, we need you to sign a short rental agreement. Could you please share your email address so we can send it to you via DocuSign? Thank you!"
  
  To send a Guesty message, navigate to the inbox conversation URL: https://app.guesty.com/inbox-v2/[conversationId]/reservation?view=0
  Then click the message box and type/send the message.

### 5. Post Slack Summary
After processing all guests, post a summary to the Bald Rock / Airbnb Slack channel:

```
🏡 *Bald Rock — Daily Contract Check* ([date])

📤 *Contracts sent today:*
• [Guest Name] ([channel]) — Check-in [date]

💬 *Email requests sent (Airbnb guests):*
• [Guest Name] — Check-in [date]

⏭️ *Skipped (already had envelope):*
• [Guest Name] — Check-in [date]

ℹ️ No guests in the 14-16 day window today.
```

## Notes
- Only process confirmed reservations
- Never send a second contract if one already exists
- The 14-16 day window (instead of exactly 15) prevents missing guests if the task is delayed by a day
- If DocuSign MCP is unavailable, use the Chrome browser approach: navigate to apps.docusign.com, get JWT token from /api/send/__settings, and POST to https://apps.docusign.com/api/esign/na1/restapi/v2.1/accounts/320a0ff8-3001-4e1a-93b4-4fc3004b1116/envelopes with Authorization: Bearer [token]
