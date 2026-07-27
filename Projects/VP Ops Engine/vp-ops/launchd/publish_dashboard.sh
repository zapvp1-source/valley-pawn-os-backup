#!/bin/bash
# Native launchd wrapper for publish_dashboard — see BUILD_SPEC.md Hard Rule #7
exec /usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/VP Ops Engine/vp-ops/jobs/publish_dashboard.py" --live
