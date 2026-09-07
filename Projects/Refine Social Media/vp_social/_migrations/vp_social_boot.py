#!/usr/bin/env python3
"""
Bootstrap for launchd runs. Lives at ~/vp_social_boot.py (copy of this file).

Why it exists: under launchd, `cd '<project>' && python3 -m vp_social` fails with
"No module named vp_social" — the working directory is not on sys.path the way it is in
an interactive shell. Putting the project root on sys.path explicitly fixes it. Reads of
the project folder itself are fine; only the implicit cwd entry was missing.
"""
import sys

RSM = "/Users/joshuadavis/Documents/Claude/Projects/Refine Social Media"
if RSM not in sys.path:
    sys.path.insert(0, RSM)

from vp_social.cli import main  # noqa: E402

raise SystemExit(main(sys.argv[1:]))
