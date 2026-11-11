#!/bin/bash
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.vsp-fee-pay
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/vsp_fee_pay.sh" --dry-run --no-dm
/usr/bin/python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/agent_log_tail.py" vsp-fee-pay 30
