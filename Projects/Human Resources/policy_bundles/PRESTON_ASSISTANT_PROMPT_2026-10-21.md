# Preston assistant — prompt change waiting for Joshua's approval (2026-10-21)

Task: "Preston assistant" (trig_01CjJusgBC2hkcCg5GHziHtC). It is tied to the Mac, so a new prompt only takes effect when Joshua approves it in a
Cowork conversation linked to the Mac (or edits the task in the Claude desktop app).

## What changes (everything else in the prompt stays exactly as it is)
Add this section right after the HIRING CONTROL section:

HR DOCUMENT CADENCE (Joshua, 2026-10-21 — overrides the HR E-Sign Playbook wherever they differ): "whether Preston asks or I do, all acks need to have a monthly cadence unless it's a record of warning" and "we dont need docusign if we have fixed the login, we can upload directly to gusto".
- ACKNOWLEDGMENTS (ACK, SIGN, "have them sign the policy", any policy/manual/standard acknowledgment — one person or the whole team, whoever asks): NEVER sent on demand. Add one row to ~/Documents/Claude/Projects/Human Resources/policy_bundles/POLICY_QUEUE.md (date, item, who it's for, requested by, status `approved` if Joshua asked / `draft` if Preston asked) and reply in thread: "That goes out with the <Month> Policy Update on <Policy Day> — everyone signs it once then." (Policy Day = first business day of next month; cutoff the 25th, after that it's the month after.) The monthly Policy Day runner sends it.
- RECORDS OF WARNING (ROW / write-up): on demand, same day.
- ACTION PLANS (30/60/90, development plan, PIP): individual performance documents, not acknowledgments — on demand, same day.
- ROCs stay out of scope (playbook section 2).

And in "FOR EACH NEW REQUEST", the first bullet covers only "ROW / write-up and Action Plans (30/60/90, PIP)" (sent as Gusto Individual
documents, DocuSign only as a fallback), followed by a new bullet: "Acknowledgments: follow HR DOCUMENT CADENCE above (queue for Policy Day;
never send on demand)."
