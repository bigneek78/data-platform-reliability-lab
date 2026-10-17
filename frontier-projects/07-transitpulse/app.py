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
    arrivals=d['arrivals'];target=number(d['target'],'target',0);hold=number(d['max_hold'],'max_hold',0)
    if target<=0: raise ValueError("Positive target required")
    for x in arrivals: number(x,'arrival',0)
    if any(a>b for a,b in zip(arrivals,arrivals[1:])): raise ValueError("Arrivals must be ordered")
    payload=f"{target} {hold} {len(arrivals)}\n"+' '.join(map(str,arrivals))+'\n'
    proc=subprocess.run(['java','--source','17',str(Path(__file__).parent/'Transit.java')],input=payload,capture_output=True,text=True,check=True)
    departures=json.loads(proc.stdout);raw=[b-a for a,b in zip(arrivals,arrivals[1:])];controlled=[b-a for a,b in zip(departures,departures[1:])]
    def rmse(xs): return (sum((x-target)**2 for x in xs)/len(xs))**.5 if xs else 0
    return {'departures':departures,'metrics':{'arrival_headway_rmse':rmse(raw),'departure_headway_rmse':rmse(controlled),'total_hold_minutes':sum(b-a for a,b in zip(arrivals,departures))},'trace':[dict(arrival=a,departure=b,hold=b-a) for a,b in zip(arrivals,departures)]}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
