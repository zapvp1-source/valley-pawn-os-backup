#!/usr/bin/env python3
"""northwest_profile_prefs.py — RETIRED 2026-10-19: every native browser check shares ONE automation profile
(~/Library/Application Support/valleypawn/pw-vp); the prefs live in bin/vp_browser.py (prefs()). This name is
kept so older notes still work; it just applies the shared prefs (only while that Chrome is closed)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_browser
print(vp_browser.prefs())
