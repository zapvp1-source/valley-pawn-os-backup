p = '/Users/joshuadavis/Documents/Claude/Scheduled/asset-recovery-daily-refresh/SKILL.md'
s = open(p).read()

block = """

## MANDATORY CLEANUP — leave Bravo usable for the tasks behind you (added 2026-08-12)

You run at 7:17 PM. Behind you tonight: jewelry-onhand-nightly-pull (8:30 PM),
jewelry-onhand-nightly-compare (9:45 PM), and jewelry-count-reconciliation (7:47 PM).
They all share the one Bravo login. If you leave Bravo wedged, they all die.

THIS HAS ALREADY HAPPENED. On 2026-08-11 this task failed a password submit during the
Lexington store switch (19:21:41 Submit -> 19:22:07 "timeout waiting for LEX, onLogin=yes").
Bravo was left parked on the Lexington login screen. The auth circuit breaker correctly
stopped this task after 3 consecutive failures — but nothing un-wedged Bravo. Recovery
attempts at 20:37, 05:04, 05:06, 05:10, 05:11, 07:25, 07:26, 07:30, 07:32, 08:08, 08:10,
08:13 and 08:15 all re-submitted the password into the same dead screen and timed out.
The state only cleared when a VM restart ran at 08:19 the next morning. The 8:30 PM jewelry
pull got nothing. 13 hours of outage from one failed submit.

SO: whenever your run finishes with anything other than a clean success — partial, error,
aborted, or the auth circuit breaker tripped — you MUST leave Bravo verified healthy before
you end your turn:

    bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_health_gate.sh"

Exit 0 = PASS (Bravo verified on a Dashboard), exit 1 = FAIL. It escalates on its own:
start the VM, bounce a dead guest agent, relaunch Bravo, then restart the VM. Poll with
short osascript calls (the wrapper dies around 25s — never one long sleep).

If it returns PASS, say so in your run output and stop. If it returns FAIL, send Joshua ONE
plain-language Slack DM (D03BHQH5VGT) saying Bravo needs a look — no technical detail in the
DM, all of it in your run output.

NOTE — this is NOT a credentials problem, do not "fix" it by re-entering the password.
Verified 2026-08-12: the stored credential is correct, and on the failing run Culpeper and
Harrisonburg both logged in successfully with it minutes before Lexington failed. The defect
is that Bravo intermittently does not process the Submit click, and the recovery path retries
the identical action forever instead of escalating. Escalating is what this step adds.
"""

if 'MANDATORY CLEANUP' in s:
    print('already patched, skipping')
else:
    open(p, 'w').write(s.rstrip() + '\n' + block)
    print('patched:', p)
