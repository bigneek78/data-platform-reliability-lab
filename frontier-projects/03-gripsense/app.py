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


def run(d):
    xs=d['readings'];n=integer(d['calibration'],'calibration',2)
    alpha=number(d['alpha'],'alpha',0);threshold=number(d['threshold'],'threshold',0)
    if not 0<alpha<=1 or threshold<=0 or n>=len(xs): raise ValueError("Invalid detector configuration")
    for x in xs: number(x,'reading')
    baseline=sum(xs[:n])/n;trace=[];alerts=[]
    for i,x in enumerate(xs):
        residual=x-baseline;flag=i>=n and abs(residual)>threshold
        if flag: alerts.append(i)
        if i>=n and not flag: baseline=alpha*x+(1-alpha)*baseline
        trace.append({'sample':i,'value':x,'baseline':baseline,'flag':flag,'residual':residual})
    return {'alerts':alerts,'metrics':{'flagged_samples':len(alerts),'reviewed_samples':len(xs)-n},'trace':trace}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
