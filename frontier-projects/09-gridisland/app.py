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
    demand,solar,price=d['demand'],d['solar'],d['price'];n=len(demand)
    if not n or len(solar)!=n or len(price)!=n: raise ValueError("Aligned nonempty series required")
    for k in ('capacity','initial','reserve','terminal','rate','grid_limit'): integer(d[k],k)
    if not d['reserve']<=d['initial']<=d['capacity'] or not d['reserve']<=d['terminal']<=d['capacity']: raise ValueError("SOC outside bounds")
    for x in demand+solar: integer(x,'energy')
    for x in price: number(x,'price',0)
    states={d['initial']:(0,[])}
    for h in range(n):
        nxt={}
        for soc,(cost,path) in states.items():
            for after in range(d['reserve'],d['capacity']+1):
                delta=after-soc
                if abs(delta)>d['rate']: continue
                grid=max(0,demand[h]+delta-solar[h]);curtail=max(0,solar[h]-demand[h]-delta)
                if grid>d['grid_limit']: continue
                candidate=(cost+grid*price[h],path+[{'hour':h,'soc_before':soc,'soc_after':after,'grid':grid,'curtailed':curtail,'demand':demand[h],'solar':solar[h]}])
                if after not in nxt or candidate[0]<nxt[after][0]: nxt[after]=candidate
        states=nxt
    feasible=[(cost,soc,path) for soc,(cost,path) in states.items() if soc>=d['terminal']]
    if not feasible: raise ValueError("No feasible schedule under reserve and grid limits")
    cost,soc,path=min(feasible,key=lambda x:(x[0],x[1]))
    baseline=sum(max(0,a-b)*p for a,b,p in zip(demand,solar,price))
    return {'metrics':{'dispatch_cost_units':cost,'no_battery_cost_units':baseline,'terminal_soc':soc,'imported_kwh':sum(x['grid'] for x in path)},'trace':path,'assumptions':['one-hour slots','integer kWh','ideal 100-percent battery efficiency','no export revenue']}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
