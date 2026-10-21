#!/bin/bash
# wave 3 second pass - READ-ONLY probes (no joins, no posts, no pulls)
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3b_probe.py" slack
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3b_probe.py" files
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3b_probe.py" sheet
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3b_probe.py" chekkit
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/w3b_probe.py" usearch
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" scrap-bucket-name-check 60000
python3 "/Users/joshuadavis/Documents/Claude/Projects/Valley Pawn OS/bin/skill_dump.py" ceo-monthly-scorecard 60000
