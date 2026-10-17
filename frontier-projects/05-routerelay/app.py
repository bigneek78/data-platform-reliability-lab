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
    nodes=d['nodes'];edges=d['edges'];unique(edges)
    if len(nodes)!=len(set(nodes)) or d['start'] not in nodes or d['goal'] not in nodes: raise ValueError("Invalid nodes")
    for e in edges:
        number(e['cost'],'cost',0)
        if e['source'] not in nodes or e['target'] not in nodes: raise ValueError("Unknown endpoint")
    if set(d.get('closed',[]))-{e['id'] for e in edges}: raise ValueError("Unknown closure")
    proc=subprocess.run(['node',str(Path(__file__).parent/'route.mjs')],input=json.dumps(d),text=True,capture_output=True,check=True)
    result=json.loads(proc.stdout)
    return {**result,'metrics':{'route_cost':result['cost'],'edges_used':max(0,len(result['path'])-1)},'trace':result['settled']}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
