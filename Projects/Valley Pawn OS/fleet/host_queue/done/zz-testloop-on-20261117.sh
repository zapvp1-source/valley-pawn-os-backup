#!/bin/bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.email-test-loop-apply
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.email-test-loop-grade
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/email_test_loop.py" probe
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/email_test_loop.py" apply --render
