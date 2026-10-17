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


import sqlite3
def run(d):
    lots,requests=d['lots'],d['requests'];unique(lots);unique(requests);horizon=integer(d['horizon'],'horizon')
    for lot in lots:
        for k in ('available','expires','units'): integer(lot[k],k)
        if lot['expires']<=lot['available']: raise ValueError("Lot must expire after availability")
    for q in requests:
        integer(q['time'],'request time');integer(q['units'],'request units')
        if q['time']>horizon: raise ValueError("Request after reporting horizon")
    db=sqlite3.connect(':memory:');db.executescript((Path(__file__).parent/'schema.sql').read_text())
    allocations=[];unmet={};trace=[]
    with db:
        db.executemany('INSERT INTO lot VALUES (?,?,?,?)',[(x['id'],x['available'],x['expires'],x['units']) for x in lots])
        for q in sorted(requests,key=lambda x:(x['time'],x['id'])):
            needed=q['units']
            eligible=db.execute('SELECT id, units FROM lot WHERE available<=? AND expires>? AND units>0 ORDER BY expires,id',(q['time'],q['time'])).fetchall()
            for ident,units in eligible:
                take=min(needed,units)
                if not take: break
                db.execute('UPDATE lot SET units=units-? WHERE id=?',(take,ident));allocations.append({'request':q['id'],'lot':ident,'time':q['time'],'units':take});needed-=take
            unmet[q['id']]=needed;trace.append({'request':q['id'],'fulfilled':q['units']-needed,'unmet':needed})
        remaining=db.execute('SELECT COALESCE(SUM(units),0) FROM lot').fetchone()[0]
        expired=db.execute('SELECT COALESCE(SUM(units),0) FROM lot WHERE expires<=?',(horizon,)).fetchone()[0]
    db.close()
    return {'allocations':allocations,'unmet':unmet,'metrics':{'allocated_units':sum(x['units'] for x in allocations),'unmet_units':sum(unmet.values()),'remaining_units':remaining,'expired_remaining_units':expired},'trace':trace}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
