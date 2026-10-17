import json, math, sys
from pathlib import Path

def number(x, name, minimum=None):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError(name + " must be a finite number")
    if minimum is not None and x < minimum:
        raise ValueError(name + " is below its minimum")
    return x

def integer(x, name, minimum=0):
    number(x, name, minimum)
    if not isinstance(x, int):
        raise ValueError(name + " must be an integer")
    return x

def unique(items, name="id"):
    values = [x[name] for x in items]
    if any(not isinstance(x, str) or not x for x in values) or len(set(values)) != len(values):
        raise ValueError("Identifiers must be nonempty unique strings")


import subprocess
def run(d):
    limit=number(d['max_age'],'max_age',0);events=d['events'];previous=-1
    for e in events:
        t=number(e['time'],'time',0);number(e['age'],'age',0)
        if t<previous: raise ValueError("Events must be ordered")
        previous=t
        if not isinstance(e['estop'],bool) or not isinstance(e['reset'],bool): raise ValueError("Boolean control required")
    home=Path(__file__).parent;build=home/'.build';build.mkdir(exist_ok=True);exe=build/'watchdog'
    if not exe.exists() or exe.stat().st_mtime < (home/'watchdog.c').stat().st_mtime:
        subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(home/'watchdog.c'),'-o',str(exe)],check=True,capture_output=True,text=True)
    payload=f"{limit} {len(events)}\n"+'\n'.join(f"{e['age']} {int(e['estop'])} {int(e['reset'])}" for e in events)+'\n'
    states=json.loads(subprocess.run([str(exe)],input=payload,capture_output=True,text=True,check=True).stdout)
    trace=[dict(time=e['time'],state=s,age=e['age']) for e,s in zip(events,states)]
    return {'trace':trace,'metrics':{'stopped_events':states.count('STOP'),'ready_events':states.count('READY')}}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
