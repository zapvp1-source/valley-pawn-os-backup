#!/bin/bash
# Native launchd wrapper for job_employee_rankings — see BUILD_SPEC.md Hard Rule #7
# (launchd jobs touching ~/Documents must run via ~/bin/vp-runner, which
# execs its argument through /bin/sh rather than respecting a Python
# shebang — so this thin .sh wrapper is the vp-runner entry point).
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/VP Ops Engine/vp-ops/jobs/job_employee_rankings.py" --live
