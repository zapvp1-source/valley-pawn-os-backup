#!/usr/bin/env python3
"""Valley Pawn Command Center v2 — local control panel at http://127.0.0.1:8765
v2 adds the Schedules panel: view/pause/resume/re-time local launchd jobs and
put any task folder on a local schedule (runs via vp-runner -> vp_agent or native
script). Claude-cloud schedules shown read-only from the trigger export.
Localhost-only. Pure stdlib. Managed jobs: ~/Library/LaunchAgents/com.valleypawn.*.plist
"""
import json, os, re, glob, plistlib, subprocess, time, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8765
HOME = os.path.expanduser("~")
SCHEDULED = os.path.join(HOME, "Documents/Claude/Scheduled")
AGENT_DIR = os.path.join(HOME, "Documents/Claude/Projects/VP Agent")
AGENT = os.path.join(AGENT_DIR, "vp_agent.py")
RUNNER = os.path.join(HOME, "bin/vp-runner")
LA_DIR = os.path.join(HOME, "Library/LaunchAgents")
EXPORT_GLOB = os.path.join(SCHEDULED, "_ccr-trigger-export", "ccr_triggers_export_*.json")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1AVg9av3L7wJyQgX49uMYg5hBjbDz5Jwllxen3xkEkqk/edit"
NATIVE_RUNNERS = {
    "dashboard-data-collector": f"{SCHEDULED}/dashboard-data-collector/collect.sh",
    "daily-loan-inventory-text": f"{SCHEDULED}/daily-loan-inventory-text/daily_run.sh",
}
RUN_LOG = os.path.join(AGENT_DIR, "logs", "command_center_runs.log")
PROTECTED = {"com.valleypawn.commandcenter"}
LABEL_RE = re.compile(r"^com\.valleypawn\.[a-z0-9._-]+$")


