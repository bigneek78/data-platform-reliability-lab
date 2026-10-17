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
    number(d['retry'],'retry',0)
    if d['retry']<=0: raise ValueError("Positive retry delay required")
    previous=-1
    for e in d['events']:
        t=number(e['time'],'time',0)
        if t<previous: raise ValueError("Events must be ordered")
        previous=t
        if e['op'] not in ('enqueue','tick','ack'): raise ValueError("Unknown operation")
        if e['op']=='tick':
            if not isinstance(e['online'],bool): raise ValueError("online must be boolean")
        else:
            if not isinstance(e['id'],str) or not e['id']: raise ValueError("Message id required")
        if e['op']=='enqueue':
            number(e['ttl'],'ttl',0)
            if e['ttl']<=0 or not isinstance(e['body'],str): raise ValueError("Positive TTL and text body required")
    proc=subprocess.run(['node',str(Path(__file__).parent/'queue.ts')],input=json.dumps(d),capture_output=True,text=True,check=True)
    return json.loads(proc.stdout)

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
