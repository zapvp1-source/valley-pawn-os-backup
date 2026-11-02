#!/usr/bin/env python3
"""fleet_deck.py — VP Fleet Deck: live at-a-glance status of every agent on the Mac Studio.

Native, stdlib-only, READ-ONLY (it never starts, stops or edits anything). Installed as
com.valleypawn.fleet-deck (via ~/bin/vp-runner -> bin/fleet_deck_run.sh). Serves
http://127.0.0.1:8790 (localhost only) and refreshes its snapshot every 20 s:

  * every ~/Library/LaunchAgents/com.valleypawn*.plist (+ vpops): loaded? pid? last exit?
    schedule (parsed from the plist), next fire, latest log activity, dormant (vp_live gate)
  * the existing health files: FLEET_HEALTH.md, FIELD_SCORECARD.md (today table),
    fleet/FAILURE_LEDGER.md open rows, fleet/connector_health.json, fleet/state/fleet_scorecard.json,
    fleet/host_queue (pending + recent done), Life OS/HUMAN_QUEUE.md
  * the Cowork scheduled-task registry (enabled tasks + lastRunAt)
  * Mac vitals: memory pressure/swap, load, disk, uptime; Claude.app / Chrome / Parallels VM alive,
    Chrome-extension bridge state (Claude main.log), Bravo pipeline results/triggers

Writes fleet/state/fleet_deck.json every cycle so other tooling (and cloud sessions via Drive)
can read the same picture. Endpoints: /  /api/status  /api/log?label=<launchd label>

  fleet_deck.py --serve         run the server (what launchd does)
  fleet_deck.py --once          print one JSON snapshot and exit
  fleet_deck.py --port 8790     override the port (default 8790)
"""
import datetime as dt
import glob
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOME = os.path.expanduser("~")
OS_DIR = os.path.join(HOME, "Documents/Claude/Projects/Valley Pawn OS")
LIFE_DIR = os.path.join(HOME, "Documents/Claude/Projects/Life OS")
BRAVO = os.path.join(HOME, "Documents/Claude/Projects/Bravo Data Extraction")
FLEET = os.path.join(OS_DIR, "fleet")
LA_DIR = os.path.join(HOME, "Library/LaunchAgents")
VLOG = os.path.join(HOME, "Library/Logs/valleypawn")
STATE_OUT = os.path.join(FLEET, "state/fleet_deck.json")
REGGLOB = os.path.join(HOME, "Library/Application Support/Claude/local-agent-mode-sessions/*/*/scheduled-tasks.json")
CLAUDE_MAIN_LOG = os.path.join(HOME, "Library/Logs/Claude/main.log")
TRIAGE_EXPECT = os.path.join(FLEET, "log_triage_expectations.json")

PORT = 8790
REFRESH_S = 30
HEARTBEAT_S = 3600
HISTORY_N = 180  # 1 h of 20 s samples
STATE_EVERY_S = 300  # fleet/state/fleet_deck.json is Drive-synced: write it every 5 min, not every cycle

_snapshot = {"generated": None, "error": "warming up"}
_lock = threading.Lock()
_history = deque(maxlen=HISTORY_N)
_sched_cache = {}  # plist path -> (mtime, parsed)


def now():
    return dt.datetime.now()


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception:
        return ""


def mtime(p):
    try:
        return os.path.getmtime(p)
    except Exception:
        return None


def iso(ts):
    if ts is None:
        return None
    return dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def read_text(p, max_bytes=400000):
    try:
        with open(p, "rb") as f:
            if max_bytes and os.path.getsize(p) > max_bytes:
                f.seek(-max_bytes, 2)
            return f.read().decode("utf-8", "replace")
    except Exception:
        return ""


def tail_lines(p, n):
    t = read_text(p, max(8000, n * 400))
    if not t:
        return []
    return [l for l in t.splitlines() if l.strip()][-n:]


def load_json(p, default):
    try:
        v = json.load(open(p))
        return v if isinstance(v, type(default)) else default
    except Exception:
        return default


# ------------------------------------------------------------------ schedule parsing
WD = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def describe_calendar(entries):
    """Human text + expected gap (hours) for a StartCalendarInterval list."""
    if not entries:
        return "", None
    times = set()
    days = set()
    monthly = False
    hourly = False
    for e in entries:
        h, m = e.get("Hour"), e.get("Minute", 0)
        if h is None:
            hourly = True
        else:
            times.add("%02d:%02d" % (h, m))
        if "Weekday" in e:
            days.add(e["Weekday"] % 7)
        if "Day" in e:
            monthly = True
            days.add("d%d" % e["Day"])
    tl = ", ".join(sorted(times))
    if hourly:
        text, gap = "hourly at :%02d" % entries[0].get("Minute", 0), 3
    elif monthly:
        text, gap = "monthly (day %s) %s" % (",".join(str(d)[1:] for d in sorted(days, key=str)), tl), 24 * 32
    elif days:
        wdays = sorted(d for d in days if isinstance(d, int))
        if len(wdays) >= 6:
            label = "Mon-Sat" if 0 not in wdays else "daily"
        else:
            label = "/".join(WD[d] for d in wdays)
        text = "%s %s" % (label, tl)
        gap = 26 if len(wdays) >= 5 else (24 * 7 + 6) / max(1, len(wdays)) * 1.15
    else:
        text = "daily %s" % tl
        gap = 26 if len(times) <= 1 else 26.0 / len(times) * 1.6
    return text, gap


def next_fire(entries, ref):
    best = None
    for e in entries:
        for dback in range(0, 70):
            day = (ref + dt.timedelta(days=dback)).date()
            if "Weekday" in e and (day.weekday() + 1) % 7 != e["Weekday"] % 7:
                continue
            if "Day" in e and day.day != e["Day"]:
                continue
            if "Month" in e and day.month != e["Month"]:
                continue
            m = e.get("Minute", 0)
            if e.get("Hour") is None:
                hours = range(24)
            else:
                hours = [e["Hour"]]
            cand = None
            for h in hours:
                c = dt.datetime.combine(day, dt.time(h, m))
                if c > ref:
                    cand = c
                    break
            if cand:
                if best is None or cand < best:
                    best = cand
                break
    return best


def prev_fire_cal(entries, ref):
    """Most recent launchd StartCalendarInterval slot strictly before ref (local naive), or None."""
    best = None
    for e in entries:
        for dback in range(0, 40):
            day = (ref - dt.timedelta(days=dback)).date()
            if "Weekday" in e and (day.weekday() + 1) % 7 != e["Weekday"] % 7:
                continue
            if "Day" in e and day.day != e["Day"]:
                continue
            if "Month" in e and day.month != e["Month"]:
                continue
            m = e.get("Minute", 0)
            hours = range(23, -1, -1) if e.get("Hour") is None else [e["Hour"]]
            cand = None
            for h in hours:
                c = dt.datetime.combine(day, dt.time(h, m))
                if c < ref:
                    cand = c
                    break
            if cand:
                if best is None or cand > best:
                    best = cand
                break
    return best


