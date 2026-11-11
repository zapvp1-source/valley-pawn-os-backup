#!/bin/bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vsp_fee_pay.sh" --read --no-dm
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/agent_log_tail.py" vsp-fee-pay 7
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/host_diag.sh" agents
