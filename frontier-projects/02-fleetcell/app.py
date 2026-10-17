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
    robots,jobs=d['robots'],d['jobs'];unique(robots);unique(jobs)
    if len(robots)>16 or len(jobs)>len(robots): raise ValueError("Assignment size outside demo limit")
    for item in robots+jobs:
        number(item['x'],'x');number(item['y'],'y')
    def cost(i,j):
        r,t=robots[i],jobs[j]
        return abs(r['x']-t['x'])+abs(r['y']-t['y']) if t['skill'] in r['skills'] else math.inf
    @lru_cache(None)
    def best(j,mask):
        if j==len(jobs): return (0,())
        options=[]
        for i in range(len(robots)):
            if mask>>i&1 or not math.isfinite(cost(i,j)): continue
            tail,allocation=best(j+1,mask|1<<i)
            options.append((cost(i,j)+tail,(i,)+allocation))
        return min(options,default=(math.inf,()))
    total,indices=best(0,0)
    if not math.isfinite(total): raise ValueError("No capability-feasible complete assignment")
    used=set();greedy=0
    for j in range(len(jobs)):
        options=[(cost(i,j),i) for i in range(len(robots)) if i not in used and math.isfinite(cost(i,j))]
        if not options: greedy=None;break
        c,i=min(options);used.add(i);greedy+=c
    assignments=[{'job':jobs[j]['id'],'robot':robots[i]['id'],'distance':cost(i,j)} for j,i in enumerate(indices)]
    return {'assignments':assignments,'metrics':{'optimal_distance':total,'greedy_distance':greedy},'trace':[x['distance'] for x in assignments]}

if __name__ == "__main__":
    try:
        fixture = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "fixtures/demo.json"
        print(json.dumps(run(json.loads(fixture.read_text())), indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, RuntimeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
