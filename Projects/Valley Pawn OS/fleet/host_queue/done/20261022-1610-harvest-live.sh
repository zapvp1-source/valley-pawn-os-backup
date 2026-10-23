#!/bin/bash
echo ===== install agent (dormant until native_live flag exists)
bash "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/install_agent.sh" com.valleypawn.knowledge-harvest
echo ===== live October run from the sources pulled at 15:35
/usr/bin/python3 -u "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/knowledge_harvest_monthly.py" --asof 2026-10-22 --reuse
