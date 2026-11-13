#!/bin/bash
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/ivr_app_link_text.py" --render --hours 3
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/agent_log_tail.py" ivr_app_link_text/run 10
