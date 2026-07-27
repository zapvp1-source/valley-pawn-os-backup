---
name: annual-board-review
description: Create Valley Pawn's annual board review presentation for the prior year and upload it to Google Drive
model: claude-opus-4-8
---


> ⚠️ **FAILURE POLICY — DO NOT POST TO SLACK ON FAILURE.** If this task fails, errors out, or cannot complete its intended work for any reason, DO NOT post anything to Slack — no error messages, no partial results, no "I couldn't finish" notices. Joshua reviews every run inside Claude to confirm success or failure, so a failed run must stay completely silent on Slack. Only post to Slack once the task has genuinely completed the work it was designed to do. Posting failure or error noise clutters Slack and reflects poorly on the team.

Create the Annual Board Review presentation for Full Circle Finance Inc DBA Valley Pawn for the PRIOR calendar year (e.g., if today is January 1, 2027, create the 2026 Annual Board Review).

## Objective
Build a polished, data-rich PowerPoint presentation (.pptx) summarizing Valley Pawn's annual performance across all 5 stores, then upload it to Google Drive at: Annual Board Reviews / {YEAR} / Valley_Pawn_{YEAR}_Board_Review.pptx

## Data Sources to Pull

### 1. Google Drive — Search for the prior year's data
Use the Google Drive MCP (search_files, read_file_content) to find and read:
- Annual Report PDFs (search: title contains 'Annual Report {YEAR}')
- SWOT Review PDFs (search: title contains 'SWOT' and '{YEAR}')
- Financial trend folders (search: title contains '{YEAR}' and mimeType = folder)
- Any existing meeting presentations from that year (search: title contains '{YEAR}' and mimeType contains 'presentation')
- Tax return documents (search: title contains '{YEAR}' and title contains 'Tax')
- Monthly business minutes/reports from that year

### 2. Slack — Pull business changes & policy updates
Use the Slack MCP to search for key business developments from the prior year:
- Search in #policy channel for policy changes and updates
- Search messages from Preston and Joshua (jdavis@fcfpawn.com) for strategic announcements
- Search for mentions of: new stores, closures, rebrand, rate changes, new services, compliance changes, staffing changes
- Time range: January 1 through December 31 of the prior year

### 3. QuickBooks Online — Financial summary
Use the QBO MCP or web UI (if available) to pull:
- Annual revenue, gross profit, net income
- Year-over-year comparison
- Major expense categories

### 4. Reference the 2025 Board Review as a template
The 2025 deck is in Google Drive: Annual Board Reviews / 2025 / Valley_Pawn_2025_Board_Review.pptx (Drive file ID: 1ej8GDvUdNipT_rwEXw8qkl34SvqQkBMJ). Download and read it to match the slide structure and design language.

## Presentation Structure (12-15 slides)
1. **Title slide** — "Valley Pawn {YEAR} Annual Board Review", Full Circle Finance Inc, date
2. **Year in Review** — Executive summary, key wins, major challenges
3. **Company Overview** — All 5 store locations, any changes (openings, closures, moves)
4. **Financial Highlights** — Revenue, gross profit, net income vs prior year (use chart)
5. **Loan Portfolio** — Total loans, average loan value, redemption rates by store
6. **Sales Performance** — Retail sales by store, top categories, YoY comparison
7. **Store Rankings** — Performance ranking table for all 5 locations
8. **Inventory** — Aged inventory stats, turns, categories
9. **Operations** — Staffing headcount, turnover, any operational changes
10. **Policy & Compliance Changes** — Any regulatory, policy, or process changes made during the year (from Slack)
11. **SWOT Analysis** — Strengths, Weaknesses, Opportunities, Threats for the year
12. **Goals Review** — Prior year goals: what was achieved vs missed
13. **Goals for Coming Year** — Strategic objectives for the new year
14. **Closing slide** — Contact, date, company branding

## Design
- Match the 2025 deck's color scheme: dark navy/black backgrounds with gold/yellow accents
- Use Valley Pawn branding
- Keep text concise — bullet points and data, not paragraphs
- Include charts/graphs where financial data is available

## File Creation
- Use the pptx skill (read /sessions/*/mnt/.claude/skills/pptx/SKILL.md for instructions)
- Save the final .pptx to the working directory
- Upload to Google Drive using the local sync folder method:
  - First create the year folder if it doesn't exist: ~/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/Corporate Governance/Annual Board Reviews/{YEAR}/
  - Copy the file there: cp "Valley_Pawn_{YEAR}_Board_Review.pptx" "~/Library/CloudStorage/GoogleDrive-jdavis@fcfpawn.com/My Drive/Corporate Governance/Annual Board Reviews/{YEAR}/"
  - Verify the file appears in Google Drive by checking the Drive MCP

## Success Criteria
- Presentation saved to Google Drive in the correct year folder
- All 5 stores represented
- Financial data included (even if estimated or from prior reports)
- At least 12 slides
- Slack-sourced policy/business changes included on the compliance/changes slide

## Notes
- Google Drive account: jdavis@fcfpawn.com (Workspace/Drive — NOT fullcirclepawn@gmail.com which is only for Google My Business)
- Valley Pawn has 5 stores: Waynesboro, Staunton, Lexington, Culpeper, and Roanoke
- Company: Full Circle Finance Inc DBA Valley Pawn
- If specific financial data is unavailable for the year, note it as "data unavailable" and use the best available estimates from surrounding years

<!-- migrated to working model 2026-06-15 -->