def parse_plist(path):
    mt = mtime(path)
    c = _sched_cache.get(path)
    if c and c[0] == mt:
        return c[1]
    info = {"label": os.path.basename(path)[:-6], "schedule": "", "gap_h": None, "calendar": [],
            "interval": None, "keepalive": False, "runatload": False, "disabled": False,
            "out_log": None, "err_log": None, "program": None, "args": [], "plist_mtime": mt,
            "gate": None, "note": "", "agent_name": None, "always_on": False}
    try:
        with open(path, "rb") as f:
            p = plistlib.load(f)
        info["label"] = p.get("Label", info["label"])
        args = p.get("ProgramArguments") or ([p["Program"]] if p.get("Program") else [])
        info["args"] = args
        info["program"] = args[1] if len(args) > 1 and args[0].endswith("vp-runner") else (args[0] if args else None)
        info["out_log"] = p.get("StandardOutPath")
        info["err_log"] = p.get("StandardErrorPath")
        info["runatload"] = bool(p.get("RunAtLoad"))
        info["disabled"] = bool(p.get("Disabled"))
        ka = p.get("KeepAlive")
        info["keepalive"] = ka is True or (isinstance(ka, dict) and len(ka) > 0)
        info["always_on"] = ka is True
        cal = p.get("StartCalendarInterval")
        if isinstance(cal, dict):
            cal = [cal]
        if cal:
            info["calendar"] = cal
            info["schedule"], info["gap_h"] = describe_calendar(cal)
        elif p.get("StartInterval"):
            iv = int(p["StartInterval"])
            info["interval"] = iv
            info["schedule"] = "every %s" % (("%ds" % iv) if iv < 120 else ("%dm" % (iv // 60)) if iv < 7200 else ("%.1fh" % (iv / 3600)))
            info["gap_h"] = max(1.0, iv * 2.5 / 3600)
        elif info["keepalive"]:
            info["schedule"] = "always on (KeepAlive)"
        elif info["runatload"]:
            info["schedule"] = "at login / one-shot"
        # dormant gate: wrapper sources vp_live.sh and gates on fleet/state/native_live/<id>
        prog = info["program"]
        if prog and prog.endswith(".sh") and os.path.isfile(prog):
            src = read_text(prog, 60000)
            m0 = re.search(r'^\s*AGENT="?([A-Za-z0-9_.-]+)"?', src, re.M)
            if m0:
                info["agent_name"] = m0.group(1)
            if "vp_live_gate" in src:
                m = re.search(r'vp_live_gate\s+"?([^"\s;]+)', src)
                gate = m.group(1) if m else None
                if gate and "$" in gate:
                    m2 = re.search(r'\bAGENT="?([^"\s;]+)', src)
                    gate = m2.group(1) if m2 and "$" not in m2.group(1) else None
                info["gate"] = gate or "?"
    except Exception as e:
        info["note"] = "plist unreadable: %s" % e
    _sched_cache[path] = (mt, info)
    return info


# ------------------------------------------------------------------ launchd
def launchctl_rows():
    rows = {}
    out = run(["launchctl", "list"])
    for l in out.splitlines():
        parts = l.split("\t")
        if len(parts) != 3:
            parts = l.split()
        if len(parts) == 3 and ("valleypawn" in parts[2] or "vpops" in parts[2]):
            rows[parts[2]] = (parts[0], parts[1])
    return rows


def agent_logs(info):
    label = info["label"]
    short = label.replace("com.valleypawn.", "").replace("com.valleypawn.vpops.", "vpops.")
    cands = [info.get("out_log"), info.get("err_log"),
             os.path.join(VLOG, short + ".log"), os.path.join(VLOG, short + ".out.log"), os.path.join(VLOG, short + ".err.log")]
    # wrapper's AGENT= name (vlog target) may differ from the label
    if info.get("agent_name"):
        cands.append(os.path.join(VLOG, info["agent_name"] + ".log"))
    seen, out = set(), []
    for c in cands:
        if c and c not in seen and os.path.isfile(c):
            seen.add(c)
            out.append(c)
    return out


def _evidence_mtime(expect, logs, label):
    ev = expect.get("evidence") or {}
    aliases = expect.get("aliases") or {}
    pats = []
    for lg in logs:
        pats += ev.get(os.path.basename(lg), [])
    for logname, lab in aliases.items():
        if lab == label:
            pats.append(os.path.join(VLOG, logname))
    best = None
    for pat in pats:
        for f in glob.glob(os.path.expanduser(pat)):
            m = mtime(f)
            if m and (best is None or m > best):
                best = m
    return best


MISSED_GRACE_H = 3.0   # a calendar slot counts as missed only this long after it was due


def collect_agents(expect):
    rows = launchctl_rows()
    agents = []
    plists = sorted(glob.glob(os.path.join(LA_DIR, "com.valleypawn*.plist")))
    retired = set((expect.get("retired") or {}).keys())
    gaps = expect.get("gap_hours") or {}
    t = time.time()
    for p in plists:
        info = parse_plist(p)
        label = info["label"]
        pid, last_exit = rows.get(label, (None, None))
        loaded = label in rows
        running = loaded and pid not in (None, "-")
        logs = agent_logs(info)
        last_act = max([mtime(x) for x in logs] or [None], key=lambda v: v or 0)
        evm = _evidence_mtime(expect, logs, label)
        if evm and (last_act is None or evm > last_act):
            last_act = evm
        is_retired = any(os.path.basename(lg) in retired for lg in logs)
        event_only = any(float(gaps.get(os.path.basename(lg), 0)) >= 168 for lg in logs)
        dormant = bool(info["gate"]) and info["gate"] != "?" and not os.path.exists(os.path.join(FLEET, "state/native_live", info["gate"]))
        nxt = next_fire(info["calendar"], now()) if info["calendar"] else None
        status, why = "ok", ""
        if info["disabled"]:
            status, why = "disabled", "plist marked Disabled"
        elif not loaded:
            status, why = "notloaded", "installed but not loaded in launchd"
        elif dormant:
            status, why = "dormant", "installed dormant (vp_live gate '%s' not switched on)" % info["gate"]
        elif running:
            status, why = "running", "pid %s" % pid
        elif last_exit not in (None, "0", "-"):
            status, why = "error", "last run exited %s" % last_exit
        elif info["calendar"] and not is_retired and not event_only:
            # calendar job: was its most recent slot (older than the grace) followed by any activity?
            slot = prev_fire_cal(info["calendar"], now() - dt.timedelta(hours=MISSED_GRACE_H))
            pm = info["plist_mtime"] or 0
            if slot and slot.timestamp() > pm:
                if last_act is None:
                    status, why = "quiet", "no log yet — first scheduled run was %s" % slot.strftime("%a %-m/%-d %H:%M")
                elif last_act < slot.timestamp() - 120:
                    status, why = "stale", "missed its %s run — last activity %s" % (
                        slot.strftime("%a %-m/%-d %H:%M"), dt.datetime.fromtimestamp(last_act).strftime("%a %-m/%-d %H:%M"))
        # interval / KeepAlive agents: launchd itself proves they are firing; health = loaded + exit 0 (+ pid for
        # KeepAlive). Their logs are event-only (texts, calls, questions), so log silence is NOT a fault.
        if status == "ok" and info["always_on"] and not running and loaded and not info["calendar"] and not info["interval"]:
            status, why = "error", "always-on agent is not running"
        agents.append({
            "label": label, "name": label.replace("com.valleypawn.", ""), "status": status, "why": why,
            "pid": pid if running else None, "last_exit": last_exit, "loaded": loaded,
            "schedule": info["schedule"], "next_fire": nxt.isoformat(timespec="minutes") if nxt else None,
            "last_activity": iso(last_act), "last_activity_ts": last_act, "logs": logs,
            "program": os.path.basename(info["program"]) if info["program"] else None,
            "keepalive": info["keepalive"], "always_on": info["always_on"], "interval": info["interval"], "calendar": bool(info["calendar"]), "runatload": info["runatload"], "gate": info["gate"], "note": info["note"],
        })
    agents.sort(key=lambda a: a["name"])
    return agents


# ------------------------------------------------------------------ other sources
def fleet_health_latest():
    t = read_text(os.path.join(OS_DIR, "FLEET_HEALTH.md"), 60000)
    parts = t.split("\n## ")
    if len(parts) < 2:
        return None
    top = parts[1]
    hdr = top.splitlines()[0]
    items = [l[2:].strip() for l in top.splitlines() if l.startswith("- ")]
    return {"header": hdr.strip(), "green": "ALL GREEN" in hdr, "items": items}


def field_scorecard_today():
    t = read_text(os.path.join(FLEET, "FIELD_SCORECARD.md"), 200000)
    if not t:
        return None
    m = re.search(r"## TODAY \(([^)]*)\)(.*?)\n---", t, re.S)
    if not m:
        return None
    rows = []
    for l in m.group(2).splitlines():
        if l.startswith("|") and not l.startswith("|---") and "| Task |" not in l:
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) >= 3:
                rows.append({"task": c[0], "status": c[1], "sched": c[2], "note": c[3] if len(c) > 3 else ""})
    mm = re.search(r"Right now: ([^*]+)\*\*", m.group(2))
    return {"day": m.group(1), "summary": mm.group(1).strip() if mm else "", "rows": rows,
            "missed": sum(1 for r in rows if r["status"].startswith("MISSED")),
            "posted": sum(1 for r in rows if r["status"] == "POSTED"),
            "mtime": iso(mtime(os.path.join(FLEET, "FIELD_SCORECARD.md")))}


def ledger_open():
    p = os.path.join(FLEET, "FAILURE_LEDGER.md")
    t = read_text(p, 300000)
    rows = [l for l in t.splitlines() if l.startswith("|") and "| OPEN |" in l]
    out = []
    for l in rows[-8:]:
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        out.append({"when": c[0] if c else "", "task": c[1] if len(c) > 1 else "", "what": c[2] if len(c) > 2 else ""})
    return {"open": len(rows), "recent": out[::-1], "mtime": iso(mtime(p))}


def human_queue():
    p = os.path.join(LIFE_DIR, "HUMAN_QUEUE.md")
    t = read_text(p, 200000)
    rows = [l for l in t.splitlines() if l.startswith("|") and not l.startswith("|---") and "OPEN" in l.upper()]
    return {"open_rows": len(rows), "mtime": iso(mtime(p))}


def host_queue():
    q = os.path.join(FLEET, "host_queue")
    pending = sorted(glob.glob(os.path.join(q, "*.sh")))
    done = sorted(glob.glob(os.path.join(q, "done", "*.log")), key=lambda x: mtime(x) or 0)[-6:]
    recent = []
    for d in done[::-1]:
        tl = tail_lines(d, 3)
        rc = None
        for l in tl:
            m = re.match(r"exit=(-?\d+)", l)
            if m:
                rc = int(m.group(1))
        recent.append({"job": os.path.basename(d)[:-4], "rc": rc, "when": iso(mtime(d))})
    return {"pending": [os.path.basename(x) for x in pending], "recent": recent}


def registry_tasks():
    files = sorted(glob.glob(REGGLOB), key=lambda x: mtime(x) or 0, reverse=True)
    if not files:
        return {"found": False, "enabled": [], "total": 0}
    d = load_json(files[0], {})
    tasks = d.get("scheduledTasks", []) or []
    en = []
    for t in tasks:
        if t.get("enabled"):
            en.append({"id": t.get("id"), "name": t.get("name") or t.get("id"), "cron": t.get("cronExpression"),
                       "last_run": t.get("lastRunAt")})
    return {"found": True, "enabled": en, "total": len(tasks), "disabled": len(tasks) - len(en),
            "skips_7d": sum(len(v) for v in (d.get("recordedSkips") or {}).values()), "file_mtime": iso(mtime(files[0]))}


def chrome_bridge():
    t = read_text(CLAUDE_MAIN_LOG, 400000)
    state, when = "unknown", None
    for l in t.splitlines()[::-1]:
        if "Chrome extension connected to bridge" in l or "Selected Chrome extension" in l:
            state = "connected"
        elif "Chrome extension disconnected from bridge" in l or "No Chrome extension connected" in l:
            state = "disconnected"
        else:
            continue
        m = re.match(r"\[?(\d{4}-\d\d-\d\d[T ]\d\d:\d\d:\d\d)", l)
        when = m.group(1) if m else None
        break
    return {"state": state, "since": when}


def procs():
    def alive(pat):
        return subprocess.run(["pgrep", "-f", pat], capture_output=True).returncode == 0
    return {
        "claude_app": alive("Claude.app/Contents/MacOS/Claude"),
        "chrome": alive("Google Chrome.app/Contents/MacOS/Google Chrome"),
        "parallels_vm": alive("prl_vm_app"),
        "ollama": alive("ollama"),
    }


def bravo_pipeline():
    res = sorted(glob.glob(os.path.join(BRAVO, "results", "*.result.json")), key=lambda x: mtime(x) or 0)
    last = res[-1] if res else None
    trig = glob.glob(os.path.join(BRAVO, "triggers", "*.json"))
    claimed = glob.glob(os.path.join(BRAVO, "triggers", "claimed", "*.json"))
    active = False
    for c in claimed:
        b = os.path.basename(c)[:-5]
        lm = mtime(os.path.join(BRAVO, "logs", b + ".log"))
        if lm and time.time() - lm < 300:
            active = True
    cert = os.path.exists(os.path.join(BRAVO, "logs", "_morning_pull_status_%s.txt" % now().date().isoformat()))
    return {"last_result": os.path.basename(last)[:-12] if last else None, "last_result_at": iso(mtime(last)) if last else None,
            "pending_triggers": len(trig), "claimed": len(claimed), "watcher_active": active, "morning_cert_today": cert}


def vitals():
    v = {}
    try:
        total = int(run(["sysctl", "-n", "hw.memsize"]).strip())
        vs = run(["vm_stat"])
        ps = int(re.search(r"page size of (\d+)", vs).group(1))
        def pg(name):
            m = re.search(name + r":\s+(\d+)", vs)
            return int(m.group(1)) * ps if m else 0
        wired, active, comp = pg("Pages wired down"), pg("Pages active"), pg("Pages occupied by compressor")
        used = wired + active + comp
        v["mem_total_gb"] = round(total / 2**30, 1)
        v["mem_used_gb"] = round(used / 2**30, 1)
        v["mem_used_pct"] = round(100.0 * used / total, 1)
        v["mem_compressed_gb"] = round(comp / 2**30, 1)
    except Exception:
        pass
    mp = run(["memory_pressure", "-Q"], 8)
    m = re.search(r"free percentage:\s*(\d+)%", mp)
    if m:
        v["mem_free_pct_sys"] = int(m.group(1))
    sw = run(["sysctl", "-n", "vm.swapusage"])
    m = re.search(r"total = ([\d.]+)M\s+used = ([\d.]+)M", sw)
    if m:
        v["swap_total_gb"] = round(float(m.group(1)) / 1024, 2)
        v["swap_used_gb"] = round(float(m.group(2)) / 1024, 2)
    try:
        la = os.getloadavg()
        v["load_1"], v["load_5"], v["load_15"] = [round(x, 2) for x in la]
        v["ncpu"] = os.cpu_count() or 1
    except Exception:
        pass
    try:
        du = shutil.disk_usage(HOME)
        v["disk_total_gb"] = round(du.total / 2**30)
        v["disk_free_gb"] = round(du.free / 2**30)
        v["disk_used_pct"] = round(100.0 * (du.total - du.free) / du.total, 1)
    except Exception:
        pass
    bt = run(["sysctl", "-n", "kern.boottime"])
    m = re.search(r"sec = (\d+)", bt)
    if m:
        v["uptime_h"] = round((time.time() - int(m.group(1))) / 3600, 1)
    return v


def recent_log_lines(agents, n=14):
    """Newest last line from the most recently written agent logs (the live ticker)."""
    cands = []
    for a in agents:
        for lg in a["logs"]:
            mt = mtime(lg)
            if mt and time.time() - mt < 6 * 3600:
                cands.append((mt, a["name"], lg))
    cands.sort(reverse=True)
    out, seen = [], set()
    for mt, name, lg in cands:
        if name in seen:
            continue
        seen.add(name)
        tl = tail_lines(lg, 1)
        if tl:
            line = re.sub(r"\s+", " ", tl[-1]).strip()
            out.append({"at": iso(mt), "agent": name, "line": line[:220]})
        if len(out) >= n:
            break
    return out


# ------------------------------------------------------------------ snapshot
def build_snapshot():
    t0 = time.time()
    expect = load_json(TRIAGE_EXPECT, {})
    agents = collect_agents(expect)
    counts = {}
    for a in agents:
        counts[a["status"]] = counts.get(a["status"], 0) + 1
    vit = vitals()
    _history.append({"t": int(t0), "mem": vit.get("mem_used_pct"), "swap": vit.get("swap_used_gb"), "load": vit.get("load_1")})
    fh = fleet_health_latest()
    fs = field_scorecard_today()
    led = ledger_open()
    reg = registry_tasks()
    pr = procs()
    br = chrome_bridge()
    bv = bravo_pipeline()
    sc = load_json(os.path.join(FLEET, "state/fleet_scorecard.json"), {})
    hist = sc.get("history", {}) or {}
    days = sorted(hist.keys())[-10:]
    streak = []
    for d in days:
        h = hist[d]
        streak.append({"day": d, "green": bool(h.get("green")), "ontime": h.get("ontime"), "total": h.get("total")})
    conn = load_json(os.path.join(FLEET, "connector_health.json"), {})
    med_state = load_json(os.path.join(FLEET, "state/fleet_medic.json"), {})
    med_actions = []
    for l in tail_lines(os.path.join(FLEET, "medic/actions.jsonl"), 40):
        try:
            med_actions.append(json.loads(l))
        except Exception:
            pass
    today = now().date().isoformat()
    medic = {"last_run": med_state.get("last_run"), "observe_only": med_state.get("observe_only", False),
             "actions": med_actions[::-1][:12],
             "today": sum(1 for x in med_actions if str(x.get("ts", "")).startswith(today) and x.get("kind") in ("restart", "reload")),
             "routed_today": sum(1 for x in med_actions if str(x.get("ts", "")).startswith(today) and x.get("kind") in ("route", "handoff", "escalate"))}

    attention = []
    for a in agents:
        if a["status"] in ("error", "notloaded", "stale"):
            attention.append({"sev": "bad" if a["status"] in ("error", "notloaded") else "warn",
                              "what": a["name"], "why": a["why"], "kind": "agent"})
    if not pr["claude_app"]:
        attention.append({"sev": "bad", "what": "Claude app", "why": "not running — cloud scheduled tasks cannot fire on this Mac", "kind": "proc"})
    if br["state"] == "disconnected":
        attention.append({"sev": "warn", "what": "Chrome extension bridge", "why": "disconnected (watchdog self-heals every 2 min)", "kind": "proc"})
    if not pr["parallels_vm"]:
        attention.append({"sev": "warn", "what": "Parallels VM", "why": "no VM process — Bravo pipeline cannot pull", "kind": "proc"})
    if fs and fs["missed"]:
        attention.append({"sev": "warn", "what": "Field scorecard", "why": "%d Tier-1 report(s) missed today" % fs["missed"], "kind": "report"})
    if led["open"]:
        attention.append({"sev": "warn", "what": "Failure ledger", "why": "%d open row(s)" % led["open"], "kind": "report"})
    if vit.get("mem_free_pct_sys") is not None and vit["mem_free_pct_sys"] < 10:
        attention.append({"sev": "warn", "what": "Memory pressure", "why": "only %d%% free system-wide" % vit["mem_free_pct_sys"], "kind": "vital"})
    if vit.get("disk_free_gb") is not None and vit["disk_free_gb"] < 60:
        attention.append({"sev": "warn", "what": "Disk", "why": "%d GB free" % vit["disk_free_gb"], "kind": "vital"})
    for hq in host_queue()["recent"][:3]:
        if hq["rc"] not in (None, 0):
            attention.append({"sev": "warn", "what": "Host queue job " + hq["job"], "why": "exited %s" % hq["rc"], "kind": "queue"})
    bad = sum(1 for x in attention if x["sev"] == "bad")
    warn = sum(1 for x in attention if x["sev"] == "warn")
    overall = "red" if bad else ("amber" if warn else "green")

    snap = {
        "generated": now().isoformat(timespec="seconds"), "host": os.uname().nodename, "build_ms": None,
        "overall": overall, "attention": attention, "counts": counts, "agents": agents,
        "vitals": vit, "history": list(_history), "procs": pr, "chrome_bridge": br, "bravo": bv,
        "fleet_health": fh, "field_scorecard": fs, "ledger": led, "human_queue": human_queue(),
        "host_queue": host_queue(), "registry": reg, "scorecard_streak": streak,
        "connectors": {"checked_at": conn.get("checked_at"), "results": conn.get("results", {})},
        "tape": recent_log_lines(agents), "refresh_s": REFRESH_S, "medic": medic,
    }
    snap["build_ms"] = int((time.time() - t0) * 1000)
    return snap


def write_state(snap):
    try:
        os.makedirs(os.path.dirname(STATE_OUT), exist_ok=True)
        slim = dict(snap)
        slim["agents"] = [{k: v for k, v in a.items() if k != "logs"} for a in snap["agents"]]
        tmp = STATE_OUT + ".tmp"
        with open(tmp, "w") as f:
            json.dump(slim, f, indent=1, default=str)
        os.replace(tmp, STATE_OUT)
    except Exception as e:
        print("state write failed: %s" % e, flush=True)


def refresher():
    global _snapshot
    last_hb = 0
    last_state = 0
    while True:
        try:
            snap = build_snapshot()
            with _lock:
                _snapshot = snap
            if time.time() - last_state > STATE_EVERY_S:
                write_state(snap)
                last_state = time.time()
            if time.time() - last_hb > HEARTBEAT_S:
                c = snap["counts"]
                print("%s heartbeat ok — %d agents (%d running, %d error, %d not loaded, %d stale) overall=%s build=%dms" % (
                    now().strftime("%Y-%m-%d %H:%M:%S"), len(snap["agents"]), c.get("running", 0), c.get("error", 0),
                    c.get("notloaded", 0), c.get("stale", 0), snap["overall"], snap["build_ms"]), flush=True)
                last_hb = time.time()
        except Exception as e:
            with _lock:
                _snapshot = {"generated": now().isoformat(timespec="seconds"), "error": "collector exception: %s" % e,
                             "trace": traceback.format_exc()[-2000:]}
            print("collector exception: %s" % e, flush=True)
        time.sleep(REFRESH_S)


# ------------------------------------------------------------------ http
class H(BaseHTTPRequestHandler):
    server_version = "FleetDeck/1.0"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/status":
            with _lock:
                body = json.dumps(_snapshot, default=str)
            return self._send(200, body, "application/json")
        if u.path == "/api/log":
            label = (parse_qs(u.query).get("label") or [""])[0]
            with _lock:
                agents = _snapshot.get("agents", [])
            a = next((x for x in agents if x["label"] == label or x["name"] == label), None)
            if not a:
                return self._send(404, json.dumps({"error": "unknown agent"}), "application/json")
            out = {}
            for lg in a["logs"]:
                out[os.path.basename(lg)] = tail_lines(lg, 60)
            return self._send(200, json.dumps({"label": a["label"], "logs": out}), "application/json")
        if u.path in ("/", "/index.html"):
            return self._send(200, HTML, "text/html; charset=utf-8")
        if u.path == "/health":
            return self._send(200, "ok", "text/plain")
        self._send(404, "not found", "text/plain")


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VP Fleet Deck</title>
<style>
:root{
  --bg:#0a0e13; --bg2:#0f141b; --panel:#131a22; --panel2:#182129; --line:#22303c; --line2:#2d3d4b;
  --ink:#e6edf3; --ink2:#9fb0bf; --muted:#5f7282;
  --gold:#c9a227; --ok:#3fb27f; --warn:#d9a13b; --bad:#d96b6b; --info:#4fa3d9; --violet:#8b7cf6;
  --mono:"JetBrains Mono","SF Mono",Menlo,ui-monospace,monospace;
  --sans:"SF Pro Display",-apple-system,"Helvetica Neue",Inter,system-ui,sans-serif;
}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:radial-gradient(1200px 700px at 70% -10%,#13202b 0%,var(--bg) 55%);color:var(--ink);font-family:var(--sans);font-size:14px;overflow:hidden}
body::after{content:"";pointer-events:none;position:fixed;inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.018) 0 1px,transparent 1px 3px);mix-blend-mode:overlay;z-index:50}
#app{display:grid;grid-template-rows:auto auto 1fr auto;height:100vh;gap:10px;padding:12px 14px}
/* header */
header{display:flex;align-items:center;gap:18px;padding:10px 16px;background:linear-gradient(90deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:12px;position:relative;overflow:hidden}
header::before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent);opacity:.8}
.brand{display:flex;flex-direction:column;line-height:1.05}
.brand b{font-family:var(--mono);font-size:19px;letter-spacing:.14em;color:var(--gold)}
.brand span{font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;color:var(--muted);margin-top:4px}
.beacon{display:flex;align-items:center;gap:12px;padding:8px 14px;border-radius:10px;border:1px solid var(--line2);background:#0c1117}
.beacon .dot{width:18px;height:18px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 4px rgba(63,178,127,.15),0 0 22px var(--ok);animation:pulse 2.2s infinite}
.beacon.amber .dot{background:var(--warn);box-shadow:0 0 0 4px rgba(217,161,59,.15),0 0 22px var(--warn)}
.beacon.red .dot{background:var(--bad);box-shadow:0 0 0 4px rgba(217,107,107,.18),0 0 26px var(--bad);animation-duration:1s}
.beacon.grey .dot{background:var(--muted);box-shadow:none;animation:none}
.beacon .txt{font-family:var(--mono);letter-spacing:.12em;font-size:15px;font-weight:700}
.beacon small{display:block;color:var(--ink2);letter-spacing:.04em;font-weight:400;font-size:11px;font-family:var(--sans)}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-left:auto}
.chip{font-family:var(--mono);font-size:12px;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:#0c1117;color:var(--ink2);display:flex;gap:7px;align-items:center;cursor:pointer;user-select:none}
.chip b{color:var(--ink);font-size:14px}
.chip i{width:8px;height:8px;border-radius:2px;display:inline-block}
.chip.active{border-color:var(--gold);color:var(--ink)}
.clock{font-family:var(--mono);text-align:right;line-height:1.15}
.clock b{font-size:26px;letter-spacing:.06em;color:var(--ink)}
.clock span{display:block;font-size:11px;color:var(--muted);letter-spacing:.1em}
/* vitals */
.vitals{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}
.v{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 12px;position:relative;overflow:hidden;min-height:78px}
.v h4{margin:0 0 6px;font-family:var(--mono);font-size:10.5px;letter-spacing:.18em;color:var(--muted);font-weight:600}
.v .big{font-family:var(--mono);font-size:22px;font-weight:700;letter-spacing:.02em}
.v .big small{font-size:12px;color:var(--ink2);font-weight:400;margin-left:4px}
.v .sub{font-size:11.5px;color:var(--ink2);margin-top:2px}
.bar{height:5px;background:#0c1117;border-radius:3px;margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--ok);border-radius:3px;transition:width .6s}
.bar i.warn{background:var(--warn)}.bar i.bad{background:var(--bad)}
.v svg{position:absolute;right:8px;bottom:8px;opacity:.9}
/* main */
main{display:grid;grid-template-columns:minmax(0,1fr) 440px;gap:10px;min-height:0}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;display:flex;flex-direction:column;min-height:0;overflow:hidden}
.panel>h3{margin:0;padding:10px 14px;font-family:var(--mono);font-size:11px;letter-spacing:.2em;color:var(--muted);border-bottom:1px solid var(--line);display:flex;align-items:center;gap:10px;font-weight:600}
.panel>h3 .r{margin-left:auto;color:var(--ink2);letter-spacing:.04em;font-weight:400;font-size:11px}
.scroll{overflow:auto;min-height:0;flex:1}
.toolbar{display:flex;gap:8px;padding:8px 12px;border-bottom:1px solid var(--line);align-items:center;flex-wrap:wrap}
.toolbar input{background:#0c1117;border:1px solid var(--line2);color:var(--ink);font-family:var(--mono);font-size:12px;padding:6px 10px;border-radius:8px;width:220px;outline:none}
.toolbar input:focus{border-color:var(--gold)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:6px;padding:10px 12px}
.tile{position:relative;background:#0c1117;border:1px solid var(--line);border-left:3px solid var(--muted);border-radius:7px;padding:7px 8px 7px 10px;cursor:pointer;transition:transform .12s,border-color .12s;min-height:52px}
.tile:hover{transform:translateY(-1px);border-color:var(--line2)}
.tile .n{font-family:var(--mono);font-size:11.5px;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tile .s{font-size:10.5px;color:var(--muted);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-family:var(--mono)}
.tile .st{position:absolute;right:7px;top:7px;font-family:var(--mono);font-size:9px;letter-spacing:.12em;padding:1px 5px;border-radius:4px;background:#121a22;color:var(--ink2)}
.tile.ok{border-left-color:var(--ok)}
.tile.running{border-left-color:var(--info);box-shadow:inset 0 0 0 1px rgba(79,163,217,.25)}
.tile.running .st{color:var(--info)}
.tile.running::after{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--info);animation:runpulse 1.4s infinite;border-radius:7px 0 0 7px}
@keyframes runpulse{0%,100%{opacity:.35}50%{opacity:1}}
.tile.error{border-left-color:var(--bad);background:linear-gradient(90deg,rgba(217,107,107,.12),#0c1117 60%)}
.tile.error .st{color:var(--bad)}
.tile.notloaded{border-left-color:var(--bad);border-style:dashed}
.tile.notloaded .st{color:var(--bad)}
.tile.stale{border-left-color:var(--warn);background:linear-gradient(90deg,rgba(217,161,59,.10),#0c1117 60%)}
.tile.stale .st{color:var(--warn)}
.tile.quiet{border-left-color:var(--violet)}
.tile.dormant,.tile.disabled{border-left-color:var(--muted);opacity:.55}
.sect{font-family:var(--mono);font-size:10px;letter-spacing:.22em;color:var(--muted);padding:10px 14px 0}
/* right column */
.right{display:grid;grid-template-rows:auto auto minmax(170px,1fr);gap:10px;min-height:0}
.att{list-style:none;margin:0;padding:6px 0}
.att li{display:flex;gap:10px;padding:7px 14px;border-bottom:1px dashed var(--line);align-items:flex-start}
.att li:last-child{border-bottom:0}
.att .sev{width:9px;height:9px;border-radius:50%;margin-top:5px;flex:none}
.att .sev.bad{background:var(--bad);box-shadow:0 0 10px var(--bad)}.att .sev.warn{background:var(--warn)}
.att b{font-family:var(--mono);font-size:12px;display:block}
.att span{font-size:11.5px;color:var(--ink2)}
.allclear{padding:18px 14px;color:var(--ok);font-family:var(--mono);letter-spacing:.1em;text-align:center}
.kv{display:grid;grid-template-columns:1fr 1fr;gap:5px;padding:8px 10px}
.k{background:#0c1117;border:1px solid var(--line);border-radius:8px;padding:5px 9px;display:flex;gap:9px;align-items:center}
.k .led{width:10px;height:10px;border-radius:50%;flex:none;background:var(--muted)}
.k .led.ok{background:var(--ok);box-shadow:0 0 8px var(--ok)}.k .led.bad{background:var(--bad);box-shadow:0 0 8px var(--bad)}.k .led.warn{background:var(--warn)}.k .led.info{background:var(--info)}
.k b{display:block;font-size:12px;font-family:var(--mono)}
.k span{display:block;font-size:10.5px;color:var(--ink2);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:165px}
table{width:100%;border-collapse:collapse;font-size:12px}
td,th{padding:5px 12px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
th{font-family:var(--mono);font-size:10px;letter-spacing:.16em;color:var(--muted);font-weight:600;position:sticky;top:0;background:var(--panel)}
td.tag{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em}
.tag.POSTED,.tag.OK{color:var(--ok)}.tag.MISSED{color:var(--bad);font-weight:700}.tag.GRACE,.tag.DUE,.tag.PENDING{color:var(--ink2)}.tag.UNVERIFIED{color:var(--warn)}
.streak{display:flex;gap:5px;padding:0 12px 10px}
.streak i{flex:1;height:10px;border-radius:3px;background:#22303c}
.streak i.g{background:var(--ok)}.streak i.r{background:var(--bad)}
/* ticker */
footer{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:8px 14px;height:118px;overflow:hidden;position:relative}
footer h3{margin:0 0 4px;font-family:var(--mono);font-size:10px;letter-spacing:.22em;color:var(--muted);font-weight:600}
.tick{font-family:var(--mono);font-size:11px;line-height:1.55;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tick b{color:var(--gold);font-weight:600}.tick time{color:var(--muted);margin-right:8px}
/* drawer */
#drawer{position:fixed;top:0;right:-560px;width:540px;height:100vh;background:#0c1117;border-left:1px solid var(--line2);box-shadow:-20px 0 60px rgba(0,0,0,.6);transition:right .25s;z-index:60;display:flex;flex-direction:column}
#drawer.open{right:0}
#drawer .hd{padding:16px 18px;border-bottom:1px solid var(--line)}
#drawer .hd b{font-family:var(--mono);font-size:15px;color:var(--gold)}
#drawer .hd .x{position:absolute;right:14px;top:12px;cursor:pointer;color:var(--muted);font-size:20px;font-family:var(--mono)}
#drawer dl{display:grid;grid-template-columns:120px 1fr;gap:4px 10px;margin:10px 0 0;font-size:12px}
#drawer dt{color:var(--muted);font-family:var(--mono);font-size:10.5px;letter-spacing:.1em}
#drawer dd{margin:0;color:var(--ink);word-break:break-all}
#drawer pre{flex:1;margin:0;padding:14px 18px;overflow:auto;font-family:var(--mono);font-size:11px;line-height:1.5;color:var(--ink2);background:#080b0f}
#drawer pre .f{color:var(--gold);display:block;margin-top:10px;letter-spacing:.1em}
.err{color:var(--bad);font-family:var(--mono);padding:14px}
#offline{position:fixed;left:50%;top:14px;transform:translateX(-50%);background:var(--bad);color:#120606;font-family:var(--mono);font-weight:700;padding:8px 16px;border-radius:8px;display:none;z-index:70;letter-spacing:.08em}
</style>
</head>
<body>
<div id="offline">COLLECTOR OFFLINE — showing last snapshot</div>
<div id="app">
  <header>
    <div class="brand"><b>VALLEY PAWN // FLEET DECK</b><span id="host">MAC STUDIO · LIVE AGENT STATUS</span></div>
    <div class="beacon grey" id="beacon"><div class="dot"></div><div class="txt" id="beacon-txt">CONNECTING<small id="beacon-sub">waiting for collector…</small></div></div>
    <div class="chips" id="chips"></div>
    <div class="clock"><b id="clock">--:--:--</b><span id="date">—</span></div>
  </header>
  <section class="vitals" id="vitals"></section>
  <main>
    <div class="panel">
      <h3>AGENT MATRIX <span class="r" id="matrix-count"></span></h3>
      <div class="toolbar">
        <input id="q" placeholder="filter agents…  (type to search)">
        <div class="chip" data-f="all">all</div><div class="chip" data-f="problems">problems</div><div class="chip" data-f="running">running</div><div class="chip" data-f="ok">healthy</div><div class="chip" data-f="dormant">dormant</div>
        <span class="r" style="margin-left:auto;color:var(--muted);font-family:var(--mono);font-size:10.5px" id="gen"></span>
      </div>
      <div class="scroll" id="matrix"></div>
    </div>
    <div class="right">
      <div class="panel"><h3>NEEDS ATTENTION <span class="r" id="att-count"></span></h3><div class="scroll" style="max-height:170px"><ul class="att" id="att"></ul></div></div>
      <div class="panel" style="max-height:300px"><h3>SYSTEMS &amp; LINKS</h3><div class="scroll"><div class="kv" id="systems"></div></div></div>
      <div class="panel"><h3>TODAY'S TIER-1 REPORTS <span class="r" id="fs-sum"></span></h3><div class="streak" id="streak" title="fleet scorecard: last 10 days (green = every report on time)"></div><div class="scroll"><table id="fs"></table></div></div>
    </div>
  </main>
  <footer><h3>LIVE LOG TAPE</h3><div id="tape"></div></footer>
</div>
<div id="drawer"><div class="hd"><span class="x" onclick="closeDrawer()">×</span><b id="d-title">—</b><dl id="d-meta"></dl></div><pre id="d-log">loading…</pre></div>
<script>
const STATUS_LABEL={ok:"OK",running:"RUN",error:"ERR",notloaded:"OFF",stale:"STALE",quiet:"QUIET",dormant:"DORMANT",disabled:"DISABLED"};
const STATUS_ORDER=["error","notloaded","stale","running","quiet","ok","dormant","disabled"];
const STATUS_COLOR={ok:"var(--ok)",running:"var(--info)",error:"var(--bad)",notloaded:"var(--bad)",stale:"var(--warn)",quiet:"var(--violet)",dormant:"var(--muted)",disabled:"var(--muted)"};
let S=null, filter="all", query="", failures=0;
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function ago(isoStr){if(!isoStr)return "never";const d=(Date.now()-new Date(isoStr).getTime())/1000;if(d<0)return "in "+fmtDur(-d);return fmtDur(d)+" ago"}
function fmtDur(s){if(s<60)return Math.round(s)+"s";if(s<3600)return Math.round(s/60)+"m";if(s<86400)return (s/3600).toFixed(s<36000?1:0)+"h";return (s/86400).toFixed(1)+"d"}
function tick(){const n=new Date();$("clock").textContent=n.toLocaleTimeString([], {hour12:false});$("date").textContent=n.toLocaleDateString([], {weekday:"long",month:"short",day:"numeric",year:"numeric"}).toUpperCase();}
setInterval(tick,1000);tick();

async function load(){
  try{
    const r=await fetch("/api/status",{cache:"no-store"});
    const d=await r.json();
    failures=0;$("offline").style.display="none";
    if(d.error){renderError(d);return}
    S=d;render();
  }catch(e){failures++;if(failures>=2)$("offline").style.display="block";}
}
function renderError(d){
  $("beacon").className="beacon grey";$("beacon-txt").firstChild.textContent="COLLECTOR ERROR";$("beacon-sub").textContent=d.error;
  $("matrix").innerHTML='<div class="err">'+esc(d.error)+'\n'+esc(d.trace||"")+'</div>';
}
function render(){
  const c=S.counts||{}, total=(S.agents||[]).length;
  // beacon
  const b=$("beacon");b.className="beacon "+S.overall;
  const bad=S.attention.filter(a=>a.sev==="bad").length, warn=S.attention.filter(a=>a.sev==="warn").length;
  $("beacon-txt").firstChild.textContent=S.overall==="green"?"ALL SYSTEMS NOMINAL":S.overall==="amber"?"ATTENTION ADVISED":"ACTION REQUIRED";
  $("beacon-sub").textContent=S.overall==="green"?total+" agents watched · nothing needs you":(bad?bad+" critical · ":"")+warn+" to review";
  $("host").textContent=(S.host||"MAC STUDIO").toUpperCase()+" · LIVE AGENT STATUS · refresh "+S.refresh_s+"s";
  $("gen").textContent="snapshot "+S.generated.slice(11,19)+" · built in "+S.build_ms+"ms";
  // chips
  $("chips").innerHTML=STATUS_ORDER.filter(k=>c[k]).map(k=>`<div class="chip ${filter===k?'active':''}" data-f="${k}"><i style="background:${STATUS_COLOR[k]}"></i>${STATUS_LABEL[k]} <b>${c[k]}</b></div>`).join("")+`<div class="chip"><i style="background:var(--gold)"></i>TOTAL <b>${total}</b></div>`;
  document.querySelectorAll(".chip[data-f]").forEach(el=>el.onclick=()=>{filter=el.dataset.f===filter&&el.dataset.f!=="all"?"all":el.dataset.f;render()});
  renderVitals();renderMatrix();renderAttention();renderSystems();renderScorecard();renderTape();
}
function spark(hist,key,color){
  const v=hist.map(h=>h[key]).filter(x=>x!=null);if(v.length<3)return "";
  const w=90,h=28,mx=Math.max(...v),mn=Math.min(...v),rg=(mx-mn)||1;
  const pts=v.map((x,i)=>`${(i/(v.length-1)*w).toFixed(1)},${(h-2-(x-mn)/rg*(h-4)).toFixed(1)}`).join(" ");
  return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"><polyline points="${pts}" fill="none" stroke="${color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" opacity=".85"/></svg>`;
}
function renderVitals(){
  const v=S.vitals||{},hist=S.history||[];
  const memPct=v.mem_used_pct, free=v.mem_free_pct_sys;
  const memCls=free!=null?(free<10?"bad":free<20?"warn":""):(memPct>90?"bad":memPct>80?"warn":"");
  const swap=v.swap_used_gb??0, swapCls=swap>4?"bad":swap>1.5?"warn":"";
  const load=v.load_1, ncpu=v.ncpu||10, loadCls=load>ncpu?"bad":load>ncpu*0.7?"warn":"";
  const dCls=v.disk_free_gb<60?"bad":v.disk_free_gb<150?"warn":"";
  const run=(S.counts||{}).running||0, err=((S.counts||{}).error||0)+((S.counts||{}).notloaded||0);
  const reg=S.registry||{};
  $("vitals").innerHTML=`
  <div class="v"><h4>MEMORY</h4><div class="big">${memPct??"—"}<small>% used</small></div><div class="sub">${v.mem_used_gb??"?"} / ${v.mem_total_gb??"?"} GB${free!=null?" · "+free+"% free (sys)":""}${v.mem_compressed_gb?" · "+v.mem_compressed_gb+" GB compressed":""}</div><div class="bar"><i class="${memCls}" style="width:${memPct||0}%"></i></div>${spark(hist,"mem","var(--info)")}</div>
  <div class="v"><h4>SWAP</h4><div class="big">${swap.toFixed(1)}<small>GB</small></div><div class="sub">of ${v.swap_total_gb??"?"} GB allocated</div><div class="bar"><i class="${swapCls}" style="width:${v.swap_total_gb?Math.min(100,swap/v.swap_total_gb*100):0}%"></i></div>${spark(hist,"swap","var(--violet)")}</div>
  <div class="v"><h4>CPU LOAD</h4><div class="big">${load??"—"}<small>/ ${ncpu} cores</small></div><div class="sub">5m ${v.load_5??"—"} · 15m ${v.load_15??"—"}</div><div class="bar"><i class="${loadCls}" style="width:${Math.min(100,(load||0)/ncpu*100)}%"></i></div>${spark(hist,"load","var(--gold)")}</div>
  <div class="v"><h4>DISK</h4><div class="big">${v.disk_free_gb??"—"}<small>GB free</small></div><div class="sub">${v.disk_used_pct??"?"}% of ${v.disk_total_gb??"?"} GB used</div><div class="bar"><i class="${dCls}" style="width:${v.disk_used_pct||0}%"></i></div></div>
  <div class="v"><h4>UPTIME</h4><div class="big">${v.uptime_h!=null?(v.uptime_h>48?(v.uptime_h/24).toFixed(1)+"<small>days</small>":v.uptime_h+"<small>h</small>"):"—"}</div><div class="sub">Mac Studio since last boot</div></div>
  <div class="v"><h4>AGENTS</h4><div class="big">${(S.agents||[]).length}<small>native</small></div><div class="sub"><span style="color:var(--info)">${run} running</span> · <span style="color:${err?'var(--bad)':'var(--ink2)'}">${err} failing</span> · ${(S.counts||{}).dormant||0} dormant</div></div>
  <div class="v"><h4>CLOUD TASKS</h4><div class="big">${reg.found?reg.enabled.length:"—"}<small>enabled</small></div><div class="sub">${reg.found?reg.total+" registered · "+reg.disabled+" off · "+reg.skips_7d+" skips/7d":"registry not readable"}</div></div>`;
}
function matches(a){
  if(query&&!(a.name+" "+a.schedule+" "+a.status).toLowerCase().includes(query))return false;
  if(filter==="all")return true;
  if(filter==="problems")return ["error","notloaded","stale"].includes(a.status);
  return a.status===filter;
}
function renderMatrix(){
  const list=(S.agents||[]).filter(matches);
  $("matrix-count").textContent=list.length+" shown";
  const groups={};list.forEach(a=>(groups[a.status]=groups[a.status]||[]).push(a));
  let html="";
  STATUS_ORDER.forEach(k=>{if(!groups[k])return;
    html+=`<div class="sect">${STATUS_LABEL[k]} · ${groups[k].length}</div><div class="grid">`+groups[k].map(a=>`<div class="tile ${a.status}" onclick="openDrawer('${esc(a.label)}')" title="${esc(a.why||"")}">
      <div class="n">${esc(a.name)}</div><div class="s">${esc(a.status==="running"?"pid "+a.pid+" · "+(a.schedule||""):a.status==="error"?"exit "+a.last_exit+" · "+ago(a.last_activity):a.status==="stale"?"quiet "+ago(a.last_activity).replace(" ago",""):(a.schedule||"")+(a.next_fire?" · next "+a.next_fire.slice(5,16).replace("T"," "):""))}</div><span class="st">${STATUS_LABEL[a.status]}</span></div>`).join("")+"</div>";
  });
  $("matrix").innerHTML=html||'<div class="allclear">no agents match</div>';
}
function renderAttention(){
  const at=S.attention||[];$("att-count").textContent=at.length?at.length+" item"+(at.length>1?"s":""):"";
  $("att").innerHTML=at.length?at.map(a=>`<li><span class="sev ${a.sev}"></span><div><b>${esc(a.what)}</b><span>${esc(a.why)}</span></div></li>`).join(""):'<div class="allclear">✓ NOTHING NEEDS YOU</div>';
}
function led(ok,warn){return ok===true?"ok":ok===false?(warn?"warn":"bad"):"warn"}
function renderSystems(){
  const p=S.procs||{},br=S.chrome_bridge||{},bv=S.bravo||{},hq=S.host_queue||{},reg=S.registry||{},fh=S.fleet_health,cn=S.connectors||{},hqq=S.human_queue||{},led_=S.ledger||{};
  const connBad=Object.entries(cn.results||{}).filter(([k,v])=>v!=="ok");
  const items=[
    ["Claude app",p.claude_app?"running":"NOT RUNNING",led(p.claude_app)],
    ["Chrome bridge",br.state+(br.since?" · "+br.since.slice(5,16):""),br.state==="connected"?"ok":br.state==="disconnected"?"warn":"warn"],
    ["Parallels / Bravo VM",p.parallels_vm?(bv.watcher_active?"VM up · watcher busy":"VM up · idle"):"VM not running",p.parallels_vm?(bv.watcher_active?"info":"ok"):"warn"],
    ["Bravo pipeline",bv.last_result?"last result "+ago(bv.last_result_at)+(bv.pending_triggers?" · "+bv.pending_triggers+" queued":""):"no results found",bv.last_result_at&&(Date.now()-new Date(bv.last_result_at))<36*3600e3?"ok":"warn"],
    ["Morning pull cert",bv.morning_cert_today?"today ✓":"none yet today",bv.morning_cert_today?"ok":(new Date().getHours()>=9?"warn":"info")],
    ["Host job queue",(hq.pending||[]).length+" pending · last "+((hq.recent||[])[0]?(hq.recent[0].rc===0?"ok":"rc "+hq.recent[0].rc)+" "+ago(hq.recent[0].when):"—"),(hq.recent||[])[0]&&hq.recent[0].rc!==0?"warn":"ok"],
    ["Fleet health sentinel",fh?(fh.green?"all green":fh.items.length+" issue"+(fh.items.length>1?"s":""))+" · "+fh.header.slice(0,16):"no report",fh?(fh.green?"ok":"warn"):"warn"],
    ["Connectors",cn.checked_at?(connBad.length?connBad.map(x=>x[0]).join(", ")+" failing":Object.keys(cn.results).length+" ok · "+String(cn.checked_at).slice(5,16)):"no check yet",cn.checked_at?(connBad.length?"bad":"ok"):"warn"],
    ["Failure ledger",led_.open+" open row"+(led_.open===1?"":"s"),led_.open?"warn":"ok"],
    ["Human queue",hqq.open_rows+" open · "+ago(hqq.mtime).replace(" ago"," since touch"),hqq.open_rows?"info":"ok"],
    ["Ollama (local AI)",p.ollama?"running":"stopped",p.ollama?"ok":"info"],
    ["Cloud registry",reg.found?"readable · "+ago(reg.file_mtime):"NOT FOUND",reg.found?"ok":"bad"],
    ["Fleet medic",S.medic&&S.medic.last_run?(S.medic.observe_only?"OBSERVE ONLY · ":"")+"ran "+ago(S.medic.last_run)+" · "+S.medic.today+" fixed, "+S.medic.routed_today+" handed off today":"not running yet",S.medic&&S.medic.last_run&&(Date.now()-new Date(S.medic.last_run))<15*60e3?(S.medic.observe_only?"warn":"ok"):"bad"],
  ];
  $("systems").innerHTML=items.map(([k,v,l])=>`<div class="k"><span class="led ${l}"></span><div><b>${esc(k)}</b><span title="${esc(v)}">${esc(v)}</span></div></div>`).join("");
}
function renderScorecard(){
  const fs=S.field_scorecard;
  $("streak").innerHTML=(S.scorecard_streak||[]).map(d=>`<i class="${d.green?'g':(d.total?'r':'')}" title="${d.day}: ${d.ontime??'?'} / ${d.total??'?'} on time"></i>`).join("")||"";
  if(!fs){$("fs").innerHTML="";$("fs-sum").textContent="no scorecard";return}
  $("fs-sum").textContent=fs.posted+" posted · "+fs.missed+" missed";
  const order={MISSED:0,"IN GRACE":2,"NOT DUE YET":3,UNVERIFIED:1,POSTED:4};
  const rows=[...fs.rows].sort((a,b)=>(order[a.status.split(" TODAY")[0]]??2)-(order[b.status.split(" TODAY")[0]]??2)||a.sched.localeCompare(b.sched));
  $("fs").innerHTML="<tr><th>report</th><th>status</th><th>due</th></tr>"+rows.map(r=>`<tr><td title="${esc(r.note)}">${esc(r.task)}</td><td class="tag ${esc(r.status.split(" ")[0])} ${r.status.includes('GRACE')?'GRACE':''} ${r.status.includes('DUE')?'DUE':''}">${esc(r.status)}</td><td style="color:var(--muted)">${esc(r.sched)}</td></tr>`).join("");
}
function renderTape(){
  const med=((S.medic||{}).actions||[]).filter(x=>(Date.now()-new Date(x.ts))<6*3600e3).slice(0,3).map(x=>({at:x.ts,agent:"⚕ medic → "+x.agent,line:x.what+(x.ok?"":" (failed)"),med:1}));
  const lines=[...med,...(S.tape||[])];
  $("tape").innerHTML=lines.slice(0,6).map(l=>`<div class="tick"${l.med?' style="color:var(--ok)"':''}><time>${esc((l.at||"").slice(11,19))}</time><b${l.med?' style="color:var(--ok)"':''}>${esc(l.agent)}</b> ${esc(l.line)}</div>`).join("")||'<div class="tick" style="color:var(--muted)">no log writes in the last 6 h</div>';
}
async function openDrawer(label){
  const a=(S.agents||[]).find(x=>x.label===label);if(!a)return;
  $("d-title").textContent=a.name;
  $("d-meta").innerHTML=[["status",STATUS_LABEL[a.status]+(a.why?" — "+a.why:"")],["schedule",a.schedule||"—"],["next fire",a.next_fire?a.next_fire.replace("T"," "):"—"],["last activity",a.last_activity?a.last_activity.replace("T"," ")+" ("+ago(a.last_activity)+")":"never"],["last exit",a.last_exit??"—"],["pid",a.pid??"—"],["program",a.program||"—"],["gate",a.gate||"—"],["label",a.label]].map(([k,v])=>`<dt>${k}</dt><dd>${esc(v)}</dd>`).join("");
  $("d-log").textContent="loading log tail…";$("drawer").classList.add("open");
  try{const r=await fetch("/api/log?label="+encodeURIComponent(a.label));const d=await r.json();
    const parts=Object.entries(d.logs||{});
    $("d-log").innerHTML=parts.length?parts.map(([f,ls])=>`<span class="f">▍ ${esc(f)}</span>`+esc(ls.join("\n"))).join("\n"):"(no log files found for this agent)";
    $("d-log").scrollTop=$("d-log").scrollHeight;
  }catch(e){$("d-log").textContent="could not load log: "+e}
}
function closeDrawer(){$("drawer").classList.remove("open")}
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDrawer()});
$("q").addEventListener("input",e=>{query=e.target.value.trim().toLowerCase();if(S)renderMatrix()});
document.querySelectorAll(".toolbar .chip").forEach(el=>el.onclick=()=>{filter=el.dataset.f;document.querySelectorAll(".toolbar .chip").forEach(x=>x.classList.toggle("active",x===el));if(S)render()});
load();setInterval(load,20000);
</script>
</body>
</html>
"""


def main():
    global PORT
    a = sys.argv[1:]
    if "--port" in a:
        PORT = int(a[a.index("--port") + 1])
    if "--once" in a:
        print(json.dumps(build_snapshot(), indent=1, default=str))
        return 0
    th = threading.Thread(target=refresher, daemon=True)
    th.start()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print("%s fleet-deck serving http://127.0.0.1:%d" % (now().strftime("%Y-%m-%d %H:%M:%S"), PORT), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
