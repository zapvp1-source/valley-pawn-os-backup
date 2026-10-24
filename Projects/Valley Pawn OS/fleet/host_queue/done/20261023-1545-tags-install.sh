#!/bin/bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.chekkit-customer-tags
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.chekkit-roster-check
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/chekkit_tags.py" verify
