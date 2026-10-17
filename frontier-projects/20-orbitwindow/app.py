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


from bisect import bisect_right
def run(d):
    windows=d['windows'];unique(windows);blackouts=d['blackouts']
    for x in windows+blackouts:
        number(x['start'],'start',0);number(x['end'],'end',0)
        if x['end']<=x['start']: raise ValueError("Nonempty time interval required")
    for w in windows: number(w['value'],'value',0)
    excluded=[w['id'] for w in windows if any(w['start']<b['end'] and w['end']>b['start'] for b in blackouts)]
    eligible=sorted([w for w in windows if w['id'] not in excluded],key=lambda x:(x['end'],x['start'],x['id']));ends=[x['end'] for x in eligible];dp=[(0,())]
    for i,w in enumerate(eligible):
        prev=bisect_right(ends,w['start'],0,i);value,selection=dp[prev];take=(value+w['value'],selection+(i,));skip=dp[-1]
        dp.append(min((take,skip),key=lambda x:(-x[0],x[1])))
    value,selection=dp[-1];chosen=[eligible[i] for i in selection]
    return {'selected':[x['id'] for x in chosen],'excluded_by_blackout':excluded,'metrics':{'total_value':value,'selected_contacts':len(chosen),'selected_minutes':sum(x['end']-x['start'] for x in chosen),'blackout_excluded':len(excluded)},'trace':chosen,'scope':'Fictional opportunities; no orbit propagation, link budget, flight qualification, or live satellite commands.'}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
