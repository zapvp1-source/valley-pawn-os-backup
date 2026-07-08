#!/bin/bash
ISL="/Users/joshuadavis/Documents/Claude/Projects/Bravo Pipeline/island/output"
echo "=== AHK STDOUT/ERR ==="
cat "$ISL/ahk_stdout.log" 2>&1 || echo "NO AHK STDOUT"
echo "=== ISLAND LOG (tail) ==="
tail -70 "$ISL/loans75-gridread.log" 2>&1 || echo "NO LOG YET"
echo "=== OUTPUT DIR ==="
ls -la "$ISL" 2>&1
echo "=== CSV (head) ==="
head -15 "$ISL"/*loans75-gridread.csv 2>&1 || echo "NO CSV YET"
