p = '/Users/joshuadavis/Library/Application Support/Claude/local-agent-mode-sessions/823f6874-6252-4031-ae4e-a3c22d37598e/f6b75d02-cca9-4943-ad6e-88390a3f201d/local_3157f313-15bc-4ec0-933b-9afdb15f15ae/uploads/SKILL.md'
import os

# The live registered task file
live = '/Users/joshuadavis/Documents/Claude/Scheduled/jewelry-onhand-nightly-pull/SKILL.md'
target = live if os.path.exists(live) else p

s = open(target).read()

old = "- Check `logs/_health_gate_status.txt` for PASS."

new = """- RUN the health gate, do not just read its status file. The status file is written by the LAST
  gate run and is routinely hours stale, so reading it proves nothing. Execute:
      bash "/Users/joshuadavis/Documents/Claude/Projects/Bravo Data Extraction/bravo_health_gate.sh"
  It exits 0 = PASS (Bravo verified on a Dashboard) and 1 = FAIL. It escalates on its own:
  start the VM, bounce a dead guest agent, relaunch Bravo, and finally restart the VM. Give it a
  few minutes (poll with short osascript calls, never one long sleep). Only drop the trigger on
  exit 0.
  WHY THIS EXISTS (2026-08-11): asset-recovery-daily-refresh at 7:17 PM failed a password submit
  during the Lexington store switch and left Bravo parked on the LEX login screen. The auth circuit
  breaker correctly stopped that task, but nothing un-wedged Bravo. Every recovery attempt for the
  next 13 hours re-submitted the password into the same dead screen and timed out — the state only
  cleared when the health gate restarted the VM at 8:19 AM. Your 8:30 PM run was the victim: 6
  failed recovery attempts, all 5 stores skipped, zero data. Running the gate first turns that
  13-hour outage into a ~3-minute VM restart."""

assert old in s, 'anchor not found'
open(target, 'w').write(s.replace(old, new))
print('patched:', target)
