# Pending fix — chekkit-unanswered-alert (not applied; task edit was blocked pending Joshua's approval)

Bug (9/25 run): the task decided Thu 9/24 was "Wednesday", treated Waynesboro/Harrisonburg/Lexington/Roanoke as closed,
and posted a false all-clear. Correct result for 9/24: Harrisonburg 1 (Steven Mason, "Do you sell guns", ~3:52 PM,
answered 4:17 PM); every other alert was before open, after close, or a sign-off.

Changes to apply to the task prompt:
1. Step 1 computes the weekday with a command:
   TZ=America/New_York date -d yesterday '+%Y/%m/%d|%B %-d, %Y|%A'; TZ=America/New_York date '+%Y/%m/%d|%A'
   and uses only those printed values. No mental weekday math.
2. Step 3 writes a per-alert table (customer | store | ET time | counted? | reason) before tallying; the 03:07Z case
   belongs to the previous ET evening.
3. Store DM recipients are resolved each run from the Gusto active roster (department = store) + Slack user search,
   replacing the stale hard-coded map (it still lists Bree, Andrew, Nelson, Cris; it misses Joshua Burnett
   U0C3H004BUP and Joey Epperly U0BN3VC2E8G). Jacob Cox, Robert Swagger and Camden Ahern are not on Slack.
4. Publish-guard check finds vp_dryrun.py under /sessions/*/mnt/Projects when $HOME path is absent, else reads
   fleet/DRY_RUN.json (the 9/25 run skipped the guard because the path didn't resolve).