def sh(cmd, timeout=20):
    try:
        r = subprocess.run(["/bin/bash", "-c", cmd], capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return 1, "", str(e)


def scan_tasks():
    tasks, now = [], time.time()
    if not os.path.isdir(SCHEDULED):
        return tasks
    for name in sorted(os.listdir(SCHEDULED)):
        d = os.path.join(SCHEDULED, name)
        if not os.path.isdir(d) or name.startswith("_") or name == "model-check-temp":
            continue
        latest = 0
        for root, dirs, files in os.walk(d):
            if root[len(d):].count(os.sep) >= 3:
                dirs[:] = []
                continue
            for fn in files:
                try:
                    m = os.path.getmtime(os.path.join(root, fn))
                    latest = max(latest, m)
                except OSError:
                    pass
        hours = (now - latest) / 3600 if latest else None
        status = "unknown" if not latest else ("active" if hours < 48 else ("stale" if hours < 336 else "dead?"))
        runnable = "native" if name in NATIVE_RUNNERS else ("agent" if os.path.exists(os.path.join(d, "SKILL.md")) else None)
        tasks.append({"name": name, "status": status, "hours_ago": round(hours, 1) if hours else None,
                      "last_iso": datetime.datetime.utcfromtimestamp(latest).strftime("%Y-%m-%d %H:%M") if latest else "",
                      "runnable": runnable})
    return tasks


def kpi_snapshot():
    out = {}
    msg = os.path.join(SCHEDULED, "daily-loan-inventory-text", "latest_message.txt")
    if os.path.exists(msg):
        try:
            out["kpi_text"] = open(msg, errors="replace").read().strip()[:800]
            out["kpi_as_of"] = datetime.datetime.fromtimestamp(os.path.getmtime(msg)).strftime("%Y-%m-%d %H:%M")
        except OSError:
            pass
    return out


def cal_human(ci):
    if not ci:
        return "manual / keep-alive"
    items = ci if isinstance(ci, list) else [ci]
    parts = []
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for it in items:
        h, m, wd = it.get("Hour"), it.get("Minute", 0), it.get("Weekday")
        s = f"{h:02d}:{m:02d}" if h is not None else f"hourly at :{m:02d}"
        if wd is not None:
            s += f" on {days[wd % 7]}"
        if it.get("Day") is not None:
            s += f" on day {it['Day']}"
        parts.append(s)
    return " & ".join(parts)


def loaded_labels():
    _, out, _ = sh("launchctl list | awk '{print $3}'")
    return set(out.split())


def list_schedules():
    jobs, loaded = [], loaded_labels()
    for p in sorted(glob.glob(os.path.join(LA_DIR, "com.valleypawn.*.plist"))):
        try:
            with open(p, "rb") as f:
                pl = plistlib.load(f)
        except Exception:
            continue
        label = pl.get("Label", os.path.basename(p)[:-6])
        if label in PROTECTED:
            continue
        ci = pl.get("StartCalendarInterval")
        prog = " ".join(pl.get("ProgramArguments", []))[:120]
        jobs.append({"label": label, "schedule": cal_human(ci), "enabled": label in loaded,
                     "editable": ci is not None and not isinstance(ci, list), "program": prog})
    cloud = []
    exports = sorted(glob.glob(EXPORT_GLOB))
    if exports:
        try:
            data = json.load(open(exports[-1]))
            for t in data.get("triggers", []):
                if t.get("cron_expression") or (t.get("enabled") and t.get("run_once_at")):
                    cloud.append({"name": t.get("name"), "cron": t.get("cron_expression") or f"once {t.get('run_once_at')}",
                                  "enabled": t.get("enabled")})
        except Exception:
            pass
    return {"local": jobs, "cloud": cloud}


def plist_path(label):
    return os.path.join(LA_DIR, label + ".plist")


def toggle_job(label, on):
    if not LABEL_RE.match(label) or label in PROTECTED or not os.path.exists(plist_path(label)):
        return False, "bad label"
    rc, _, err = sh(f"launchctl {'load' if on else 'unload'} '{plist_path(label)}' 2>&1")
    return True, ("enabled" if on else "paused")


def settime_job(label, hour, minute, weekday):
    if not LABEL_RE.match(label) or label in PROTECTED:
        return False, "bad label"
    p = plist_path(label)
    if not os.path.exists(p):
        return False, "not found"
    try:
        with open(p, "rb") as f:
            pl = plistlib.load(f)
        ci = {}
        if minute is not None:
            ci["Minute"] = minute
        if hour is not None:
            ci["Hour"] = hour
        if weekday is not None:
            ci["Weekday"] = weekday
        if not ci:
            return False, "no time given"
        pl["StartCalendarInterval"] = ci
        sh(f"launchctl unload '{p}' 2>/dev/null")
        with open(p, "wb") as f:
            plistlib.dump(pl, f)
        sh(f"launchctl load '{p}'")
        return True, "rescheduled: " + cal_human(ci)
    except Exception as e:
        return False, str(e)


def create_job(task, hour, minute, weekday):
    task = os.path.basename(task)
    d = os.path.join(SCHEDULED, task)
    if not os.path.isdir(d):
        return False, "unknown task"
    if task in NATIVE_RUNNERS:
        args = [RUNNER, NATIVE_RUNNERS[task]]
    elif os.path.exists(os.path.join(d, "SKILL.md")):
        args = [RUNNER, "-c", f"exec /usr/bin/python3 '{AGENT}' --skill '{d}/SKILL.md'"]
    else:
        return False, "no SKILL.md or native script"
    slug = re.sub(r"[^a-z0-9-]", "-", task.lower())
    label = f"com.valleypawn.vpcc-{slug}"
    ci = {"Minute": minute if minute is not None else 0}
    if hour is not None:
        ci["Hour"] = hour
    if weekday is not None:
        ci["Weekday"] = weekday
    pl = {"Label": label, "ProgramArguments": args, "StartCalendarInterval": ci, "RunAtLoad": False,
          "StandardOutPath": f"{AGENT_DIR}/logs/{label}.out.log", "StandardErrorPath": f"{AGENT_DIR}/logs/{label}.err.log"}
    p = plist_path(label)
    sh(f"launchctl unload '{p}' 2>/dev/null")
    with open(p, "wb") as f:
        plistlib.dump(pl, f)
    sh(f"launchctl load '{p}'")
    return True, f"scheduled ({cal_human(ci)})"


def run_task_bg(name):
    name = os.path.basename(name)
    os.makedirs(os.path.dirname(RUN_LOG), exist_ok=True)
    if name in NATIVE_RUNNERS:
        cmd = f"/bin/bash '{NATIVE_RUNNERS[name]}'"
    else:
        skill = os.path.join(SCHEDULED, name, "SKILL.md")
        if not os.path.exists(skill):
            return False, "no SKILL.md"
        cmd = f"/usr/bin/python3 '{AGENT}' --skill '{skill}'"
    with open(RUN_LOG, "a") as f:
        f.write(f"{datetime.datetime.now().isoformat()} RUN {name}: {cmd}\n")
    subprocess.Popen(["/bin/bash", "-c", f"{cmd} >> '{RUN_LOG}' 2>&1"], start_new_session=True)
    return True, "started"


PAGE = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Valley Pawn — Command Center</title>
<meta name="viewport" content="width=device-width, initial-scale=1"><style>
:root{--bg:#101418;--panel:#1a2027;--line:#2a323c;--text:#e8ecf1;--dim:#9aa7b4;--gold:#c9a227;--ok:#3fb27f;--warn:#d9a13b;--bad:#d96b6b}
*{box-sizing:border-box;margin:0;padding:0}body{background:var(--bg);color:var(--text);font:15px/1.5 -apple-system,sans-serif;padding:28px}
h1{font-size:22px}h1 span{color:var(--gold)}h2{font-size:15px;color:var(--dim);margin:26px 0 10px;text-transform:uppercase;letter-spacing:.6px}
.sub{color:var(--dim);font-size:13px;margin:4px 0 20px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:8px}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 18px}
.tile .l{color:var(--dim);font-size:12px;text-transform:uppercase}.tile .v{font-size:24px;font-weight:600}
.tile .v.ok{color:var(--ok)}.tile .v.warn{color:var(--warn)}.tile .v.bad{color:var(--bad)}
.kpibox{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:14px 0;white-space:pre-wrap;font-size:14px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{text-align:left;padding:8px 13px;border-bottom:1px solid var(--line);font-size:14px}
th{color:var(--dim);font-size:11px;text-transform:uppercase;background:#151b21}tr:last-child td{border-bottom:none}
.pill{display:inline-block;padding:2px 9px;border-radius:99px;font-size:12px;font-weight:600}
.pill.active,.pill.on{background:#173527;color:var(--ok)}.pill.stale{background:#3a2f18;color:var(--warn)}
.pill.dead,.pill.off{background:#3a2020;color:var(--bad)}.pill.unknown,.pill.cloud{background:#262c33;color:var(--dim)}
button,a.btn{background:var(--panel);border:1px solid var(--line);color:var(--gold);border-radius:8px;padding:6px 11px;font-size:13px;cursor:pointer;text-decoration:none}
button.dim{color:var(--dim)}button:disabled{opacity:.4}input[type=search]{background:var(--panel);border:1px solid var(--line);color:var(--text);border-radius:8px;padding:8px 12px;width:250px}
.bar{display:flex;gap:10px;margin:10px 0 12px;flex-wrap:wrap}.foot{color:var(--dim);font-size:12px;margin-top:16px}
</style></head><body>
<h1>Valley Pawn <span>Command Center</span></h1>
<div class="sub">Runs locally on this Mac — works with or without Claude.</div>
<div class="tiles" id="tiles"></div><div class="kpibox" id="kpibox" style="display:none"></div>
<h2>Schedules — local (this Mac, Claude-independent)</h2>
<table><thead><tr><th>Job</th><th>Schedule</th><th>State</th><th style="width:210px">Adjust</th></tr></thead><tbody id="ljobs"></tbody></table>
<h2>Schedules — Claude cloud (view-only, manage in the Claude app)</h2>
<table><thead><tr><th>Task</th><th>Schedule (cron)</th><th>State</th></tr></thead><tbody id="cjobs"></tbody></table>
<h2>All tasks</h2>
<div class="bar"><input type="search" id="q" placeholder="Filter tasks…">
<a class="btn" href="{SHEET}" target="_blank">Data sheet ↗</a><button class="dim" onclick="load()">Refresh</button></div>
<table><thead><tr><th>Task</th><th>Status</th><th>Last activity</th><th style="width:250px">Actions</th></tr></thead><tbody id="rows"></tbody></table>
<div class="foot"><b>▶ run</b> executes now on this Mac (native = plain script; agent = vp-agent with configured AI engine). <b>⏰ schedule</b> creates a local recurring schedule for that task — your Claude-independent backup schedule. Logs: Projects/VP Agent/logs/.</div>
<script>
const $=id=>document.getElementById(id);
async function load(){
 const d=await (await fetch('/api/status')).json();
 const s=await (await fetch('/api/schedules')).json();
 const a=d.tasks.filter(x=>x.status==='active').length,st=d.tasks.filter(x=>x.status==='stale').length,dd=d.tasks.filter(x=>x.status==='dead?').length;
 $('tiles').innerHTML=tile('Task folders',d.tasks.length)+tile('Active 48h',a,'ok')+tile('Stale 2-14d',st,st?'warn':'ok')+tile('Silent 14d+',dd,dd?'bad':'ok')+tile('Local schedules',s.local.length,'ok');
 if(d.kpi.kpi_text){$('kpibox').style.display='block';$('kpibox').textContent=d.kpi.kpi_text+(d.kpi.kpi_as_of?'\n(as of '+d.kpi.kpi_as_of+')':'');}
 $('ljobs').innerHTML=s.local.map(j=>`<tr><td>${j.label.replace('com.valleypawn.','')}</td><td>${j.schedule}</td>
  <td><span class="pill ${j.enabled?'on':'off'}">${j.enabled?'enabled':'paused'}</span></td>
  <td><button onclick="tog('${j.label}',${j.enabled?0:1},this)">${j.enabled?'⏸ pause':'▶ resume'}</button>
  ${j.editable?`<button onclick="retime('${j.label}')">🕑 change time</button>`:''}</td></tr>`).join('')||'<tr><td colspan=4>none</td></tr>';
 $('cjobs').innerHTML=s.cloud.map(c=>`<tr><td>${c.name}</td><td>${c.cron}</td><td><span class="pill cloud">${c.enabled?'enabled':'off'}</span></td></tr>`).join('')||'<tr><td colspan=3>none</td></tr>';
 window._t=d.tasks;render();
}
function tile(l,v,c){return `<div class="tile"><div class="l">${l}</div><div class="v ${c||''}">${v}</div></div>`}
function render(){const q=$('q').value.toLowerCase();
 $('rows').innerHTML=(window._t||[]).filter(t=>t.name.includes(q)).map(t=>{
 const cls=t.status==='dead?'?'dead':t.status,ago=t.hours_ago==null?'—':(t.hours_ago<48?t.hours_ago+'h':Math.round(t.hours_ago/24)+'d')+' ago';
 const act=t.runnable?`<button onclick="run('${t.name}',this)">▶ run (${t.runnable})</button> <button class="dim" onclick="sched('${t.name}')">⏰ schedule</button>`:'—';
 return `<tr><td>${t.name}</td><td><span class="pill ${cls}">${t.status}</span></td><td>${t.last_iso} <span style="color:var(--dim)">(${ago})</span></td><td>${act}</td></tr>`}).join('');}
async function post(u){return (await fetch(u,{method:'POST'})).json()}
async function run(n,b){b.disabled=true;const d=await post('/api/run?task='+encodeURIComponent(n));b.textContent=d.ok?'✓ started':'✗ '+d.msg;setTimeout(load,6000)}
async function tog(l,on,b){b.disabled=true;await post(`/api/schedule/toggle?label=${l}&on=${on}`);load()}
function ask(){let t=prompt('Time to run, 24h format HH:MM (e.g. 07:30), or just :MM for hourly (e.g. :20):');if(!t)return null;
 let wd=prompt('Day of week (0=Sun … 6=Sat), or leave blank for every day:');let m=t.match(/^(\d{1,2}):(\d{2})$/),hm=t.match(/^:(\d{2})$/);
 if(hm)return{minute:+hm[1],weekday:wd?+wd:null};if(m)return{hour:+m[1],minute:+m[2],weekday:wd?+wd:null};alert('bad format');return null}
async function retime(l){const p=ask();if(!p)return;const d=await post(`/api/schedule/settime?label=${l}${p.hour!=null?'&hour='+p.hour:''}&minute=${p.minute}${p.weekday!=null?'&weekday='+p.weekday:''}`);alert(d.msg);load()}
async function sched(n){const p=ask();if(!p)return;const d=await post(`/api/schedule/create?task=${encodeURIComponent(n)}${p.hour!=null?'&hour='+p.hour:''}&minute=${p.minute}${p.weekday!=null?'&weekday='+p.weekday:''}`);alert(d.msg);load()}
$('q').addEventListener('input',render);load();
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def _s(self, code, body, ct="application/json"):
        b = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/":
            self._s(200, PAGE.replace("{SHEET}", SHEET_URL), "text/html; charset=utf-8")
        elif p == "/api/status":
            self._s(200, json.dumps({"tasks": scan_tasks(), "kpi": kpi_snapshot()}))
        elif p == "/api/schedules":
            self._s(200, json.dumps(list_schedules()))
        else:
            self._s(404, "{}")

    def do_POST(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)

        def gi(k):
            v = q.get(k, [None])[0]
            return int(v) if v not in (None, "",) else None
        if u.path == "/api/run":
            ok, msg = run_task_bg(q.get("task", [""])[0])
        elif u.path == "/api/schedule/toggle":
            ok, msg = toggle_job(q.get("label", [""])[0], q.get("on", ["1"])[0] == "1")
        elif u.path == "/api/schedule/settime":
            ok, msg = settime_job(q.get("label", [""])[0], gi("hour"), gi("minute"), gi("weekday"))
        elif u.path == "/api/schedule/create":
            ok, msg = create_job(q.get("task", [""])[0], gi("hour"), gi("minute"), gi("weekday"))
        else:
            self._s(404, "{}")
            return
        self._s(200, json.dumps({"ok": ok, "msg": msg}))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
