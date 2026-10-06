#!/bin/bash
# read-only: can a queue job show a dialog on the Mac? (prints the error if not)
osascript -e 'display dialog "test" giving up after 3' 2>&1; echo "plain rc=$?"
osascript -e 'tell application "System Events" to display dialog "test" giving up after 3' 2>&1; echo "sysevents rc=$?"
osascript -e 'tell application "Finder" to activate' -e 'tell application "Finder" to display dialog "test" giving up after 3' 2>&1; echo "finder rc=$?"
