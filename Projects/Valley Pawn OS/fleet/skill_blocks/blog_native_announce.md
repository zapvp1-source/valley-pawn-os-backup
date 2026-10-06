# NATIVE ANNOUNCE OVERRIDE (2026-10-05) — supersedes Step 8 and every Slack/archive instruction above

Publishing stays exactly as written (PRIMARY PATH: the wpcom Content Authoring connector, `posts.create`, then the
HTTP 200 live check). After that, STOP — the run is complete.

- Do NOT save a local archive copy, do NOT call osascript, do NOT write any file on the Mac.
- Do NOT post to Slack. The native Mac agent `com.valleypawn.blog-announce` checks the site every 30 minutes and
  posts each new article's title and link to #blog-posts itself (as Goldilocks), and logs a missed run.
- If publishing fails after one retry, end the run with a one-line plain summary of what failed. Nothing else.

Why: scheduled runs can no longer touch the Mac's files (9/17) and, from 10/6, run in the cloud. Publishing only
needs the WordPress connector; everything else moved to the Mac agent.
