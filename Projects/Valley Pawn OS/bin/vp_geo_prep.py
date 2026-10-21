#!/usr/bin/env python3
"""vp_geo_prep.py — prepare the DEDICATED GEO sign-in profile (2026-10-20).
Why a separate profile: pw-vp is shared by the native daily checks (vsp_fee_pay, clock-in, dress code, cloudcover);
each one quits any open copy of pw-vp before it launches, which closed Joshua's 8-tab GEO sign-in window at 16:56
on 10/20 before he could use it. pw-geo belongs only to the listing/GEO lane, so nothing else ever closes it.
Applies the same persistence recipe as vp_browser (exit_type Normal + 'Continue where you left off' set through
Chrome's own settings page) by calling vp_browser's functions with profile=GEO — vp_browser itself is unchanged."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vp_browser as vb

GEO = os.path.join(vb.APP_SUPPORT, "pw-geo")

def main():
    os.makedirs(GEO, exist_ok=True)
    os.chmod(GEO, 0o700)
    if vb.is_running(GEO):
        print("pw-geo already open - left alone"); return 0
    print(vb.prefs(GEO))
    if vb.startup_pref(GEO) != 1:
        with vb._pw() as p:
            v = vb.set_startup_pref(p, GEO)
        print("startup pref set ->", v, "| Secure Preferences:", vb.startup_pref(GEO))
    else:
        print("startup pref already 1")
    return 0 if vb.startup_pref(GEO) == 1 else 1

if __name__ == "__main__":
    sys.exit(main())
