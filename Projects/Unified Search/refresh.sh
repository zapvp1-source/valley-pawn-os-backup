#!/bin/bash
P="$HOME/Documents/Claude/Projects/Unified Search"
cd "$P" || exit 1
echo "=== refresh $(date) ==="
/usr/bin/python3 usearch.py mail
/usr/bin/python3 usearch.py files
/usr/bin/python3 msgindex.py
/usr/bin/python3 usearch.py stats > stats.txt
echo "=== done $(date) ==="
