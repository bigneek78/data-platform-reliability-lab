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


from functools import lru_cache
def run(d):
    slots,requests=d['slots'],d['requests'];unique(slots);unique(requests)
    if len(slots)>16 or len(requests)>16: raise ValueError("Exact demo limited to 16 slots and requests")
    for s in slots: number(s['time'],'slot time',0)
    for q in requests:
        number(q['earliest'],'earliest',0);number(q['latest'],'latest',0)
        if q['latest']<q['earliest']: raise ValueError("Invalid request window")
    def eligible(q,s): return q['earliest']<=s['time']<=q['latest'] and set(q['resources'])<=set(s['resources'])
    @lru_cache(None)
    def best(i,mask):
        if i==len(requests): return (0,0,())
        b,w,tail=best(i+1,mask);options=[(b,w,(-1,)+tail)]
        for j,s in enumerate(slots):
            if mask>>j&1 or not eligible(requests[i],s): continue
            b,w,tail=best(i+1,mask|1<<j);options.append((b+1,w+s['time']-requests[i]['earliest'],(j,)+tail))
        return min(options,key=lambda x:(-x[0],x[1],x[2]))
    count,wait,assignment=best(0,0);bookings=[];unbooked=[]
    for q,j in zip(requests,assignment):
        if j<0: unbooked.append(q['id'])
        else: bookings.append({'request':q['id'],'slot':slots[j]['id'],'time':slots[j]['time'],'wait':slots[j]['time']-q['earliest']})
    return {'bookings':bookings,'unbooked':unbooked,'metrics':{'booked':count,'unbooked':len(unbooked),'total_wait_units':wait},'trace':bookings}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
