#!/bin/bash
# Native launchd wrapper for job_gold_trend — see BUILD_SPEC.md Hard Rule #7
# (launchd jobs touching ~/Documents must run via ~/bin/vp-runner, which
# execs its argument through /bin/sh rather than respecting a Python
# shebang — so this thin .sh wrapper is the vp-runner entry point).
#
# HELD IN SHADOW MODE (2026-07-27): no prior canon exists for #gold-trend-'s
# format (BUILD_SPEC_WAVE2.md's proposed format becomes canon on the first
# real post) — needs Joshua's format review before flipping to --live, same
# as every other job. Flip to --live only after that.
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/VP Ops Engine/vp-ops/jobs/job_gold_trend.py" --shadow
