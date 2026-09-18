#!/bin/bash
# bravo_fix_terminal.sh — make the VM's default terminal the classic console host (conhost) so
# `powershell -WindowStyle Hidden` is actually hidden. With Windows Terminal as default, every
# prlctl exec pops a terminal window OVER Bravo and UIA reports "no-dashboard" (2026-09-17).
# Reversible: delete the two DelegationConsole/DelegationTerminal values to go back to WT.
AGENT=bravo-fix-terminal; . "$HOME/Documents/Claude/Projects/Valley Pawn OS/bin/vp_lib.sh"
CONHOST='{B23D10C0-E52E-411E-9D5B-C09FDF709C7D}'
vm_ps_cmd "New-Item -Path 'HKCU:\Console\%%Startup' -Force | Out-Null; Set-ItemProperty -Path 'HKCU:\Console\%%Startup' -Name DelegationConsole -Value '$CONHOST'; Set-ItemProperty -Path 'HKCU:\Console\%%Startup' -Name DelegationTerminal -Value '$CONHOST'; (Get-ItemProperty 'HKCU:\Console\%%Startup') | Select-Object DelegationConsole,DelegationTerminal | Format-List | Out-String" 2>&1 | tr -s '\r\n' ' '
echo
sleep 2
vlog "closing terminals: $(bravo_close_terminals)"
sleep 3
vlog "health gate: $(health_gate 420)"
