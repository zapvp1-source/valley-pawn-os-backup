#!/bin/bash
# host_diag.sh [section ...]   — READ-ONLY host diagnostics for the job queue (allow-listed).
# Sections: agents | registry | applog | slack-identity | scorecard | logs <name> [lines] | all
# Nothing here changes state; it exists so no job ever needs to run tail/grep/curl/launchctl
# itself. (bash 3.2 compatible — macOS /bin/bash.)
set +e
OS="$HOME/Documents/Claude/Projects/Valley Pawn OS"
VLOG="$HOME/Library/Logs/valleypawn"
sec() { echo; echo "--- $1 ---"; }
d_agents() { sec "launchd agents (valleypawn)"; launchctl list | grep valleypawn; }
d_registry() {
  sec "registries"
  /usr/bin/python3 - <<'PY'
import json,glob,os,time
for p in sorted(glob.glob(os.path.expanduser('~/Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json'))):
    try:
        d=json.load(open(p)); st=d.get('scheduledTasks',[])
        print(time.ctime(os.path.getmtime(p)), len(st),'tasks', sum(1 for t in st if t.get('enabled')),'enabled', p.replace(os.path.expanduser('~'),'~'))
    except Exception as e: print('FAIL',p,e)
PY
}
d_applog() {
  sec "Claude main.log — last 30 lines"; tail -30 "$HOME/Library/Logs/Claude/main.log" 2>&1 | cut -c1-300
  sec "ZodError lines"; grep -c ZodError "$HOME/Library/Logs/Claude/main.log" 2>/dev/null
}
d_slack() {
  sec "native bot identity (auth.test)"
  TOK=$(security find-generic-password -s vp-ops-slack-bot-token -a "$(whoami)" -w 2>/dev/null)
  if [ -n "$TOK" ]; then curl -s -H "Authorization: Bearer $TOK" https://slack.com/api/auth.test; echo; else echo "no token in Keychain"; fi
}
d_scorecard() {
  sec "field-scorecard.log tail"; tail -8 "$VLOG/field-scorecard.log" 2>&1
  sec "registry-guard.log tail"; tail -4 "$VLOG/registry-guard.log" 2>&1
}
[ $# -eq 0 ] && set -- all
while [ $# -gt 0 ]; do
  case "$1" in
    all) d_agents; d_registry; d_applog; d_slack; d_scorecard ;;
    agents) d_agents ;;
    registry) d_registry ;;
    applog) d_applog ;;
    slack-identity) d_slack ;;
    scorecard) d_scorecard ;;
    logs) NAME="$2"; N="${3:-40}"; sec "$VLOG/$NAME.log (last $N)"; tail -n "$N" "$VLOG/$NAME.log" 2>&1; shift; [ -n "$2" ] && shift ;;
    *) echo "unknown section: $1" ;;
  esac
  shift
done
exit 0
