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


from statistics import median
def run(d):
    base=d['baseline'];xs=d['readings'];threshold=number(d['threshold'],'threshold',0);resolution=number(d['resolution'],'resolution',0)
    if len(base)<5 or threshold<=0 or resolution<=0: raise ValueError("Positive configuration and five baseline points required")
    for x in base: number(x,'baseline',0)
    center=median(base);scale=max(1.4826*median([abs(x-center) for x in base]),resolution);trace=[]
    for i,x in enumerate(xs):
        if x is None: trace.append({'sample':i,'pressure':None,'score':None,'state':'UNKNOWN'});continue
        number(x,'pressure',0);score=abs(x-center)/scale
        trace.append({'sample':i,'pressure':x,'score':score,'state':'REVIEW' if score>threshold else 'WITHIN_BASELINE'})
    return {'baseline':{'median':center,'scale':scale},'metrics':{'review_readings':sum(x['state']=='REVIEW' for x in trace),'unknown_readings':sum(x['state']=='UNKNOWN' for x in trace),'observed_readings':sum(x['pressure'] is not None for x in trace)},'trace':trace}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
