#!/bin/bash
# HOST JOB - send signed FFL PDFs to KYGUNCO (they could not open links) - Joshua directed 2026-09-29
/usr/bin/python3 "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/send_ffl_set.py" info@kygunco.com "$HOME/Documents/Claude/Projects/Valley Pawn OS/fleet/outbox_ffl/kygunco.json"
