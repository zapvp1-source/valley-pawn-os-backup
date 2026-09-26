# SMS CODE — READ IT FROM THE RELAY FILE (replaces the iMessage connector step, 2026-09-25)

The `Read_and_Send_iMessages` connector is NOT available inside a scheduled run (same as
Control_your_Mac — proven 9/21 and 9/25). Do not call it and do not treat its absence as a failure.
A native agent on the Mac (`com.valleypawn.sms-code-relay`) reads Messages every 30 seconds during
this task's window and writes the newest Northwest code to:

`/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/fleet/sms_codes/northwest.json`
→ `{"code": "123456", "received": "<ISO time>", "age_s": <seconds old>, ...}`

When the portal shows the "You're almost there!" SMS screen:
1. Note the time you requested the code. Read the file with the Read tool.
2. Use `code` only if `age_s` is ≤ 600 AND `received` is AFTER you requested the code (a code from
   yesterday's run is stale — never type it).
3. If there is no fresh code yet, wait 10 s and read again, up to 12 times (2 minutes). The relay
   is faster than that; if 2 minutes pass with nothing, request the code once more and repeat once.
4. Type the code and continue. If it still has not arrived after the second request, write ONE
   FAILURE_LEDGER row (NEEDS_HUMAN: no — relay did not see the text) and stop. Never DM anyone.
