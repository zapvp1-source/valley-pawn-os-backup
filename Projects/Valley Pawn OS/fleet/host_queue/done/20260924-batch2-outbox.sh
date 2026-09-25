#!/bin/bash
BIN="$HOME/Documents/Claude/Projects/Valley Pawn OS/bin"
python3 "$BIN/install_outbox_step.py" vp-ai-search-health-check C0BCEESUANM --apply
python3 "$BIN/install_outbox_step.py" vp-ai-visibility-metrics C0BCEESUANM --apply
python3 "$BIN/install_outbox_step.py" vp-presence-audit-weekly C0BCEESUANM --apply
python3 "$BIN/install_outbox_step.py" weekly-social-media-recap C0BMRC2LN3D --apply
python3 "$BIN/install_outbox_step.py" monthly-ebay-ratings-sweep C0ANVN5KX4Y --apply
python3 "$BIN/install_outbox_step.py" vp-staff-video-prompt C0AVCANK7E3 --apply
python3 "$BIN/install_outbox_step.py" vp-staff-video-chase C0BHTEUPADB --apply
python3 "$BIN/install_outbox_step.py" weekly-online-store-audit C0ANVN5KX4Y --apply
