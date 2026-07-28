#!/bin/bash
# Native launchd wrapper for job_monthly_analytics — see BUILD_SPEC.md Hard Rule #7
# (launchd jobs touching ~/Documents must run via ~/bin/vp-runner, which
# execs its argument through /bin/sh rather than respecting a Python
# shebang — so this thin .sh wrapper is the vp-runner entry point).
# HELD IN SHADOW MODE (2026-07-27): this posts to production
# #company-performance/#store-performance with a format that was never
# byte-verified against real Slack history (see STATE.md's I-0 notes) --
# needs an explicit shadow-test review + go-ahead before flipping to --live,
# same as every other job this project. Flip to --live only after that.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/VP Ops Engine/vp-ops/jobs/job_monthly_analytics.py" --shadow
